from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
import asyncio

from app.core.deps import get_trading212_api_key, get_current_user_id, get_redis
from app.services.trading212_service import Trading212Service, Trading212APIError
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.position import Position
from app.models.pie import Pie
from app.models.historical import HistoricalData
import redis

router = APIRouter()


@router.get("/overview", response_model=Portfolio)
async def get_portfolio_overview(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Get complete portfolio overview including all pies and positions
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            # Authenticate with Trading 212
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch complete portfolio data
            portfolio = await service.fetch_portfolio_data()
            
            # Update last activity in session
            session_key = f"session:{user_id}"
            redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
            
            return portfolio
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio data: {str(e)}"
        )


@router.get("/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get portfolio-level performance and risk metrics
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            portfolio = await service.fetch_portfolio_data()
            return portfolio.metrics
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio metrics: {str(e)}"
        )


@router.get("/positions", response_model=List[Position])
async def get_portfolio_positions(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of positions to return"),
    offset: Optional[int] = Query(0, ge=0, description="Number of positions to skip"),
    sort_by: Optional[str] = Query("market_value", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order")
) -> Any:
    """
    Get all portfolio positions with pagination and sorting
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            portfolio = await service.fetch_portfolio_data()
            all_positions = portfolio.all_positions
            
            # Sort positions
            reverse_sort = sort_order == "desc"
            if sort_by == "market_value":
                all_positions.sort(key=lambda p: p.market_value, reverse=reverse_sort)
            elif sort_by == "unrealized_pnl":
                all_positions.sort(key=lambda p: p.unrealized_pnl, reverse=reverse_sort)
            elif sort_by == "unrealized_pnl_pct":
                all_positions.sort(key=lambda p: p.unrealized_pnl_pct, reverse=reverse_sort)
            elif sort_by == "symbol":
                all_positions.sort(key=lambda p: p.symbol, reverse=reverse_sort)
            
            # Apply pagination
            if offset:
                all_positions = all_positions[offset:]
            if limit:
                all_positions = all_positions[:limit]
            
            return all_positions
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch positions: {str(e)}"
        )


@router.get("/top-holdings", response_model=List[Position])
async def get_top_holdings(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    limit: int = Query(10, ge=1, le=50, description="Number of top holdings to return")
) -> Any:
    """
    Get top holdings by market value
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            portfolio = await service.fetch_portfolio_data()
            top_holdings = sorted(
                portfolio.all_positions, 
                key=lambda p: p.market_value, 
                reverse=True
            )[:limit]
            
            return top_holdings
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top holdings: {str(e)}"
        )


@router.get("/allocation")
async def get_portfolio_allocation(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    breakdown_type: str = Query("sector", regex="^(sector|country|asset_type)$", description="Type of allocation breakdown")
) -> Any:
    """
    Get portfolio allocation breakdown by sector, country, or asset type
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            portfolio = await service.fetch_portfolio_data()
            
            if breakdown_type == "sector":
                allocation = portfolio.metrics.sector_allocation
            elif breakdown_type == "country":
                allocation = portfolio.metrics.country_allocation
            elif breakdown_type == "asset_type":
                allocation = portfolio.metrics.asset_type_allocation
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid breakdown type"
                )
            
            # Convert to list format for easier frontend consumption
            allocation_list = [
                {"category": category, "percentage": float(percentage), "value": float(percentage * portfolio.metrics.total_value / 100)}
                for category, percentage in allocation.items()
            ]
            
            return {
                "breakdown_type": breakdown_type,
                "total_value": float(portfolio.metrics.total_value),
                "allocations": allocation_list
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch allocation data: {str(e)}"
        )


@router.get("/historical")
async def get_portfolio_historical_data(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    period: str = Query("1y", regex="^(1d|5d|1m|3m|6m|1y|2y|5y|10y|ytd|max)$", description="Time period for historical data"),
    data_type: str = Query("value", regex="^(value|return|allocation)$", description="Type of historical data")
) -> Any:
    """
    Get historical portfolio data (value, returns, or allocation changes)
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # For now, return placeholder data as historical data requires external API integration
            # This would be implemented with the financial calculations engine
            current_portfolio = await service.fetch_portfolio_data()
            
            # Generate sample historical data points
            end_date = datetime.utcnow()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
                data_points = 24  # Hourly data
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
                data_points = 5  # Daily data
            elif period == "1m":
                start_date = end_date - timedelta(days=30)
                data_points = 30
            elif period == "3m":
                start_date = end_date - timedelta(days=90)
                data_points = 90
            elif period == "6m":
                start_date = end_date - timedelta(days=180)
                data_points = 180
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
                data_points = 365
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
                data_points = 104  # Weekly data
            elif period == "5y":
                start_date = end_date - timedelta(days=1825)
                data_points = 260  # Weekly data
            else:
                start_date = end_date - timedelta(days=365)
                data_points = 365
            
            # Placeholder response structure
            return {
                "period": period,
                "data_type": data_type,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "current_value": float(current_portfolio.metrics.total_value),
                "data_points": data_points,
                "message": "Historical data endpoint implemented. Integration with financial calculations engine required for actual historical data."
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.post("/refresh")
async def refresh_portfolio_data(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Force refresh of portfolio data from Trading 212
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Refresh portfolio data (this clears cache and fetches fresh data)
            portfolio = await service.refresh_portfolio_data(user_id)
            
            # Update last activity in session
            session_key = f"session:{user_id}"
            redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
            
            return {
                "message": "Portfolio data refreshed successfully",
                "last_updated": portfolio.last_updated.isoformat(),
                "total_value": float(portfolio.metrics.total_value),
                "pie_count": portfolio.pie_count,
                "position_count": portfolio.total_positions
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh portfolio data: {str(e)}"
        )


@router.get("/pies", response_model=List[Pie])
async def get_portfolio_pies(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    include_positions: bool = Query(True, description="Whether to include positions in each pie")
) -> Any:
    """
    Get all pies in the portfolio
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as service:
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            portfolio = await service.fetch_portfolio_data()
            pies = portfolio.pies
            
            # Optionally exclude positions to reduce response size
            if not include_positions:
                for pie in pies:
                    pie.positions = []
            
            return pies
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pies: {str(e)}"
        )