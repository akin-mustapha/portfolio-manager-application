"""
Metrics and monitoring endpoints.

Provides endpoints for accessing application metrics, health status,
and monitoring data.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.core.deps import get_current_user_id
from app.core.logging import get_context_logger
from app.core.metrics import get_metrics_collector
from app.models.auth import SessionInfo

router = APIRouter()
logger = get_context_logger(__name__)


@router.get("/health")
async def get_health_status() -> Dict[str, Any]:
    """
    Get comprehensive health status of the application.
    
    Returns health metrics for all components including API endpoints,
    Trading 212 integration, system resources, and error rates.
    """
    logger.info("Health status requested")
    
    try:
        metrics = get_metrics_collector()
        health_report = metrics.get_comprehensive_health_report()
        
        # Determine overall health status
        trading212_health = health_report['trading212_health']['health_status']
        system_health = health_report['system_health']
        
        overall_status = "healthy"
        if trading212_health == "unhealthy" or not system_health.get('redis_connected', True):
            overall_status = "unhealthy"
        elif trading212_health == "degraded" or system_health.get('total_errors', 0) > 100:
            overall_status = "degraded"
        
        health_report['overall_status'] = overall_status
        
        logger.info(
            "Health status retrieved",
            extra={
                'overall_status': overall_status,
                'trading212_status': trading212_health,
                'total_errors': system_health.get('total_errors', 0)
            }
        )
        
        return health_report
        
    except Exception as e:
        logger.error(
            "Failed to retrieve health status",
            extra={'error_type': type(e).__name__, 'error_message': str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health status"
        )


@router.get("/health/api")
async def get_api_health() -> Dict[str, Any]:
    """Get API endpoint health metrics."""
    logger.debug("API health metrics requested")
    
    try:
        metrics = get_metrics_collector()
        api_health = metrics.get_api_health_summary()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'api_endpoints': api_health
        }
        
    except Exception as e:
        logger.error(
            "Failed to retrieve API health metrics",
            extra={'error_type': type(e).__name__},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API health metrics"
        )


@router.get("/health/trading212")
async def get_trading212_health() -> Dict[str, Any]:
    """Get Trading 212 API health metrics."""
    logger.debug("Trading 212 health metrics requested")
    
    try:
        metrics = get_metrics_collector()
        trading212_health = metrics.get_trading212_health_summary()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'trading212_api': trading212_health
        }
        
    except Exception as e:
        logger.error(
            "Failed to retrieve Trading 212 health metrics",
            extra={'error_type': type(e).__name__},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Trading 212 health metrics"
        )


@router.get("/health/system")
async def get_system_health() -> Dict[str, Any]:
    """Get system health metrics."""
    logger.debug("System health metrics requested")
    
    try:
        metrics = get_metrics_collector()
        system_health = metrics.get_system_health_summary()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': system_health
        }
        
    except Exception as e:
        logger.error(
            "Failed to retrieve system health metrics",
            extra={'error_type': type(e).__name__},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system health metrics"
        )


@router.get("/analytics/user")
async def get_user_analytics(
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get user analytics and usage metrics.
    
    Requires authentication to access user-specific analytics.
    """
    logger.info(
        "User analytics requested",
        extra={'session_id': user_id}
    )
    
    try:
        metrics = get_metrics_collector()
        user_analytics = metrics.get_user_analytics_summary()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'user_analytics': user_analytics
        }
        
    except Exception as e:
        logger.error(
            "Failed to retrieve user analytics",
            extra={
                'session_id': user_id,
                'error_type': type(e).__name__
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user analytics"
        )


@router.get("/errors/recent")
async def get_recent_errors(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get recent error records.
    
    Args:
        limit: Maximum number of errors to return (default: 50, max: 100)
    """
    logger.debug(
        "Recent errors requested",
        extra={'session_id': user_id, 'limit': limit}
    )
    
    # Limit the maximum number of errors that can be requested
    limit = min(limit, 100)
    
    try:
        metrics = get_metrics_collector()
        recent_errors = metrics.get_recent_errors(limit)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'limit': limit,
            'error_count': len(recent_errors),
            'errors': recent_errors
        }
        
    except Exception as e:
        logger.error(
            "Failed to retrieve recent errors",
            extra={
                'session_id': user_id,
                'error_type': type(e).__name__
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent errors"
        )


@router.post("/metrics/user-action")
async def record_user_action(
    action: str,
    metadata: Dict[str, Any] = None,
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, str]:
    """
    Record a user action for analytics.
    
    Args:
        action: Type of user action
        metadata: Additional action metadata
    """
    logger.debug(
        "User action recording requested",
        extra={
            'session_id': user_id,
            'action': action,
            'has_metadata': metadata is not None
        }
    )
    
    try:
        metrics = get_metrics_collector()
        await metrics.record_user_action(
            action=action,
            session_id=user_id,
            success=True,
            metadata=metadata
        )
        
        return {"message": "User action recorded successfully"}
        
    except Exception as e:
        logger.error(
            "Failed to record user action",
            extra={
                'session_id': user_id,
                'action': action,
                'error_type': type(e).__name__
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record user action"
        )