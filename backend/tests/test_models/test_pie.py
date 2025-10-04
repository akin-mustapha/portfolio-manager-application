"""
Tests for Pie and PieMetrics models.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from app.models.pie import Pie, PieMetrics
from app.models.position import Position
from app.models.risk import RiskMetrics
from app.models.enums import AssetType, RiskCategory


class TestPieMetrics:
    """Test PieMetrics model validation and functionality."""
    
    def test_valid_pie_metrics_creation(self):
        """Test creating valid pie metrics."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        assert pie_metrics.total_value == Decimal("10000.00")
        assert pie_metrics.invested_amount == Decimal("9500.00")
        assert pie_metrics.total_return == Decimal("500.00")
        assert pie_metrics.portfolio_weight == Decimal("25.5")
    
    def test_negative_total_value_validation(self):
        """Test that negative total value raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PieMetrics(
                total_value=Decimal("-1000.00"),
                invested_amount=Decimal("9500.00"),
                total_return=Decimal("500.00"),
                total_return_pct=Decimal("5.26"),
                portfolio_weight=Decimal("25.5")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_invested_amount_validation(self):
        """Test that negative invested amount raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PieMetrics(
                total_value=Decimal("10000.00"),
                invested_amount=Decimal("-9500.00"),
                total_return=Decimal("500.00"),
                total_return_pct=Decimal("5.26"),
                portfolio_weight=Decimal("25.5")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_portfolio_weight_range_validation(self):
        """Test that portfolio weight must be between 0 and 100."""
        # Test portfolio weight too high
        with pytest.raises(ValidationError) as exc_info:
            PieMetrics(
                total_value=Decimal("10000.00"),
                invested_amount=Decimal("9500.00"),
                total_return=Decimal("500.00"),
                total_return_pct=Decimal("5.26"),
                portfolio_weight=Decimal("150.0")
            )
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)
        
        # Test negative portfolio weight
        with pytest.raises(ValidationError) as exc_info:
            PieMetrics(
                total_value=Decimal("10000.00"),
                invested_amount=Decimal("9500.00"),
                total_return=Decimal("500.00"),
                total_return_pct=Decimal("5.26"),
                portfolio_weight=Decimal("-10.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_default_values(self):
        """Test default values for optional fields."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        assert pie_metrics.cash_balance == Decimal('0')
        assert pie_metrics.portfolio_contribution == Decimal('0')
        assert pie_metrics.total_dividends == Decimal('0')
        assert pie_metrics.dividend_yield == Decimal('0')
        assert pie_metrics.monthly_dividend_avg == Decimal('0')


class TestPie:
    """Test Pie model validation and functionality."""
    
    def test_valid_pie_creation(self):
        """Test creating a valid pie."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert pie.id == "pie_123"
        assert pie.name == "Tech Growth Pie"
        assert pie.metrics.total_value == Decimal("10000.00")
        assert pie.created_at == datetime(2024, 1, 1, 12, 0, 0)
    
    def test_pie_with_positions(self, sample_position_data):
        """Test pie with positions."""
        position = Position(**sample_position_data)
        
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            positions=[position],
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert len(pie.positions) == 1
        assert pie.positions[0].symbol == "AAPL"
        assert pie.position_count == 1
    
    def test_positions_validation(self):
        """Test that positions must be a list."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        with pytest.raises(ValidationError) as exc_info:
            Pie(
                id="pie_123",
                name="Tech Growth Pie",
                positions="not_a_list",
                metrics=pie_metrics,
                created_at=datetime(2024, 1, 1, 12, 0, 0)
            )
        
        assert "Input should be a valid list" in str(exc_info.value)
    
    def test_target_allocation_range_validation(self):
        """Test that target allocation must be between 0 and 100."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        # Test target allocation too high
        with pytest.raises(ValidationError) as exc_info:
            Pie(
                id="pie_123",
                name="Tech Growth Pie",
                metrics=pie_metrics,
                created_at=datetime(2024, 1, 1, 12, 0, 0),
                target_allocation=Decimal("150.0")
            )
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)
        
        # Test negative target allocation
        with pytest.raises(ValidationError) as exc_info:
            Pie(
                id="pie_123",
                name="Tech Growth Pie",
                metrics=pie_metrics,
                created_at=datetime(2024, 1, 1, 12, 0, 0),
                target_allocation=Decimal("-10.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            Pie()
        
        error_messages = str(exc_info.value)
        assert "id" in error_messages
        assert "name" in error_messages
        assert "metrics" in error_messages
        assert "created_at" in error_messages
    
    def test_default_values(self):
        """Test default values for optional fields."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert pie.positions == []
        assert pie.auto_invest is False
        assert pie.target_allocation is None
        assert pie.description is None
        assert pie.last_rebalanced is None
        assert isinstance(pie.last_updated, datetime)
    
    def test_position_count_property(self, sample_position_data):
        """Test position_count property."""
        position1 = Position(**sample_position_data)
        position2_data = sample_position_data.copy()
        position2_data["symbol"] = "MSFT"
        position2_data["name"] = "Microsoft Corp."
        position2 = Position(**position2_data)
        
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            positions=[position1, position2],
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert pie.position_count == 2
    
    def test_top_holdings_property(self, sample_position_data):
        """Test top_holdings property."""
        # Create positions with different market values
        positions = []
        for i in range(12):  # Create more than 10 positions
            pos_data = sample_position_data.copy()
            pos_data["symbol"] = f"STOCK{i}"
            pos_data["name"] = f"Stock {i}"
            pos_data["market_value"] = Decimal(str(1000 + i * 100))
            positions.append(Position(**pos_data))
        
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            positions=positions,
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        top_holdings = pie.top_holdings
        assert len(top_holdings) == 10  # Should return only top 10
        assert top_holdings[0].symbol == "STOCK11"  # Highest market value
        assert top_holdings[0].market_value == Decimal("2100")
        assert top_holdings[-1].symbol == "STOCK2"  # 10th highest
        assert top_holdings[-1].market_value == Decimal("1200")
    
    def test_json_serialization(self):
        """Test JSON serialization of pie."""
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("25.5")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        json_data = pie.model_dump()
        
        assert json_data["id"] == "pie_123"
        assert json_data["name"] == "Tech Growth Pie"
        assert json_data["auto_invest"] is False
        assert json_data["created_at"] == datetime(2024, 1, 1, 12, 0, 0)
        assert isinstance(json_data["last_updated"], datetime)