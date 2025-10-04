#!/usr/bin/env python3
"""
Test script to validate Pydantic models work correctly.
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models import (
    AssetType, RiskCategory, DividendType,
    Portfolio, PortfolioMetrics, Pie, PieMetrics,
    Position, RiskMetrics, Dividend, HistoricalData, PricePoint
)


def test_position_model():
    """Test Position model creation and validation."""
    print("Testing Position model...")
    
    position = Position(
        symbol="AAPL",
        name="Apple Inc.",
        quantity=Decimal('10'),
        average_price=Decimal('150.00'),
        current_price=Decimal('160.00'),
        market_value=Decimal('1600.00'),
        unrealized_pnl=Decimal('100.00'),
        unrealized_pnl_pct=Decimal('6.67'),
        sector="Technology",
        industry="Consumer Electronics",
        country="US",
        asset_type=AssetType.STOCK
    )
    
    print(f"✓ Position created: {position.symbol} - ${position.market_value}")
    assert position.market_value == Decimal('1600.00')
    assert position.unrealized_pnl == Decimal('100.00')
    print("✓ Position validation passed")


def test_risk_metrics_model():
    """Test RiskMetrics model creation."""
    print("\nTesting RiskMetrics model...")
    
    risk_metrics = RiskMetrics(
        volatility=Decimal('15.5'),
        sharpe_ratio=Decimal('1.2'),
        max_drawdown=Decimal('-8.5'),
        beta=Decimal('1.1'),
        risk_category=RiskCategory.MEDIUM,
        risk_score=Decimal('65')
    )
    
    print(f"✓ RiskMetrics created: {risk_metrics.risk_category} risk, score {risk_metrics.risk_score}")
    assert risk_metrics.volatility == Decimal('15.5')
    print("✓ RiskMetrics validation passed")


def test_pie_model():
    """Test Pie model creation."""
    print("\nTesting Pie model...")
    
    # Create a position for the pie
    position = Position(
        symbol="SPY",
        name="SPDR S&P 500 ETF",
        quantity=Decimal('5'),
        average_price=Decimal('400.00'),
        current_price=Decimal('420.00'),
        market_value=Decimal('2100.00'),
        unrealized_pnl=Decimal('100.00'),
        unrealized_pnl_pct=Decimal('5.00'),
        asset_type=AssetType.ETF
    )
    
    # Create pie metrics
    pie_metrics = PieMetrics(
        total_value=Decimal('2100.00'),
        invested_amount=Decimal('2000.00'),
        total_return=Decimal('100.00'),
        total_return_pct=Decimal('5.00'),
        portfolio_weight=Decimal('50.0')
    )
    
    # Create the pie
    pie = Pie(
        id="pie_123",
        name="S&P 500 Pie",
        positions=[position],
        metrics=pie_metrics,
        created_at=datetime.utcnow()
    )
    
    print(f"✓ Pie created: {pie.name} with {pie.position_count} positions")
    assert pie.metrics.total_value == Decimal('2100.00')
    print("✓ Pie validation passed")


def test_portfolio_model():
    """Test Portfolio model creation."""
    print("\nTesting Portfolio model...")
    
    # Create portfolio metrics
    portfolio_metrics = PortfolioMetrics(
        total_value=Decimal('10000.00'),
        total_invested=Decimal('9500.00'),
        total_return=Decimal('500.00'),
        total_return_pct=Decimal('5.26')
    )
    
    # Create the portfolio
    portfolio = Portfolio(
        id="portfolio_123",
        user_id="user_456",
        name="My Portfolio",
        metrics=portfolio_metrics
    )
    
    print(f"✓ Portfolio created: {portfolio.name} - ${portfolio.metrics.total_value}")
    assert portfolio.metrics.total_return == Decimal('500.00')
    print("✓ Portfolio validation passed")


def test_dividend_model():
    """Test Dividend model creation."""
    print("\nTesting Dividend model...")
    
    dividend = Dividend(
        symbol="MSFT",
        security_name="Microsoft Corporation",
        dividend_type=DividendType.CASH,
        amount_per_share=Decimal('0.68'),
        total_amount=Decimal('68.00'),
        shares_held=Decimal('100'),
        ex_dividend_date=date(2024, 2, 15),
        payment_date=date(2024, 3, 14),
        gross_amount=Decimal('68.00'),
        net_amount=Decimal('68.00')
    )
    
    print(f"✓ Dividend created: {dividend.symbol} - ${dividend.total_amount}")
    assert dividend.total_amount == Decimal('68.00')
    print("✓ Dividend validation passed")


def test_historical_data_model():
    """Test HistoricalData model creation."""
    print("\nTesting HistoricalData model...")
    
    price_points = [
        PricePoint(
            price_date=date(2024, 1, 1),
            close_price=Decimal('100.00'),
            volume=1000000
        ),
        PricePoint(
            price_date=date(2024, 1, 2),
            close_price=Decimal('102.00'),
            volume=1200000
        )
    ]
    
    historical_data = HistoricalData(
        symbol="AAPL",
        name="Apple Inc.",
        price_history=price_points,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2)
    )
    
    print(f"✓ HistoricalData created: {historical_data.symbol} with {historical_data.data_points_count} points")
    assert historical_data.latest_price == Decimal('102.00')
    print("✓ HistoricalData validation passed")


def main():
    """Run all model tests."""
    print("Running Pydantic model tests...\n")
    
    try:
        test_position_model()
        test_risk_metrics_model()
        test_pie_model()
        test_portfolio_model()
        test_dividend_model()
        test_historical_data_model()
        
        print("\n🎉 All model tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)