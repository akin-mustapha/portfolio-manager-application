"""
Pytest configuration and fixtures for testing.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import AssetType, RiskCategory, DividendType


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing."""
    return datetime(2024, 1, 15, 10, 30, 0)


@pytest.fixture
def sample_date():
    """Sample date for testing."""
    return date(2024, 1, 15)


@pytest.fixture
def sample_decimal():
    """Sample decimal for testing."""
    return Decimal('1234.56')


@pytest.fixture
def test_db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_position_data():
    """Sample position data for testing."""
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "quantity": Decimal("10.5"),
        "average_price": Decimal("150.25"),
        "current_price": Decimal("155.75"),
        "market_value": Decimal("1635.38"),
        "unrealized_pnl": Decimal("57.75"),
        "unrealized_pnl_pct": Decimal("3.66"),
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "country": "US",
        "currency": "USD",
        "asset_type": AssetType.STOCK
    }


@pytest.fixture
def sample_risk_metrics_data():
    """Sample risk metrics data for testing."""
    return {
        "volatility": Decimal("15.25"),
        "sharpe_ratio": Decimal("1.45"),
        "max_drawdown": Decimal("-8.75"),
        "beta": Decimal("1.15"),
        "alpha": Decimal("2.35"),
        "correlation": Decimal("0.85"),
        "tracking_error": Decimal("3.25"),
        "var_95": Decimal("-5.25"),
        "risk_category": RiskCategory.MEDIUM,
        "risk_score": Decimal("65.5")
    }


@pytest.fixture
def sample_dividend_data():
    """Sample dividend data for testing."""
    return {
        "symbol": "AAPL",
        "security_name": "Apple Inc.",
        "dividend_type": DividendType.CASH,
        "amount_per_share": Decimal("0.25"),
        "total_amount": Decimal("2.50"),
        "shares_held": Decimal("10"),
        "ex_dividend_date": date(2024, 1, 10),
        "payment_date": date(2024, 1, 25),
        "gross_amount": Decimal("2.50"),
        "tax_withheld": Decimal("0.00"),
        "net_amount": Decimal("2.50"),
        "currency": "USD",
        "is_reinvested": False
    }