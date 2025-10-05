"""
Metrics collection and monitoring system for the Trading 212 Portfolio Dashboard.

This module provides comprehensive metrics collection for application performance,
API health monitoring, user analytics, and system health tracking.
"""

import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Deque
from dataclasses import dataclass, field
from enum import Enum
import json

import redis.asyncio as redis
from app.core.logging import get_context_logger
from app.core.config import settings


logger = get_context_logger(__name__)


class MetricType(str, Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class APIHealthMetrics:
    """Metrics for API health monitoring."""
    endpoint: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = float('inf')
    error_rate: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    response_times: Deque[float] = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class Trading212APIMetrics:
    """Specific metrics for Trading 212 API monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    rate_limited_requests: int = 0
    failed_requests: int = 0
    authentication_failures: int = 0
    current_rate_limit: int = 60
    remaining_requests: int = 60
    rate_limit_reset_time: Optional[datetime] = None
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    consecutive_failures: int = 0
    error_rate: float = 0.0
    health_status: str = "unknown"  # healthy, degraded, unhealthy


@dataclass
class UserActionMetrics:
    """Metrics for user actions and behavior."""
    total_sessions: int = 0
    active_sessions: int = 0
    api_key_setups: int = 0
    api_key_validations: int = 0
    portfolio_data_fetches: int = 0
    dashboard_views: int = 0
    avg_session_duration: float = 0.0
    session_durations: Deque[float] = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class SystemHealthMetrics:
    """System-wide health metrics."""
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    redis_connected: bool = False
    database_connected: bool = False
    active_connections: int = 0
    total_errors: int = 0
    error_rate_per_minute: float = 0.0


class MetricsCollector:
    """
    Comprehensive metrics collection system.
    
    Collects and aggregates metrics for application performance monitoring,
    API health tracking, user analytics, and system health.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.start_time = datetime.utcnow()
        
        # In-memory metric storage
        self.api_metrics: Dict[str, APIHealthMetrics] = {}
        self.trading212_metrics = Trading212APIMetrics()
        self.user_metrics = UserActionMetrics()
        self.system_metrics = SystemHealthMetrics()
        
        # Metric points for time series data
        self.metric_points: Deque[MetricPoint] = deque(maxlen=10000)
        
        # Error tracking
        self.recent_errors: Deque[Dict[str, Any]] = deque(maxlen=1000)
        
        logger.info("MetricsCollector initialized")
    
    async def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        error_type: Optional[str] = None
    ) -> None:
        """
        Record API endpoint performance metrics.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: Response status code
            response_time: Request duration in seconds
            error_type: Type of error if request failed
        """
        metric_key = f"{method} {endpoint}"
        if metric_key not in self.api_metrics:
            self.api_metrics[metric_key] = APIHealthMetrics(endpoint=endpoint)
        metrics = self.api_metrics[metric_key]
        
        # Update request counts
        metrics.total_requests += 1
        if 200 <= status_code < 300:
            metrics.successful_requests += 1
            metrics.last_success = datetime.utcnow()
        else:
            metrics.failed_requests += 1
            metrics.last_failure = datetime.utcnow()
        
        # Update response time metrics
        metrics.response_times.append(response_time)
        if metrics.response_times:
            metrics.avg_response_time = sum(metrics.response_times) / len(metrics.response_times)
            metrics.max_response_time = max(metrics.max_response_time, response_time)
            metrics.min_response_time = min(metrics.min_response_time, response_time)
        
        # Calculate error rate
        if metrics.total_requests > 0:
            metrics.error_rate = (metrics.failed_requests / metrics.total_requests) * 100
        
        # Record metric points for time series
        await self._record_metric_point(
            f"api.requests.{metric_key.replace(' ', '_').replace('/', '_')}",
            1,
            MetricType.COUNTER,
            {
                'endpoint': endpoint,
                'method': method,
                'status_code': str(status_code),
                'success': str(200 <= status_code < 300)
            }
        )
        
        await self._record_metric_point(
            f"api.response_time.{metric_key.replace(' ', '_').replace('/', '_')}",
            response_time * 1000,  # Convert to milliseconds
            MetricType.HISTOGRAM,
            {
                'endpoint': endpoint,
                'method': method
            }
        )
        
        logger.debug(
            "API request metrics recorded",
            extra={
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time_ms': round(response_time * 1000, 2),
                'total_requests': metrics.total_requests,
                'error_rate': round(metrics.error_rate, 2)
            }
        )
    
    async def record_trading212_request(
        self,
        endpoint: str,
        success: bool,
        response_time: float,
        rate_limited: bool = False,
        auth_failure: bool = False,
        rate_limit_remaining: Optional[int] = None,
        rate_limit_reset: Optional[datetime] = None
    ) -> None:
        """
        Record Trading 212 API specific metrics.
        
        Args:
            endpoint: Trading 212 API endpoint
            success: Whether the request was successful
            response_time: Request duration in seconds
            rate_limited: Whether the request was rate limited
            auth_failure: Whether the request failed due to authentication
            rate_limit_remaining: Current rate limit remaining
            rate_limit_reset: When rate limit resets
        """
        metrics = self.trading212_metrics
        
        # Update request counts
        metrics.total_requests += 1
        metrics.last_request_time = datetime.utcnow()
        
        if success:
            metrics.successful_requests += 1
            metrics.consecutive_failures = 0
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
        
        if rate_limited:
            metrics.rate_limited_requests += 1
        
        if auth_failure:
            metrics.authentication_failures += 1
        
        # Update rate limit info
        if rate_limit_remaining is not None:
            metrics.remaining_requests = rate_limit_remaining
        
        if rate_limit_reset is not None:
            metrics.rate_limit_reset_time = rate_limit_reset
        
        # Update response time
        if success:
            # Simple moving average
            if metrics.total_requests == 1:
                metrics.avg_response_time = response_time
            else:
                metrics.avg_response_time = (
                    (metrics.avg_response_time * (metrics.successful_requests - 1) + response_time) /
                    metrics.successful_requests
                )
        
        # Calculate error rate
        if metrics.total_requests > 0:
            metrics.error_rate = (metrics.failed_requests / metrics.total_requests) * 100
        
        # Determine health status
        if metrics.consecutive_failures >= 5:
            metrics.health_status = "unhealthy"
        elif metrics.consecutive_failures >= 2 or (metrics.error_rate > 10 and metrics.total_requests > 10):
            metrics.health_status = "degraded"
        else:
            metrics.health_status = "healthy"
        
        # Record metric points
        await self._record_metric_point(
            "trading212.requests.total",
            1,
            MetricType.COUNTER,
            {
                'endpoint': endpoint,
                'success': str(success),
                'rate_limited': str(rate_limited),
                'auth_failure': str(auth_failure)
            }
        )
        
        await self._record_metric_point(
            "trading212.rate_limit.remaining",
            metrics.remaining_requests,
            MetricType.GAUGE,
            {'limit': str(metrics.current_rate_limit)}
        )
        
        await self._record_metric_point(
            "trading212.health.consecutive_failures",
            metrics.consecutive_failures,
            MetricType.GAUGE,
            {'status': metrics.health_status}
        )
        
        logger.debug(
            "Trading 212 API metrics recorded",
            extra={
                'endpoint': endpoint,
                'success': success,
                'response_time_ms': round(response_time * 1000, 2),
                'rate_limited': rate_limited,
                'remaining_requests': metrics.remaining_requests,
                'health_status': metrics.health_status,
                'consecutive_failures': metrics.consecutive_failures
            }
        )
    
    async def record_user_action(
        self,
        action: str,
        session_id: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record user action metrics.
        
        Args:
            action: Type of user action
            session_id: User session ID
            success: Whether the action was successful
            metadata: Additional action metadata
        """
        metrics = self.user_metrics
        
        # Update action-specific counters
        if action == "session_created":
            metrics.total_sessions += 1
        elif action == "api_key_setup":
            metrics.api_key_setups += 1
        elif action == "api_key_validation":
            metrics.api_key_validations += 1
        elif action == "portfolio_data_fetch":
            metrics.portfolio_data_fetches += 1
        elif action == "dashboard_view":
            metrics.dashboard_views += 1
        
        # Record metric point
        await self._record_metric_point(
            f"user.actions.{action}",
            1,
            MetricType.COUNTER,
            {
                'success': str(success),
                'session_id': session_id or 'unknown',
                **(metadata or {})
            }
        )
        
        logger.debug(
            "User action metrics recorded",
            extra={
                'action': action,
                'session_id': session_id,
                'success': success,
                'metadata': metadata
            }
        )
    
    async def record_error(
        self,
        error_type: str,
        error_message: str,
        component: str,
        severity: str = "error",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record error metrics and details.
        
        Args:
            error_type: Type/category of error
            error_message: Error message
            component: Component where error occurred
            severity: Error severity level
            metadata: Additional error metadata
        """
        error_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'component': component,
            'severity': severity,
            'metadata': metadata or {}
        }
        
        self.recent_errors.append(error_record)
        self.system_metrics.total_errors += 1
        
        # Record metric point
        await self._record_metric_point(
            f"errors.{component}.{error_type}",
            1,
            MetricType.COUNTER,
            {
                'severity': severity,
                'component': component,
                'error_type': error_type
            }
        )
        
        logger.debug(
            "Error metrics recorded",
            extra={
                'error_type': error_type,
                'component': component,
                'severity': severity,
                'total_errors': self.system_metrics.total_errors
            }
        )
    
    async def update_system_metrics(
        self,
        memory_usage_mb: Optional[float] = None,
        cpu_usage_percent: Optional[float] = None,
        active_connections: Optional[int] = None,
        redis_connected: Optional[bool] = None,
        database_connected: Optional[bool] = None
    ) -> None:
        """
        Update system health metrics.
        
        Args:
            memory_usage_mb: Current memory usage in MB
            cpu_usage_percent: Current CPU usage percentage
            active_connections: Number of active connections
            redis_connected: Redis connection status
            database_connected: Database connection status
        """
        metrics = self.system_metrics
        
        # Update uptime
        metrics.uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        if memory_usage_mb is not None:
            metrics.memory_usage_mb = memory_usage_mb
            await self._record_metric_point(
                "system.memory.usage_mb",
                memory_usage_mb,
                MetricType.GAUGE
            )
        
        if cpu_usage_percent is not None:
            metrics.cpu_usage_percent = cpu_usage_percent
            await self._record_metric_point(
                "system.cpu.usage_percent",
                cpu_usage_percent,
                MetricType.GAUGE
            )
        
        if active_connections is not None:
            metrics.active_connections = active_connections
            await self._record_metric_point(
                "system.connections.active",
                active_connections,
                MetricType.GAUGE
            )
        
        if redis_connected is not None:
            metrics.redis_connected = redis_connected
            await self._record_metric_point(
                "system.redis.connected",
                1 if redis_connected else 0,
                MetricType.GAUGE
            )
        
        if database_connected is not None:
            metrics.database_connected = database_connected
            await self._record_metric_point(
                "system.database.connected",
                1 if database_connected else 0,
                MetricType.GAUGE
            )
        
        # Record uptime
        await self._record_metric_point(
            "system.uptime.seconds",
            metrics.uptime_seconds,
            MetricType.GAUGE
        )
        
        logger.debug(
            "System metrics updated",
            extra={
                'uptime_seconds': round(metrics.uptime_seconds, 2),
                'memory_usage_mb': memory_usage_mb,
                'cpu_usage_percent': cpu_usage_percent,
                'active_connections': active_connections,
                'redis_connected': redis_connected,
                'database_connected': database_connected
            }
        )
    
    async def _record_metric_point(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric point for time series data."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            metric_type=metric_type
        )
        
        self.metric_points.append(point)
        
        # Optionally store in Redis for persistence
        if self.redis_client:
            try:
                await self._store_metric_in_redis(point)
            except Exception as e:
                logger.warning(
                    "Failed to store metric in Redis",
                    extra={
                        'metric_name': name,
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                )
    
    async def _store_metric_in_redis(self, point: MetricPoint) -> None:
        """Store metric point in Redis for persistence."""
        if not self.redis_client:
            return
        
        # Store in time series format
        key = f"metrics:{point.name}:{point.timestamp.strftime('%Y%m%d%H')}"
        data = {
            'timestamp': point.timestamp.isoformat(),
            'value': point.value,
            'tags': json.dumps(point.tags),
            'type': point.metric_type.value
        }
        
        await self.redis_client.lpush(key, json.dumps(data))
        await self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
    
    def get_api_health_summary(self) -> Dict[str, Any]:
        """Get summary of API health metrics."""
        summary = {}
        for endpoint, metrics in self.api_metrics.items():
            summary[endpoint] = {
                'total_requests': metrics.total_requests,
                'success_rate': round(
                    (metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0,
                    2
                ),
                'avg_response_time_ms': round(metrics.avg_response_time * 1000, 2),
                'error_rate': round(metrics.error_rate, 2),
                'last_success': metrics.last_success.isoformat() if metrics.last_success else None,
                'last_failure': metrics.last_failure.isoformat() if metrics.last_failure else None
            }
        return summary
    
    def get_trading212_health_summary(self) -> Dict[str, Any]:
        """Get Trading 212 API health summary."""
        metrics = self.trading212_metrics
        return {
            'health_status': metrics.health_status,
            'total_requests': metrics.total_requests,
            'success_rate': round(
                (metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0,
                2
            ),
            'rate_limit_remaining': metrics.remaining_requests,
            'rate_limit_total': metrics.current_rate_limit,
            'rate_limit_reset': metrics.rate_limit_reset_time.isoformat() if metrics.rate_limit_reset_time else None,
            'avg_response_time_ms': round(metrics.avg_response_time * 1000, 2),
            'consecutive_failures': metrics.consecutive_failures,
            'authentication_failures': metrics.authentication_failures,
            'rate_limited_requests': metrics.rate_limited_requests,
            'last_request': metrics.last_request_time.isoformat() if metrics.last_request_time else None
        }
    
    def get_user_analytics_summary(self) -> Dict[str, Any]:
        """Get user analytics summary."""
        metrics = self.user_metrics
        return {
            'total_sessions': metrics.total_sessions,
            'active_sessions': metrics.active_sessions,
            'api_key_setups': metrics.api_key_setups,
            'api_key_validations': metrics.api_key_validations,
            'portfolio_data_fetches': metrics.portfolio_data_fetches,
            'dashboard_views': metrics.dashboard_views,
            'avg_session_duration_minutes': round(metrics.avg_session_duration / 60, 2) if metrics.avg_session_duration > 0 else 0
        }
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary."""
        metrics = self.system_metrics
        return {
            'uptime_hours': round(metrics.uptime_seconds / 3600, 2),
            'memory_usage_mb': metrics.memory_usage_mb,
            'cpu_usage_percent': metrics.cpu_usage_percent,
            'redis_connected': metrics.redis_connected,
            'database_connected': metrics.database_connected,
            'active_connections': metrics.active_connections,
            'total_errors': metrics.total_errors,
            'error_rate_per_minute': metrics.error_rate_per_minute
        }
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent error records."""
        return list(self.recent_errors)[-limit:]
    
    def get_comprehensive_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report with all metrics."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'api_health': self.get_api_health_summary(),
            'trading212_health': self.get_trading212_health_summary(),
            'user_analytics': self.get_user_analytics_summary(),
            'system_health': self.get_system_health_summary(),
            'recent_errors': self.get_recent_errors(10)
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def initialize_metrics_collector(redis_client: Optional[redis.Redis] = None) -> MetricsCollector:
    """Initialize the global metrics collector with Redis client."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(redis_client)
    logger.info("Global metrics collector initialized")
    return _metrics_collector