"""
Tests for SQLAlchemy database models.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    PortfolioTable, PieTable, PositionTable, DividendTable, 
    HistoricalDataTable, PerformanceSnapshotTable,
    AssetTypeEnum, RiskCategoryEnum, DividendTypeEnum
)


class TestPortfolioTable:
    """Test PortfolioTable database model."""
    
    def test_create_portfolio(self, test_db_session):
        """Test creating a portfolio record."""
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456",
            name="Test Portfolio",
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved = test_db_session.query(PortfolioTable).filter_by(id="portfolio_123").first()
        assert retrieved is not None
        assert retrieved.user_id == "user_456"
        assert retrieved.name == "Test Portfolio"
        assert retrieved.total_value == Decimal("50000.00")
        assert retrieved.base_currency == "USD"  # Default value
    
    def test_portfolio_required_fields(self, test_db_session):
        """Test that required fields are enforced."""
        # Missing user_id should fail
        portfolio = PortfolioTable(
            id="portfolio_123",
            total_value=Decimal("50000.00"),
            total_invested=Decimal("45000.00"),
            total_return=Decimal("5000.00"),
            total_return_pct=Decimal("11.11")
        )
        
        test_db_session.add(portfolio)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_portfolio_default_values(self, test_db_session):
        """Test default values for portfolio fields."""
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        retrieved = test_db_session.query(PortfolioTable).filter_by(id="portfolio_123").first()
        assert retrieved.name == "Main Portfolio"
        assert retrieved.base_currency == "USD"
        assert retrieved.total_value == Decimal("0")
        assert retrieved.total_invested == Decimal("0")
        assert retrieved.cash_balance == Decimal("0")
        assert retrieved.total_return == Decimal("0")
        assert retrieved.total_return_pct == Decimal("0")
        assert retrieved.total_dividends == Decimal("0")
        assert retrieved.dividend_yield == Decimal("0")
        assert retrieved.annual_dividend_projection == Decimal("0")
    
    def test_portfolio_timestamps(self, test_db_session):
        """Test that timestamps are set correctly."""
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        retrieved = test_db_session.query(PortfolioTable).filter_by(id="portfolio_123").first()
        assert retrieved.created_at is not None
        assert retrieved.last_updated is not None
        assert isinstance(retrieved.created_at, datetime)
        assert isinstance(retrieved.last_updated, datetime)


class TestPieTable:
    """Test PieTable database model."""
    
    def test_create_pie(self, test_db_session):
        """Test creating a pie record."""
        # First create a portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create pie
        pie = PieTable(
            id="pie_123",
            portfolio_id="portfolio_123",
            name="Tech Growth Pie",
            total_value=Decimal("10000.00"),
            invested_amount=Decimal("9500.00"),
            total_return=Decimal("500.00"),
            total_return_pct=Decimal("5.26"),
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        test_db_session.add(pie)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved = test_db_session.query(PieTable).filter_by(id="pie_123").first()
        assert retrieved is not None
        assert retrieved.portfolio_id == "portfolio_123"
        assert retrieved.name == "Tech Growth Pie"
        assert retrieved.total_value == Decimal("10000.00")
        assert retrieved.auto_invest is False  # Default value
    
    def test_pie_portfolio_relationship(self, test_db_session):
        """Test relationship between pie and portfolio."""
        # Create portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create pie
        pie = PieTable(
            id="pie_123",
            portfolio_id="portfolio_123",
            name="Tech Growth Pie",
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        test_db_session.add(pie)
        test_db_session.commit()
        
        # Test relationship
        retrieved_pie = test_db_session.query(PieTable).filter_by(id="pie_123").first()
        assert retrieved_pie.portfolio.id == "portfolio_123"
        
        retrieved_portfolio = test_db_session.query(PortfolioTable).filter_by(id="portfolio_123").first()
        assert len(retrieved_portfolio.pies) == 1
        assert retrieved_portfolio.pies[0].id == "pie_123"
    
    def test_pie_required_fields(self, test_db_session):
        """Test that required fields are enforced."""
        # Missing portfolio_id should fail
        pie = PieTable(
            id="pie_123",
            name="Tech Growth Pie",
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        test_db_session.add(pie)
        with pytest.raises(IntegrityError):
            test_db_session.commit()


class TestPositionTable:
    """Test PositionTable database model."""
    
    def test_create_position_in_portfolio(self, test_db_session):
        """Test creating a position in a portfolio."""
        # Create portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create position
        position = PositionTable(
            portfolio_id="portfolio_123",
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10.5"),
            average_price=Decimal("150.25"),
            current_price=Decimal("155.75"),
            market_value=Decimal("1635.38"),
            unrealized_pnl=Decimal("57.75"),
            unrealized_pnl_pct=Decimal("3.66"),
            asset_type=AssetTypeEnum.STOCK
        )
        
        test_db_session.add(position)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved = test_db_session.query(PositionTable).filter_by(symbol="AAPL").first()
        assert retrieved is not None
        assert retrieved.portfolio_id == "portfolio_123"
        assert retrieved.name == "Apple Inc."
        assert retrieved.asset_type == AssetTypeEnum.STOCK
        assert retrieved.currency == "USD"  # Default value
    
    def test_create_position_in_pie(self, test_db_session):
        """Test creating a position in a pie."""
        # Create portfolio and pie
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        pie = PieTable(
            id="pie_123",
            portfolio_id="portfolio_123",
            name="Tech Growth Pie",
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        test_db_session.add(pie)
        test_db_session.commit()
        
        # Create position in pie
        position = PositionTable(
            pie_id="pie_123",
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10.5"),
            average_price=Decimal("150.25"),
            current_price=Decimal("155.75"),
            market_value=Decimal("1635.38"),
            unrealized_pnl=Decimal("57.75"),
            unrealized_pnl_pct=Decimal("3.66"),
            asset_type=AssetTypeEnum.STOCK
        )
        
        test_db_session.add(position)
        test_db_session.commit()
        
        # Test relationship
        retrieved_position = test_db_session.query(PositionTable).filter_by(symbol="AAPL").first()
        assert retrieved_position.pie.id == "pie_123"
        
        retrieved_pie = test_db_session.query(PieTable).filter_by(id="pie_123").first()
        assert len(retrieved_pie.positions) == 1
        assert retrieved_pie.positions[0].symbol == "AAPL"
    
    def test_position_asset_type_enum(self, test_db_session):
        """Test that asset type enum works correctly."""
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Test different asset types
        for asset_type in AssetTypeEnum:
            position = PositionTable(
                portfolio_id="portfolio_123",
                symbol=f"TEST_{asset_type.value}",
                name=f"Test {asset_type.value}",
                quantity=Decimal("10"),
                average_price=Decimal("100"),
                current_price=Decimal("110"),
                market_value=Decimal("1100"),
                unrealized_pnl=Decimal("100"),
                unrealized_pnl_pct=Decimal("10"),
                asset_type=asset_type
            )
            test_db_session.add(position)
        
        test_db_session.commit()
        
        # Verify all asset types were saved correctly
        positions = test_db_session.query(PositionTable).all()
        asset_types = [pos.asset_type for pos in positions]
        assert len(set(asset_types)) == len(AssetTypeEnum)


class TestDividendTable:
    """Test DividendTable database model."""
    
    def test_create_dividend(self, test_db_session):
        """Test creating a dividend record."""
        # Create portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create dividend
        dividend = DividendTable(
            id="dividend_123",
            portfolio_id="portfolio_123",
            symbol="AAPL",
            security_name="Apple Inc.",
            dividend_type=DividendTypeEnum.CASH,
            amount_per_share=Decimal("0.25"),
            total_amount=Decimal("2.50"),
            shares_held=Decimal("10"),
            ex_dividend_date=date(2024, 1, 10),
            payment_date=date(2024, 1, 25),
            gross_amount=Decimal("2.50"),
            net_amount=Decimal("2.50")
        )
        
        test_db_session.add(dividend)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved = test_db_session.query(DividendTable).filter_by(id="dividend_123").first()
        assert retrieved is not None
        assert retrieved.portfolio_id == "portfolio_123"
        assert retrieved.symbol == "AAPL"
        assert retrieved.dividend_type == DividendTypeEnum.CASH
        assert retrieved.amount_per_share == Decimal("0.25")
        assert retrieved.ex_dividend_date == date(2024, 1, 10)
        assert retrieved.is_reinvested is False  # Default value
    
    def test_dividend_portfolio_relationship(self, test_db_session):
        """Test relationship between dividend and portfolio."""
        # Create portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create dividend
        dividend = DividendTable(
            id="dividend_123",
            portfolio_id="portfolio_123",
            symbol="AAPL",
            security_name="Apple Inc.",
            dividend_type=DividendTypeEnum.CASH,
            amount_per_share=Decimal("0.25"),
            total_amount=Decimal("2.50"),
            shares_held=Decimal("10"),
            ex_dividend_date=date(2024, 1, 10),
            payment_date=date(2024, 1, 25),
            gross_amount=Decimal("2.50"),
            net_amount=Decimal("2.50")
        )
        test_db_session.add(dividend)
        test_db_session.commit()
        
        # Test relationship
        retrieved_dividend = test_db_session.query(DividendTable).filter_by(id="dividend_123").first()
        assert retrieved_dividend.portfolio.id == "portfolio_123"
        
        retrieved_portfolio = test_db_session.query(PortfolioTable).filter_by(id="portfolio_123").first()
        assert len(retrieved_portfolio.dividends) == 1
        assert retrieved_portfolio.dividends[0].id == "dividend_123"


class TestHistoricalDataTable:
    """Test HistoricalDataTable database model."""
    
    def test_create_historical_data(self, test_db_session):
        """Test creating historical data records."""
        historical_data = HistoricalDataTable(
            symbol="AAPL",
            price_date=date(2024, 1, 15),
            open_price=Decimal("150.00"),
            high_price=Decimal("155.00"),
            low_price=Decimal("149.00"),
            close_price=Decimal("154.50"),
            adjusted_close=Decimal("154.50"),
            volume=1000000
        )
        
        test_db_session.add(historical_data)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved = test_db_session.query(HistoricalDataTable).filter_by(symbol="AAPL").first()
        assert retrieved is not None
        assert retrieved.price_date == date(2024, 1, 15)
        assert retrieved.close_price == Decimal("154.50")
        assert retrieved.volume == 1000000
        assert retrieved.currency == "USD"  # Default value
    
    def test_historical_data_required_fields(self, test_db_session):
        """Test that required fields are enforced."""
        # Missing close_price should fail
        historical_data = HistoricalDataTable(
            symbol="AAPL",
            price_date=date(2024, 1, 15)
        )
        
        test_db_session.add(historical_data)
        with pytest.raises(IntegrityError):
            test_db_session.commit()


class TestPerformanceSnapshotTable:
    """Test PerformanceSnapshotTable database model."""
    
    def test_create_performance_snapshot(self, test_db_session):
        """Test creating a performance snapshot record."""
        # Create portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create performance snapshot
        snapshot = PerformanceSnapshotTable(
            portfolio_id="portfolio_123",
            entity_type="portfolio",
            snapshot_date=date(2024, 1, 31),
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            start_value=Decimal("45000.00"),
            end_value=Decimal("47500.00"),
            total_return=Decimal("2500.00"),
            total_return_pct=Decimal("5.56")
        )
        
        test_db_session.add(snapshot)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved = test_db_session.query(PerformanceSnapshotTable).filter_by(
            portfolio_id="portfolio_123"
        ).first()
        assert retrieved is not None
        assert retrieved.entity_type == "portfolio"
        assert retrieved.snapshot_date == date(2024, 1, 31)
        assert retrieved.total_return == Decimal("2500.00")
        assert retrieved.dividends_received == Decimal("0")  # Default value
    
    def test_performance_snapshot_portfolio_relationship(self, test_db_session):
        """Test relationship between performance snapshot and portfolio."""
        # Create portfolio
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        # Create performance snapshot
        snapshot = PerformanceSnapshotTable(
            portfolio_id="portfolio_123",
            entity_type="portfolio",
            snapshot_date=date(2024, 1, 31),
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            start_value=Decimal("45000.00"),
            end_value=Decimal("47500.00"),
            total_return=Decimal("2500.00"),
            total_return_pct=Decimal("5.56")
        )
        test_db_session.add(snapshot)
        test_db_session.commit()
        
        # Test relationship
        retrieved_snapshot = test_db_session.query(PerformanceSnapshotTable).filter_by(
            portfolio_id="portfolio_123"
        ).first()
        assert retrieved_snapshot.portfolio.id == "portfolio_123"
        
        retrieved_portfolio = test_db_session.query(PortfolioTable).filter_by(id="portfolio_123").first()
        assert len(retrieved_portfolio.performance_snapshots) == 1
        assert retrieved_portfolio.performance_snapshots[0].entity_type == "portfolio"


class TestDatabaseConstraints:
    """Test database constraints and relationships."""
    
    def test_cascade_delete_portfolio_pies(self, test_db_session):
        """Test that deleting a portfolio cascades to pies."""
        # Create portfolio with pie
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        pie = PieTable(
            id="pie_123",
            portfolio_id="portfolio_123",
            name="Tech Growth Pie",
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        test_db_session.add(pie)
        test_db_session.commit()
        
        # Verify pie exists
        assert test_db_session.query(PieTable).filter_by(id="pie_123").first() is not None
        
        # Delete portfolio
        test_db_session.delete(portfolio)
        test_db_session.commit()
        
        # Verify pie was also deleted
        assert test_db_session.query(PieTable).filter_by(id="pie_123").first() is None
    
    def test_cascade_delete_pie_positions(self, test_db_session):
        """Test that deleting a pie cascades to positions."""
        # Create portfolio, pie, and position
        portfolio = PortfolioTable(
            id="portfolio_123",
            user_id="user_456"
        )
        test_db_session.add(portfolio)
        test_db_session.commit()
        
        pie = PieTable(
            id="pie_123",
            portfolio_id="portfolio_123",
            name="Tech Growth Pie",
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        test_db_session.add(pie)
        test_db_session.commit()
        
        position = PositionTable(
            pie_id="pie_123",
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10"),
            average_price=Decimal("150"),
            current_price=Decimal("155"),
            market_value=Decimal("1550"),
            unrealized_pnl=Decimal("50"),
            unrealized_pnl_pct=Decimal("3.33"),
            asset_type=AssetTypeEnum.STOCK
        )
        test_db_session.add(position)
        test_db_session.commit()
        
        # Verify position exists
        assert test_db_session.query(PositionTable).filter_by(symbol="AAPL").first() is not None
        
        # Delete pie
        test_db_session.delete(pie)
        test_db_session.commit()
        
        # Verify position was also deleted
        assert test_db_session.query(PositionTable).filter_by(symbol="AAPL").first() is None