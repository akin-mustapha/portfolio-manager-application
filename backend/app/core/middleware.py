"""
Middleware for request context tracking and logging.

This module provides middleware for adding request context to logs,
tracking request/response cycles, and managing user context across
async operations.
"""

import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.core.logging import get_context_logger, request_id_var, user_id_var
from app.core.metrics import get_metrics_collector


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request context to logs and track request/response cycles.
    
    This middleware:
    - Generates unique request IDs for tracking
    - Extracts user context from JWT tokens
    - Logs request start/completion/errors
    - Adds timing information
    - Manages context variables for async operations
    """
    
    def __init__(self, app, logger_name: str = "app.requests"):
        super().__init__(app)
        self.logger = get_context_logger(logger_name)
        self.metrics = get_metrics_collector()
    
    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        """Process request with context tracking and logging."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user ID from request
        user_id = await self._extract_user_id(request)
        if user_id:
            user_id_var.set(user_id)
        
        # Prepare request context
        request_context = {
            'request_id': request_id,
            'user_id': user_id,
            'method': request.method,
            'url': str(request.url),
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'user_agent': request.headers.get('user-agent'),
            'ip_address': self._get_client_ip(request),
            'content_type': request.headers.get('content-type'),
            'content_length': request.headers.get('content-length')
        }
        
        # Log request start
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra=request_context
        )
        
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log successful request completion
            self.logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    **request_context,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'response_size': response.headers.get('content-length')
                }
            )
            
            # Record metrics
            await self.metrics.record_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time=duration_ms / 1000  # Convert to seconds
            )
            
            # Add request ID to response headers for tracing
            response.headers['X-Request-ID'] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration for failed request
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log request error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    **request_context,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'duration_ms': duration_ms
                },
                exc_info=True
            )
            
            # Record error metrics
            await self.metrics.record_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=500,  # Internal server error
                response_time=duration_ms / 1000,  # Convert to seconds
                error_type=type(e).__name__
            )
            
            await self.metrics.record_error(
                error_type=type(e).__name__,
                error_message=str(e),
                component="api_request",
                severity="error",
                metadata={
                    'endpoint': request.url.path,
                    'method': request.method,
                    'user_id': user_id
                }
            )
            
            # Re-raise the exception
            raise
        
        finally:
            # Clean up context variables
            try:
                request_id_var.set("")
                user_id_var.set(None)
            except Exception:
                pass
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        Extract user ID from JWT token in Authorization header.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User ID if found, None otherwise
        """
        try:
            auth_header = request.headers.get('authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header.split(' ')[1]
            
            # Import here to avoid circular imports
            from app.core.security import decode_access_token
            
            payload = decode_access_token(token)
            return payload.get('sub') if payload else None
            
        except Exception as e:
            self.logger.debug(
                "Failed to extract user ID from token",
                extra={'error': str(e)}
            )
            return None
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        Get client IP address from request headers.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded headers first (for proxy/load balancer scenarios)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else None


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for security event logging.
    
    This middleware logs security-related events such as:
    - Authentication attempts
    - Suspicious request patterns
    - Rate limiting violations
    - Invalid token usage
    """
    
    def __init__(self, app, logger_name: str = "app.security"):
        super().__init__(app)
        self.logger = get_context_logger(logger_name)
        self.suspicious_patterns = [
            '/admin', '/.env', '/config', '/backup',
            'wp-admin', 'phpmyadmin', '.git', '.svn'
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        """Process request with security monitoring."""
        # Check for suspicious patterns
        if any(pattern in request.url.path.lower() for pattern in self.suspicious_patterns):
            self.logger.warning(
                "Suspicious request pattern detected",
                extra={
                    'path': request.url.path,
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.headers.get('user-agent'),
                    'pattern_type': 'suspicious_path'
                }
            )
        
        # Check for potential SQL injection patterns
        query_string = str(request.query_params)
        if any(pattern in query_string.lower() for pattern in ['union select', 'drop table', '1=1', 'or 1=1']):
            self.logger.warning(
                "Potential SQL injection attempt detected",
                extra={
                    'path': request.url.path,
                    'query_params': dict(request.query_params),
                    'ip_address': self._get_client_ip(request),
                    'pattern_type': 'sql_injection'
                }
            )
        
        # Process request normally
        response = await call_next(request)
        
        # Log authentication failures
        if response.status_code == 401:
            self.logger.warning(
                "Authentication failure",
                extra={
                    'path': request.url.path,
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.headers.get('user-agent'),
                    'status_code': response.status_code
                }
            )
        
        # Log authorization failures
        elif response.status_code == 403:
            self.logger.warning(
                "Authorization failure",
                extra={
                    'path': request.url.path,
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.headers.get('user-agent'),
                    'status_code': response.status_code
                }
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address from request headers."""
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else None


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring and logging.
    
    This middleware tracks:
    - Request processing times
    - Slow requests
    - Resource usage patterns
    - API endpoint performance
    """
    
    def __init__(self, app, slow_request_threshold: float = 1.0, logger_name: str = "app.performance"):
        super().__init__(app)
        self.logger = get_context_logger(logger_name)
        self.slow_request_threshold = slow_request_threshold  # seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        """Process request with performance monitoring."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log slow requests
            if processing_time > self.slow_request_threshold:
                self.logger.warning(
                    f"Slow request detected: {request.method} {request.url.path}",
                    extra={
                        'method': request.method,
                        'path': request.url.path,
                        'processing_time_seconds': round(processing_time, 3),
                        'threshold_seconds': self.slow_request_threshold,
                        'status_code': response.status_code
                    }
                )
            
            # Log performance metrics for all requests
            self.logger.debug(
                f"Request performance: {request.method} {request.url.path}",
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'processing_time_ms': round(processing_time * 1000, 2),
                    'status_code': response.status_code
                }
            )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.error(
                f"Request error: {request.method} {request.url.path}",
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'processing_time_seconds': round(processing_time, 3),
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                },
                exc_info=True
            )
            
            raise