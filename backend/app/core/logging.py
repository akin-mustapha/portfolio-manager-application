"""
Comprehensive logging infrastructure for the Trading 212 Portfolio Dashboard.

This module provides structured logging with security filtering, contextual formatting,
and centralized log management capabilities.
"""

import json
import logging
import logging.handlers
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional, Set
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id')
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class SecurityFilter(logging.Filter):
    """
    Filter to remove sensitive data from logs.
    
    This filter sanitizes log records to prevent sensitive information
    like API keys, tokens, and passwords from being logged.
    """
    
    SENSITIVE_KEYS: Set[str] = {
        'password', 'api_key', 'token', 'secret', 'authorization',
        'trading212_api_key', 'encrypted_key', 'refresh_token', 'access_token',
        'jwt', 'bearer', 'credentials', 'private_key', 'session_id'
    }
    
    SENSITIVE_PATTERNS = [
        re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
        re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9]+', re.IGNORECASE),
        re.compile(r'token["\']?\s*[:=]\s*["\']?[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and sanitize log record."""
        try:
            # Sanitize the main message
            if hasattr(record, 'msg') and isinstance(record.msg, str):
                record.msg = self._sanitize_string(record.msg)
            elif hasattr(record, 'msg') and isinstance(record.msg, dict):
                record.msg = self._sanitize_dict(record.msg)
            
            # Sanitize arguments
            if hasattr(record, 'args') and record.args:
                record.args = tuple(self._sanitize_value(arg) for arg in record.args)
            
            # Sanitize extra data if present
            if hasattr(record, '__dict__'):
                for key, value in list(record.__dict__.items()):
                    if key.lower() in self.SENSITIVE_KEYS:
                        setattr(record, key, "[REDACTED]")
                    elif isinstance(value, (str, dict)):
                        setattr(record, key, self._sanitize_value(value))
        
        except Exception:
            # If sanitization fails, allow the record through but mark it
            record.msg = f"[SANITIZATION_ERROR] {getattr(record, 'msg', 'Unknown message')}"
        
        return True
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive keys from dictionary."""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_value(item) for item in value]
            else:
                sanitized[key] = self._sanitize_value(value)
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize sensitive patterns in strings."""
        if not isinstance(text, str):
            return text
        
        sanitized = text
        for pattern in self.SENSITIVE_PATTERNS:
            sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized
    
    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize individual values."""
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, dict):
            return self._sanitize_dict(value)
        elif isinstance(value, list):
            return [self._sanitize_value(item) for item in value]
        else:
            return value


class ContextualFormatter(logging.Formatter):
    """
    Custom formatter that includes request context and outputs structured JSON logs.
    
    This formatter adds request context, timestamps, and formats logs as JSON
    for better parsing and analysis in centralized logging systems.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        try:
            # Add timestamp in ISO format
            record.timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Build base log data
            log_data = {
                'timestamp': record.timestamp,
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'thread': record.thread,
                'process': record.process
            }
            
            # Add request context if available
            request_context = self._get_request_context()
            if request_context:
                log_data['request_context'] = request_context
            
            # Add exception information if present
            if record.exc_info:
                log_data['exception'] = {
                    'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                    'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                    'traceback': self.formatException(record.exc_info) if record.exc_info else None
                }
            
            # Add any extra fields from the log record
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in {
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                    'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                    'thread', 'threadName', 'processName', 'process', 'getMessage',
                    'exc_info', 'exc_text', 'stack_info', 'timestamp'
                }:
                    extra_fields[key] = value
            
            if extra_fields:
                log_data['extra'] = extra_fields
            
            return json.dumps(log_data, default=str, ensure_ascii=False)
        
        except Exception as e:
            # Fallback to simple format if JSON formatting fails
            return f"[FORMATTING_ERROR] {record.levelname}: {record.getMessage()} (Error: {e})"
    
    def _get_request_context(self) -> Optional[Dict[str, Any]]:
        """Get current request context from context variables."""
        context = {}
        
        try:
            context['request_id'] = request_id_var.get()
        except LookupError:
            pass
        
        try:
            user_id = user_id_var.get()
            if user_id:
                context['user_id'] = user_id
        except LookupError:
            pass
        
        return context if context else None


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    centralized_host: Optional[str] = None,
    centralized_url: Optional[str] = None
) -> None:
    """
    Set up comprehensive logging configuration.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
        centralized_host: Host for centralized logging (optional)
        centralized_url: URL endpoint for centralized logging (optional)
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create security filter
    security_filter = SecurityFilter()
    
    # Create formatters
    contextual_formatter = ContextualFormatter()
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'application.log'),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(contextual_formatter)
    file_handler.addFilter(security_filter)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(simple_formatter)
    console_handler.addFilter(security_filter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set up centralized logging if configured
    if centralized_host and centralized_url:
        try:
            http_handler = logging.handlers.HTTPHandler(
                host=centralized_host,
                url=centralized_url,
                method='POST'
            )
            http_handler.setLevel(logging.WARNING)
            http_handler.setFormatter(contextual_formatter)
            http_handler.addFilter(security_filter)
            root_logger.addHandler(http_handler)
        except Exception as e:
            logging.warning(f"Failed to set up centralized logging: {e}")
    
    # Configure specific loggers
    _configure_specific_loggers()


def _configure_specific_loggers() -> None:
    """Configure specific loggers for different components."""
    # Application logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.DEBUG)
    
    # Trading 212 service logger
    trading212_logger = logging.getLogger('trading212_service')
    trading212_logger.setLevel(logging.INFO)
    
    # Authentication service logger
    auth_logger = logging.getLogger('auth_service')
    auth_logger.setLevel(logging.INFO)
    
    # Database logger
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.WARNING)  # Only log warnings and errors
    
    # HTTP requests logger
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)
    
    # Uvicorn logger
    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

class ContextLogger:
    """
    Logger that automatically includes request context in all log messages.
    
    This class wraps the standard Python logger and automatically adds
    request context (request ID, user ID) to all log messages.
    """
    
    def __init__(self, name: str):
        """
        Initialize context logger.
        
        Args:
            name: Logger name (typically module name)
        """
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _get_extra_context(self, extra: Optional[Dict] = None) -> Dict:
        """Get current request context and merge with provided extra data."""
        context = {}
        
        # Add request context if available
        try:
            context['request_id'] = request_id_var.get()
        except LookupError:
            pass
        
        try:
            user_id = user_id_var.get()
            if user_id:
                context['user_id'] = user_id
        except LookupError:
            pass
        
        # Merge with provided extra data
        if extra:
            context.update(extra)
        
        return context
    
    def debug(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log debug message with context."""
        self.logger.debug(message, extra=self._get_extra_context(extra))
    
    def info(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log info message with context."""
        self.logger.info(message, extra=self._get_extra_context(extra))
    
    def warning(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log warning message with context."""
        self.logger.warning(message, extra=self._get_extra_context(extra))
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False) -> None:
        """Log error message with context."""
        self.logger.error(message, extra=self._get_extra_context(extra), exc_info=exc_info)
    
    def critical(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False) -> None:
        """Log critical message with context."""
        self.logger.critical(message, extra=self._get_extra_context(extra), exc_info=exc_info)
    
    def exception(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log exception with context and traceback."""
        self.logger.exception(message, extra=self._get_extra_context(extra))


# Convenience function to create context loggers
def get_context_logger(name: str) -> ContextLogger:
    """
    Get a context-aware logger instance.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        ContextLogger instance
    """
    return ContextLogger(name)