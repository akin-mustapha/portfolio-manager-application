from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_context_logger
from app.core.middleware import LoggingMiddleware, SecurityLoggingMiddleware, PerformanceLoggingMiddleware
from app.core.metrics import initialize_metrics_collector
from app.api.v1.api import api_router

# Initialize logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_dir=settings.LOG_DIR,
    max_bytes=settings.LOG_MAX_BYTES,
    backup_count=settings.LOG_BACKUP_COUNT,
    centralized_host=settings.CENTRALIZED_LOG_HOST,
    centralized_url=settings.CENTRALIZED_LOG_URL
)

# Get application logger
logger = get_context_logger(__name__)

# Initialize metrics collector
metrics_collector = initialize_metrics_collector()

# Create FastAPI application
app = FastAPI(
    title="Trading 212 Portfolio Dashboard API",
    description="API for Trading 212 portfolio analysis and visualization",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Log application startup
logger.info(
    "Starting Trading 212 Portfolio Dashboard API",
    extra={
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
        "structured_logging": settings.ENABLE_STRUCTURED_LOGGING
    }
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Add custom middleware for logging and monitoring
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityLoggingMiddleware)
app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold=2.0)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint for health check"""
    logger.debug("Root endpoint accessed")
    return JSONResponse(
        content={
            "message": "Trading 212 Portfolio Dashboard API",
            "version": "1.0.0",
            "status": "healthy"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )