"""
Benchmark data fetching service.

This service handles fetching benchmark data from various market data APIs,
caching, and providing benchmark comparison functionality.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import re

import httpx
import redis.asyncio as redis
import pandas as pd
import numpy as np
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.models.benchmark import (
    BenchmarkInfo, BenchmarkData, BenchmarkDataPoint, BenchmarkComparison,
    CustomBenchmark, BenchmarkAnalysis
)
from app.models.portfolio import Portfolio
from app.models.pie import Pie


logger = logging.getLogger(__name__)


class BenchmarkAPIError(Exception):
    """Custom exception for benchmark API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_type: str = "api_error"):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)


class BenchmarkService:
    """
    Service for fetching and managing benchmark data.
    
    Supports multiple data sources including Alpha Vantage and Yahoo Finance.
    Provides caching and comparison functionality.
    """
    
    # Predefined benchmark indices
    SUPPORTED_BENCHMARKS = {
        "SPY": BenchmarkInfo(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            description="Tracks the S&P 500 Index",
            category="US Equity"
        ),
        "QQQ": BenchmarkInfo(
            symbol="QQQ",
            name="Invesco QQQ Trust",
            description="Tracks the NASDAQ-100 Index",
            category="US Technology"
        ),
        "VTI": BenchmarkInfo(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            description="Tracks the entire US stock market",
            category="US Total Market"
        ),
        "VXUS": BenchmarkInfo(
            symbol="VXUS",
            name="Vanguard Total International Stock ETF",
            description="Tracks international developed and emerging markets",
            category="International Equity"
        ),
        "EFA": BenchmarkInfo(
            symbol="EFA",
            name="iShares MSCI EAFE ETF",
            description="Tracks developed markets excluding US and Canada",
            category="International Developed"
        ),
        "VWO": BenchmarkInfo(
            symbol="VWO",
            name="Vanguard Emerging Markets Stock ETF",
            description="Tracks emerging markets equity",
            category="Emerging Markets"
        ),
        "AGG": BenchmarkInfo(
            symbol="AGG",
            name="iShares Core US Aggregate Bond ETF",
            description="Tracks the US investment-grade bond market",
            category="US Bonds"
        ),
        "VNQ": BenchmarkInfo(
            symbol="VNQ",
            name="Vanguard Real Estate ETF",
            description="Tracks US real estate investment trusts",
            category="Real Estate"
        )
    }
    
    def __init__(self, alpha_vantage_api_key: Optional[str] = None):
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self.session: Optional[httpx.AsyncClient] = None
        self.redis_client: Optional[redis.Redis] = None
        self._rate_limits = {
            "alpha_vantage": {"requests": 0, "reset_time": datetime.utcnow()},
            "yahoo_finance": {"requests": 0, "reset_time": datetime.utcnow()}
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
    
    async def _init_session(self):
        """Initialize HTTP session and Redis connection."""
        # Initialize HTTP client
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": "Trading212-Portfolio-Dashboard/1.0",
                "Accept": "application/json"
            }
        )
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connection established for benchmark service")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def _close_session(self):
        """Close HTTP session and Redis connection."""
        if self.session:
            await self.session.aclose()
        if self.redis_client:
            await self.redis_client.close()
    
    def get_supported_benchmarks(self) -> Dict[str, BenchmarkInfo]:
        """
        Get list of supported benchmark indices.
        
        Returns:
            Dictionary of supported benchmarks
        """
        return self.SUPPORTED_BENCHMARKS.copy()
    
    async def _check_rate_limit(self, provider: str) -> bool:
        """
        Check if we're within rate limits for a provider.
        
        Args:
            provider: API provider name
            
        Returns:
            True if within limits, False otherwise
        """
        if provider not in self._rate_limits:
            return True
        
        rate_info = self._rate_limits[provider]
        now = datetime.utcnow()
        
        # Reset counters if enough time has passed
        if now >= rate_info["reset_time"]:
            rate_info["requests"] = 0
            if provider == "alpha_vantage":
                rate_info["reset_time"] = now + timedelta(minutes=1)  # 5 calls per minute
            elif provider == "yahoo_finance":
                rate_info["reset_time"] = now + timedelta(seconds=1)  # More lenient
        
        # Check limits
        if provider == "alpha_vantage" and rate_info["requests"] >= 5:
            return False
        elif provider == "yahoo_finance" and rate_info["requests"] >= 100:
            return False
        
        return True
    
    async def _increment_rate_limit(self, provider: str):
        """Increment rate limit counter for a provider."""
        if provider in self._rate_limits:
            self._rate_limits[provider]["requests"] += 1
    
    async def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from Redis cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        return None
    
    async def _set_cached_data(self, cache_key: str, data: Dict[str, Any], ttl: int = 3600):
        """
        Store data in Redis cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    async def _fetch_alpha_vantage_data(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch historical data from Alpha Vantage API.
        
        Args:
            symbol: Stock/ETF symbol
            period: Time period (1y, 2y, 5y, max)
            
        Returns:
            Raw API response data or None if failed
        """
        if not self.alpha_vantage_api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None
        
        if not await self._check_rate_limit("alpha_vantage"):
            logger.warning("Alpha Vantage rate limit exceeded")
            return None
        
        try:
            # Map period to Alpha Vantage function
            if period in ["1d", "5d"]:
                function = "TIME_SERIES_INTRADAY"
                interval = "60min"
            else:
                function = "TIME_SERIES_DAILY_ADJUSTED"
                interval = None
            
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.alpha_vantage_api_key,
                "outputsize": "full"
            }
            
            if interval:
                params["interval"] = interval
            
            response = await self.session.get(
                "https://www.alphavantage.co/query",
                params=params
            )
            
            await self._increment_rate_limit("alpha_vantage")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error: {data['Error Message']}")
                    return None
                
                if "Note" in data:
                    logger.warning(f"Alpha Vantage note: {data['Note']}")
                    return None
                
                return data
            else:
                logger.error(f"Alpha Vantage API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Alpha Vantage request failed: {e}")
            return None
    
    async def _fetch_yahoo_finance_data(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch historical data from Yahoo Finance (unofficial API).
        
        Args:
            symbol: Stock/ETF symbol
            period: Time period (1y, 2y, 5y, max)
            
        Returns:
            Raw API response data or None if failed
        """
        if not await self._check_rate_limit("yahoo_finance"):
            logger.warning("Yahoo Finance rate limit exceeded")
            return None
        
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            elif period == "5y":
                start_date = end_date - timedelta(days=1825)
            else:  # max
                start_date = end_date - timedelta(days=3650)  # 10 years
            
            # Convert to Unix timestamps
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            # Yahoo Finance query URL
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "period1": start_timestamp,
                "period2": end_timestamp,
                "interval": "1d",
                "includePrePost": "false",
                "events": "div,splits"
            }
            
            response = await self.session.get(url, params=params)
            await self._increment_rate_limit("yahoo_finance")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for errors
                if "chart" not in data or not data["chart"]["result"]:
                    logger.error(f"Yahoo Finance error: No data for {symbol}")
                    return None
                
                return data
            else:
                logger.error(f"Yahoo Finance API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Yahoo Finance request failed: {e}")
            return None
    
    def _transform_alpha_vantage_data(
        self, 
        raw_data: Dict[str, Any], 
        symbol: str,
        period: str
    ) -> Optional[BenchmarkData]:
        """
        Transform Alpha Vantage data to internal BenchmarkData model.
        
        Args:
            raw_data: Raw Alpha Vantage response
            symbol: Benchmark symbol
            period: Time period
            
        Returns:
            BenchmarkData model or None if transformation failed
        """
        try:
            # Find the time series data
            time_series_key = None
            for key in raw_data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                logger.error("No time series data found in Alpha Vantage response")
                return None
            
            time_series = raw_data[time_series_key]
            
            # Transform data points
            data_points = []
            prices = []
            dates = []
            
            for date_str, values in sorted(time_series.items()):
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    close_price = Decimal(str(values.get("4. close", values.get("close", 0))))
                    volume = int(values.get("6. volume", values.get("volume", 0)))
                    
                    data_points.append(BenchmarkDataPoint(
                        date=date_obj,
                        price=close_price,
                        volume=volume
                    ))
                    
                    prices.append(float(close_price))
                    dates.append(date_obj)
                    
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid data point: {e}")
                    continue
            
            if not data_points:
                logger.error("No valid data points found")
                return None
            
            # Calculate returns for each data point
            for i in range(1, len(data_points)):
                prev_price = data_points[i-1].price
                curr_price = data_points[i].price
                if prev_price > 0:
                    return_pct = (curr_price - prev_price) / prev_price * 100
                    data_points[i].return_pct = return_pct
            
            # Calculate summary statistics
            if len(prices) > 1:
                total_return_pct = (prices[-1] - prices[0]) / prices[0] * 100
                
                # Calculate annualized return
                days = (dates[-1] - dates[0]).days
                if days > 0:
                    years = days / 365.25
                    annualized_return_pct = ((prices[-1] / prices[0]) ** (1/years) - 1) * 100
                else:
                    annualized_return_pct = total_return_pct
                
                # Calculate volatility (daily returns standard deviation)
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized
                
                # Calculate maximum drawdown
                peak = prices[0]
                max_drawdown = 0
                for price in prices:
                    if price > peak:
                        peak = price
                    drawdown = (peak - price) / peak
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                max_drawdown_pct = max_drawdown * 100
                
                # Calculate Sharpe ratio (assuming 2% risk-free rate)
                risk_free_rate = 2.0
                if volatility > 0:
                    sharpe_ratio = (annualized_return_pct - risk_free_rate) / volatility
                else:
                    sharpe_ratio = 0
            else:
                total_return_pct = 0
                annualized_return_pct = 0
                volatility = 0
                max_drawdown_pct = 0
                sharpe_ratio = 0
            
            # Get benchmark info
            benchmark_info = self.SUPPORTED_BENCHMARKS.get(symbol)
            benchmark_name = benchmark_info.name if benchmark_info else symbol
            
            return BenchmarkData(
                symbol=symbol,
                name=benchmark_name,
                period=period,
                start_date=dates[0] if dates else datetime.utcnow(),
                end_date=dates[-1] if dates else datetime.utcnow(),
                data_points=data_points,
                total_return_pct=Decimal(str(total_return_pct)),
                annualized_return_pct=Decimal(str(annualized_return_pct)),
                volatility=Decimal(str(volatility)),
                max_drawdown=Decimal(str(max_drawdown_pct)),
                sharpe_ratio=Decimal(str(sharpe_ratio))
            )
            
        except Exception as e:
            logger.error(f"Failed to transform Alpha Vantage data: {e}")
            return None
    
    def _transform_yahoo_finance_data(
        self, 
        raw_data: Dict[str, Any], 
        symbol: str,
        period: str
    ) -> Optional[BenchmarkData]:
        """
        Transform Yahoo Finance data to internal BenchmarkData model.
        
        Args:
            raw_data: Raw Yahoo Finance response
            symbol: Benchmark symbol
            period: Time period
            
        Returns:
            BenchmarkData model or None if transformation failed
        """
        try:
            chart_data = raw_data["chart"]["result"][0]
            
            # Extract timestamps and prices
            timestamps = chart_data["timestamp"]
            indicators = chart_data["indicators"]["quote"][0]
            closes = indicators["close"]
            volumes = indicators.get("volume", [None] * len(closes))
            
            # Transform data points
            data_points = []
            prices = []
            dates = []
            
            for i, (timestamp, close, volume) in enumerate(zip(timestamps, closes, volumes)):
                if close is None:
                    continue
                
                try:
                    date_obj = datetime.fromtimestamp(timestamp)
                    close_price = Decimal(str(close))
                    vol = int(volume) if volume is not None else None
                    
                    data_points.append(BenchmarkDataPoint(
                        date=date_obj,
                        price=close_price,
                        volume=vol
                    ))
                    
                    prices.append(float(close_price))
                    dates.append(date_obj)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid data point: {e}")
                    continue
            
            if not data_points:
                logger.error("No valid data points found")
                return None
            
            # Calculate returns for each data point
            for i in range(1, len(data_points)):
                prev_price = data_points[i-1].price
                curr_price = data_points[i].price
                if prev_price > 0:
                    return_pct = (curr_price - prev_price) / prev_price * 100
                    data_points[i].return_pct = return_pct
            
            # Calculate summary statistics (same logic as Alpha Vantage)
            if len(prices) > 1:
                total_return_pct = (prices[-1] - prices[0]) / prices[0] * 100
                
                days = (dates[-1] - dates[0]).days
                if days > 0:
                    years = days / 365.25
                    annualized_return_pct = ((prices[-1] / prices[0]) ** (1/years) - 1) * 100
                else:
                    annualized_return_pct = total_return_pct
                
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                volatility = np.std(returns) * np.sqrt(252) * 100
                
                peak = prices[0]
                max_drawdown = 0
                for price in prices:
                    if price > peak:
                        peak = price
                    drawdown = (peak - price) / peak
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                max_drawdown_pct = max_drawdown * 100
                
                risk_free_rate = 2.0
                if volatility > 0:
                    sharpe_ratio = (annualized_return_pct - risk_free_rate) / volatility
                else:
                    sharpe_ratio = 0
            else:
                total_return_pct = 0
                annualized_return_pct = 0
                volatility = 0
                max_drawdown_pct = 0
                sharpe_ratio = 0
            
            # Get benchmark info
            benchmark_info = self.SUPPORTED_BENCHMARKS.get(symbol)
            benchmark_name = benchmark_info.name if benchmark_info else symbol
            
            return BenchmarkData(
                symbol=symbol,
                name=benchmark_name,
                period=period,
                start_date=dates[0] if dates else datetime.utcnow(),
                end_date=dates[-1] if dates else datetime.utcnow(),
                data_points=data_points,
                total_return_pct=Decimal(str(total_return_pct)),
                annualized_return_pct=Decimal(str(annualized_return_pct)),
                volatility=Decimal(str(volatility)),
                max_drawdown=Decimal(str(max_drawdown_pct)),
                sharpe_ratio=Decimal(str(sharpe_ratio))
            )
            
        except Exception as e:
            logger.error(f"Failed to transform Yahoo Finance data: {e}")
            return None
    
    async def fetch_benchmark_data(
        self, 
        symbol: str, 
        period: str = "1y",
        use_cache: bool = True
    ) -> Optional[BenchmarkData]:
        """
        Fetch benchmark historical data from available APIs.
        
        Args:
            symbol: Benchmark symbol (e.g., SPY, QQQ)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            use_cache: Whether to use cached data
            
        Returns:
            BenchmarkData model or None if failed
        """
        # Check cache first
        cache_key = f"benchmark:{symbol}:{period}"
        if use_cache:
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                try:
                    return BenchmarkData(**cached_data)
                except ValidationError as e:
                    logger.warning(f"Invalid cached data: {e}")
        
        # Try Alpha Vantage first, then Yahoo Finance
        benchmark_data = None
        
        # Try Alpha Vantage
        if self.alpha_vantage_api_key:
            raw_data = await self._fetch_alpha_vantage_data(symbol, period)
            if raw_data:
                benchmark_data = self._transform_alpha_vantage_data(raw_data, symbol, period)
        
        # Fallback to Yahoo Finance
        if not benchmark_data:
            raw_data = await self._fetch_yahoo_finance_data(symbol, period)
            if raw_data:
                benchmark_data = self._transform_yahoo_finance_data(raw_data, symbol, period)
        
        # Cache successful result
        if benchmark_data and use_cache:
            cache_ttl = 3600  # 1 hour for daily data
            if period in ["1d", "5d"]:
                cache_ttl = 300  # 5 minutes for short-term data
            elif period in ["1y", "2y", "5y", "max"]:
                cache_ttl = 7200  # 2 hours for long-term data
            
            await self._set_cached_data(cache_key, benchmark_data.dict(), cache_ttl)
        
        if benchmark_data:
            logger.info(f"Successfully fetched benchmark data for {symbol} ({period})")
        else:
            logger.error(f"Failed to fetch benchmark data for {symbol} ({period})")
        
        return benchmark_data
    
    async def fetch_multiple_benchmarks(
        self, 
        symbols: List[str], 
        period: str = "1y",
        use_cache: bool = True
    ) -> Dict[str, Optional[BenchmarkData]]:
        """
        Fetch data for multiple benchmarks concurrently.
        
        Args:
            symbols: List of benchmark symbols
            period: Time period
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary mapping symbols to BenchmarkData
        """
        tasks = [
            self.fetch_benchmark_data(symbol, period, use_cache)
            for symbol in symbols
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        benchmark_data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {symbol}: {result}")
                benchmark_data[symbol] = None
            else:
                benchmark_data[symbol] = result
        
        return benchmark_data
    
    async def get_benchmark_info(self, symbol: str) -> Optional[BenchmarkInfo]:
        """
        Get information about a benchmark.
        
        Args:
            symbol: Benchmark symbol
            
        Returns:
            BenchmarkInfo or None if not found
        """
        return self.SUPPORTED_BENCHMARKS.get(symbol)
    
    async def search_benchmarks(self, query: str) -> List[BenchmarkInfo]:
        """
        Search for benchmarks by name or symbol.
        
        Args:
            query: Search query
            
        Returns:
            List of matching BenchmarkInfo objects
        """
        query_lower = query.lower()
        matches = []
        
        for benchmark in self.SUPPORTED_BENCHMARKS.values():
            if (query_lower in benchmark.symbol.lower() or 
                query_lower in benchmark.name.lower() or 
                query_lower in benchmark.description.lower() or
                query_lower in benchmark.category.lower()):
                matches.append(benchmark)
        
        return matches
    
    async def clear_benchmark_cache(self, symbol: Optional[str] = None):
        """
        Clear benchmark data cache.
        
        Args:
            symbol: Specific symbol to clear, or None to clear all
        """
        if not self.redis_client:
            return
        
        try:
            if symbol:
                # Clear specific symbol
                pattern = f"benchmark:{symbol}:*"
            else:
                # Clear all benchmark data
                pattern = "benchmark:*"
            
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} benchmark cache entries")
        except Exception as e:
            logger.error(f"Failed to clear benchmark cache: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of benchmark data sources.
        
        Returns:
            Health status for each data source
        """
        health_status = {
            "alpha_vantage": {"available": False, "error": None},
            "yahoo_finance": {"available": False, "error": None},
            "redis_cache": {"available": False, "error": None}
        }
        
        # Test Alpha Vantage
        if self.alpha_vantage_api_key:
            try:
                test_data = await self._fetch_alpha_vantage_data("SPY", "1d")
                health_status["alpha_vantage"]["available"] = test_data is not None
            except Exception as e:
                health_status["alpha_vantage"]["error"] = str(e)
        else:
            health_status["alpha_vantage"]["error"] = "API key not configured"
        
        # Test Yahoo Finance
        try:
            test_data = await self._fetch_yahoo_finance_data("SPY", "1d")
            health_status["yahoo_finance"]["available"] = test_data is not None
        except Exception as e:
            health_status["yahoo_finance"]["error"] = str(e)
        
        # Test Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health_status["redis_cache"]["available"] = True
            except Exception as e:
                health_status["redis_cache"]["error"] = str(e)
        else:
            health_status["redis_cache"]["error"] = "Redis not configured"
        
        return health_status
    
    # Benchmark Comparison Methods
    
    def _calculate_returns_series(self, data_points: List[BenchmarkDataPoint]) -> pd.Series:
        """
        Calculate returns series from benchmark data points.
        
        Args:
            data_points: List of benchmark data points
            
        Returns:
            Pandas Series of returns
        """
        if len(data_points) < 2:
            return pd.Series(dtype=float)
        
        prices = [float(dp.price) for dp in data_points]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        dates = [dp.date for dp in data_points[1:]]  # Skip first date since no return
        
        return pd.Series(returns, index=dates)
    
    def _calculate_portfolio_returns_series(self, portfolio: Portfolio, period: str) -> pd.Series:
        """
        Calculate portfolio returns series for comparison.
        
        Args:
            portfolio: Portfolio object
            period: Time period for calculation
            
        Returns:
            Pandas Series of portfolio returns
        """
        # This is a simplified implementation
        # In a real scenario, you'd need historical portfolio values
        # For now, we'll create a mock series based on current metrics
        
        end_date = datetime.utcnow()
        if period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Generate daily dates
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # For demonstration, create synthetic returns based on portfolio metrics
        # In production, this would come from historical portfolio data
        total_return = float(portfolio.metrics.total_return_pct) if portfolio.metrics.total_return_pct else 0
        daily_return = total_return / len(dates) / 100  # Convert to daily decimal return
        
        # Add some realistic volatility
        np.random.seed(42)  # For reproducible results
        volatility = 0.01  # 1% daily volatility
        random_returns = np.random.normal(daily_return, volatility, len(dates))
        
        return pd.Series(random_returns, index=dates)
    
    def _calculate_pie_returns_series(self, pie: Pie, period: str) -> pd.Series:
        """
        Calculate pie returns series for comparison.
        
        Args:
            pie: Pie object
            period: Time period for calculation
            
        Returns:
            Pandas Series of pie returns
        """
        # Similar to portfolio returns, this would need historical data
        # For now, create synthetic data based on pie metrics
        
        end_date = datetime.utcnow()
        if period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        total_return = float(pie.metrics.total_return_pct) if pie.metrics.total_return_pct else 0
        daily_return = total_return / len(dates) / 100
        
        np.random.seed(hash(pie.id) % 2**32)  # Unique seed per pie
        volatility = 0.012  # Slightly higher volatility for individual pies
        random_returns = np.random.normal(daily_return, volatility, len(dates))
        
        return pd.Series(random_returns, index=dates)
    
    async def calculate_benchmark_comparison(
        self,
        entity_returns: pd.Series,
        benchmark_data: BenchmarkData,
        entity_type: str,
        entity_id: str,
        entity_name: str
    ) -> BenchmarkComparison:
        """
        Calculate comprehensive benchmark comparison metrics.
        
        Args:
            entity_returns: Returns series for portfolio/pie
            benchmark_data: Benchmark data
            entity_type: "portfolio" or "pie"
            entity_id: Entity identifier
            entity_name: Entity name
            
        Returns:
            BenchmarkComparison object with all metrics
        """
        try:
            # Get benchmark returns
            benchmark_returns = self._calculate_returns_series(benchmark_data.data_points)
            
            # Align time series (use common dates)
            common_dates = entity_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) < 10:  # Need at least 10 data points
                raise BenchmarkAPIError("Insufficient overlapping data for comparison")
            
            entity_aligned = entity_returns.loc[common_dates]
            benchmark_aligned = benchmark_returns.loc[common_dates]
            
            # Calculate basic performance metrics
            entity_total_return = (1 + entity_aligned).prod() - 1
            benchmark_total_return = (1 + benchmark_aligned).prod() - 1
            
            entity_return_pct = entity_total_return * 100
            benchmark_return_pct = benchmark_total_return * 100
            
            # Calculate alpha and beta using linear regression
            # Beta = Covariance(entity, benchmark) / Variance(benchmark)
            covariance = np.cov(entity_aligned, benchmark_aligned)[0, 1]
            benchmark_variance = np.var(benchmark_aligned)
            
            if benchmark_variance > 0:
                beta = covariance / benchmark_variance
            else:
                beta = 0
            
            # Alpha = Entity Return - (Risk-free rate + Beta * (Benchmark Return - Risk-free rate))
            risk_free_rate = 0.02 / 252  # 2% annual risk-free rate, daily
            alpha_daily = entity_aligned.mean() - (risk_free_rate + beta * (benchmark_aligned.mean() - risk_free_rate))
            alpha = alpha_daily * 252 * 100  # Annualized alpha in percentage
            
            # Calculate tracking error (standard deviation of excess returns)
            excess_returns = entity_aligned - benchmark_aligned
            tracking_error = excess_returns.std() * np.sqrt(252) * 100  # Annualized
            
            # Calculate correlation
            correlation = entity_aligned.corr(benchmark_aligned)
            if pd.isna(correlation):
                correlation = 0
            
            # Calculate R-squared (coefficient of determination)
            r_squared = correlation ** 2
            
            # Calculate Information Ratio (Alpha / Tracking Error)
            if tracking_error > 0:
                information_ratio = alpha / tracking_error
            else:
                information_ratio = 0
            
            # Calculate Up/Down Capture Ratios
            up_periods = benchmark_aligned > 0
            down_periods = benchmark_aligned < 0
            
            if up_periods.sum() > 0:
                up_capture = (entity_aligned[up_periods].mean() / benchmark_aligned[up_periods].mean()) * 100
            else:
                up_capture = 0
            
            if down_periods.sum() > 0:
                down_capture = (entity_aligned[down_periods].mean() / benchmark_aligned[down_periods].mean()) * 100
            else:
                down_capture = 0
            
            # Determine if outperforming
            outperforming = entity_return_pct > benchmark_return_pct
            outperformance_amount = entity_return_pct - benchmark_return_pct
            
            return BenchmarkComparison(
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                benchmark_symbol=benchmark_data.symbol,
                benchmark_name=benchmark_data.name,
                period=benchmark_data.period,
                start_date=benchmark_data.start_date,
                end_date=benchmark_data.end_date,
                entity_return_pct=Decimal(str(entity_return_pct)),
                benchmark_return_pct=Decimal(str(benchmark_return_pct)),
                alpha=Decimal(str(alpha)),
                beta=Decimal(str(beta)),
                tracking_error=Decimal(str(tracking_error)),
                correlation=Decimal(str(correlation)),
                r_squared=Decimal(str(r_squared)),
                information_ratio=Decimal(str(information_ratio)) if not pd.isna(information_ratio) else None,
                up_capture=Decimal(str(up_capture)) if not pd.isna(up_capture) else None,
                down_capture=Decimal(str(down_capture)) if not pd.isna(down_capture) else None,
                outperforming=outperforming,
                outperformance_amount=Decimal(str(outperformance_amount))
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate benchmark comparison: {e}")
            raise BenchmarkAPIError(f"Benchmark comparison calculation failed: {str(e)}")
    
    async def compare_portfolio_to_benchmark(
        self,
        portfolio: Portfolio,
        benchmark_symbol: str,
        period: str = "1y"
    ) -> BenchmarkComparison:
        """
        Compare portfolio performance to a benchmark.
        
        Args:
            portfolio: Portfolio object
            benchmark_symbol: Benchmark symbol (e.g., SPY)
            period: Time period for comparison
            
        Returns:
            BenchmarkComparison object
        """
        # Fetch benchmark data
        benchmark_data = await self.fetch_benchmark_data(benchmark_symbol, period)
        if not benchmark_data:
            raise BenchmarkAPIError(f"Failed to fetch benchmark data for {benchmark_symbol}")
        
        # Calculate portfolio returns series
        portfolio_returns = self._calculate_portfolio_returns_series(portfolio, period)
        
        # Calculate comparison
        return await self.calculate_benchmark_comparison(
            entity_returns=portfolio_returns,
            benchmark_data=benchmark_data,
            entity_type="portfolio",
            entity_id=portfolio.id,
            entity_name=portfolio.name
        )
    
    async def compare_pie_to_benchmark(
        self,
        pie: Pie,
        benchmark_symbol: str,
        period: str = "1y"
    ) -> BenchmarkComparison:
        """
        Compare pie performance to a benchmark.
        
        Args:
            pie: Pie object
            benchmark_symbol: Benchmark symbol (e.g., SPY)
            period: Time period for comparison
            
        Returns:
            BenchmarkComparison object
        """
        # Fetch benchmark data
        benchmark_data = await self.fetch_benchmark_data(benchmark_symbol, period)
        if not benchmark_data:
            raise BenchmarkAPIError(f"Failed to fetch benchmark data for {benchmark_symbol}")
        
        # Calculate pie returns series
        pie_returns = self._calculate_pie_returns_series(pie, period)
        
        # Calculate comparison
        return await self.calculate_benchmark_comparison(
            entity_returns=pie_returns,
            benchmark_data=benchmark_data,
            entity_type="pie",
            entity_id=pie.id,
            entity_name=pie.name
        )
    
    async def compare_multiple_entities_to_benchmark(
        self,
        portfolio: Portfolio,
        benchmark_symbol: str,
        period: str = "1y",
        include_pies: bool = True
    ) -> BenchmarkAnalysis:
        """
        Compare portfolio and optionally all pies to a benchmark.
        
        Args:
            portfolio: Portfolio object
            benchmark_symbol: Benchmark symbol
            period: Time period for comparison
            include_pies: Whether to include pie comparisons
            
        Returns:
            BenchmarkAnalysis with all comparisons
        """
        try:
            # Compare portfolio
            portfolio_comparison = await self.compare_portfolio_to_benchmark(
                portfolio, benchmark_symbol, period
            )
            
            # Compare pies if requested
            pie_comparisons = []
            if include_pies:
                for pie in portfolio.pies:
                    try:
                        pie_comparison = await self.compare_pie_to_benchmark(
                            pie, benchmark_symbol, period
                        )
                        pie_comparisons.append(pie_comparison)
                    except Exception as e:
                        logger.warning(f"Failed to compare pie {pie.name}: {e}")
            
            # Calculate summary statistics
            summary_stats = {
                "total_entities": 1 + len(pie_comparisons),
                "outperforming_entities": sum([
                    1 if portfolio_comparison.outperforming else 0,
                    sum(1 for pc in pie_comparisons if pc.outperforming)
                ]),
                "average_alpha": float(np.mean([
                    float(portfolio_comparison.alpha),
                    *[float(pc.alpha) for pc in pie_comparisons]
                ])),
                "average_beta": float(np.mean([
                    float(portfolio_comparison.beta),
                    *[float(pc.beta) for pc in pie_comparisons]
                ])),
                "average_correlation": float(np.mean([
                    float(portfolio_comparison.correlation),
                    *[float(pc.correlation) for pc in pie_comparisons]
                ]))
            }
            
            return BenchmarkAnalysis(
                analysis_type="comprehensive",
                period=period,
                benchmark_symbol=benchmark_symbol,
                portfolio_analysis=portfolio_comparison,
                pie_analyses=pie_comparisons,
                summary_stats=summary_stats
            )
            
        except Exception as e:
            logger.error(f"Failed to perform benchmark analysis: {e}")
            raise BenchmarkAPIError(f"Benchmark analysis failed: {str(e)}")
    
    async def get_benchmark_selection_recommendations(
        self,
        portfolio: Portfolio
    ) -> List[BenchmarkInfo]:
        """
        Recommend appropriate benchmarks based on portfolio composition.
        
        Args:
            portfolio: Portfolio object
            
        Returns:
            List of recommended benchmarks
        """
        recommendations = []
        
        # Analyze portfolio composition
        total_value = float(portfolio.metrics.total_value)
        if total_value == 0:
            return [self.SUPPORTED_BENCHMARKS["SPY"]]  # Default recommendation
        
        # Count asset types and regions
        us_equity_weight = 0
        international_weight = 0
        tech_weight = 0
        bond_weight = 0
        reit_weight = 0
        
        all_positions = []
        for pie in portfolio.pies:
            all_positions.extend(pie.positions)
        all_positions.extend(portfolio.individual_positions)
        
        for position in all_positions:
            weight = float(position.market_value) / total_value
            
            # Simplified sector/region classification
            if position.country and position.country.upper() == "US":
                us_equity_weight += weight
                if position.sector and "technology" in position.sector.lower():
                    tech_weight += weight
            else:
                international_weight += weight
            
            # Asset type classification
            if position.asset_type.value == "ETF":
                if "bond" in position.name.lower() or "fixed" in position.name.lower():
                    bond_weight += weight
                elif "reit" in position.name.lower() or "real estate" in position.name.lower():
                    reit_weight += weight
        
        # Make recommendations based on weights
        if us_equity_weight > 0.3:  # 30% or more US equity
            if tech_weight > 0.2:  # Significant tech exposure
                recommendations.append(self.SUPPORTED_BENCHMARKS["QQQ"])
            recommendations.append(self.SUPPORTED_BENCHMARKS["SPY"])
            recommendations.append(self.SUPPORTED_BENCHMARKS["VTI"])
        
        if international_weight > 0.2:  # 20% or more international
            recommendations.append(self.SUPPORTED_BENCHMARKS["VXUS"])
            recommendations.append(self.SUPPORTED_BENCHMARKS["EFA"])
        
        if bond_weight > 0.1:  # 10% or more bonds
            recommendations.append(self.SUPPORTED_BENCHMARKS["AGG"])
        
        if reit_weight > 0.05:  # 5% or more REITs
            recommendations.append(self.SUPPORTED_BENCHMARKS["VNQ"])
        
        # If no specific recommendations, default to broad market
        if not recommendations:
            recommendations = [
                self.SUPPORTED_BENCHMARKS["SPY"],
                self.SUPPORTED_BENCHMARKS["VTI"]
            ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec.symbol not in seen:
                seen.add(rec.symbol)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Limit to top 5 recommendations
    
    async def prepare_performance_comparison_chart_data(
        self,
        entity_returns: pd.Series,
        benchmark_data: BenchmarkData,
        entity_name: str
    ) -> Dict[str, Any]:
        """
        Prepare data for performance comparison charts.
        
        Args:
            entity_returns: Returns series for entity
            benchmark_data: Benchmark data
            entity_name: Name of the entity being compared
            
        Returns:
            Chart data dictionary
        """
        try:
            # Get benchmark returns
            benchmark_returns = self._calculate_returns_series(benchmark_data.data_points)
            
            # Align time series
            common_dates = entity_returns.index.intersection(benchmark_returns.index)
            entity_aligned = entity_returns.loc[common_dates]
            benchmark_aligned = benchmark_returns.loc[common_dates]
            
            # Calculate cumulative returns
            entity_cumulative = (1 + entity_aligned).cumprod()
            benchmark_cumulative = (1 + benchmark_aligned).cumprod()
            
            # Prepare chart data
            chart_data = {
                "dates": [date.isoformat() for date in common_dates],
                "entity_cumulative_returns": [float(val) for val in entity_cumulative],
                "benchmark_cumulative_returns": [float(val) for val in benchmark_cumulative],
                "entity_name": entity_name,
                "benchmark_name": benchmark_data.name,
                "benchmark_symbol": benchmark_data.symbol,
                "period": benchmark_data.period,
                "start_date": benchmark_data.start_date.isoformat(),
                "end_date": benchmark_data.end_date.isoformat()
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to prepare chart data: {e}")
            raise BenchmarkAPIError(f"Chart data preparation failed: {str(e)}")
    
    async def create_custom_benchmark(
        self,
        name: str,
        components: List[Dict[str, Any]],
        user_id: str,
        description: Optional[str] = None
    ) -> CustomBenchmark:
        """
        Create a custom benchmark from multiple components.
        
        Args:
            name: Custom benchmark name
            components: List of components with symbols and weights
            user_id: User ID creating the benchmark
            description: Optional description
            
        Returns:
            CustomBenchmark object
        """
        try:
            # Validate components
            total_weight = Decimal('0')
            validated_components = []
            
            for component in components:
                symbol = component.get('symbol', '').upper()
                weight = Decimal(str(component.get('weight', 0)))
                
                if symbol not in self.SUPPORTED_BENCHMARKS:
                    raise BenchmarkAPIError(f"Unsupported benchmark symbol: {symbol}")
                
                if weight <= 0:
                    raise BenchmarkAPIError(f"Invalid weight for {symbol}: {weight}")
                
                total_weight += weight
                validated_components.append({
                    'symbol': symbol,
                    'weight': float(weight),
                    'name': self.SUPPORTED_BENCHMARKS[symbol].name
                })
            
            if abs(total_weight - 100) > 0.01:  # Allow small rounding errors
                raise BenchmarkAPIError(f"Component weights must sum to 100, got {total_weight}")
            
            # Create custom benchmark
            custom_benchmark = CustomBenchmark(
                id=f"custom_{user_id}_{int(datetime.utcnow().timestamp())}",
                name=name,
                description=description,
                components=validated_components,
                total_weight=total_weight,
                created_by=user_id,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            # Cache the custom benchmark
            cache_key = f"custom_benchmark:{custom_benchmark.id}"
            await self._set_cached_data(cache_key, custom_benchmark.dict(), ttl=86400)  # 24 hours
            
            logger.info(f"Created custom benchmark: {name}")
            return custom_benchmark
            
        except Exception as e:
            logger.error(f"Failed to create custom benchmark: {e}")
            raise BenchmarkAPIError(f"Custom benchmark creation failed: {str(e)}")
    
    async def calculate_custom_benchmark_data(
        self,
        custom_benchmark: CustomBenchmark,
        period: str = "1y"
    ) -> BenchmarkData:
        """
        Calculate performance data for a custom benchmark.
        
        Args:
            custom_benchmark: Custom benchmark configuration
            period: Time period for calculation
            
        Returns:
            BenchmarkData for the custom benchmark
        """
        try:
            # Fetch data for all components
            component_data = {}
            for component in custom_benchmark.components:
                symbol = component['symbol']
                data = await self.fetch_benchmark_data(symbol, period)
                if data:
                    component_data[symbol] = data
                else:
                    logger.warning(f"Failed to fetch data for component {symbol}")
            
            if not component_data:
                raise BenchmarkAPIError("No data available for custom benchmark components")
            
            # Find common date range
            all_dates = None
            for data in component_data.values():
                dates = set(point.date for point in data.data_points)
                if all_dates is None:
                    all_dates = dates
                else:
                    all_dates = all_dates.intersection(dates)
            
            if not all_dates:
                raise BenchmarkAPIError("No overlapping dates found for custom benchmark components")
            
            all_dates = sorted(all_dates)
            
            # Calculate weighted returns for each date
            custom_data_points = []
            for date in all_dates:
                weighted_price = Decimal('0')
                total_weight = Decimal('0')
                
                for component in custom_benchmark.components:
                    symbol = component['symbol']
                    weight = Decimal(str(component['weight'])) / 100  # Convert percentage to decimal
                    
                    if symbol in component_data:
                        # Find price for this date
                        for point in component_data[symbol].data_points:
                            if point.date == date:
                                weighted_price += point.price * weight
                                total_weight += weight
                                break
                
                if total_weight > 0:
                    custom_data_points.append(BenchmarkDataPoint(
                        date=date,
                        price=weighted_price,
                        volume=None  # Not applicable for custom benchmarks
                    ))
            
            # Calculate returns for each data point
            for i in range(1, len(custom_data_points)):
                prev_price = custom_data_points[i-1].price
                curr_price = custom_data_points[i].price
                if prev_price > 0:
                    return_pct = (curr_price - prev_price) / prev_price * 100
                    custom_data_points[i].return_pct = return_pct
            
            # Calculate summary statistics
            if len(custom_data_points) > 1:
                prices = [float(point.price) for point in custom_data_points]
                total_return_pct = (prices[-1] - prices[0]) / prices[0] * 100
                
                days = (all_dates[-1] - all_dates[0]).days
                if days > 0:
                    years = days / 365.25
                    annualized_return_pct = ((prices[-1] / prices[0]) ** (1/years) - 1) * 100
                else:
                    annualized_return_pct = total_return_pct
                
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                volatility = np.std(returns) * np.sqrt(252) * 100
                
                # Calculate maximum drawdown
                peak = prices[0]
                max_drawdown = 0
                for price in prices:
                    if price > peak:
                        peak = price
                    drawdown = (peak - price) / peak
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                max_drawdown_pct = max_drawdown * 100
                
                # Calculate Sharpe ratio
                risk_free_rate = 2.0
                if volatility > 0:
                    sharpe_ratio = (annualized_return_pct - risk_free_rate) / volatility
                else:
                    sharpe_ratio = 0
            else:
                total_return_pct = 0
                annualized_return_pct = 0
                volatility = 0
                max_drawdown_pct = 0
                sharpe_ratio = 0
            
            return BenchmarkData(
                symbol=custom_benchmark.id,
                name=custom_benchmark.name,
                period=period,
                start_date=all_dates[0] if all_dates else datetime.utcnow(),
                end_date=all_dates[-1] if all_dates else datetime.utcnow(),
                data_points=custom_data_points,
                total_return_pct=Decimal(str(total_return_pct)),
                annualized_return_pct=Decimal(str(annualized_return_pct)),
                volatility=Decimal(str(volatility)),
                max_drawdown=Decimal(str(max_drawdown_pct)),
                sharpe_ratio=Decimal(str(sharpe_ratio))
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate custom benchmark data: {e}")
            raise BenchmarkAPIError(f"Custom benchmark calculation failed: {str(e)}")
    
    async def get_advanced_comparison_metrics(
        self,
        entity_returns: pd.Series,
        benchmark_returns: pd.Series,
        entity_name: str,
        benchmark_name: str
    ) -> Dict[str, Any]:
        """
        Calculate advanced comparison metrics beyond basic alpha/beta.
        
        Args:
            entity_returns: Returns series for entity
            benchmark_returns: Returns series for benchmark
            entity_name: Name of the entity
            benchmark_name: Name of the benchmark
            
        Returns:
            Dictionary with advanced metrics
        """
        try:
            # Align time series
            common_dates = entity_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) < 30:  # Need sufficient data
                raise BenchmarkAPIError("Insufficient data for advanced metrics")
            
            entity_aligned = entity_returns.loc[common_dates]
            benchmark_aligned = benchmark_returns.loc[common_dates]
            
            # Calculate rolling correlations (30-day window)
            rolling_correlation = entity_aligned.rolling(window=30).corr(benchmark_aligned)
            
            # Calculate rolling beta (30-day window)
            rolling_beta = []
            for i in range(29, len(entity_aligned)):
                entity_window = entity_aligned.iloc[i-29:i+1]
                benchmark_window = benchmark_aligned.iloc[i-29:i+1]
                
                covariance = np.cov(entity_window, benchmark_window)[0, 1]
                variance = np.var(benchmark_window)
                
                if variance > 0:
                    beta = covariance / variance
                else:
                    beta = 0
                
                rolling_beta.append(beta)
            
            # Calculate Treynor ratio
            entity_mean_return = entity_aligned.mean() * 252  # Annualized
            risk_free_rate = 0.02  # 2% annual
            
            # Calculate beta for Treynor ratio
            covariance = np.cov(entity_aligned, benchmark_aligned)[0, 1]
            benchmark_variance = np.var(benchmark_aligned)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            treynor_ratio = (entity_mean_return - risk_free_rate) / beta if beta != 0 else 0
            
            # Calculate Jensen's Alpha
            benchmark_mean_return = benchmark_aligned.mean() * 252  # Annualized
            jensens_alpha = entity_mean_return - (risk_free_rate + beta * (benchmark_mean_return - risk_free_rate))
            
            # Calculate Sortino ratio (downside deviation)
            downside_returns = entity_aligned[entity_aligned < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = (entity_mean_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            # Calculate Maximum Drawdown Duration
            cumulative_returns = (1 + entity_aligned).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            
            # Find longest drawdown period
            in_drawdown = drawdown < 0
            drawdown_periods = []
            start_idx = None
            
            for i, is_dd in enumerate(in_drawdown):
                if is_dd and start_idx is None:
                    start_idx = i
                elif not is_dd and start_idx is not None:
                    drawdown_periods.append(i - start_idx)
                    start_idx = None
            
            max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
            
            # Calculate Calmar ratio (annual return / max drawdown)
            max_drawdown = abs(drawdown.min())
            calmar_ratio = entity_mean_return / max_drawdown if max_drawdown > 0 else 0
            
            return {
                "entity_name": entity_name,
                "benchmark_name": benchmark_name,
                "treynor_ratio": float(treynor_ratio),
                "jensens_alpha": float(jensens_alpha * 100),  # Convert to percentage
                "sortino_ratio": float(sortino_ratio),
                "calmar_ratio": float(calmar_ratio),
                "max_drawdown_duration_days": int(max_drawdown_duration),
                "rolling_correlation_mean": float(rolling_correlation.mean()) if not rolling_correlation.empty else 0,
                "rolling_correlation_std": float(rolling_correlation.std()) if not rolling_correlation.empty else 0,
                "rolling_beta_mean": float(np.mean(rolling_beta)) if rolling_beta else 0,
                "rolling_beta_std": float(np.std(rolling_beta)) if rolling_beta else 0,
                "correlation_stability": "high" if rolling_correlation.std() < 0.1 else "medium" if rolling_correlation.std() < 0.2 else "low",
                "beta_stability": "high" if np.std(rolling_beta) < 0.1 else "medium" if np.std(rolling_beta) < 0.2 else "low"
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate advanced metrics: {e}")
            raise BenchmarkAPIError(f"Advanced metrics calculation failed: {str(e)}")