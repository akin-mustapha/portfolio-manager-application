from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from core.deps import get_trading212_api_key, get_current_user_id
from core.config import settings
from services.trading212_service import Trading212Service, Trading212APIError
from services.benchmark_service import BenchmarkService, BenchmarkAPIError
from models.benchmark import BenchmarkData, BenchmarkComparison, BenchmarkInfo

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/available")
async def get_available_benchmarks() -> Any:
    """
    Get list of available benchmark indices for comparison
    """
    try:
        async with BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as service:
            supported_benchmarks = service.get_supported_benchmarks()
            
            benchmarks = []
            for symbol, info in supported_benchmarks.items():
                benchmarks.append({
                    "symbol": info.symbol,
                    "name": info.name,
                    "description": info.description,
                    "category": info.category
                })
            
            return {
                "benchmarks": benchmarks,
                "total_count": len(benchmarks)
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available benchmarks: {str(e)}"
        )


@router.get("/{benchmark_symbol}/data")
async def get_benchmark_data(
    benchmark_symbol: str,
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period for benchmark data"),
    use_cache: bool = Query(True, description="Whether to use cached data"),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Get historical data for a specific benchmark
    """
    try:
        async with BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as service:
            # Check if benchmark is supported
            benchmark_info = await service.get_benchmark_info(benchmark_symbol.upper())
            if not benchmark_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Benchmark {benchmark_symbol} not available"
                )
            
            # Fetch benchmark data
            benchmark_data = await service.fetch_benchmark_data(
                symbol=benchmark_symbol.upper(),
                period=period,
                use_cache=use_cache
            )
            
            if not benchmark_data:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to fetch data for benchmark {benchmark_symbol}"
                )
            
            return benchmark_data.dict()
            
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get benchmark data: {str(e)}"
        )


@router.post("/compare")
async def compare_portfolio_to_benchmark(
    benchmark_symbol: str = Query(..., description="Benchmark symbol to compare against"),
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Comparison period"),
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
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Compare portfolio to benchmark
            comparison = await benchmark_service.compare_portfolio_to_benchmark(
                portfolio=portfolio,
                benchmark_symbol=benchmark_symbol.upper(),
                period=period
            )
            
            return comparison.dict()
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
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
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Comparison period"),
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
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Filter pies if specific IDs provided
            pies_to_compare = portfolio.pies
            if pie_ids:
                pie_id_list = [pid.strip() for pid in pie_ids.split(",")]
                pies_to_compare = [p for p in portfolio.pies if p.id in pie_id_list]
            
            # Compare each pie to benchmark
            pie_comparisons = []
            for pie in pies_to_compare:
                try:
                    comparison = await benchmark_service.compare_pie_to_benchmark(
                        pie=pie,
                        benchmark_symbol=benchmark_symbol.upper(),
                        period=period
                    )
                    pie_comparisons.append(comparison.dict())
                except Exception as e:
                    logger.warning(f"Failed to compare pie {pie.name}: {e}")
            
            # Sort by alpha (outperformance)
            pie_comparisons.sort(key=lambda x: float(x["alpha"]), reverse=True)
            
            # Get benchmark info for response
            benchmark_info = await benchmark_service.get_benchmark_info(benchmark_symbol.upper())
            
            return {
                "comparison_period": period,
                "benchmark": {
                    "symbol": benchmark_symbol.upper(),
                    "name": benchmark_info.name if benchmark_info else benchmark_symbol,
                    "description": benchmark_info.description if benchmark_info else ""
                },
                "pie_comparisons": pie_comparisons,
                "summary": {
                    "total_pies": len(pie_comparisons),
                    "outperforming_count": sum(1 for p in pie_comparisons if p["outperforming"]),
                    "best_performer": pie_comparisons[0] if pie_comparisons else None,
                    "worst_performer": pie_comparisons[-1] if pie_comparisons else None,
                    "average_alpha": sum(float(p["alpha"]) for p in pie_comparisons) / len(pie_comparisons) if pie_comparisons else 0
                }
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare pies to benchmark: {str(e)}"
        )


@router.post("/custom/create")
async def create_custom_benchmark(
    name: str = Query(..., description="Custom benchmark name"),
    symbols: str = Query(..., description="Comma-separated list of symbols with optional weights (e.g., 'SPY:60,AGG:40')"),
    description: Optional[str] = Query(None, description="Optional description for the custom benchmark"),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Create a custom benchmark from multiple indices with specified weights
    """
    try:
        async with BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as service:
            # Parse symbols and weights
            components = []
            
            for component in symbols.split(","):
                component = component.strip()
                if ":" in component:
                    symbol, weight_str = component.split(":")
                    weight = float(weight_str)
                else:
                    symbol = component
                    weight = 100 / len(symbols.split(","))  # Equal weight if not specified
                
                components.append({
                    "symbol": symbol.upper(),
                    "weight": weight
                })
            
            # Create custom benchmark
            custom_benchmark = await service.create_custom_benchmark(
                name=name,
                components=components,
                user_id=user_id,
                description=description
            )
            
            return custom_benchmark.dict()
            
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
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


@router.post("/analysis/comprehensive")
async def get_comprehensive_benchmark_analysis(
    benchmark_symbol: str = Query(..., description="Benchmark symbol for analysis"),
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Analysis period"),
    include_pies: bool = Query(True, description="Whether to include pie comparisons"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get comprehensive benchmark analysis for portfolio and pies
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Perform comprehensive analysis
            analysis = await benchmark_service.compare_multiple_entities_to_benchmark(
                portfolio=portfolio,
                benchmark_symbol=benchmark_symbol.upper(),
                period=period,
                include_pies=include_pies
            )
            
            return analysis.dict()
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform comprehensive analysis: {str(e)}"
        )


@router.get("/recommendations")
async def get_benchmark_recommendations(
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get benchmark recommendations based on portfolio composition
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Get recommendations
            recommendations = await benchmark_service.get_benchmark_selection_recommendations(portfolio)
            
            return {
                "recommendations": [rec.dict() for rec in recommendations],
                "total_count": len(recommendations),
                "portfolio_summary": {
                    "total_value": float(portfolio.metrics.total_value),
                    "pie_count": len(portfolio.pies),
                    "individual_positions": len(portfolio.individual_positions)
                }
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get benchmark recommendations: {str(e)}"
        )


@router.get("/search")
async def search_benchmarks(
    query: str = Query(..., description="Search query for benchmarks"),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Search for benchmarks by name, symbol, or description
    """
    try:
        async with BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as service:
            matches = await service.search_benchmarks(query)
            
            return {
                "query": query,
                "matches": [match.dict() for match in matches],
                "total_count": len(matches)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search benchmarks: {str(e)}"
        )


@router.get("/chart-data/{benchmark_symbol}")
async def get_benchmark_chart_data(
    benchmark_symbol: str,
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    entity_type: str = Query("portfolio", regex="^(portfolio|pie)$", description="Entity type to compare"),
    entity_id: Optional[str] = Query(None, description="Entity ID (required for pie comparison)"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get chart data for benchmark comparison visualization
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Fetch benchmark data
            benchmark_data = await benchmark_service.fetch_benchmark_data(
                symbol=benchmark_symbol.upper(),
                period=period
            )
            
            if not benchmark_data:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to fetch benchmark data for {benchmark_symbol}"
                )
            
            # Prepare entity returns based on type
            if entity_type == "portfolio":
                entity_returns = benchmark_service._calculate_portfolio_returns_series(portfolio, period)
                entity_name = portfolio.name
            else:  # pie
                if not entity_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Entity ID required for pie comparison"
                    )
                
                pie = next((p for p in portfolio.pies if p.id == entity_id), None)
                if not pie:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Pie with ID {entity_id} not found"
                    )
                
                entity_returns = benchmark_service._calculate_pie_returns_series(pie, period)
                entity_name = pie.name
            
            # Prepare chart data
            chart_data = await benchmark_service.prepare_performance_comparison_chart_data(
                entity_returns=entity_returns,
                benchmark_data=benchmark_data,
                entity_name=entity_name
            )
            
            return chart_data
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chart data: {str(e)}"
        )


@router.delete("/cache")
async def clear_benchmark_cache(
    symbol: Optional[str] = Query(None, description="Specific symbol to clear, or all if not provided"),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Clear benchmark data cache
    """
    try:
        async with BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as service:
            await service.clear_benchmark_cache(symbol)
            
            return {
                "message": f"Cache cleared for {'all benchmarks' if not symbol else symbol}",
                "cleared_symbol": symbol
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.post("/compare/advanced")
async def get_advanced_benchmark_comparison(
    benchmark_symbol: str = Query(..., description="Benchmark symbol to compare against"),
    entity_type: str = Query("portfolio", regex="^(portfolio|pie)$", description="Entity type to compare"),
    entity_id: Optional[str] = Query(None, description="Entity ID (required for pie comparison)"),
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Comparison period"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Get advanced benchmark comparison with additional metrics like Treynor ratio, Jensen's alpha, etc.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Fetch benchmark data
            benchmark_data = await benchmark_service.fetch_benchmark_data(
                symbol=benchmark_symbol.upper(),
                period=period
            )
            
            if not benchmark_data:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to fetch benchmark data for {benchmark_symbol}"
                )
            
            # Get entity returns and name
            if entity_type == "portfolio":
                entity_returns = benchmark_service._calculate_portfolio_returns_series(portfolio, period)
                entity_name = portfolio.name
            else:  # pie
                if not entity_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Entity ID required for pie comparison"
                    )
                
                pie = next((p for p in portfolio.pies if p.id == entity_id), None)
                if not pie:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Pie with ID {entity_id} not found"
                    )
                
                entity_returns = benchmark_service._calculate_pie_returns_series(pie, period)
                entity_name = pie.name
            
            # Get benchmark returns
            benchmark_returns = benchmark_service._calculate_returns_series(benchmark_data.data_points)
            
            # Calculate basic comparison
            basic_comparison = await benchmark_service.calculate_benchmark_comparison(
                entity_returns=entity_returns,
                benchmark_data=benchmark_data,
                entity_type=entity_type,
                entity_id=entity_id or portfolio.id,
                entity_name=entity_name
            )
            
            # Calculate advanced metrics
            advanced_metrics = await benchmark_service.get_advanced_comparison_metrics(
                entity_returns=entity_returns,
                benchmark_returns=benchmark_returns,
                entity_name=entity_name,
                benchmark_name=benchmark_data.name
            )
            
            return {
                "basic_comparison": basic_comparison.dict(),
                "advanced_metrics": advanced_metrics,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get advanced comparison: {str(e)}"
        )


@router.post("/custom/{custom_benchmark_id}/compare")
async def compare_to_custom_benchmark(
    custom_benchmark_id: str,
    entity_type: str = Query("portfolio", regex="^(portfolio|pie)$", description="Entity type to compare"),
    entity_id: Optional[str] = Query(None, description="Entity ID (required for pie comparison)"),
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Comparison period"),
    user_id: str = Depends(get_current_user_id),
    api_key: str = Depends(get_trading212_api_key)
) -> Any:
    """
    Compare portfolio or pie performance against a custom benchmark
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading 212 API key not configured"
        )
    
    try:
        async with Trading212Service() as trading_service, BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as benchmark_service:
            # Authenticate with Trading 212
            auth_result = await trading_service.authenticate(api_key)
            if not auth_result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Trading 212 authentication failed: {auth_result.message}"
                )
            
            # Fetch portfolio data
            portfolio = await trading_service.fetch_portfolio_data()
            
            # Get custom benchmark from cache
            cache_key = f"custom_benchmark:{custom_benchmark_id}"
            cached_data = await benchmark_service._get_cached_data(cache_key)
            
            if not cached_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Custom benchmark {custom_benchmark_id} not found"
                )
            
            from app.models.benchmark import CustomBenchmark
            custom_benchmark = CustomBenchmark(**cached_data)
            
            # Calculate custom benchmark data
            custom_benchmark_data = await benchmark_service.calculate_custom_benchmark_data(
                custom_benchmark, period
            )
            
            # Get entity returns and name
            if entity_type == "portfolio":
                entity_returns = benchmark_service._calculate_portfolio_returns_series(portfolio, period)
                entity_name = portfolio.name
            else:  # pie
                if not entity_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Entity ID required for pie comparison"
                    )
                
                pie = next((p for p in portfolio.pies if p.id == entity_id), None)
                if not pie:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Pie with ID {entity_id} not found"
                    )
                
                entity_returns = benchmark_service._calculate_pie_returns_series(pie, period)
                entity_name = pie.name
            
            # Calculate comparison
            comparison = await benchmark_service.calculate_benchmark_comparison(
                entity_returns=entity_returns,
                benchmark_data=custom_benchmark_data,
                entity_type=entity_type,
                entity_id=entity_id or portfolio.id,
                entity_name=entity_name
            )
            
            return {
                "comparison": comparison.dict(),
                "custom_benchmark": custom_benchmark.dict(),
                "custom_benchmark_performance": {
                    "total_return_pct": float(custom_benchmark_data.total_return_pct),
                    "annualized_return_pct": float(custom_benchmark_data.annualized_return_pct),
                    "volatility": float(custom_benchmark_data.volatility),
                    "sharpe_ratio": float(custom_benchmark_data.sharpe_ratio)
                }
            }
            
    except Trading212APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trading 212 API error: {e.message}"
        )
    except BenchmarkAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare to custom benchmark: {str(e)}"
        )


@router.get("/health")
async def get_benchmark_service_health() -> Any:
    """
    Check the health of benchmark data sources
    """
    try:
        async with BenchmarkService(settings.ALPHA_VANTAGE_API_KEY) as service:
            health_status = await service.health_check()
            
            return {
                "status": "healthy" if any(source["available"] for source in health_status.values()) else "unhealthy",
                "data_sources": health_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


