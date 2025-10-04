"""
Integration tests for allocation and diversification API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from decimal import Decimal

from app.main import app
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.position import Position
from app.models.pie import Pie, PieMetrics
from app.models.enums import AssetType


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_portfolio():
    """Create mock portfolio for testing."""
    positions = [
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
        )
    ]
    
    metrics = PortfolioMetrics(
        total_value=Decimal('5100.00'),
        total_invested=Decimal('4900.00'),
        total_return=Decimal('200.00'),
        total_return_pct=Decimal('4.08'),
        sector_allocation={
            "Technology": Decimal('31.37'),
            "Healthcare": Decimal('68.63')
        },
        industry_allocation={
            "Consumer Electronics": Decimal('31.37'),
            "Pharmaceuticals": Decimal('68.63')
        },
        country_allocation={
            "US": Decimal('100.00')
        },
        asset_type_allocation={
            "STOCK": Decimal('100.00')
        },
        diversification_score=Decimal('50.0'),
        concentration_risk=Decimal('25.0'),
        top_10_weight=Decimal('100.0')
    )
    
    return Portfolio(
        id="test-portfolio",
        user_id="test-user",
        pies=[],
        individual_positions=positions,
        metrics=metrics
    )


@patch('app.api.v1.endpoints.portfolio.get_current_user_id')
@patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
@patch('app.api.v1.endpoints.portfolio.Trading212Service')
def test_get_portfolio_allocation_endpoint(mock_service, mock_api_key, mock_user_id, client, mock_portfolio):
    """Test portfolio allocation endpoint."""
    # Setup mocks
    mock_user_id.return_value = "test-user"
    mock_api_key.return_value = "test-api-key"
    
    mock_service_instance = Mock()
    mock_service.return_value.__aenter__.return_value = mock_service_instance
    mock_service_instance.authenticate.return_value = Mock(success=True)
    mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
    
    # Test sector allocation
    response = client.get("/api/v1/portfolio/allocation?breakdown_type=sector")
    assert response.status_code == 200
    
    data = response.json()
    assert data["breakdown_type"] == "sector"
    assert "allocations" in data
    assert len(data["allocations"]) == 2
    
    # Check allocation data
    allocations = {item["category"]: item["percentage"] for item in data["allocations"]}
    assert "Technology" in allocations
    assert "Healthcare" in allocations


@patch('app.api.v1.endpoints.portfolio.get_current_user_id')
@patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
@patch('app.api.v1.endpoints.portfolio.Trading212Service')
def test_get_diversification_analysis_endpoint(mock_service, mock_api_key, mock_user_id, client, mock_portfolio):
    """Test diversification analysis endpoint."""
    # Setup mocks
    mock_user_id.return_value = "test-user"
    mock_api_key.return_value = "test-api-key"
    
    mock_service_instance = Mock()
    mock_service.return_value.__aenter__.return_value = mock_service_instance
    mock_service_instance.authenticate.return_value = Mock(success=True)
    mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
    
    response = client.get("/api/v1/portfolio/diversification")
    assert response.status_code == 200
    
    data = response.json()
    assert "diversification_scores" in data
    assert "total_positions" in data
    assert "total_value" in data
    
    scores = data["diversification_scores"]
    assert "overall_score" in scores
    assert "sector_diversification" in scores
    assert "industry_diversification" in scores


@patch('app.api.v1.endpoints.portfolio.get_current_user_id')
@patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
@patch('app.api.v1.endpoints.portfolio.Trading212Service')
def test_get_concentration_analysis_endpoint(mock_service, mock_api_key, mock_user_id, client, mock_portfolio):
    """Test concentration analysis endpoint."""
    # Setup mocks
    mock_user_id.return_value = "test-user"
    mock_api_key.return_value = "test-api-key"
    
    mock_service_instance = Mock()
    mock_service.return_value.__aenter__.return_value = mock_service_instance
    mock_service_instance.authenticate.return_value = Mock(success=True)
    mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
    
    response = client.get("/api/v1/portfolio/concentration")
    assert response.status_code == 200
    
    data = response.json()
    assert "herfindahl_index" in data
    assert "concentration_level" in data
    assert "top_holdings" in data
    assert "concentration_buckets" in data


@patch('app.api.v1.endpoints.portfolio.get_current_user_id')
@patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
@patch('app.api.v1.endpoints.portfolio.Trading212Service')
def test_get_comprehensive_allocation_analysis_endpoint(mock_service, mock_api_key, mock_user_id, client, mock_portfolio):
    """Test comprehensive allocation analysis endpoint."""
    # Setup mocks
    mock_user_id.return_value = "test-user"
    mock_api_key.return_value = "test-api-key"
    
    mock_service_instance = Mock()
    mock_service.return_value.__aenter__.return_value = mock_service_instance
    mock_service_instance.authenticate.return_value = Mock(success=True)
    mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
    
    response = client.get("/api/v1/portfolio/allocation-analysis")
    assert response.status_code == 200
    
    data = response.json()
    assert "allocations" in data
    assert "diversification" in data
    assert "concentration" in data
    assert "top_holdings" in data
    assert "summary" in data
    
    # Check allocations structure
    allocations = data["allocations"]
    assert "sector" in allocations
    assert "industry" in allocations
    assert "country" in allocations
    assert "asset_type" in allocations


@patch('app.api.v1.endpoints.portfolio.get_current_user_id')
@patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
@patch('app.api.v1.endpoints.portfolio.Trading212Service')
def test_detect_allocation_drift_endpoint(mock_service, mock_api_key, mock_user_id, client, mock_portfolio):
    """Test allocation drift detection endpoint."""
    # Setup mocks
    mock_user_id.return_value = "test-user"
    mock_api_key.return_value = "test-api-key"
    
    mock_service_instance = Mock()
    mock_service.return_value.__aenter__.return_value = mock_service_instance
    mock_service_instance.authenticate.return_value = Mock(success=True)
    mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
    
    # Test drift detection
    target_allocations = {
        "sector": {
            "Technology": 50.0,
            "Healthcare": 50.0
        }
    }
    
    response = client.post(
        "/api/v1/portfolio/allocation-drift?tolerance_pct=5.0",
        json=target_allocations
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "drift_detected" in data
    assert "category_drifts" in data
    assert "recommendations" in data


def test_allocation_endpoint_without_api_key(client):
    """Test allocation endpoint without API key."""
    with patch('app.api.v1.endpoints.portfolio.get_trading212_api_key', return_value=None):
        response = client.get("/api/v1/portfolio/allocation")
        assert response.status_code == 400
        assert "API key not configured" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__])