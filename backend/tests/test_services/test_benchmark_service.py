"""
Tests for benchmark service data fetching and caching functionality.

This test file covers:
- Benchmark data fetching from different APIs
- Caching mechanisms and cache invalidation
- Comparison calculations with known datasets
- Error handling and edge cases
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import numpy as np
import httpx

from app.services.benchmark_service import BenchmarkService, BenchmarkAPIError
from app.models.benchmark import (
    BenchmarkData, BenchmarkDataPoint, BenchmarkInfo, BenchmarkComparison,
    CustomBenchmark, BenchmarkAnalysis
)
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.pie import Pie, PieMetrics


class TestBenchmarkDataFetching:
    """Test benchmark data fetching from external APIs."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        service = BenchmarkService(alpha_vantage_api_key="test_api_key")
        return service
    
    @pytest.fixture
    def mock_alpha_vantage_response(self):
        """Mock Alpha Vantage API response."""
        return {
            "Meta Data": {
                "1. Information": "Daily Adjusted Prices and Volume",
                "2. Symbol": "SPY",
                "3. Last Refreshed": "2024-01-30",
                "4. Output Size": "Full size",
                "5. Time Zone": "US/Eastern"
            },
            "Time Series (Daily)": {
                "2024-01-30": {
                    "1. open": "100.0000",
                    "2. high": "102.0000",
                    "3. low": "99.5000",
                    "4. close": "101.5000",
                    "5. adjusted close": "101.5000",
                    "6. volume": "1000000"
                },
                "2024-01-29": {
                    "1. open": "99.0000",
                    "2. high": "100.5000",
                    "3. low": "98.5000",
                    "4. close": "100.0000",
                    "5. adjusted close": "100.0000",
                    "6. volume": "950000"
                },
                "2024-01-28": {
                    "1. open": "98.5000",
                    "2. high": "99.5000",
                    "3. low": "98.0000",
                    "4. close": "99.0000",
                    "5. adjusted close": "99.0000",
                    "6. volume": "900000"
                }
            }
        }
    
    @pytest.fixture
    def mock_yahoo_finance_response(self):
        """Mock Yahoo Finance API response."""
        return {
            "chart": {
                "result": [{
                    "meta": {
                        "currency": "USD",
                        "symbol": "SPY",
                        "exchangeName": "PCX",
                        "instrumentType": "ETF",
                        "firstTradeDate": 863703600,
                        "regularMarketTime": 1706644800,
                        "gmtoffset": -18000,
                        "timezone": "EST",
                        "exchangeTimezoneName": "America/New_York"
                    },
                    "timestamp": [1706558400, 1706644800, 1706731200],
                    "indicators": {
                        "quote": [{
                            "open": [99.0, 100.0, 101.0],
                            "high": [99.5, 102.0, 102.5],
                            "low": [98.5, 99.5, 100.5],
                            "close": [99.0, 100.0, 101.5],
                            "volume": [900000, 950000, 1000000]
                        }]
                    }
                }],
                "error": None
            }
        }
    
    @pytest.mark.asyncio
    async def test_fetch_alpha_vantage_data_success(
        self, 
        benchmark_service, 
        mock_alpha_vantage_response
    ):
        """Test successful Alpha Vantage data fetching."""
        # Create a proper mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_alpha_vantage_response
        
        # Mock the session.get method to return the mock response
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)
            
            result = await benchmark_service._fetch_alpha_vantage_data("SPY", "1y")
            
            assert result is not None
            assert result == mock_alpha_vantage_response
            mock_session.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_alpha_vantage_data_api_error(self, benchmark_service):
        """Test Alpha Vantage API error handling."""
        error_response = {
            "Error Message": "Invalid API call. Please retry or visit the documentation"
        }
        
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = error_response
            mock_session.get.return_value = mock_response
            
            benchmark_service.session = mock_session
            
            result = await benchmark_service._fetch_alpha_vantage_data("INVALID", "1y")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_alpha_vantage_data_rate_limit(self, benchmark_service):
        """Test Alpha Vantage rate limiting."""
        rate_limit_response = {
            "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute"
        }
        
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = rate_limit_response
            mock_session.get.return_value = mock_response
            
            benchmark_service.session = mock_session
            
            result = await benchmark_service._fetch_alpha_vantage_data("SPY", "1y")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_yahoo_finance_data_success(
        self, 
        benchmark_service, 
        mock_yahoo_finance_response
    ):
        """Test successful Yahoo Finance data fetching."""
        # Create a proper mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_yahoo_finance_response
        
        # Mock the session.get method to return the mock response
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)
            
            result = await benchmark_service._fetch_yahoo_finance_data("SPY", "1y")
            
            assert result is not None
            assert result == mock_yahoo_finance_response
            mock_session.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_yahoo_finance_data_no_data(self, benchmark_service):
        """Test Yahoo Finance response with no data."""
        no_data_response = {
            "chart": {
                "result": None,
                "error": None
            }
        }
        
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = no_data_response
            mock_session.get.return_value = mock_response
            
            benchmark_service.session = mock_session
            
            result = await benchmark_service._fetch_yahoo_finance_data("INVALID", "1y")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_yahoo_finance_data_http_error(self, benchmark_service):
        """Test Yahoo Finance HTTP error handling."""
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_session.get.return_value = mock_response
            
            benchmark_service.session = mock_session
            
            result = await benchmark_service._fetch_yahoo_finance_data("SPY", "1y")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_transform_alpha_vantage_data(
        self, 
        benchmark_service, 
        mock_alpha_vantage_response
    ):
        """Test transformation of Alpha Vantage data to internal format."""
        result = benchmark_service._transform_alpha_vantage_data(
            mock_alpha_vantage_response, "SPY", "1y"
        )
        
        assert isinstance(result, BenchmarkData)
        assert result.symbol == "SPY"
        assert result.name == "SPDR S&P 500 ETF Trust"
        assert result.period == "1y"
        assert len(result.data_points) == 3
        
        # Check data points are sorted by date
        dates = [dp.date for dp in result.data_points]
        assert dates == sorted(dates)
        
        # Check price values
        assert result.data_points[0].price == Decimal("99.0")
        assert result.data_points[1].price == Decimal("100.0")
        assert result.data_points[2].price == Decimal("101.5")
        
        # Check return calculations
        assert result.data_points[0].return_pct is None  # First point has no return
        assert result.data_points[1].return_pct is not None
        assert result.data_points[2].return_pct is not None
    
    @pytest.mark.asyncio
    async def test_transform_yahoo_finance_data(
        self, 
        benchmark_service, 
        mock_yahoo_finance_response
    ):
        """Test transformation of Yahoo Finance data to internal format."""
        result = benchmark_service._transform_yahoo_finance_data(
            mock_yahoo_finance_response, "SPY", "1y"
        )
        
        assert isinstance(result, BenchmarkData)
        assert result.symbol == "SPY"
        assert result.name == "SPDR S&P 500 ETF Trust"
        assert result.period == "1y"
        assert len(result.data_points) == 3
        
        # Check price values
        assert result.data_points[0].price == Decimal("99.0")
        assert result.data_points[1].price == Decimal("100.0")
        assert result.data_points[2].price == Decimal("101.5")
    
    @pytest.mark.asyncio
    async def test_transform_data_invalid_format(self, benchmark_service):
        """Test transformation with invalid data format."""
        invalid_data = {"invalid": "format"}
        
        result = benchmark_service._transform_alpha_vantage_data(
            invalid_data, "SPY", "1y"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_rate_limit_checking(self, benchmark_service):
        """Test rate limit checking functionality."""
        # Test within limits
        assert await benchmark_service._check_rate_limit("alpha_vantage") is True
        
        # Simulate hitting rate limit
        benchmark_service._rate_limits["alpha_vantage"]["requests"] = 5
        assert await benchmark_service._check_rate_limit("alpha_vantage") is False
        
        # Test rate limit reset
        benchmark_service._rate_limits["alpha_vantage"]["reset_time"] = datetime.utcnow() - timedelta(minutes=2)
        assert await benchmark_service._check_rate_limit("alpha_vantage") is True
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_benchmarks(self, benchmark_service):
        """Test fetching multiple benchmarks concurrently."""
        mock_data = BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1y",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 30),
            data_points=[],
            total_return_pct=Decimal("10.0"),
            annualized_return_pct=Decimal("10.0"),
            volatility=Decimal("15.0"),
            max_drawdown=Decimal("5.0"),
            sharpe_ratio=Decimal("0.6")
        )
        
        with patch.object(benchmark_service, 'fetch_benchmark_data', return_value=mock_data):
            results = await benchmark_service.fetch_multiple_benchmarks(
                ["SPY", "QQQ", "VTI"], "1y"
            )
            
            assert len(results) == 3
            assert all(symbol in results for symbol in ["SPY", "QQQ", "VTI"])
            assert all(isinstance(data, BenchmarkData) for data in results.values())


class TestBenchmarkCaching:
    """Test benchmark data caching functionality."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_api_key")
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        mock_redis = AsyncMock()
        return mock_redis
    
    @pytest.fixture
    def sample_benchmark_data(self):
        """Sample benchmark data for caching tests."""
        return BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1y",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 30),
            data_points=[
                BenchmarkDataPoint(
                    date=datetime(2024, 1, 1),
                    price=Decimal("100.0"),
                    volume=1000000
                )
            ],
            total_return_pct=Decimal("10.0"),
            annualized_return_pct=Decimal("10.0"),
            volatility=Decimal("15.0"),
            max_drawdown=Decimal("5.0"),
            sharpe_ratio=Decimal("0.6")
        )
    
    @pytest.mark.asyncio
    async def test_cache_get_success(self, benchmark_service, mock_redis_client, sample_benchmark_data):
        """Test successful cache retrieval."""
        benchmark_service.redis_client = mock_redis_client
        
        # Mock cached data
        cached_data = json.dumps(sample_benchmark_data.model_dump(), default=str)
        mock_redis_client.get.return_value = cached_data
        
        result = await benchmark_service._get_cached_data("test_key")
        
        assert result is not None
        assert result["symbol"] == "SPY"
        mock_redis_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_cache_get_miss(self, benchmark_service, mock_redis_client):
        """Test cache miss."""
        benchmark_service.redis_client = mock_redis_client
        mock_redis_client.get.return_value = None
        
        result = await benchmark_service._get_cached_data("test_key")
        
        assert result is None
        mock_redis_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_cache_get_error(self, benchmark_service, mock_redis_client):
        """Test cache retrieval error handling."""
        benchmark_service.redis_client = mock_redis_client
        mock_redis_client.get.side_effect = Exception("Redis connection error")
        
        result = await benchmark_service._get_cached_data("test_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_set_success(self, benchmark_service, mock_redis_client):
        """Test successful cache storage."""
        benchmark_service.redis_client = mock_redis_client
        
        test_data = {"symbol": "SPY", "name": "Test"}
        await benchmark_service._set_cached_data("test_key", test_data, 3600)
        
        mock_redis_client.setex.assert_called_once()
        args = mock_redis_client.setex.call_args[0]
        assert args[0] == "test_key"
        assert args[1] == 3600
        assert json.loads(args[2]) == test_data
    
    @pytest.mark.asyncio
    async def test_cache_set_error(self, benchmark_service, mock_redis_client):
        """Test cache storage error handling."""
        benchmark_service.redis_client = mock_redis_client
        mock_redis_client.setex.side_effect = Exception("Redis connection error")
        
        # Should not raise exception
        await benchmark_service._set_cached_data("test_key", {"data": "test"}, 3600)
    
    @pytest.mark.asyncio
    async def test_cache_set_no_redis(self, benchmark_service):
        """Test cache storage when Redis is not available."""
        benchmark_service.redis_client = None
        
        # Should not raise exception
        await benchmark_service._set_cached_data("test_key", {"data": "test"}, 3600)
    
    @pytest.mark.asyncio
    async def test_fetch_benchmark_data_with_cache(
        self, 
        benchmark_service, 
        mock_redis_client, 
        sample_benchmark_data
    ):
        """Test benchmark data fetching with cache hit."""
        benchmark_service.redis_client = mock_redis_client
        
        # Mock cache hit
        cached_data = json.dumps(sample_benchmark_data.model_dump(), default=str)
        mock_redis_client.get.return_value = cached_data
        
        result = await benchmark_service.fetch_benchmark_data("SPY", "1y", use_cache=True)
        
        assert isinstance(result, BenchmarkData)
        assert result.symbol == "SPY"
        mock_redis_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_benchmark_data_cache_miss_fallback(
        self, 
        benchmark_service, 
        mock_redis_client
    ):
        """Test benchmark data fetching with cache miss and API fallback."""
        benchmark_service.redis_client = mock_redis_client
        
        # Mock cache miss
        mock_redis_client.get.return_value = None
        
        # Create mock Yahoo Finance response
        mock_yahoo_finance_response = {
            "chart": {
                "result": [{
                    "meta": {
                        "currency": "USD",
                        "symbol": "SPY",
                        "exchangeName": "PCX",
                        "instrumentType": "ETF",
                        "firstTradeDate": 863703600,
                        "regularMarketTime": 1706644800,
                        "gmtoffset": -18000,
                        "timezone": "EST",
                        "exchangeTimezoneName": "America/New_York"
                    },
                    "timestamp": [1706558400, 1706644800, 1706731200],
                    "indicators": {
                        "quote": [{
                            "open": [99.0, 100.0, 101.0],
                            "high": [99.5, 102.0, 102.5],
                            "low": [98.5, 99.5, 100.5],
                            "close": [99.0, 100.0, 101.5],
                            "volume": [900000, 950000, 1000000]
                        }]
                    }
                }],
                "error": None
            }
        }
        
        # Mock successful API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_yahoo_finance_response
        
        with patch.object(benchmark_service, 'session') as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)
            
            result = await benchmark_service.fetch_benchmark_data("SPY", "1y", use_cache=True)
            
            assert isinstance(result, BenchmarkData)
            assert result.symbol == "SPY"
            
            # Should have tried to cache the result
            mock_redis_client.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_benchmark_cache_specific(self, benchmark_service, mock_redis_client):
        """Test clearing cache for specific benchmark."""
        benchmark_service.redis_client = mock_redis_client
        mock_redis_client.keys.return_value = ["benchmark:SPY:1y", "benchmark:SPY:2y"]
        
        await benchmark_service.clear_benchmark_cache("SPY")
        
        mock_redis_client.keys.assert_called_once_with("benchmark:SPY:*")
        mock_redis_client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_benchmark_cache_all(self, benchmark_service, mock_redis_client):
        """Test clearing all benchmark cache."""
        benchmark_service.redis_client = mock_redis_client
        mock_redis_client.keys.return_value = ["benchmark:SPY:1y", "benchmark:QQQ:1y"]
        
        await benchmark_service.clear_benchmark_cache()
        
        mock_redis_client.keys.assert_called_once_with("benchmark:*")
        mock_redis_client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_cache_no_redis(self, benchmark_service):
        """Test clearing cache when Redis is not available."""
        benchmark_service.redis_client = None
        
        # Should not raise exception
        await benchmark_service.clear_benchmark_cache("SPY")


class TestBenchmarkComparisonCalculations:
    """Test benchmark comparison calculations with known datasets."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_api_key")
    
    @pytest.fixture
    def known_benchmark_data(self):
        """Create benchmark data with known statistical properties."""
        # Create 252 trading days of data (1 year)
        dates = pd.date_range(start='2024-01-01', periods=252, freq='B')  # Business days
        
        # Generate benchmark returns with known properties
        np.random.seed(42)  # For reproducible results
        daily_returns = np.random.normal(0.0008, 0.012, 252)  # ~20% annual return, 19% volatility
        
        # Calculate cumulative prices starting from 100
        prices = [100.0]
        for ret in daily_returns:
            prices.append(prices[-1] * (1 + ret))
        
        data_points = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            return_pct = daily_returns[i-1] * 100 if i > 0 else None
            data_points.append(BenchmarkDataPoint(
                date=date.to_pydatetime(),
                price=Decimal(str(round(price, 2))),
                return_pct=Decimal(str(round(return_pct, 4))) if return_pct is not None else None,
                volume=1000000
            ))
        
        return BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1y",
            start_date=dates[0].to_pydatetime(),
            end_date=dates[-1].to_pydatetime(),
            data_points=data_points,
            total_return_pct=Decimal(str(round((prices[-1] - prices[0]) / prices[0] * 100, 2))),
            annualized_return_pct=Decimal("20.0"),
            volatility=Decimal("19.0"),
            max_drawdown=Decimal("8.5"),
            sharpe_ratio=Decimal("0.95")
        )
    
    @pytest.fixture
    def known_entity_returns(self):
        """Create entity returns with known statistical properties."""
        dates = pd.date_range(start='2024-01-01', periods=252, freq='B')
        
        # Generate entity returns that outperform benchmark
        np.random.seed(123)  # Different seed for entity
        daily_returns = np.random.normal(0.001, 0.015, 252)  # ~25% annual return, 24% volatility
        
        return pd.Series(daily_returns, index=dates)
    
    @pytest.mark.asyncio
    async def test_calculate_benchmark_comparison_known_data(
        self, 
        benchmark_service, 
        known_benchmark_data, 
        known_entity_returns
    ):
        """Test benchmark comparison with known statistical properties."""
        comparison = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=known_entity_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        assert isinstance(comparison, BenchmarkComparison)
        
        # Test basic properties
        assert comparison.entity_type == "portfolio"
        assert comparison.entity_id == "test_portfolio"
        assert comparison.benchmark_symbol == "SPY"
        
        # Test statistical properties are reasonable
        assert -1 <= float(comparison.correlation) <= 1
        assert 0 <= float(comparison.r_squared) <= 1
        assert float(comparison.tracking_error) >= 0
        
        # Test that beta is reasonable (can be positive or negative depending on correlation)
        assert isinstance(comparison.beta, Decimal)
        
        # Test that alpha calculation is reasonable
        assert isinstance(comparison.alpha, Decimal)
        
        # Test outperformance calculation
        entity_return = float(comparison.entity_return_pct)
        benchmark_return = float(comparison.benchmark_return_pct)
        expected_outperformance = entity_return - benchmark_return
        
        assert abs(float(comparison.outperformance_amount) - expected_outperformance) < 0.01
        assert comparison.outperforming == (entity_return > benchmark_return)
    
    @pytest.mark.asyncio
    async def test_calculate_returns_series_known_data(
        self, 
        benchmark_service, 
        known_benchmark_data
    ):
        """Test returns series calculation with known data."""
        returns_series = benchmark_service._calculate_returns_series(known_benchmark_data.data_points)
        
        assert isinstance(returns_series, pd.Series)
        assert len(returns_series) == len(known_benchmark_data.data_points) - 1
        
        # Test that returns are reasonable (not too extreme)
        assert returns_series.abs().max() < 0.1  # No single day return > 10%
        
        # Test that returns have expected statistical properties
        annualized_volatility = returns_series.std() * np.sqrt(252)
        assert 0.1 < annualized_volatility < 0.5  # Between 10% and 50% annual volatility
    
    @pytest.mark.asyncio
    async def test_beta_calculation_accuracy(
        self, 
        benchmark_service, 
        known_benchmark_data
    ):
        """Test beta calculation accuracy with controlled data."""
        # Create entity returns with known beta relationship
        benchmark_returns = benchmark_service._calculate_returns_series(known_benchmark_data.data_points)
        
        # Create entity returns with beta = 1.2
        true_beta = 1.2
        alpha_daily = 0.0002  # Small positive alpha
        
        entity_returns = alpha_daily + true_beta * benchmark_returns + np.random.normal(0, 0.005, len(benchmark_returns))
        entity_returns.index = benchmark_returns.index
        
        comparison = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=entity_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        calculated_beta = float(comparison.beta)
        
        # Beta should be close to true beta (within 0.1)
        assert abs(calculated_beta - true_beta) < 0.1
    
    @pytest.mark.asyncio
    async def test_correlation_calculation_accuracy(
        self, 
        benchmark_service, 
        known_benchmark_data
    ):
        """Test correlation calculation accuracy."""
        benchmark_returns = benchmark_service._calculate_returns_series(known_benchmark_data.data_points)
        
        # Create entity returns with known correlation
        # High correlation case
        noise = np.random.normal(0, 0.002, len(benchmark_returns))
        high_corr_returns = 0.8 * benchmark_returns + noise
        high_corr_returns.index = benchmark_returns.index
        
        comparison = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=high_corr_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        # Should have high correlation
        assert float(comparison.correlation) > 0.7
        
        # Low correlation case
        low_corr_returns = pd.Series(
            np.random.normal(0.001, 0.015, len(benchmark_returns)),
            index=benchmark_returns.index
        )
        
        comparison_low = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=low_corr_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        # Should have lower correlation
        assert float(comparison_low.correlation) < float(comparison.correlation)
    
    @pytest.mark.asyncio
    async def test_tracking_error_calculation(
        self, 
        benchmark_service, 
        known_benchmark_data
    ):
        """Test tracking error calculation."""
        benchmark_returns = benchmark_service._calculate_returns_series(known_benchmark_data.data_points)
        
        # Create entity returns that closely track benchmark
        close_tracking_returns = benchmark_returns + np.random.normal(0, 0.001, len(benchmark_returns))
        close_tracking_returns.index = benchmark_returns.index
        
        comparison_close = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=close_tracking_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        # Create entity returns with higher tracking error
        high_tracking_returns = benchmark_returns + np.random.normal(0, 0.01, len(benchmark_returns))
        high_tracking_returns.index = benchmark_returns.index
        
        comparison_high = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=high_tracking_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        # Higher noise should result in higher tracking error
        assert float(comparison_high.tracking_error) > float(comparison_close.tracking_error)
        
        # Both should be positive
        assert float(comparison_close.tracking_error) > 0
        assert float(comparison_high.tracking_error) > 0
    
    @pytest.mark.asyncio
    async def test_information_ratio_calculation(
        self, 
        benchmark_service, 
        known_benchmark_data
    ):
        """Test information ratio calculation."""
        benchmark_returns = benchmark_service._calculate_returns_series(known_benchmark_data.data_points)
        
        # Create entity returns with positive alpha and reasonable tracking error
        alpha_daily = 0.0005  # Positive alpha
        entity_returns = benchmark_returns + alpha_daily + np.random.normal(0, 0.005, len(benchmark_returns))
        entity_returns.index = benchmark_returns.index
        
        comparison = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=entity_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        # Information ratio should be positive (positive alpha / positive tracking error)
        if comparison.information_ratio is not None:
            assert float(comparison.information_ratio) > 0
    
    @pytest.mark.asyncio
    async def test_up_down_capture_ratios(
        self, 
        benchmark_service, 
        known_benchmark_data
    ):
        """Test up and down capture ratio calculations."""
        benchmark_returns = benchmark_service._calculate_returns_series(known_benchmark_data.data_points)
        
        # Create entity returns with asymmetric behavior
        # Higher capture in up markets, lower in down markets
        entity_returns = benchmark_returns.copy()
        entity_returns[benchmark_returns > 0] *= 1.1  # 110% up capture
        entity_returns[benchmark_returns < 0] *= 0.9  # 90% down capture
        
        comparison = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=entity_returns,
            benchmark_data=known_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        if comparison.up_capture is not None and comparison.down_capture is not None:
            # Up capture should be higher than down capture
            assert float(comparison.up_capture) > float(comparison.down_capture)
            
            # Up capture should be around 110%
            assert 100 < float(comparison.up_capture) < 120
            
            # Down capture should be around 90%
            assert 80 < float(comparison.down_capture) < 100


class TestBenchmarkServiceHealthCheck:
    """Test benchmark service health check functionality."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_api_key")
    
    @pytest.mark.asyncio
    async def test_health_check_all_services_available(self, benchmark_service):
        """Test health check when all services are available."""
        mock_redis = AsyncMock()
        benchmark_service.redis_client = mock_redis
        
        with patch.object(benchmark_service, '_fetch_alpha_vantage_data', return_value={"test": "data"}):
            with patch.object(benchmark_service, '_fetch_yahoo_finance_data', return_value={"test": "data"}):
                health_status = await benchmark_service.health_check()
                
                assert health_status["alpha_vantage"]["available"] is True
                assert health_status["yahoo_finance"]["available"] is True
                assert health_status["redis_cache"]["available"] is True
                assert health_status["alpha_vantage"]["error"] is None
                assert health_status["yahoo_finance"]["error"] is None
                assert health_status["redis_cache"]["error"] is None
    
    @pytest.mark.asyncio
    async def test_health_check_alpha_vantage_unavailable(self, benchmark_service):
        """Test health check when Alpha Vantage is unavailable."""
        mock_redis = AsyncMock()
        benchmark_service.redis_client = mock_redis
        
        with patch.object(benchmark_service, '_fetch_alpha_vantage_data', return_value=None):
            with patch.object(benchmark_service, '_fetch_yahoo_finance_data', return_value={"test": "data"}):
                health_status = await benchmark_service.health_check()
                
                assert health_status["alpha_vantage"]["available"] is False
                assert health_status["yahoo_finance"]["available"] is True
                assert health_status["redis_cache"]["available"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_no_api_key(self, benchmark_service):
        """Test health check when Alpha Vantage API key is not configured."""
        benchmark_service.alpha_vantage_api_key = None
        mock_redis = AsyncMock()
        benchmark_service.redis_client = mock_redis
        
        with patch.object(benchmark_service, '_fetch_yahoo_finance_data', return_value={"test": "data"}):
            health_status = await benchmark_service.health_check()
            
            assert health_status["alpha_vantage"]["available"] is False
            assert health_status["alpha_vantage"]["error"] == "API key not configured"
            assert health_status["yahoo_finance"]["available"] is True
            assert health_status["redis_cache"]["available"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_redis_unavailable(self, benchmark_service):
        """Test health check when Redis is unavailable."""
        benchmark_service.redis_client = None
        
        with patch.object(benchmark_service, '_fetch_alpha_vantage_data', return_value={"test": "data"}):
            with patch.object(benchmark_service, '_fetch_yahoo_finance_data', return_value={"test": "data"}):
                health_status = await benchmark_service.health_check()
                
                assert health_status["alpha_vantage"]["available"] is True
                assert health_status["yahoo_finance"]["available"] is True
                assert health_status["redis_cache"]["available"] is False
                assert health_status["redis_cache"]["error"] == "Redis not configured"
    
    @pytest.mark.asyncio
    async def test_health_check_service_errors(self, benchmark_service):
        """Test health check when services throw errors."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Redis connection failed")
        benchmark_service.redis_client = mock_redis
        
        with patch.object(benchmark_service, '_fetch_alpha_vantage_data', side_effect=Exception("API error")):
            with patch.object(benchmark_service, '_fetch_yahoo_finance_data', side_effect=Exception("Network error")):
                health_status = await benchmark_service.health_check()
                
                assert health_status["alpha_vantage"]["available"] is False
                assert "API error" in health_status["alpha_vantage"]["error"]
                assert health_status["yahoo_finance"]["available"] is False
                assert "Network error" in health_status["yahoo_finance"]["error"]
                assert health_status["redis_cache"]["available"] is False
                assert "Redis connection failed" in health_status["redis_cache"]["error"]


class TestBenchmarkServiceEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_api_key")
    
    @pytest.mark.asyncio
    async def test_fetch_benchmark_data_no_api_key(self):
        """Test fetching data without API key."""
        service = BenchmarkService(alpha_vantage_api_key=None)
        
        with patch.object(service, '_fetch_yahoo_finance_data', return_value=None):
            result = await service.fetch_benchmark_data("SPY", "1y")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_benchmark_data_all_apis_fail(self, benchmark_service):
        """Test fetching data when all APIs fail."""
        with patch.object(benchmark_service, '_fetch_alpha_vantage_data', return_value=None):
            with patch.object(benchmark_service, '_fetch_yahoo_finance_data', return_value=None):
                result = await benchmark_service.fetch_benchmark_data("SPY", "1y")
                assert result is None
    
    @pytest.mark.asyncio
    async def test_comparison_with_empty_data_points(self, benchmark_service):
        """Test comparison calculation with empty data points."""
        empty_benchmark_data = BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1y",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 30),
            data_points=[],  # Empty data points
            total_return_pct=Decimal("0"),
            annualized_return_pct=Decimal("0"),
            volatility=Decimal("0"),
            max_drawdown=Decimal("0"),
            sharpe_ratio=Decimal("0")
        )
        
        entity_returns = pd.Series([0.01, 0.02, -0.01], 
                                 index=pd.date_range('2024-01-01', periods=3))
        
        with pytest.raises(BenchmarkAPIError):
            await benchmark_service.calculate_benchmark_comparison(
                entity_returns=entity_returns,
                benchmark_data=empty_benchmark_data,
                entity_type="portfolio",
                entity_id="test_portfolio",
                entity_name="Test Portfolio"
            )
    
    @pytest.mark.asyncio
    async def test_comparison_with_mismatched_dates(self, benchmark_service):
        """Test comparison with completely mismatched date ranges."""
        benchmark_data = BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1y",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 30),
            data_points=[
                BenchmarkDataPoint(
                    date=datetime(2023, 1, 1),
                    price=Decimal("100.0"),
                    volume=1000000
                ),
                BenchmarkDataPoint(
                    date=datetime(2023, 1, 2),
                    price=Decimal("101.0"),
                    volume=1000000
                )
            ],
            total_return_pct=Decimal("1.0"),
            annualized_return_pct=Decimal("1.0"),
            volatility=Decimal("5.0"),
            max_drawdown=Decimal("1.0"),
            sharpe_ratio=Decimal("0.2")
        )
        
        # Entity returns from different year
        entity_returns = pd.Series([0.01, 0.02, -0.01], 
                                 index=pd.date_range('2024-01-01', periods=3))
        
        with pytest.raises(BenchmarkAPIError) as exc_info:
            await benchmark_service.calculate_benchmark_comparison(
                entity_returns=entity_returns,
                benchmark_data=benchmark_data,
                entity_type="portfolio",
                entity_id="test_portfolio",
                entity_name="Test Portfolio"
            )
        
        assert "Insufficient overlapping data" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_supported_benchmarks(self, benchmark_service):
        """Test getting supported benchmarks list."""
        benchmarks = benchmark_service.get_supported_benchmarks()
        
        assert isinstance(benchmarks, dict)
        assert len(benchmarks) > 0
        assert "SPY" in benchmarks
        assert "QQQ" in benchmarks
        
        # Check that it returns a copy (modifications don't affect original)
        original_count = len(benchmarks)
        benchmarks["TEST"] = BenchmarkInfo(
            symbol="TEST", name="Test", description="Test", category="Test"
        )
        
        new_benchmarks = benchmark_service.get_supported_benchmarks()
        assert len(new_benchmarks) == original_count
        assert "TEST" not in new_benchmarks
    
    @pytest.mark.asyncio
    async def test_search_benchmarks(self, benchmark_service):
        """Test benchmark search functionality."""
        # Search by symbol
        results = await benchmark_service.search_benchmarks("SPY")
        assert len(results) >= 1
        assert any(b.symbol == "SPY" for b in results)
        
        # Search by name
        results = await benchmark_service.search_benchmarks("S&P 500")
        assert len(results) >= 1
        
        # Search by category
        results = await benchmark_service.search_benchmarks("US Equity")
        assert len(results) >= 1
        
        # Search with no matches
        results = await benchmark_service.search_benchmarks("NONEXISTENT")
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_get_benchmark_info(self, benchmark_service):
        """Test getting specific benchmark info."""
        info = await benchmark_service.get_benchmark_info("SPY")
        assert info is not None
        assert info.symbol == "SPY"
        assert info.name == "SPDR S&P 500 ETF Trust"
        
        # Test non-existent benchmark
        info = await benchmark_service.get_benchmark_info("NONEXISTENT")
        assert info is None