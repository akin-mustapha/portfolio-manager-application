"""
Tests for Benchmark comparison models.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from pydantic import ValidationError

from app.models.benchmark import BenchmarkData, BenchmarkComparison
from app.models.historical import HistoricalData, PricePoint


class TestBenchmarkData:
    """Test BenchmarkData model validation and functionality."""
    
    def test_valid_benchmark_data_creation(self):
        """Test creating valid benchmark data."""
        # Create historical data for benchmark
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("4500.00")),
            PricePoint(price_date=date(2024, 1, 16), close_price=Decimal("4520.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="SPY",
            name="SPDR S&P 500 ETF",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 16)
        )
        
        benchmark_data = BenchmarkData(
            symbol="SPY",
            name="S&P 500",
            description="S&P 500 Index tracking ETF",
            historical_data=historical_data,
            asset_class="equity",
            geography="US",
            market_cap="Large"
        )
        
        assert benchmark_data.symbol == "SPY"
        assert benchmark_data.name == "S&P 500"
        assert benchmark_data.description == "S&P 500 Index tracking ETF"
        assert benchmark_data.asset_class == "equity"
        assert benchmark_data.geography == "US"
        assert benchmark_data.market_cap == "Large"
        assert benchmark_data.historical_data.symbol == "SPY"
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkData()
        
        error_messages = str(exc_info.value)
        assert "symbol" in error_messages
        assert "name" in error_messages
        assert "historical_data" in error_messages
        assert "asset_class" in error_messages
        assert "geography" in error_messages
    
    def test_optional_fields_none(self):
        """Test that optional fields can be None."""
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("4500.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="SPY",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 15)
        )
        
        benchmark_data = BenchmarkData(
            symbol="SPY",
            name="S&P 500",
            historical_data=historical_data,
            asset_class="equity",
            geography="US"
        )
        
        assert benchmark_data.description is None
        assert benchmark_data.market_cap is None
        assert benchmark_data.data_provider is None
        assert isinstance(benchmark_data.last_updated, datetime)
    
    def test_json_serialization(self):
        """Test JSON serialization of benchmark data."""
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("4500.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="SPY",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 15)
        )
        
        benchmark_data = BenchmarkData(
            symbol="SPY",
            name="S&P 500",
            historical_data=historical_data,
            asset_class="equity",
            geography="US"
        )
        
        json_data = benchmark_data.model_dump()
        
        assert json_data["symbol"] == "SPY"
        assert json_data["name"] == "S&P 500"
        assert json_data["asset_class"] == "equity"
        assert json_data["geography"] == "US"
        assert "historical_data" in json_data
        assert isinstance(json_data["last_updated"], datetime)


class TestBenchmarkComparison:
    """Test BenchmarkComparison model validation and functionality."""
    
    def test_valid_benchmark_comparison_creation(self):
        """Test creating a valid benchmark comparison."""
        comparison = BenchmarkComparison(
            portfolio_id="portfolio_123",
            benchmark_symbol="SPY",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            portfolio_return=Decimal("8.50"),
            benchmark_return=Decimal("7.25"),
            excess_return=Decimal("1.25"),
            alpha=Decimal("1.15"),
            beta=Decimal("1.05"),
            correlation=Decimal("0.85"),
            tracking_error=Decimal("2.50"),
            information_ratio=Decimal("0.50"),
            outperformance_periods=18,
            total_periods=21,
            win_rate=Decimal("85.71"),
            max_drawdown_portfolio=Decimal("-5.25"),
            max_drawdown_benchmark=Decimal("-4.75"),
            drawdown_difference=Decimal("-0.50"),
            volatility_portfolio=Decimal("12.50"),
            volatility_benchmark=Decimal("11.25"),
            volatility_ratio=Decimal("1.11")
        )
        
        assert comparison.portfolio_id == "portfolio_123"
        assert comparison.benchmark_symbol == "SPY"
        assert comparison.portfolio_return == Decimal("8.50")
        assert comparison.benchmark_return == Decimal("7.25")
        assert comparison.excess_return == Decimal("1.25")
        assert comparison.alpha == Decimal("1.15")
        assert comparison.beta == Decimal("1.05")
        assert comparison.win_rate == Decimal("85.71")
    
    def test_correlation_range_validation(self):
        """Test that correlation must be between -1 and 1."""
        # Test correlation too high
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11"),
                correlation=Decimal("1.5")
            )
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
        
        # Test correlation too low
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11"),
                correlation=Decimal("-1.5")
            )
        
        assert "Input should be greater than or equal to -1" in str(exc_info.value)
    
    def test_negative_tracking_error_validation(self):
        """Test that negative tracking error raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11"),
                tracking_error=Decimal("-2.50")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_outperformance_periods_validation(self):
        """Test that negative outperformance periods raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11"),
                outperformance_periods=-5
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_zero_total_periods_validation(self):
        """Test that zero total periods raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=0,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_negative_volatility_validation(self):
        """Test that negative volatility raises validation error."""
        # Test negative portfolio volatility
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("-12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
        
        # Test negative benchmark volatility
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("-11.25"),
                volatility_ratio=Decimal("1.11")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_zero_volatility_ratio_validation(self):
        """Test that zero volatility ratio raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("0")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_win_rate_range_validation(self):
        """Test that win rate must be between 0 and 100."""
        # Test win rate too high
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11"),
                win_rate=Decimal("150.0")
            )
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)
        
        # Test negative win rate
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison(
                benchmark_symbol="SPY",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                portfolio_return=Decimal("8.50"),
                benchmark_return=Decimal("7.25"),
                excess_return=Decimal("1.25"),
                total_periods=21,
                max_drawdown_portfolio=Decimal("-5.25"),
                max_drawdown_benchmark=Decimal("-4.75"),
                drawdown_difference=Decimal("-0.50"),
                volatility_portfolio=Decimal("12.50"),
                volatility_benchmark=Decimal("11.25"),
                volatility_ratio=Decimal("1.11"),
                win_rate=Decimal("-10.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            BenchmarkComparison()
        
        error_messages = str(exc_info.value)
        assert "benchmark_symbol" in error_messages
        assert "start_date" in error_messages
        assert "end_date" in error_messages
        assert "portfolio_return" in error_messages
        assert "benchmark_return" in error_messages
        assert "excess_return" in error_messages
        assert "total_periods" in error_messages
        assert "max_drawdown_portfolio" in error_messages
        assert "max_drawdown_benchmark" in error_messages
        assert "drawdown_difference" in error_messages
        assert "volatility_portfolio" in error_messages
        assert "volatility_benchmark" in error_messages
        assert "volatility_ratio" in error_messages
    
    def test_default_values(self):
        """Test default values for optional fields."""
        comparison = BenchmarkComparison(
            benchmark_symbol="SPY",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            portfolio_return=Decimal("8.50"),
            benchmark_return=Decimal("7.25"),
            excess_return=Decimal("1.25"),
            total_periods=21,
            max_drawdown_portfolio=Decimal("-5.25"),
            max_drawdown_benchmark=Decimal("-4.75"),
            drawdown_difference=Decimal("-0.50"),
            volatility_portfolio=Decimal("12.50"),
            volatility_benchmark=Decimal("11.25"),
            volatility_ratio=Decimal("1.11")
        )
        
        assert comparison.portfolio_id is None
        assert comparison.pie_id is None
        assert comparison.alpha is None
        assert comparison.beta is None
        assert comparison.correlation is None
        assert comparison.tracking_error is None
        assert comparison.information_ratio is None
        assert comparison.outperformance_periods == 0
        assert comparison.win_rate == Decimal('0')
        assert isinstance(comparison.calculation_date, datetime)
    
    def test_json_serialization(self):
        """Test JSON serialization of benchmark comparison."""
        comparison = BenchmarkComparison(
            portfolio_id="portfolio_123",
            benchmark_symbol="SPY",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            portfolio_return=Decimal("8.50"),
            benchmark_return=Decimal("7.25"),
            excess_return=Decimal("1.25"),
            total_periods=21,
            max_drawdown_portfolio=Decimal("-5.25"),
            max_drawdown_benchmark=Decimal("-4.75"),
            drawdown_difference=Decimal("-0.50"),
            volatility_portfolio=Decimal("12.50"),
            volatility_benchmark=Decimal("11.25"),
            volatility_ratio=Decimal("1.11")
        )
        
        json_data = comparison.model_dump()
        
        assert json_data["portfolio_id"] == "portfolio_123"
        assert json_data["benchmark_symbol"] == "SPY"
        assert json_data["start_date"] == "2024-01-01"
        assert json_data["end_date"] == "2024-01-31"
        assert json_data["portfolio_return"] == 8.50
        assert json_data["benchmark_return"] == 7.25
        assert json_data["excess_return"] == 1.25
        assert isinstance(json_data["calculation_date"], datetime)