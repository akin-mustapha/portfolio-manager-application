from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from datetime import datetime

from app.core.deps import get_trading212_api_key, get_current_user_id
from app.services.trading212_service import Trading212Service, Trading212APIError
from app.models.pie import Pie, PieMetrics
from app.models.position import Position

router = APIRouter()


@router.get("/{pie_id}", response_model=Pie)
async def get_pie_details(
    pie_id: str = Path(..., description="Unique pie identifier"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get detailed information for a specific pie
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
            
            # Find the specific pie
            pie = next((p for p in portfolio.pies if p.id == pie_id), None)
            if not pie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pie with ID {pie_id} not found"
                )
            
            return pie
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pie details: {str(e)}"
        )


@router.get("/{pie_id}/metrics", response_model=PieMetrics)
async def get_pie_metrics(
    pie_id: str = Path(..., description="Unique pie identifier"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get performance and risk metrics for a specific pie
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
            
            # Find the specific pie
            pie = next((p for p in portfolio.pies if p.id == pie_id), None)
            if not pie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pie with ID {pie_id} not found"
                )
            
            return pie.metrics
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pie metrics: {str(e)}"
        )


@router.get("/{pie_id}/positions", response_model=List[Position])
async def get_pie_positions(
    pie_id: str = Path(..., description="Unique pie identifier"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of positions to return"),
    sort_by: Optional[str] = Query("market_value", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order")
) -> Any:
    """
    Get all positions within a specific pie
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
            
            # Find the specific pie
            pie = next((p for p in portfolio.pies if p.id == pie_id), None)
            if not pie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pie with ID {pie_id} not found"
                )
            
            positions = pie.positions.copy()
            
            # Sort positions
            reverse_sort = sort_order == "desc"
            if sort_by == "market_value":
                positions.sort(key=lambda p: p.market_value, reverse=reverse_sort)
            elif sort_by == "unrealized_pnl":
                positions.sort(key=lambda p: p.unrealized_pnl, reverse=reverse_sort)
            elif sort_by == "unrealized_pnl_pct":
                positions.sort(key=lambda p: p.unrealized_pnl_pct, reverse=reverse_sort)
            elif sort_by == "symbol":
                positions.sort(key=lambda p: p.symbol, reverse=reverse_sort)
            
            # Apply limit
            if limit:
                positions = positions[:limit]
            
            return positions
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pie positions: {str(e)}"
        )


@router.get("/{pie_id}/allocation")
async def get_pie_allocation(
    pie_id: str = Path(..., description="Unique pie identifier"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    breakdown_type: str = Query("sector", regex="^(sector|country|asset_type|position)$", description="Type of allocation breakdown")
) -> Any:
    """
    Get allocation breakdown for a specific pie
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
            
            # Find the specific pie
            pie = next((p for p in portfolio.pies if p.id == pie_id), None)
            if not pie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pie with ID {pie_id} not found"
                )
            
            total_value = pie.metrics.total_value
            allocations = []
            
            if breakdown_type == "position":
                # Position-level allocation
                for position in pie.positions:
                    percentage = (position.market_value / total_value * 100) if total_value > 0 else 0
                    allocations.append({
                        "category": f"{position.symbol} - {position.name}",
                        "symbol": position.symbol,
                        "percentage": float(percentage),
                        "value": float(position.market_value)
                    })
            elif breakdown_type == "sector":
                # Sector allocation
                sector_totals = {}
                for position in pie.positions:
                    sector = position.sector or "Unknown"
                    sector_totals[sector] = sector_totals.get(sector, 0) + position.market_value
                
                for sector, value in sector_totals.items():
                    percentage = (value / total_value * 100) if total_value > 0 else 0
                    allocations.append({
                        "category": sector,
                        "percentage": float(percentage),
                        "value": float(value)
                    })
            elif breakdown_type == "country":
                # Country allocation
                country_totals = {}
                for position in pie.positions:
                    country = position.country or "Unknown"
                    country_totals[country] = country_totals.get(country, 0) + position.market_value
                
                for country, value in country_totals.items():
                    percentage = (value / total_value * 100) if total_value > 0 else 0
                    allocations.append({
                        "category": country,
                        "percentage": float(percentage),
                        "value": float(value)
                    })
            elif breakdown_type == "asset_type":
                # Asset type allocation
                asset_totals = {}
                for position in pie.positions:
                    asset_type = position.asset_type.value
                    asset_totals[asset_type] = asset_totals.get(asset_type, 0) + position.market_value
                
                for asset_type, value in asset_totals.items():
                    percentage = (value / total_value * 100) if total_value > 0 else 0
                    allocations.append({
                        "category": asset_type,
                        "percentage": float(percentage),
                        "value": float(value)
                    })
            
            # Sort by value descending
            allocations.sort(key=lambda x: x["value"], reverse=True)
            
            return {
                "pie_id": pie_id,
                "pie_name": pie.name,
                "breakdown_type": breakdown_type,
                "total_value": float(total_value),
                "allocations": allocations
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pie allocation: {str(e)}"
        )


@router.get("/{pie_id}/top-holdings", response_model=List[Position])
async def get_pie_top_holdings(
    pie_id: str = Path(..., description="Unique pie identifier"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    limit: int = Query(10, ge=1, le=50, description="Number of top holdings to return")
) -> Any:
    """
    Get top holdings within a specific pie by market value
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
            
            # Find the specific pie
            pie = next((p for p in portfolio.pies if p.id == pie_id), None)
            if not pie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pie with ID {pie_id} not found"
                )
            
            top_holdings = sorted(
                pie.positions, 
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
            detail=f"Failed to fetch pie top holdings: {str(e)}"
        )


@router.get("/compare")
async def compare_pies(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    pie_ids: Optional[str] = Query(None, description="Comma-separated list of pie IDs to compare"),
    metric: str = Query("total_return_pct", description="Metric to compare pies by"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of pies to return")
) -> Any:
    """
    Compare pies by various metrics
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
            
            # Filter pies if specific IDs provided
            pies_to_compare = portfolio.pies
            if pie_ids:
                pie_id_list = [pid.strip() for pid in pie_ids.split(",")]
                pies_to_compare = [p for p in portfolio.pies if p.id in pie_id_list]
            
            # Extract comparison data
            comparison_data = []
            for pie in pies_to_compare:
                pie_data = {
                    "pie_id": pie.id,
                    "name": pie.name,
                    "total_value": float(pie.metrics.total_value),
                    "invested_amount": float(pie.metrics.invested_amount),
                    "total_return": float(pie.metrics.total_return),
                    "total_return_pct": float(pie.metrics.total_return_pct),
                    "portfolio_weight": float(pie.metrics.portfolio_weight),
                    "portfolio_contribution": float(pie.metrics.portfolio_contribution),
                    "dividend_yield": float(pie.metrics.dividend_yield),
                    "position_count": pie.position_count,
                    "last_updated": pie.last_updated.isoformat()
                }
                
                # Add risk metrics if available
                if pie.metrics.risk_metrics:
                    pie_data.update({
                        "volatility": float(pie.metrics.risk_metrics.volatility),
                        "sharpe_ratio": float(pie.metrics.risk_metrics.sharpe_ratio),
                        "max_drawdown": float(pie.metrics.risk_metrics.max_drawdown),
                        "beta": float(pie.metrics.risk_metrics.beta)
                    })
                
                comparison_data.append(pie_data)
            
            # Sort by the specified metric
            reverse_sort = True  # Most metrics are better when higher
            if metric in ["volatility", "max_drawdown"]:  # These are better when lower
                reverse_sort = False
            
            if metric in comparison_data[0] if comparison_data else False:
                comparison_data.sort(key=lambda x: x.get(metric, 0), reverse=reverse_sort)
            
            # Apply limit
            comparison_data = comparison_data[:limit]
            
            return {
                "comparison_metric": metric,
                "total_pies": len(pies_to_compare),
                "pies": comparison_data
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare pies: {str(e)}"
        )


@router.get("/ranking")
async def get_pie_ranking(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key),
    rank_by: str = Query("total_return_pct", description="Metric to rank pies by"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Ranking order")
) -> Any:
    """
    Get pies ranked by performance metrics
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
            
            # Create ranking data
            ranking_data = []
            for pie in portfolio.pies:
                pie_data = {
                    "pie_id": pie.id,
                    "name": pie.name,
                    "total_value": float(pie.metrics.total_value),
                    "total_return_pct": float(pie.metrics.total_return_pct),
                    "portfolio_weight": float(pie.metrics.portfolio_weight),
                    "dividend_yield": float(pie.metrics.dividend_yield)
                }
                
                # Add risk metrics if available
                if pie.metrics.risk_metrics:
                    pie_data.update({
                        "volatility": float(pie.metrics.risk_metrics.volatility),
                        "sharpe_ratio": float(pie.metrics.risk_metrics.sharpe_ratio),
                        "max_drawdown": float(pie.metrics.risk_metrics.max_drawdown)
                    })
                
                ranking_data.append(pie_data)
            
            # Sort by ranking metric
            reverse_sort = order == "desc"
            if rank_by in ranking_data[0] if ranking_data else False:
                ranking_data.sort(key=lambda x: x.get(rank_by, 0), reverse=reverse_sort)
            
            # Add ranking positions
            for i, pie_data in enumerate(ranking_data):
                pie_data["rank"] = i + 1
            
            return {
                "ranking_metric": rank_by,
                "ranking_order": order,
                "total_pies": len(ranking_data),
                "rankings": ranking_data
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pie rankings: {str(e)}"
        )