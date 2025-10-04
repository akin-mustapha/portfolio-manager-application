"""
Tests for benchmark comparison functionality in BenchmarkService.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.benchmark_service import BenchmarkService, BenchmarkAPIError
from app.models.benchmark import BenchmarkData, BenchmarkDataPoint, BenchmarkComparison, CustomBenchmark
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.pie import Pie, PieMetrics


class TestBenchmarkComparison:
    """Test benchmark comparison calculations."""
    
    @pytest.fixture
    def sample_benchmark_data(self):
        """Create sample benchmark data for testing."""
        start_date = datetime(2024, 1, 1)
        data_points = []
        
        # Create 30 days of sample data
        for i in range(30):
            date = start_date + timedelta(days=i)
            price = Decimal("100") + Decimal(str(i * 0.5))  # Gradual increase
            return_pct = Decimal("0.5") if i > 0 else None
            
            data_points.append(BenchmarkDataPoint(
                date=date,
                price=price,
                return_pct=return_pct,
                volume=1000000
            ))
        
        return BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1mo",
            start_date=start_date,
            end_date=start_date + timedelta(days=29),
            data_points=data_points,
            total_return_pct=Decimal("14.5"),
            annualized_return_pct=Decimal("10.2"),
            volatility=Decimal("15.5"),
            max_drawdown=Decimal("5.2"),
            sharpe_ratio=Decimal("0.65")
        )
    
    @pytest.fixture
    def sample_entity_returns(self):
        """Create sample entity returns series."""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        # Create returns that slightly outperform the benchmark
        returns = np.random.normal(0.006, 0.02, 30)  # 0.6% daily return with 2% volatility
        return pd.Series(returns, index=dates)
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_key")
    
    @pytest.mark.asyncio
    async def test_calculate_benchmark_comparison_basic_metrics(
        self, 
        benchmark_service, 
        sample_benchmark_data, 
        sample_entity_returns
    ):
        """Test basic benchmark comparison metrics calculation."""
        comparison = await benchmark_service.calculate_benchmark_comparison(
            entity_returns=sample_entity_returns,
            benchmark_data=sample_benchmark_data,
            entity_type="portfolio",
            entity_id="test_portfolio",
            entity_name="Test Portfolio"
        )
        
        assert isinstance(comparison, BenchmarkComparison)
        assert comparison.entity_type == "portfolio"
        assert comparison.entity_id == "test_portfolio"
        assert comparison.entity_name == "Test Portfolio"
        assert comparison.benchmark_symbol == "SPY"
        assert comparison.benchmark_name == "SPDR S&P 500 ETF Trust"
        
        # Check that metrics are calculated
        assert comparison.alpha is not None
        assert comparison.beta is not None
        assert comparison.tracking_error is not None
        assert comparison.correlation is not None
        assert comparison.r_squared is not None
        
        # Check that correlation is within valid range
        assert -1 <= float(comparison.correlation) <= 1
        assert 0 <= float(comparison.r_squared) <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_benchmark_comparison_insufficient_data(
        self, 
        benchmark_service, 
        sample_benchmark_data
    ):
        """Test benchmark comparison with insufficient data."""
        # Create very short returns series
        dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
        short_returns = pd.Series([0.01, 0.02, -0.01, 0.005, 0.015], index=dates)
        
        with pytest.raises(BenchmarkAPIError) as exc_info:
            await benchmark_service.calculate_benchmark_comparison(
                entity_returns=short_returns,
                benchmark_data=sample_benchmark_data,
                entity_type="portfolio",
                entity_id="test_portfolio",
                entity_name="Test Portfolio"
            )
        
        assert "Insufficient overlapping data" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_advanced_comparison_metrics(
        self, 
        benchmark_service, 
        sample_entity_returns
    ):
        """Test advanced comparison metrics calculation."""
        # Create benchmark returns series
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        benchmark_returns = pd.Series(np.random.normal(0.005, 0.015, 30), index=dates)
        
        advanced_metrics = await benchmark_service.get_advanced_comparison_metrics(
            entity_returns=sample_entity_returns,
            benchmark_returns=benchmark_returns,
            entity_name="Test Portfolio",
            benchmark_name="Test Benchmark"
        )
        
        assert isinstance(advanced_metrics, dict)
        assert "treynor_ratio" in advanced_metrics
        assert "jensens_alpha" in advanced_metrics
        assert "sortino_ratio" in advanced_metrics
        assert "calmar_ratio" in advanced_metrics
        assert "max_drawdown_duration_days" in advanced_metrics
        assert "rolling_correlation_mean" in advanced_metrics
        assert "rolling_beta_mean" in advanced_metrics
        assert "correlation_stability" in advanced_metrics
        assert "beta_stability" in advanced_metrics
        
        # Check stability classifications
        assert advanced_metrics["correlation_stability"] in ["high", "medium", "low"]
        assert advanced_metrics["beta_stability"] in ["high", "medium", "low"]
    
    @pytest.mark.asyncio
    async def test_get_advanced_comparison_metrics_insufficient_data(
        self, 
        benchmark_service
    ):
        """Test advanced metrics with insufficient data."""
        # Create very short series
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        short_entity_returns = pd.Series(np.random.normal(0.005, 0.02, 20), index=dates)
        short_benchmark_returns = pd.Series(np.random.normal(0.005, 0.015, 20), index=dates)
        
        with pytest.raises(BenchmarkAPIError) as exc_info:
            await benchmark_service.get_advanced_comparison_metrics(
                entity_returns=short_entity_returns,
                benchmark_returns=short_benchmark_returns,
                entity_name="Test Portfolio",
                benchmark_name="Test Benchmark"
            )
        
        assert "Insufficient data for advanced metrics" in str(exc_info.value)
    
    def test_calculate_returns_series(self, benchmark_service, sample_benchmark_data):
        """Test calculation of returns series from benchmark data."""
        returns_series = benchmark_service._calculate_returns_series(sample_benchmark_data.data_points)
        
        assert isinstance(returns_series, pd.Series)
        # Returns series should have one less element than data points (first point has no return)
        assert len(returns_series) == len(sample_benchmark_data.data_points) - 1
        
        # Subsequent returns should be calculated
        for i in range(1, len(returns_series)):
            if not pd.isna(returns_series.iloc[i]):
                assert isinstance(returns_series.iloc[i], (int, float))


class TestCustomBenchmark:
    """Test custom benchmark functionality."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_key")
    
    @pytest.fixture
    def sample_custom_benchmark(self):
        """Create sample custom benchmark."""
        return CustomBenchmark(
            id="custom_test_123",
            name="Test Custom Benchmark",
            description="A test custom benchmark",
            components=[
                {"symbol": "SPY", "weight": 60.0, "name": "SPDR S&P 500 ETF Trust"},
                {"symbol": "AGG", "weight": 40.0, "name": "iShares Core US Aggregate Bond ETF"}
            ],
            total_weight=Decimal("100.0"),
            created_by="test_user",
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_create_custom_benchmark_valid(self, benchmark_service):
        """Test creating a valid custom benchmark."""
        components = [
            {"symbol": "SPY", "weight": 60},
            {"symbol": "AGG", "weight": 40}
        ]
        
        with patch.object(benchmark_service, '_set_cached_data', new_callable=AsyncMock):
            custom_benchmark = await benchmark_service.create_custom_benchmark(
                name="Test Benchmark",
                components=components,
                user_id="test_user",
                description="Test description"
            )
        
        assert isinstance(custom_benchmark, CustomBenchmark)
        assert custom_benchmark.name == "Test Benchmark"
        assert custom_benchmark.description == "Test description"
        assert len(custom_benchmark.components) == 2
        assert custom_benchmark.total_weight == 100
        assert custom_benchmark.created_by == "test_user"
    
    @pytest.mark.asyncio
    async def test_create_custom_benchmark_invalid_weights(self, benchmark_service):
        """Test creating custom benchmark with invalid weights."""
        components = [
            {"symbol": "SPY", "weight": 60},
            {"symbol": "AGG", "weight": 30}  # Total = 90, not 100
        ]
        
        with pytest.raises(BenchmarkAPIError) as exc_info:
            await benchmark_service.create_custom_benchmark(
                name="Test Benchmark",
                components=components,
                user_id="test_user"
            )
        
        assert "Component weights must sum to 100" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_custom_benchmark_unsupported_symbol(self, benchmark_service):
        """Test creating custom benchmark with unsupported symbol."""
        components = [
            {"symbol": "INVALID", "weight": 100}
        ]
        
        with pytest.raises(BenchmarkAPIError) as exc_info:
            await benchmark_service.create_custom_benchmark(
                name="Test Benchmark",
                components=components,
                user_id="test_user"
            )
        
        assert "Unsupported benchmark symbol: INVALID" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_custom_benchmark_zero_weight(self, benchmark_service):
        """Test creating custom benchmark with zero weight."""
        components = [
            {"symbol": "SPY", "weight": 0},
            {"symbol": "AGG", "weight": 100}
        ]
        
        with pytest.raises(BenchmarkAPIError) as exc_info:
            await benchmark_service.create_custom_benchmark(
                name="Test Benchmark",
                components=components,
                user_id="test_user"
            )
        
        assert "Invalid weight for SPY: 0" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_calculate_custom_benchmark_data(
        self, 
        benchmark_service, 
        sample_custom_benchmark
    ):
        """Test calculating custom benchmark data."""
        # Mock the fetch_benchmark_data method
        mock_spy_data = BenchmarkData(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            period="1y",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 30),
            data_points=[
                BenchmarkDataPoint(date=datetime(2024, 1, 1), price=Decimal("100"), volume=1000),
                BenchmarkDataPoint(date=datetime(2024, 1, 2), price=Decimal("101"), volume=1000)
            ],
            total_return_pct=Decimal("10.0"),
            annualized_return_pct=Decimal("10.0"),
            volatility=Decimal("15.0"),
            max_drawdown=Decimal("5.0"),
            sharpe_ratio=Decimal("0.6")
        )
        
        mock_agg_data = BenchmarkData(
            symbol="AGG",
            name="iShares Core US Aggregate Bond ETF",
            period="1y",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 30),
            data_points=[
                BenchmarkDataPoint(date=datetime(2024, 1, 1), price=Decimal("50"), volume=500),
                BenchmarkDataPoint(date=datetime(2024, 1, 2), price=Decimal("50.5"), volume=500)
            ],
            total_return_pct=Decimal("5.0"),
            annualized_return_pct=Decimal("5.0"),
            volatility=Decimal("8.0"),
            max_drawdown=Decimal("2.0"),
            sharpe_ratio=Decimal("0.4")
        )
        
        with patch.object(benchmark_service, 'fetch_benchmark_data') as mock_fetch:
            mock_fetch.side_effect = lambda symbol, period: {
                "SPY": mock_spy_data,
                "AGG": mock_agg_data
            }.get(symbol)
            
            custom_data = await benchmark_service.calculate_custom_benchmark_data(
                custom_benchmark=sample_custom_benchmark,
                period="1y"
            )
        
        assert isinstance(custom_data, BenchmarkData)
        assert custom_data.symbol == sample_custom_benchmark.id
        assert custom_data.name == sample_custom_benchmark.name
        assert len(custom_data.data_points) == 2  # Common dates
        
        # Check that weighted prices are calculated correctly
        # SPY: 60% weight, AGG: 40% weight
        expected_price_1 = Decimal("100") * Decimal("0.6") + Decimal("50") * Decimal("0.4")  # 60 + 20 = 80
        expected_price_2 = Decimal("101") * Decimal("0.6") + Decimal("50.5") * Decimal("0.4")  # 60.6 + 20.2 = 80.8
        
        assert abs(custom_data.data_points[0].price - expected_price_1) < Decimal("0.01")
        assert abs(custom_data.data_points[1].price - expected_price_2) < Decimal("0.01")
    
    @pytest.mark.asyncio
    async def test_calculate_custom_benchmark_data_no_component_data(
        self, 
        benchmark_service, 
        sample_custom_benchmark
    ):
        """Test calculating custom benchmark data when component data is unavailable."""
        with patch.object(benchmark_service, 'fetch_benchmark_data', return_value=None):
            with pytest.raises(BenchmarkAPIError) as exc_info:
                await benchmark_service.calculate_custom_benchmark_data(
                    custom_benchmark=sample_custom_benchmark,
                    period="1y"
                )
        
        assert "No data available for custom benchmark components" in str(exc_info.value)


class TestBenchmarkRecommendations:
    """Test benchmark recommendation functionality."""
    
    @pytest.fixture
    def benchmark_service(self):
        """Create a BenchmarkService instance for testing."""
        return BenchmarkService(alpha_vantage_api_key="test_key")
    
    @pytest.fixture
    def sample_portfolio(self):
        """Create sample portfolio for testing recommendations."""
        from app.models.position import Position
        from app.models.enums import AssetType
        
        positions = [
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal("10"),
                average_price=Decimal("150"),
                current_price=Decimal("160"),
                market_value=Decimal("1600"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("6.67"),
                sector="Technology",
                industry="Consumer Electronics",
                country="US",
                asset_type=AssetType.STOCK
            ),
            Position(
                symbol="MSFT",
                name="Microsoft Corporation",
                quantity=Decimal("5"),
                average_price=Decimal("300"),
                current_price=Decimal("320"),
                market_value=Decimal("1600"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("6.67"),
                sector="Technology",
                industry="Software",
                country="US",
                asset_type=AssetType.STOCK
            )
        ]
        
        metrics = PortfolioMetrics(
            total_value=Decimal("3200"),
            total_invested=Decimal("3000"),
            total_return=Decimal("200"),
            total_return_pct=Decimal("6.67")
        )
        
        return Portfolio(
            id="test_portfolio",
            name="Test Portfolio",
            user_id="test_user",
            pies=[],
            individual_positions=positions,
            metrics=metrics,
            last_updated=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_get_benchmark_selection_recommendations_us_tech_heavy(
        self, 
        benchmark_service, 
        sample_portfolio
    ):
        """Test benchmark recommendations for US tech-heavy portfolio."""
        recommendations = await benchmark_service.get_benchmark_selection_recommendations(
            portfolio=sample_portfolio
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should recommend tech-focused benchmarks for tech-heavy portfolio
        symbols = [rec.symbol for rec in recommendations]
        assert "QQQ" in symbols  # Tech-focused
        assert "SPY" in symbols or "VTI" in symbols  # Broad US market
    
    @pytest.mark.asyncio
    async def test_get_benchmark_selection_recommendations_empty_portfolio(
        self, 
        benchmark_service
    ):
        """Test benchmark recommendations for empty portfolio."""
        empty_metrics = PortfolioMetrics(
            total_value=Decimal("0"),
            total_invested=Decimal("0"),
            total_return=Decimal("0"),
            total_return_pct=Decimal("0")
        )
        
        empty_portfolio = Portfolio(
            id="empty_portfolio",
            name="Empty Portfolio",
            user_id="test_user",
            pies=[],
            individual_positions=[],
            metrics=empty_metrics,
            last_updated=datetime.utcnow()
        )
        
        recommendations = await benchmark_service.get_benchmark_selection_recommendations(
            portfolio=empty_portfolio
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) >= 1
        # Should default to SPY for empty portfolio
        assert recommendations[0].symbol == "SPY"