from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis

from app.core.security import verify_token
from app.core.config import settings
from db.session import SessionLocal

# Security scheme for JWT tokens
security = HTTPBearer()

# Redis client for session management
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db() -> Generator:
    """Database dependency"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """Redis dependency"""
    return redis_client


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get current user ID from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        if user_id is None:
            raise credentials_exception
        return user_id
    except Exception:
        raise credentials_exception


async def get_current_session(
    user_id: str = Depends(get_current_user_id),
    redis_client: redis.Redis = Depends(get_redis)
) -> dict:
    """Get current user session data"""
    session_key = f"session:{user_id}"
    session_data = redis_client.hgetall(session_key)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired"
        )
    
    return session_data


async def get_trading212_api_key(
    session_data: dict = Depends(get_current_session)
) -> Optional[str]:
    """Get Trading 212 API key from session"""
    # For now, return the API key directly (bypassing encryption for demo)
    # In production, this should be properly encrypted/decrypted
    api_key = session_data.get("trading212_api_key")
    if not api_key:
        return None
    
    # If it looks like an encrypted key, try to decrypt it
    if len(api_key) > 50:  # Encrypted keys are longer
        from app.core.security import decrypt_api_key
        try:
            return decrypt_api_key(api_key)
        except Exception:
            # If decryption fails, assume it's already decrypted
            pass
    
    return api_key