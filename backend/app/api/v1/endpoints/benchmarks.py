from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.deps import get_trading212_api_key, get_current_user_id
from app.services.trading212_service import Trading212Service, Trading212APIError
from app.models.benchmark import BenchmarkData, BenchmarkComparison

router = APIRouter()

# Common benchmark indices
AVAILABLE_BENCHMARKS = {
    "SPY": {"name": "SPDR S&P 500 ETF", "description": "S&P 500 Index"},
    "VTI": {"name": "Vanguard Total Stock Market ETF", "description": "Total US Stock Market"},
    "VXUS": {"name": "Vanguard Total International Stock ETF", "description": "Total International Stock Market"},
    "VEA": {"name": "Vanguard FTSE Developed Markets ETF", "description": "Developed Markets"},
    "VWO": {"name": "Vanguard FTSE Emerging Markets ETF", "description": "Emerging Markets"},
    "BND": {"name": "Vanguard Total Bond Market ETF", "description": "Total Bond Market"},
    "QQQ": {"name": "Invesco QQQ Trust", "description": "NASDAQ-100 Index"},
    "IWM": {"name": "iShares Russell 2000 ETF", "description": "Russell 2000 Small Cap"},
    "EFA": {"name": "iShares MSCI EAFE ETF", "description": "MSCI EAFE Index"},
    "AGG": {"name": "iShares Core US Aggregate Bond ETF", "description": "US Aggregate Bond Index"}
}


@router.get("/available")
async def get_available_benchmarks() -> Any:
    """
    Get list of available benchmark indices for comparison
    """
    benchmarks = []
    for symbol, info in AVAILABLE_BENCHMARKS.items():
        benchmarks.append({
            "symbol": symbol,
            "name": info["name"],
            "description": info["description"],
            "category": _get_benchmark_category(symbol)
        })
    
    return {
        "benchmarks": benchmarks,
        "total_count": len(benchmarks)
    }


@router.get("/{benchmark_symbol}/data")
async def get_benchmark_data(
    benchmark_symbol: str,
    period: str = Query("1y", regex="^(1d|5d|1m|3m|6m|1y|2y|5y|10y|ytd|max)$", description="Time period for benchmark data"),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Get historical data for a specific benchmark
    """
    if benchmark_symbol.upper() not in AVAILABLE_BENCHMARKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {benchmark_symbol} not available"
        )
    
    # This would integrate with external market data APIs
    # For now, return placeholder structure
    benchmark_info = AVAILABLE_BENCHMARKS[benchmark_symbol.upper()]
    
    return {
        "symbol": benchmark_symbol.upper(),
        "name": benchmark_info["name"],
        "description": benchmark_info["description"],
        "period": period,
        "data_points": _get_data_points_for_period(period),
        "message": "Benchmark data endpoint implemented. Integration with market data APIs (Alpha Vantage, Yahoo Finance) required for actual historical data."
    }


@router.post("/compare")
async def compare_portfolio_to_benchmark(
    benchmark_symbol: str = Query(..., description="Benchmark symbol to compare against"),
    period: str = Query("1y", regex="^(1d|5d|1m|3m|6m|1y|2y|5y|10y|ytd|max)$", description="Comparison period"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Compare portfolio performance against a benchmark index
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    if benchmark_symbol.upper() not in AVAILABLE_BENCHMARKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {benchmark_symbol} not available"
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
            benchmark_info = AVAILABLE_BENCHMARKS[benchmark_symbol.upper()]
            
            # Calculate basic comparison metrics
            # This would be enhanced with actual historical data and financial calculations
            portfolio_return = float(portfolio.metrics.total_return_pct)
            
            # Placeholder benchmark return (would come from market data API)
            benchmark_return = _get_placeholder_benchmark_return(benchmark_symbol.upper(), period)
            
            # Calculate comparison metrics
            alpha = portfolio_return - benchmark_return
            tracking_error = abs(alpha)  # Simplified calculation
            correlation = 0.85  # Placeholder correlation
            
            # Determine outperformance
            outperforming = portfolio_return > benchmark_return
            
            return {
                "comparison_period": period,
                "benchmark": {
                    "symbol": benchmark_symbol.upper(),
                    "name": benchmark_info["name"],
                    "return_pct": benchmark_return
                },
                "portfolio": {
                    "return_pct": portfolio_return,
                    "total_value": float(portfolio.metrics.total_value),
                    "volatility": float(portfolio.metrics.risk_metrics.volatility) if portfolio.metrics.risk_metrics else None
                },
                "comparison_metrics": {
                    "alpha": alpha,
                    "tracking_error": tracking_error,
                    "correlation": correlation,
                    "outperforming": outperforming,
                    "outperformance_amount": alpha
                },
                "message": "Portfolio vs benchmark comparison implemented. Integration with financial calculations engine required for accurate metrics."
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare portfolio to benchmark: {str(e)}"
        )


@router.post("/compare/pies")
async def compare_pies_to_benchmark(
    benchmark_symbol: str = Query(..., description="Benchmark symbol to compare against"),
    pie_ids: Optional[str] = Query(None, description="Comma-separated list of pie IDs to compare"),
    period: str = Query("1y", regex="^(1d|5d|1m|3m|6m|1y|2y|5y|10y|ytd|max)$", description="Comparison period"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Compare individual pies performance against a benchmark index
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    if benchmark_symbol.upper() not in AVAILABLE_BENCHMARKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {benchmark_symbol} not available"
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
            benchmark_info = AVAILABLE_BENCHMARKS[benchmark_symbol.upper()]
            
            # Filter pies if specific IDs provided
            pies_to_compare = portfolio.pies
            if pie_ids:
                pie_id_list = [pid.strip() for pid in pie_ids.split(",")]
                pies_to_compare = [p for p in portfolio.pies if p.id in pie_id_list]
            
            # Placeholder benchmark return
            benchmark_return = _get_placeholder_benchmark_return(benchmark_symbol.upper(), period)
            
            # Compare each pie to benchmark
            pie_comparisons = []
            for pie in pies_to_compare:
                pie_return = float(pie.metrics.total_return_pct)
                alpha = pie_return - benchmark_return
                
                pie_comparison = {
                    "pie_id": pie.id,
                    "pie_name": pie.name,
                    "pie_return_pct": pie_return,
                    "pie_value": float(pie.metrics.total_value),
                    "alpha": alpha,
                    "outperforming": pie_return > benchmark_return,
                    "tracking_error": abs(alpha),
                    "correlation": 0.80  # Placeholder
                }
                
                # Add risk metrics if available
                if pie.metrics.risk_metrics:
                    pie_comparison.update({
                        "volatility": float(pie.metrics.risk_metrics.volatility),
                        "sharpe_ratio": float(pie.metrics.risk_metrics.sharpe_ratio),
                        "beta": float(pie.metrics.risk_metrics.beta)
                    })
                
                pie_comparisons.append(pie_comparison)
            
            # Sort by alpha (outperformance)
            pie_comparisons.sort(key=lambda x: x["alpha"], reverse=True)
            
            return {
                "comparison_period": period,
                "benchmark": {
                    "symbol": benchmark_symbol.upper(),
                    "name": benchmark_info["name"],
                    "return_pct": benchmark_return
                },
                "pie_comparisons": pie_comparisons,
                "summary": {
                    "total_pies": len(pie_comparisons),
                    "outperforming_count": sum(1 for p in pie_comparisons if p["outperforming"]),
                    "best_performer": pie_comparisons[0] if pie_comparisons else None,
                    "worst_performer": pie_comparisons[-1] if pie_comparisons else None
                }
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare pies to benchmark: {str(e)}"
        )


@router.get("/custom/create")
async def create_custom_benchmark(
    name: str = Query(..., description="Custom benchmark name"),
    symbols: str = Query(..., description="Comma-separated list of symbols with optional weights (e.g., 'SPY:60,BND:40')"),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Create a custom benchmark from multiple indices with specified weights
    """
    try:
        # Parse symbols and weights
        benchmark_components = []
        total_weight = 0
        
        for component in symbols.split(","):
            component = component.strip()
            if ":" in component:
                symbol, weight_str = component.split(":")
                weight = float(weight_str)
            else:
                symbol = component
                weight = 100 / len(symbols.split(","))  # Equal weight if not specified
            
            symbol = symbol.upper()
            if symbol not in AVAILABLE_BENCHMARKS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Symbol {symbol} not available for benchmarking"
                )
            
            benchmark_components.append({
                "symbol": symbol,
                "name": AVAILABLE_BENCHMARKS[symbol]["name"],
                "weight": weight
            })
            total_weight += weight
        
        # Validate weights sum to 100%
        if abs(total_weight - 100) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Weights must sum to 100%, got {total_weight}%"
            )
        
        # Create custom benchmark ID
        custom_benchmark_id = f"custom_{user_id}_{hash(symbols)}".replace("-", "")[:20]
        
        return {
            "benchmark_id": custom_benchmark_id,
            "name": name,
            "components": benchmark_components,
            "total_weight": total_weight,
            "created_at": datetime.utcnow().isoformat(),
            "message": "Custom benchmark created. This would be stored for future comparisons in a full implementation."
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid weight format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom benchmark: {str(e)}"
        )


@router.get("/analysis/correlation")
async def get_correlation_analysis(
    benchmark_symbol: str = Query(..., description="Benchmark symbol for correlation analysis"),
    period: str = Query("1y", regex="^(1d|5d|1m|3m|6m|1y|2y|5y|10y|ytd|max)$", description="Analysis period"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get correlation analysis between portfolio/pies and benchmark
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    if benchmark_symbol.upper() not in AVAILABLE_BENCHMARKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {benchmark_symbol} not available"
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
            benchmark_info = AVAILABLE_BENCHMARKS[benchmark_symbol.upper()]
            
            # Calculate correlation metrics for portfolio and each pie
            portfolio_correlation = {
                "entity_type": "portfolio",
                "entity_id": portfolio.id,
                "entity_name": portfolio.name,
                "correlation": 0.85,  # Placeholder
                "beta": 1.1,  # Placeholder
                "r_squared": 0.72,  # Placeholder
                "tracking_error": 2.5  # Placeholder
            }
            
            pie_correlations = []
            for pie in portfolio.pies:
                pie_correlation = {
                    "entity_type": "pie",
                    "entity_id": pie.id,
                    "entity_name": pie.name,
                    "correlation": 0.75 + (hash(pie.id) % 20) / 100,  # Placeholder with variation
                    "beta": 0.9 + (hash(pie.id) % 40) / 100,  # Placeholder with variation
                    "r_squared": 0.60 + (hash(pie.id) % 30) / 100,  # Placeholder with variation
                    "tracking_error": 1.5 + (hash(pie.id) % 30) / 10  # Placeholder with variation
                }
                pie_correlations.append(pie_correlation)
            
            # Sort pies by correlation
            pie_correlations.sort(key=lambda x: x["correlation"], reverse=True)
            
            return {
                "analysis_period": period,
                "benchmark": {
                    "symbol": benchmark_symbol.upper(),
                    "name": benchmark_info["name"]
                },
                "portfolio_correlation": portfolio_correlation,
                "pie_correlations": pie_correlations,
                "summary": {
                    "highest_correlation": pie_correlations[0] if pie_correlations else None,
                    "lowest_correlation": pie_correlations[-1] if pie_correlations else None,
                    "average_correlation": sum(p["correlation"] for p in pie_correlations) / len(pie_correlations) if pie_correlations else 0
                },
                "message": "Correlation analysis implemented. Integration with financial calculations engine required for accurate correlation metrics."
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform correlation analysis: {str(e)}"
        )


def _get_benchmark_category(symbol: str) -> str:
    """Get category for benchmark symbol"""
    categories = {
        "SPY": "US Equity",
        "VTI": "US Equity",
        "QQQ": "US Equity",
        "IWM": "US Equity",
        "VXUS": "International Equity",
        "VEA": "International Equity",
        "VWO": "Emerging Markets",
        "EFA": "International Equity",
        "BND": "Fixed Income",
        "AGG": "Fixed Income"
    }
    return categories.get(symbol, "Other")


def _get_data_points_for_period(period: str) -> int:
    """Get number of data points for a given period"""
    data_points = {
        "1d": 24,
        "5d": 5,
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365,
        "2y": 104,  # Weekly
        "5y": 260,  # Weekly
        "10y": 520,  # Weekly
        "ytd": 250,
        "max": 1000
    }
    return data_points.get(period, 365)


def _get_placeholder_benchmark_return(symbol: str, period: str) -> float:
    """Get placeholder benchmark return for demonstration"""
    # Placeholder returns based on typical market performance
    base_returns = {
        "SPY": 10.5,
        "VTI": 11.2,
        "QQQ": 15.8,
        "IWM": 8.9,
        "VXUS": 7.3,
        "VEA": 6.8,
        "VWO": 5.2,
        "EFA": 6.5,
        "BND": 2.1,
        "AGG": 1.8
    }
    
    # Adjust for period
    period_multipliers = {
        "1d": 0.03,
        "5d": 0.15,
        "1m": 0.8,
        "3m": 2.5,
        "6m": 5.0,
        "1y": 1.0,
        "2y": 2.1,
        "5y": 5.5,
        "10y": 11.2,
        "ytd": 0.7,
        "max": 8.5
    }
    
    base_return = base_returns.get(symbol, 8.0)
    multiplier = period_multipliers.get(period, 1.0)
    
    return base_return * multiplier