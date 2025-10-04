"""
Tests for Historical data models.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from pydantic import ValidationError

from app.models.historical import PricePoint, HistoricalData, PerformanceSnapshot


class TestPricePoint:
    """Test PricePoint model validation and functionality."""
    
    def test_valid_price_point_creation(self):
        """Test creating a valid price point."""
        price_point = PricePoint(
            price_date=date(2024, 1, 15),
            open_price=Decimal("150.00"),
            high_price=Decimal("155.00"),
            low_price=Decimal("149.00"),
            close_price=Decimal("154.50"),
            volume=1000000,
            adjusted_close=Decimal("154.50")
        )
        
        assert price_point.price_date == date(2024, 1, 15)
        assert price_point.open_price == Decimal("150.00")
        assert price_point.close_price == Decimal("154.50")
        assert price_point.volume == 1000000
    
    def test_zero_close_price_validation(self):
        """Test that zero close price raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PricePoint(
                price_date=date(2024, 1, 15),
                close_price=Decimal("0")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_negative_close_price_validation(self):
        """Test that negative close price raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PricePoint(
                price_date=date(2024, 1, 15),
                close_price=Decimal("-150.00")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_zero_optional_prices_validation(self):
        """Test that zero optional prices raise validation errors."""
        # Test zero open price
        with pytest.raises(ValidationError) as exc_info:
            PricePoint(
                price_date=date(2024, 1, 15),
                open_price=Decimal("0"),
                close_price=Decimal("150.00")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
        
        # Test zero high price
        with pytest.raises(ValidationError) as exc_info:
            PricePoint(
                price_date=date(2024, 1, 15),
                high_price=Decimal("0"),
                close_price=Decimal("150.00")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_negative_volume_validation(self):
        """Test that negative volume raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PricePoint(
                price_date=date(2024, 1, 15),
                close_price=Decimal("150.00"),
                volume=-1000
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            PricePoint()
        
        error_messages = str(exc_info.value)
        assert "price_date" in error_messages
        assert "close_price" in error_messages
    
    def test_optional_fields_none(self):
        """Test that optional fields can be None."""
        price_point = PricePoint(
            price_date=date(2024, 1, 15),
            close_price=Decimal("150.00")
        )
        
        assert price_point.open_price is None
        assert price_point.high_price is None
        assert price_point.low_price is None
        assert price_point.volume is None
        assert price_point.adjusted_close is None
    
    def test_json_serialization(self):
        """Test JSON serialization of price point."""
        price_point = PricePoint(
            price_date=date(2024, 1, 15),
            close_price=Decimal("150.00"),
            volume=1000000
        )
        
        json_data = price_point.model_dump()
        
        assert str(json_data["price_date"]) == "2024-01-15"
        assert json_data["close_price"] == 150.00
        assert json_data["volume"] == 1000000


class TestHistoricalData:
    """Test HistoricalData model validation and functionality."""
    
    def test_valid_historical_data_creation(self):
        """Test creating valid historical data."""
        price_points = [
            PricePoint(
                price_date=date(2024, 1, 15),
                close_price=Decimal("150.00")
            ),
            PricePoint(
                price_date=date(2024, 1, 16),
                close_price=Decimal("152.00")
            )
        ]
        
        historical_data = HistoricalData(
            symbol="AAPL",
            name="Apple Inc.",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 16)
        )
        
        assert historical_data.symbol == "AAPL"
        assert historical_data.name == "Apple Inc."
        assert len(historical_data.price_history) == 2
        assert historical_data.start_date == date(2024, 1, 15)
        assert historical_data.end_date == date(2024, 1, 16)
        assert historical_data.frequency == "daily"  # Default value
        assert historical_data.currency == "USD"  # Default value
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            HistoricalData()
        
        error_messages = str(exc_info.value)
        assert "symbol" in error_messages
        assert "price_history" in error_messages
        assert "start_date" in error_messages
        assert "end_date" in error_messages
    
    def test_data_points_count_property(self):
        """Test data_points_count property."""
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("150.00")),
            PricePoint(price_date=date(2024, 1, 16), close_price=Decimal("152.00")),
            PricePoint(price_date=date(2024, 1, 17), close_price=Decimal("151.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="AAPL",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17)
        )
        
        assert historical_data.data_points_count == 3
    
    def test_latest_price_property(self):
        """Test latest_price property."""
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("150.00")),
            PricePoint(price_date=date(2024, 1, 16), close_price=Decimal("152.00")),
            PricePoint(price_date=date(2024, 1, 17), close_price=Decimal("151.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="AAPL",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17)
        )
        
        assert historical_data.latest_price == Decimal("151.00")
    
    def test_earliest_price_property(self):
        """Test earliest_price property."""
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("150.00")),
            PricePoint(price_date=date(2024, 1, 16), close_price=Decimal("152.00")),
            PricePoint(price_date=date(2024, 1, 17), close_price=Decimal("151.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="AAPL",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17)
        )
        
        assert historical_data.earliest_price == Decimal("150.00")
    
    def test_empty_price_history_properties(self):
        """Test properties with empty price history."""
        historical_data = HistoricalData(
            symbol="AAPL",
            price_history=[],
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17)
        )
        
        assert historical_data.data_points_count == 0
        assert historical_data.latest_price is None
        assert historical_data.earliest_price is None
    
    def test_default_values(self):
        """Test default values for optional fields."""
        historical_data = HistoricalData(
            symbol="AAPL",
            price_history=[],
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17)
        )
        
        assert historical_data.name is None
        assert historical_data.frequency == "daily"
        assert historical_data.currency == "USD"
        assert historical_data.data_source is None
        assert isinstance(historical_data.last_updated, datetime)
    
    def test_json_serialization(self):
        """Test JSON serialization of historical data."""
        price_points = [
            PricePoint(price_date=date(2024, 1, 15), close_price=Decimal("150.00"))
        ]
        
        historical_data = HistoricalData(
            symbol="AAPL",
            price_history=price_points,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 15)
        )
        
        json_data = historical_data.model_dump()
        
        assert json_data["symbol"] == "AAPL"
        assert str(json_data["start_date"]) == "2024-01-15"
        assert str(json_data["end_date"]) == "2024-01-15"
        assert len(json_data["price_history"]) == 1
        assert isinstance(json_data["last_updated"], datetime)


class TestPerformanceSnapshot:
    """Test PerformanceSnapshot model validation and functionality."""
    
    def test_valid_performance_snapshot_creation(self):
        """Test creating a valid performance snapshot."""
        snapshot = PerformanceSnapshot(
            entity_id="portfolio_123",
            entity_type="portfolio",
            snapshot_date=date(2024, 1, 31),
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            start_value=Decimal("45000.00"),
            end_value=Decimal("47500.00"),
            total_return=Decimal("2500.00"),
            total_return_pct=Decimal("5.56")
        )
        
        assert snapshot.entity_id == "portfolio_123"
        assert snapshot.entity_type == "portfolio"
        assert snapshot.snapshot_date == date(2024, 1, 31)
        assert snapshot.start_value == Decimal("45000.00")
        assert snapshot.end_value == Decimal("47500.00")
        assert snapshot.total_return == Decimal("2500.00")
        assert snapshot.total_return_pct == Decimal("5.56")
    
    def test_negative_start_value_validation(self):
        """Test that negative start value raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceSnapshot(
                entity_id="portfolio_123",
                entity_type="portfolio",
                snapshot_date=date(2024, 1, 31),
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                start_value=Decimal("-45000.00"),
                end_value=Decimal("47500.00"),
                total_return=Decimal("2500.00"),
                total_return_pct=Decimal("5.56")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_end_value_validation(self):
        """Test that negative end value raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceSnapshot(
                entity_id="portfolio_123",
                entity_type="portfolio",
                snapshot_date=date(2024, 1, 31),
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                start_value=Decimal("45000.00"),
                end_value=Decimal("-47500.00"),
                total_return=Decimal("2500.00"),
                total_return_pct=Decimal("5.56")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_dividends_received_validation(self):
        """Test that negative dividends received raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceSnapshot(
                entity_id="portfolio_123",
                entity_type="portfolio",
                snapshot_date=date(2024, 1, 31),
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                start_value=Decimal("45000.00"),
                end_value=Decimal("47500.00"),
                total_return=Decimal("2500.00"),
                total_return_pct=Decimal("5.56"),
                dividends_received=Decimal("-100.00")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_withdrawals_validation(self):
        """Test that negative withdrawals raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceSnapshot(
                entity_id="portfolio_123",
                entity_type="portfolio",
                snapshot_date=date(2024, 1, 31),
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                start_value=Decimal("45000.00"),
                end_value=Decimal("47500.00"),
                total_return=Decimal("2500.00"),
                total_return_pct=Decimal("5.56"),
                withdrawals=Decimal("-1000.00")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceSnapshot()
        
        error_messages = str(exc_info.value)
        assert "entity_id" in error_messages
        assert "entity_type" in error_messages
        assert "snapshot_date" in error_messages
        assert "period_start" in error_messages
        assert "period_end" in error_messages
        assert "start_value" in error_messages
        assert "end_value" in error_messages
        assert "total_return" in error_messages
        assert "total_return_pct" in error_messages
    
    def test_default_values(self):
        """Test default values for optional fields."""
        snapshot = PerformanceSnapshot(
            entity_id="portfolio_123",
            entity_type="portfolio",
            snapshot_date=date(2024, 1, 31),
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            start_value=Decimal("45000.00"),
            end_value=Decimal("47500.00"),
            total_return=Decimal("2500.00"),
            total_return_pct=Decimal("5.56")
        )
        
        assert snapshot.dividends_received == Decimal('0')
        assert snapshot.contributions == Decimal('0')
        assert snapshot.withdrawals == Decimal('0')
        assert isinstance(snapshot.created_at, datetime)
    
    def test_json_serialization(self):
        """Test JSON serialization of performance snapshot."""
        snapshot = PerformanceSnapshot(
            entity_id="portfolio_123",
            entity_type="portfolio",
            snapshot_date=date(2024, 1, 31),
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            start_value=Decimal("45000.00"),
            end_value=Decimal("47500.00"),
            total_return=Decimal("2500.00"),
            total_return_pct=Decimal("5.56")
        )
        
        json_data = snapshot.model_dump()
        
        assert json_data["entity_id"] == "portfolio_123"
        assert json_data["entity_type"] == "portfolio"
        assert str(json_data["snapshot_date"]) == "2024-01-31"
        assert str(json_data["period_start"]) == "2024-01-01"
        assert str(json_data["period_end"]) == "2024-01-31"
        assert json_data["start_value"] == 45000.00
        assert json_data["end_value"] == 47500.00
        assert isinstance(json_data["created_at"], datetime)