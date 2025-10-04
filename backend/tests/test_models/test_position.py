"""
Tests for Position model.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from app.models.position import Position
from app.models.enums import AssetType


class TestPosition:
    """Test Position model validation and functionality."""
    
    def test_valid_position_creation(self, sample_position_data):
        """Test creating a valid position."""
        position = Position(**sample_position_data)
        
        assert position.symbol == "AAPL"
        assert position.name == "Apple Inc."
        assert position.quantity == Decimal("10.5")
        assert position.average_price == Decimal("150.25")
        assert position.current_price == Decimal("155.75")
        assert position.asset_type == AssetType.STOCK
        assert position.currency == "USD"
    
    def test_market_value_calculation(self):
        """Test automatic market value calculation."""
        position_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": Decimal("10"),
            "average_price": Decimal("100"),
            "current_price": Decimal("110"),
            "market_value": Decimal("0"),  # This should be recalculated
            "unrealized_pnl": Decimal("0"),
            "unrealized_pnl_pct": Decimal("0"),
            "asset_type": AssetType.STOCK
        }
        
        position = Position(**position_data)
        assert position.market_value == Decimal("1100")  # 10 * 110
    
    def test_unrealized_pnl_calculation(self):
        """Test automatic unrealized P&L calculation."""
        position_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": Decimal("10"),
            "average_price": Decimal("100"),
            "current_price": Decimal("110"),
            "market_value": Decimal("1100"),
            "unrealized_pnl": Decimal("0"),  # This should be recalculated
            "unrealized_pnl_pct": Decimal("0"),
            "asset_type": AssetType.STOCK
        }
        
        position = Position(**position_data)
        assert position.unrealized_pnl == Decimal("100")  # 10 * (110 - 100)
    
    def test_unrealized_pnl_percentage_calculation(self):
        """Test automatic unrealized P&L percentage calculation."""
        position_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": Decimal("10"),
            "average_price": Decimal("100"),
            "current_price": Decimal("110"),
            "market_value": Decimal("1100"),
            "unrealized_pnl": Decimal("100"),
            "unrealized_pnl_pct": Decimal("0"),  # This should be recalculated
            "asset_type": AssetType.STOCK
        }
        
        position = Position(**position_data)
        assert position.unrealized_pnl_pct == Decimal("10")  # (110 - 100) / 100 * 100
    
    def test_negative_quantity_validation(self):
        """Test that negative quantity raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal("-1"),
                average_price=Decimal("100"),
                current_price=Decimal("110"),
                market_value=Decimal("1100"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("10"),
                asset_type=AssetType.STOCK
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_average_price_validation(self):
        """Test that negative average price raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal("10"),
                average_price=Decimal("-100"),
                current_price=Decimal("110"),
                market_value=Decimal("1100"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("10"),
                asset_type=AssetType.STOCK
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_current_price_validation(self):
        """Test that negative current price raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal("10"),
                average_price=Decimal("100"),
                current_price=Decimal("-110"),
                market_value=Decimal("1100"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("10"),
                asset_type=AssetType.STOCK
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_market_value_validation(self):
        """Test that negative market value raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal("10"),
                average_price=Decimal("100"),
                current_price=Decimal("110"),
                market_value=Decimal("-1100"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("10"),
                asset_type=AssetType.STOCK
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            Position()
        
        error_messages = str(exc_info.value)
        assert "symbol" in error_messages
        assert "name" in error_messages
        assert "quantity" in error_messages
        assert "asset_type" in error_messages
    
    def test_invalid_asset_type(self):
        """Test that invalid asset type raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal("10"),
                average_price=Decimal("100"),
                current_price=Decimal("110"),
                market_value=Decimal("1100"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("10"),
                asset_type="INVALID_TYPE"
            )
        
        assert "Input should be" in str(exc_info.value)
    
    def test_default_currency(self):
        """Test that default currency is USD."""
        position = Position(
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10"),
            average_price=Decimal("100"),
            current_price=Decimal("110"),
            market_value=Decimal("1100"),
            unrealized_pnl=Decimal("100"),
            unrealized_pnl_pct=Decimal("10"),
            asset_type=AssetType.STOCK
        )
        
        assert position.currency == "USD"
    
    def test_last_updated_default(self):
        """Test that last_updated has a default value."""
        position = Position(
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10"),
            average_price=Decimal("100"),
            current_price=Decimal("110"),
            market_value=Decimal("1100"),
            unrealized_pnl=Decimal("100"),
            unrealized_pnl_pct=Decimal("10"),
            asset_type=AssetType.STOCK
        )
        
        assert isinstance(position.last_updated, datetime)
    
    def test_json_serialization(self, sample_position_data):
        """Test JSON serialization of position."""
        position = Position(**sample_position_data)
        json_data = position.model_dump()
        
        assert json_data["symbol"] == "AAPL"
        assert json_data["asset_type"] == "STOCK"
        assert isinstance(json_data["last_updated"], datetime)
    
    def test_optional_fields(self):
        """Test that optional fields can be None."""
        position = Position(
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10"),
            average_price=Decimal("100"),
            current_price=Decimal("110"),
            market_value=Decimal("1100"),
            unrealized_pnl=Decimal("100"),
            unrealized_pnl_pct=Decimal("10"),
            asset_type=AssetType.STOCK,
            sector=None,
            industry=None,
            country=None
        )
        
        assert position.sector is None
        assert position.industry is None
        assert position.country is None