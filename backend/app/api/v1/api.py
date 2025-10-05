from fastapi import APIRouter

# Import routers
from api.v1.endpoints import auth, portfolio, pies, benchmarks, dividends

api_router = APIRouter()

# Health check endpoint for API v1
@api_router.get("/health")
async def api_health():
    """API v1 health check"""
    return {"status": "healthy", "version": "v1"}

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(pies.router, prefix="/pies", tags=["pies"])
api_router.include_router(benchmarks.router, prefix="/benchmarks", tags=["benchmarks"])
api_router.include_router(dividends.router, prefix="/dividends", tags=["dividends"])