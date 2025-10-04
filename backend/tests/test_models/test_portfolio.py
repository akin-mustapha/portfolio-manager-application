"""
Tests for Portfolio and PortfolioMetrics models.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.pie import Pie, PieMetrics
from app.models.position import Position
from app.models.risk import RiskMetrics
from app.models.enums import AssetType, RiskCategory


class TestPortfolioMetrics:
    """Test PortfolioMetrics model validation and functionality."""
    
    def test_valid_portfolio_metrics_creation(self):
        """Test creating valid portfolio metrics."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        assert portfolio_metrics.total_value == Decimal("50000.00")
        assert portfolio_metrics.total_invested == Decimal("45000.00")
        assert portfolio_metrics.total_return == Decimal("5000.00")
        assert portfolio_metrics.total_return_pct == Decimal("11.11")
    
    def test_negative_total_value_validation(self):
        """Test that negative total value raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PortfolioMetrics(
                total_value=Decimal("-50000.00"),
                total_invested=Decimal("45000.00"),
                total_return=Decimal("5000.00"),
                total_return_pct=Decimal("11.11")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_total_invested_validation(self):
        """Test that negative total invested raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PortfolioMetrics(
                total_value=Decimal("50000.00"),
                total_invested=Decimal("-45000.00"),
                total_return=Decimal("5000.00"),
                total_return_pct=Decimal("11.11")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_diversification_score_range_validation(self):
        """Test that diversification score must be between 0 and 100."""
        # Test diversification score too high
        with pytest.raises(ValidationError) as exc_info:
            PortfolioMetrics(
                total_value=Decimal("50000.00"),
                total_invested=Decimal("45000.00"),
                total_return=Decimal("5000.00"),
                total_return_pct=Decimal("11.11"),
                diversification_score=Decimal("150.0")
            )
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)
        
        # Test negative diversification score
        with pytest.raises(ValidationError) as exc_info:
            PortfolioMetrics(
                total_value=Decimal("50000.00"),
                total_invested=Decimal("45000.00"),
                total_return=Decimal("5000.00"),
                total_return_pct=Decimal("11.11"),
                diversification_score=Decimal("-10.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_top_10_weight_range_validation(self):
        """Test that top 10 weight must be between 0 and 100."""
        # Test top 10 weight too high
        with pytest.raises(ValidationError) as exc_info:
            PortfolioMetrics(
                total_value=Decimal("50000.00"),
                total_invested=Decimal("45000.00"),
                total_return=Decimal("5000.00"),
                total_return_pct=Decimal("11.11"),
                top_10_weight=Decimal("150.0")
            )
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)
        
        # Test negative top 10 weight
        with pytest.raises(ValidationError) as exc_info:
            PortfolioMetrics(
                total_value=Decimal("50000.00"),
                total_invested=Decimal("45000.00"),
                total_return=Decimal("5000.00"),
                total_return_pct=Decimal("11.11"),
                top_10_weight=Decimal("-10.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_default_values(self):
        """Test default values for optional fields."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        assert portfolio_metrics.cash_balance == Decimal('0')
        assert portfolio_metrics.total_dividends == Decimal('0')
        assert portfolio_metrics.dividend_yield == Decimal('0')
        assert portfolio_metrics.annual_dividend_projection == Decimal('0')
        assert portfolio_metrics.monthly_dividend_avg == Decimal('0')
        assert portfolio_metrics.diversification_score == Decimal('0')
        assert portfolio_metrics.concentration_risk == Decimal('0')
        assert portfolio_metrics.top_10_weight == Decimal('0')
        assert portfolio_metrics.sector_allocation == {}
        assert portfolio_metrics.country_allocation == {}
        assert portfolio_metrics.asset_type_allocation == {}


class TestPortfolio:
    """Test Portfolio model validation and functionality."""
    
    def test_valid_portfolio_creation(self):
        """Test creating a valid portfolio."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        portfolio = Portfolio(
            id="portfolio_123",
            user_id="user_456",
            metrics=portfolio_metrics
        )
        
        assert portfolio.id == "portfolio_123"
        assert portfolio.user_id == "user_456"
        assert portfolio.metrics.total_value == Decimal("50000.00")
        assert portfolio.name == "Main Portfolio"  # Default value
        assert portfolio.base_currency == "USD"  # Default value
    
    def test_portfolio_with_pies_and_positions(self, sample_position_data):
        """Test portfolio with pies and individual positions."""
        # Create a pie
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("20.0")
        )
        
        pie_position = Position(**sample_position_data)
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            positions=[pie_position],
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        # Create individual position
        individual_position_data = sample_position_data.copy()
        individual_position_data["symbol"] = "MSFT"
        individual_position_data["name"] = "Microsoft Corp."
        individual_position = Position(**individual_position_data)
        
        # Create portfolio
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        portfolio = Portfolio(
            id="portfolio_123",
            user_id="user_456",
            pies=[pie],
            individual_positions=[individual_position],
            metrics=portfolio_metrics
        )
        
        assert len(portfolio.pies) == 1
        assert len(portfolio.individual_positions) == 1
        assert portfolio.pie_count == 1
        assert portfolio.total_positions == 2  # 1 from pie + 1 individual
    
    def test_pies_validation(self):
        """Test that pies must be a list."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        with pytest.raises(ValidationError) as exc_info:
            Portfolio(
                id="portfolio_123",
                user_id="user_456",
                pies="not_a_list",
                metrics=portfolio_metrics
            )
        
        assert "Input should be a valid list" in str(exc_info.value)
    
    def test_individual_positions_validation(self):
        """Test that individual positions must be a list."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        with pytest.raises(ValidationError) as exc_info:
            Portfolio(
                id="portfolio_123",
                user_id="user_456",
                individual_positions="not_a_list",
                metrics=portfolio_metrics
            )
        
        assert "Input should be a valid list" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            Portfolio()
        
        error_messages = str(exc_info.value)
        assert "id" in error_messages
        assert "user_id" in error_messages
        assert "metrics" in error_messages
    
    def test_default_values(self):
        """Test default values for optional fields."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        portfolio = Portfolio(
            id="portfolio_123",
            user_id="user_456",
            metrics=portfolio_metrics
        )
        
        assert portfolio.name == "Main Portfolio"
        assert portfolio.pies == []
        assert portfolio.individual_positions == []
        assert portfolio.base_currency == "USD"
        assert portfolio.benchmark_symbol is None
        assert isinstance(portfolio.created_at, datetime)
        assert isinstance(portfolio.last_updated, datetime)
        assert portfolio.last_sync is None
    
    def test_all_positions_property(self, sample_position_data):
        """Test all_positions property combines pie and individual positions."""
        # Create pie with position
        pie_position_data = sample_position_data.copy()
        pie_position_data["symbol"] = "AAPL"
        pie_position = Position(**pie_position_data)
        
        pie_metrics = PieMetrics(
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            portfolio_weight=Decimal("20.0")
        )
        
        pie = Pie(
            id="pie_123",
            name="Tech Growth Pie",
            positions=[pie_position],
            metrics=pie_metrics,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        # Create individual position
        individual_position_data = sample_position_data.copy()
        individual_position_data["symbol"] = "MSFT"
        individual_position = Position(**individual_position_data)
        
        # Create portfolio
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        portfolio = Portfolio(
            id="portfolio_123",
            user_id="user_456",
            pies=[pie],
            individual_positions=[individual_position],
            metrics=portfolio_metrics
        )
        
        all_positions = portfolio.all_positions
        assert len(all_positions) == 2
        symbols = [pos.symbol for pos in all_positions]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
    
    def test_top_holdings_property(self, sample_position_data):
        """Test top_holdings property returns top 10 positions by market value."""
        # Create multiple positions with different market values by varying current_price
        positions = []
        for i in range(12):  # Create more than 10 positions
            pos_data = sample_position_data.copy()
            pos_data["symbol"] = f"STOCK{i}"
            pos_data["name"] = f"Stock {i}"
            # Set different current_price to get different market_value
            # market_value = quantity * current_price = 10.5 * (100 + i * 10)
            pos_data["current_price"] = Decimal(str(100 + i * 10))
            # Set dummy values for required fields - they will be recalculated by validators
            pos_data["market_value"] = Decimal("0")
            pos_data["unrealized_pnl"] = Decimal("0")
            pos_data["unrealized_pnl_pct"] = Decimal("0")
            positions.append(Position(**pos_data))
        
        # Create portfolio with individual positions
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        portfolio = Portfolio(
            id="portfolio_123",
            user_id="user_456",
            individual_positions=positions,
            metrics=portfolio_metrics
        )
        
        top_holdings = portfolio.top_holdings
        assert len(top_holdings) == 10  # Should return only top 10
        # Positions are sorted by market value descending
        # STOCK11 has current_price = 100 + 11*10 = 210, market_value = 10.5 * 210 = 2205 (highest)
        # STOCK10 has current_price = 100 + 10*10 = 200, market_value = 10.5 * 200 = 2100 (second highest)
        # etc.
        assert top_holdings[0].symbol == "STOCK11"  # Highest market value
        assert top_holdings[0].market_value == Decimal("2205")  # 10.5 * 210
        assert top_holdings[1].symbol == "STOCK10"  # Second highest
        assert top_holdings[-1].symbol == "STOCK2"  # 10th highest (index 9)
        assert top_holdings[-1].market_value == Decimal("1260")  # 10.5 * 120
    
    def test_json_serialization(self):
        """Test JSON serialization of portfolio."""
        portfolio_metrics = PortfolioMetrics(
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        portfolio = Portfolio(
            id="portfolio_123",
            user_id="user_456",
            metrics=portfolio_metrics
        )
        
        json_data = portfolio.model_dump()
        
        assert json_data["id"] == "portfolio_123"
        assert json_data["user_id"] == "user_456"
        assert json_data["name"] == "Main Portfolio"
        assert json_data["base_currency"] == "USD"
        assert isinstance(json_data["created_at"], datetime)
        assert isinstance(json_data["last_updated"], datetime)