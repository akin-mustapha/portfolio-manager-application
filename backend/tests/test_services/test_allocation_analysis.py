"""
Tests for allocation and diversification analysis functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.services.calculations_service import CalculationsService
from app.models.position import Position
from app.models.enums import AssetType


@pytest.fixture
def sample_positions():
    """Create sample positions for testing."""
    return [
        Position(
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
        ),
        Position(
            symbol="GOOGL",
            name="Alphabet Inc.",
            quantity=Decimal('5'),
            average_price=Decimal('2500.00'),
            current_price=Decimal('2600.00'),
            market_value=Decimal('13000.00'),
            unrealized_pnl=Decimal('500.00'),
            unrealized_pnl_pct=Decimal('4.00'),
            sector="Technology",
            industry="Internet Software & Services",
            country="US",
            asset_type=AssetType.STOCK
        ),
        Position(
            symbol="JNJ",
            name="Johnson & Johnson",
            quantity=Decimal('20'),
            average_price=Decimal('170.00'),
            current_price=Decimal('175.00'),
            market_value=Decimal('3500.00'),
            unrealized_pnl=Decimal('100.00'),
            unrealized_pnl_pct=Decimal('2.94'),
            sector="Healthcare",
            industry="Pharmaceuticals",
            country="US",
            asset_type=AssetType.STOCK
        ),
        Position(
            symbol="ASML",
            name="ASML Holding N.V.",
            quantity=Decimal('3'),
            average_price=Decimal('600.00'),
            current_price=Decimal('650.00'),
            market_value=Decimal('1950.00'),
            unrealized_pnl=Decimal('150.00'),
            unrealized_pnl_pct=Decimal('8.33'),
            sector="Technology",
            industry="Semiconductors",
            country="Netherlands",
            asset_type=AssetType.STOCK
        ),
        Position(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            quantity=Decimal('25'),
            average_price=Decimal('400.00'),
            current_price=Decimal('420.00'),
            market_value=Decimal('10500.00'),
            unrealized_pnl=Decimal('500.00'),
            unrealized_pnl_pct=Decimal('5.00'),
            sector="Diversified",
            industry="Exchange Traded Fund",
            country="US",
            asset_type=AssetType.ETF
        )
    ]


@pytest.fixture
def calc_service():
    """Create calculations service instance."""
    return CalculationsService()


def test_sector_allocation_calculation(calc_service, sample_positions):
    """Test sector allocation calculation."""
    allocation = calc_service._calculate_sector_allocation(sample_positions)
    
    # Total value: 1600 + 13000 + 3500 + 1950 + 10500 = 30550
    # Technology: (1600 + 13000 + 1950) / 30550 * 100 = 54.17%
    # Healthcare: 3500 / 30550 * 100 = 11.46%
    # Diversified: 10500 / 30550 * 100 = 34.37%
    
    assert "Technology" in allocation
    assert "Healthcare" in allocation
    assert "Diversified" in allocation
    
    # Check approximate percentages (allowing for rounding)
    assert abs(float(allocation["Technology"]) - 54.17) < 0.1
    assert abs(float(allocation["Healthcare"]) - 11.46) < 0.1
    assert abs(float(allocation["Diversified"]) - 34.37) < 0.1


def test_industry_allocation_calculation(calc_service, sample_positions):
    """Test industry allocation calculation."""
    allocation = calc_service._calculate_industry_allocation(sample_positions)
    
    assert "Consumer Electronics" in allocation
    assert "Internet Software & Services" in allocation
    assert "Pharmaceuticals" in allocation
    assert "Semiconductors" in allocation
    assert "Exchange Traded Fund" in allocation
    
    # Check that all percentages sum to 100
    total_percentage = sum(float(pct) for pct in allocation.values())
    assert abs(total_percentage - 100.0) < 0.01


def test_country_allocation_calculation(calc_service, sample_positions):
    """Test country allocation calculation."""
    allocation = calc_service._calculate_country_allocation(sample_positions)
    
    assert "US" in allocation
    assert "Netherlands" in allocation
    
    # US should have majority allocation
    us_allocation = float(allocation["US"])
    netherlands_allocation = float(allocation["Netherlands"])
    
    assert us_allocation > 90  # Should be > 90%
    assert netherlands_allocation < 10  # Should be < 10%


def test_diversification_score_calculation(calc_service, sample_positions):
    """Test diversification score calculation."""
    scores = calc_service.calculate_diversification_score(sample_positions)
    
    assert "overall_score" in scores
    assert "sector_diversification" in scores
    assert "industry_diversification" in scores
    assert "geographical_diversification" in scores
    assert "asset_type_diversification" in scores
    assert "position_count_score" in scores
    
    # All scores should be between 0 and 100
    for score_name, score_value in scores.items():
        assert 0 <= float(score_value) <= 100
    
    # With 5 positions, position count score should be 50
    assert float(scores["position_count_score"]) == 50.0


def test_concentration_analysis(calc_service, sample_positions):
    """Test concentration risk analysis."""
    analysis = calc_service.calculate_concentration_analysis(sample_positions)
    
    assert "herfindahl_index" in analysis
    assert "concentration_level" in analysis
    assert "top_holdings" in analysis
    assert "concentration_buckets" in analysis
    
    # Check top holdings structure
    top_holdings = analysis["top_holdings"]
    assert len(top_holdings) == 5  # Should have all 5 positions
    
    # First holding should be GOOGL (highest value)
    assert top_holdings[0]["symbol"] == "GOOGL"
    assert top_holdings[0]["rank"] == 1
    
    # Check concentration buckets
    buckets = analysis["concentration_buckets"]
    assert "top_1" in buckets
    assert "top_5" in buckets
    assert "top_10" in buckets


def test_comprehensive_allocation_analysis(calc_service, sample_positions):
    """Test comprehensive allocation analysis."""
    analysis = calc_service.calculate_comprehensive_allocation_analysis(sample_positions)
    
    assert "allocations" in analysis
    assert "diversification" in analysis
    assert "concentration" in analysis
    assert "top_holdings" in analysis
    assert "summary" in analysis
    
    # Check allocations structure
    allocations = analysis["allocations"]
    assert "sector" in allocations
    assert "industry" in allocations
    assert "country" in allocations
    assert "asset_type" in allocations
    
    # Check summary
    summary = analysis["summary"]
    assert summary["total_positions"] == 5
    assert float(summary["total_value"]) == 30550.0


def test_allocation_drift_detection(calc_service, sample_positions):
    """Test allocation drift detection."""
    # Define target allocations
    target_allocations = {
        "sector": {
            "Technology": Decimal('50.0'),
            "Healthcare": Decimal('20.0'),
            "Diversified": Decimal('30.0')
        },
        "country": {
            "US": Decimal('90.0'),
            "Netherlands": Decimal('10.0')
        }
    }
    
    drift_analysis = calc_service.detect_allocation_drift(
        sample_positions, 
        target_allocations, 
        Decimal('5.0')
    )
    
    assert "drift_detected" in drift_analysis
    assert "category_drifts" in drift_analysis
    assert "recommendations" in drift_analysis
    
    # Check category drifts
    category_drifts = drift_analysis["category_drifts"]
    assert "sector" in category_drifts
    assert "country" in category_drifts


def test_empty_positions_handling(calc_service):
    """Test handling of empty positions list."""
    empty_positions = []
    
    # Should not raise errors and return appropriate defaults
    allocation = calc_service._calculate_sector_allocation(empty_positions)
    assert allocation == {}
    
    diversification = calc_service.calculate_diversification_score(empty_positions)
    assert float(diversification["overall_score"]) == 0.0
    
    concentration = calc_service.calculate_concentration_analysis(empty_positions)
    assert concentration["concentration_level"] == "Low"
    assert len(concentration["top_holdings"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])