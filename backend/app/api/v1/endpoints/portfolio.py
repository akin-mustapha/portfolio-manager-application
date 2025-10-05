from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio

from core.deps import get_trading212_api_key, get_current_user_id, get_redis
from services.trading212_service import Trading212Service, Trading212APIError
from services.calculations_service import CalculationsService
from models.portfolio import Portfolio, PortfolioMetrics
from models.position import Position
from models.pie import Pie
from models.historical import HistoricalData
import redis

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
async def get_portfolio(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    redis_client: redis.Redis = Depends(get_redis)
) -> Any:
    """
    Get portfolio data from Trading 212
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        # Use the Trading 212 service to fetch real portfolio data
        async with Trading212Service() as service:
            # Authenticate with Trading 212
            auth_result = await service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch account info to get basic portfolio data
            account_info = await service.get_account_info()
            cash_data = await service.get_cash_balance()
            positions_data = await service.get_positions()
            
            # Calculate portfolio totals
            total_value = Decimal('0')
            total_invested = Decimal('0')
            
            for position in positions_data:
                market_value = Decimal(str(position.get('marketValue', 0)))
                quantity = Decimal(str(position.get('quantity', 0)))
                avg_price = Decimal(str(position.get('averagePrice', 0)))
                
                total_value += market_value
                total_invested += quantity * avg_price
            
            # Add cash balance to total value
            cash_balance = Decimal(str(cash_data.get('free', 0)))
            total_value += cash_balance
            
            # Calculate returns
            total_return = total_value - total_invested
            return_percentage = (total_return / total_invested * 100) if total_invested > 0 else Decimal('0')
            
            # Update last activity in session
            session_key = f"session:{user_id}"
            redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
            
            # Return real portfolio data from Trading 212
            return {
                "id": str(account_info.get("id", "unknown")),
                "totalValue": float(total_value),
                "totalInvested": float(total_invested),
                "totalReturn": float(total_return),
                "returnPercentage": float(return_percentage),
                "cashBalance": float(cash_balance),
                "currency": account_info.get("currencyCode", "USD"),
                "lastUpdated": datetime.utcnow().isoformat()
            }
            
    except Trading212APIError as e:
        if e.error_type == "rate_limit_exceeded":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trading 212 API rate limit exceeded. Please try again later."
            )
        elif e.error_type == "authentication_failure":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Trading 212 authentication failed"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Trading 212 API error: {e.message}"
            )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Portfolio endpoint error: {str(e)}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio: {str(e)}"
        )


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
    breakdown_type: str = Query("sector", regex="^(sector|industry|country|asset_type)$", description="Type of allocation breakdown")
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
            elif breakdown_type == "industry":
                allocation = portfolio.metrics.industry_allocation
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

@router.get("/diversification")
async def get_portfolio_diversification_analysis(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get comprehensive diversification analysis for the portfolio
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
            calc_service = CalculationsService()
            
            # Calculate diversification scores
            diversification = calc_service.calculate_diversification_score(portfolio.all_positions)
            
            return {
                "diversification_scores": diversification,
                "total_positions": len(portfolio.all_positions),
                "total_value": float(portfolio.metrics.total_value)
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch diversification analysis: {str(e)}"
        )


@router.get("/concentration")
async def get_portfolio_concentration_analysis(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get concentration risk analysis for the portfolio
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
            calc_service = CalculationsService()
            
            # Calculate concentration analysis
            concentration = calc_service.calculate_concentration_analysis(portfolio.all_positions)
            
            return concentration
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch concentration analysis: {str(e)}"
        )


@router.get("/allocation-analysis")
async def get_comprehensive_allocation_analysis(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get comprehensive allocation and diversification analysis
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
            calc_service = CalculationsService()
            
            # Calculate comprehensive allocation analysis
            analysis = calc_service.calculate_comprehensive_allocation_analysis(portfolio.all_positions)
            
            return analysis
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch allocation analysis: {str(e)}"
        )


@router.post("/allocation-drift")
async def detect_allocation_drift(
    target_allocations: Dict[str, Dict[str, float]],
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    tolerance_pct: float = Query(5.0, ge=0.1, le=50.0, description="Tolerance percentage for drift detection")
) -> Any:
    """
    Detect allocation drift from target allocations and get rebalancing recommendations
    
    Expected format for target_allocations:
    {
        "sector": {"Technology": 30.0, "Healthcare": 20.0, ...},
        "country": {"US": 60.0, "UK": 20.0, ...},
        "asset_type": {"STOCK": 80.0, "ETF": 20.0}
    }
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
            calc_service = CalculationsService()
            
            # Convert float values to Decimal for calculations
            decimal_targets = {}
            for category, allocations in target_allocations.items():
                decimal_targets[category] = {
                    k: Decimal(str(v)) for k, v in allocations.items()
                }
            
            # Detect allocation drift
            drift_analysis = calc_service.detect_allocation_drift(
                portfolio.all_positions, 
                decimal_targets, 
                Decimal(str(tolerance_pct))
            )
            
            return drift_analysis
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect allocation drift: {str(e)}"
        )