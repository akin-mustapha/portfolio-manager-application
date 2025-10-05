from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
import redis
import httpx

from app.core.deps import get_redis, security, get_current_user_id, get_current_session
from app.core.logging import get_context_logger
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_refresh_token,
    encrypt_api_key,
    generate_session_id
)
from app.core.config import settings
from app.models.auth import (
    SessionCreate,
    SessionResponse,
    TokenRefresh,
    TokenResponse,
    Trading212APISetup,
    Trading212APIResponse,
    SessionInfo,
    APIKeyValidation,
    SessionUpdate
)

# Initialize logger for authentication events
logger = get_context_logger(__name__)

router = APIRouter()


@router.post("/session", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Create a new user session with JWT tokens
    """
    logger.info(
        "Session creation attempt started",
        extra={
            'session_name': session_data.session_name,
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }
    )
    
    try:
        # Generate unique session ID
        session_id = generate_session_id()
        
        # Create JWT tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(session_id, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(session_id)
        
        # Store session data in Redis
        session_key = f"session:{session_id}"
        session_info = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "session_name": session_data.session_name or "Default Session",
            "trading212_connected": "false"
        }
        
        # Set session with 7 days expiration (same as refresh token)
        redis_client.hset(session_key, mapping=session_info)
        redis_client.expire(session_key, 7 * 24 * 60 * 60)  # 7 days
        
        logger.info(
            "Session created successfully",
            extra={
                'session_id': session_id,
                'session_name': session_data.session_name or "Default Session",
                'expires_in_seconds': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                'session_expiry_days': 7
            }
        )
        
        return SessionResponse(
            session_id=session_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(
            "Session creation failed",
            extra={
                'session_name': session_data.session_name,
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Refresh access token using refresh token
    """
    logger.debug(
        "Token refresh attempt started",
        extra={
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }
    )
    
    try:
        # Verify refresh token
        session_id = verify_refresh_token(token_data.refresh_token)
        if not session_id:
            logger.warning(
                "Token refresh failed - invalid refresh token",
                extra={
                    'client_ip': request.client.host if request.client else None,
                    'failure_reason': 'invalid_refresh_token'
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if session exists
        session_key = f"session:{session_id}"
        if not redis_client.exists(session_key):
            logger.warning(
                "Token refresh failed - session not found",
                extra={
                    'session_id': session_id,
                    'client_ip': request.client.host if request.client else None,
                    'failure_reason': 'session_not_found'
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or not found"
            )
        
        # Update last activity
        redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(session_id, expires_delta=access_token_expires)
        
        logger.info(
            "Token refresh successful",
            extra={
                'session_id': session_id,
                'new_token_expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already logged above)
        raise
    except Exception as e:
        logger.error(
            "Token refresh failed with unexpected error",
            extra={
                'error_type': type(e).__name__,
                'error_message': str(e),
                'client_ip': request.client.host if request.client else None
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/session/info", response_model=SessionInfo)
async def get_session_info(
    session_data: dict = Depends(get_current_session)
) -> Any:
    """
    Get current session information
    """
    return SessionInfo(
        session_id=session_data["session_id"],
        created_at=datetime.fromisoformat(session_data["created_at"]),
        last_activity=datetime.fromisoformat(session_data["last_activity"]),
        trading212_connected=session_data.get("trading212_connected", "false") == "true",
        session_name=session_data.get("session_name")
    )


@router.put("/session/info", response_model=SessionInfo)
async def update_session_info(
    update_data: SessionUpdate,
    user_id: str = Depends(get_current_user_id),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Update session information
    """
    session_key = f"session:{user_id}"
    
    # Update session name if provided
    if update_data.session_name is not None:
        redis_client.hset(session_key, "session_name", update_data.session_name)
    
    # Update last activity
    redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
    
    # Get updated session data
    session_data = redis_client.hgetall(session_key)
    
    return SessionInfo(
        session_id=session_data["session_id"],
        created_at=datetime.fromisoformat(session_data["created_at"]),
        last_activity=datetime.fromisoformat(session_data["last_activity"]),
        trading212_connected=session_data.get("trading212_connected", "false") == "true",
        session_name=session_data.get("session_name")
    )


@router.delete("/session")
async def delete_session(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Delete current session and logout user
    """
    logger.info(
        "Session deletion requested",
        extra={
            'session_id': user_id,
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }
    )
    
    try:
        session_key = f"session:{user_id}"
        
        # Get session info before deletion for logging
        session_data = redis_client.hgetall(session_key)
        session_name = session_data.get("session_name", "Unknown") if session_data else "Unknown"
        
        # Delete session
        deleted_count = redis_client.delete(session_key)
        
        if deleted_count > 0:
            logger.info(
                "Session deleted successfully",
                extra={
                    'session_id': user_id,
                    'session_name': session_name,
                    'logout_type': 'user_initiated'
                }
            )
        else:
            logger.warning(
                "Session deletion attempted but session not found",
                extra={
                    'session_id': user_id,
                    'logout_type': 'session_not_found'
                }
            )
        
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        logger.error(
            "Session deletion failed",
            extra={
                'session_id': user_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.post("/trading212/setup", response_model=Trading212APIResponse)
async def setup_trading212_api(
    api_setup: Trading212APISetup,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Set up Trading 212 API key and validate connection
    """
    logger.info(
        "Trading 212 API key setup attempt started",
        extra={
            'session_id': user_id,
            'validate_connection': api_setup.validate_connection,
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }
    )
    
    try:
        session_key = f"session:{user_id}"
        
        # Validate API key if requested
        account_info = None
        if api_setup.validate_connection:
            logger.debug(
                "Validating Trading 212 API key",
                extra={'session_id': user_id}
            )
            
            validation_result = await validate_trading212_api_key(api_setup.api_key)
            if not validation_result.is_valid:
                logger.warning(
                    "Trading 212 API key validation failed",
                    extra={
                        'session_id': user_id,
                        'validation_error': validation_result.error_message,
                        'failure_reason': 'invalid_api_key'
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid Trading 212 API key: {validation_result.error_message}"
                )
            
            if validation_result.account_id:
                account_info = {
                    "account_id": validation_result.account_id,
                    "account_type": validation_result.account_type
                }
                logger.info(
                    "Trading 212 API key validation successful",
                    extra={
                        'session_id': user_id,
                        'account_id': validation_result.account_id,
                        'account_type': validation_result.account_type
                    }
                )
        
        # Store API key (temporarily without encryption for demo)
        # TODO: Implement proper encryption in production
        redis_client.hset(session_key, "trading212_api_key", api_setup.api_key)
        redis_client.hset(session_key, "trading212_connected", "true")
        redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
        
        logger.info(
            "Trading 212 API key setup completed successfully",
            extra={
                'session_id': user_id,
                'account_id': account_info.get('account_id') if account_info else None,
                'validation_performed': api_setup.validate_connection
            }
        )
        
        return Trading212APIResponse(
            status="success",
            message="Trading 212 API key configured successfully",
            account_info=account_info
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already logged above)
        raise
    except Exception as e:
        logger.error(
            "Trading 212 API key setup failed with unexpected error",
            extra={
                'session_id': user_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup Trading 212 API key"
        )


@router.post("/trading212/validate", response_model=APIKeyValidation)
async def validate_trading212_connection(
    api_setup: Trading212APISetup
) -> Any:
    """
    Validate Trading 212 API key without storing it
    """
    return await validate_trading212_api_key(api_setup.api_key)


@router.delete("/trading212/setup")
async def remove_trading212_api(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Remove Trading 212 API key from session
    """
    logger.info(
        "Trading 212 API key removal requested",
        extra={
            'session_id': user_id,
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }
    )
    
    try:
        session_key = f"session:{user_id}"
        
        # Remove API key and update connection status
        removed_count = redis_client.hdel(session_key, "trading212_api_key")
        redis_client.hset(session_key, "trading212_connected", "false")
        redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
        
        if removed_count > 0:
            logger.info(
                "Trading 212 API key removed successfully",
                extra={
                    'session_id': user_id,
                    'removal_type': 'user_initiated'
                }
            )
        else:
            logger.warning(
                "Trading 212 API key removal attempted but key not found",
                extra={
                    'session_id': user_id,
                    'removal_type': 'key_not_found'
                }
            )
        
        return {"message": "Trading 212 API key removed successfully"}
        
    except Exception as e:
        logger.error(
            "Trading 212 API key removal failed",
            extra={
                'session_id': user_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove Trading 212 API key"
        )


async def validate_trading212_api_key(api_key: str) -> APIKeyValidation:
    """
    Validate Trading 212 API key by making a test request
    """
    logger.debug(
        "Starting Trading 212 API key validation",
        extra={'api_key_length': len(api_key) if api_key else 0}
    )
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with account info endpoint
            response = await client.get(
                "https://live.trading212.com/api/v0/equity/account/info",
                headers=headers,
                timeout=10.0
            )
            
            logger.debug(
                "Trading 212 API validation request completed",
                extra={
                    'status_code': response.status_code,
                    'response_size': len(response.content) if response.content else 0
                }
            )
            
            if response.status_code == 200:
                account_data = response.json()
                account_id = str(account_data.get("id"))
                
                logger.info(
                    "Trading 212 API key validation successful",
                    extra={
                        'account_id': account_id,
                        'account_type': 'equity',
                        'validation_result': 'valid'
                    }
                )
                
                return APIKeyValidation(
                    is_valid=True,
                    account_id=account_id,
                    account_type="equity",  # Trading 212 equity account
                    error_message=None
                )
            elif response.status_code == 401:
                logger.warning(
                    "Trading 212 API key validation failed - unauthorized",
                    extra={
                        'status_code': response.status_code,
                        'validation_result': 'unauthorized'
                    }
                )
                return APIKeyValidation(
                    is_valid=False,
                    error_message="Invalid API key or unauthorized access"
                )
            elif response.status_code == 429:
                logger.warning(
                    "Trading 212 API key validation rate limited",
                    extra={
                        'status_code': response.status_code,
                        'validation_result': 'rate_limited'
                    }
                )
                # Rate limited - assume key is valid but can't validate right now
                return APIKeyValidation(
                    is_valid=True,
                    account_id=None,
                    account_type="equity",
                    error_message="Rate limited - validation skipped"
                )
            else:
                logger.warning(
                    "Trading 212 API key validation failed with unexpected status",
                    extra={
                        'status_code': response.status_code,
                        'validation_result': 'unexpected_status'
                    }
                )
                return APIKeyValidation(
                    is_valid=False,
                    error_message=f"API validation failed with status {response.status_code}"
                )
                
    except httpx.TimeoutException:
        logger.warning(
            "Trading 212 API key validation timeout",
            extra={
                'validation_result': 'timeout',
                'timeout_seconds': 10.0
            }
        )
        return APIKeyValidation(
            is_valid=False,
            error_message="Connection timeout - please check your internet connection"
        )
    except httpx.RequestError as e:
        logger.warning(
            "Trading 212 API key validation connection error",
            extra={
                'validation_result': 'connection_error',
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
        )
        return APIKeyValidation(
            is_valid=False,
            error_message=f"Connection error: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Trading 212 API key validation unexpected error",
            extra={
                'validation_result': 'unexpected_error',
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        return APIKeyValidation(
            is_valid=False,
            error_message=f"Unexpected error: {str(e)}"
        )