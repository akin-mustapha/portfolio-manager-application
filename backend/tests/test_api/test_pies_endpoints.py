"""
Integration tests for pies API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime

from app.main import app
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.position import Position
from app.models.pie import Pie, PieMetrics
from app.models.enums import AssetType, RiskCategory
from app.models.risk import RiskMetrics
from app.services.trading212_service import Trading212APIError


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_position():
    """Create mock position."""
    return Position(
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


@pytest.fixture
def mock_pie_metrics():
    """Create mock pie metrics."""
    return PieMetrics(
        total_value=Decimal('2000.00'),
        invested_amount=Decimal('1900.00'),
        total_return=Decimal('100.00'),
        total_return_pct=Decimal('5.26'),
        portfolio_weight=Decimal('40.0'),
        portfolio_contribution=Decimal('2.1'),
        dividend_yield=Decimal('2.5'),
        risk_metrics=RiskMetrics(
            volatility=Decimal('12.5'),
            sharpe_ratio=Decimal('1.2'),
            max_drawdown=Decimal('-6.5'),
            beta=Decimal('1.1'),
            alpha=Decimal('1.5'),
            correlation=Decimal('0.8'),
            tracking_error=Decimal('2.5'),
            var_95=Decimal('-4.5'),
            risk_category=RiskCategory.MEDIUM,
            risk_score=Decimal('60.0')
        )
    )


@pytest.fixture
def mock_pie(mock_position, mock_pie_metrics):
    """Create mock pie."""
    return Pie(
        id="test-pie-id",
        name="Test Pie",
        description="Test pie description",
        positions=[mock_position],
        metrics=mock_pie_metrics,
        last_updated=datetime.utcnow()
    )


@pytest.fixture
def mock_portfolio(mock_pie):
    """Create mock portfolio with pie."""
    return Portfolio(
        id="test-portfolio",
        user_id="test-user",
        name="Test Portfolio",
        pies=[mock_pie],
        individual_positions=[],
        metrics=PortfolioMetrics(
            total_value=Decimal('5000.00'),
            total_invested=Decimal('4800.00'),
            total_return=Decimal('200.00'),
            total_return_pct=Decimal('4.17'),
            annualized_return=Decimal('5.2'),
            sector_allocation={},
            industry_allocation={},
            country_allocation={},
            asset_type_allocation={},
            diversification_score=Decimal('75.0'),
            concentration_risk=Decimal('25.0'),
            top_10_weight=Decimal('100.0'),
            dividend_yield=Decimal('2.5')
        ),
        last_updated=datetime.utcnow()
    )


class TestPieDetailsEndpoints:
    """Test pie details endpoints."""

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_details_success(self, mock_service, mock_api_key, 
                                   mock_user_id, client, mock_portfolio):
        """Test successful pie details retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-pie-id"
        assert data["name"] == "Test Pie"
        assert "metrics" in data
        assert "positions" in data

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_details_not_found(self, mock_service, mock_api_key, 
                                     mock_user_id, client, mock_portfolio):
        """Test pie details retrieval for non-existent pie."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/non-existent-pie-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    def test_get_pie_details_no_api_key(self, mock_api_key, client):
        """Test pie details without API key."""
        mock_api_key.return_value = None
        
        response = client.get("/api/v1/pies/test-pie-id")
        
        assert response.status_code == 400
        assert "API key not configured" in response.json()["detail"]

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_details_auth_failure(self, mock_service, mock_api_key, 
                                        mock_user_id, client):
        """Test pie details with authentication failure."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "invalid-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(
            success=False, 
            message="Invalid API key"
        )
        
        response = client.get("/api/v1/pies/test-pie-id")
        
        assert response.status_code == 401
        assert "Trading 212 authentication failed" in response.json()["detail"]


class TestPieMetricsEndpoints:
    """Test pie metrics endpoints."""

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_metrics_success(self, mock_service, mock_api_key, 
                                   mock_user_id, client, mock_portfolio):
        """Test successful pie metrics retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "total_return_pct" in data
        assert "portfolio_weight" in data
        assert "risk_metrics" in data
        assert float(data["total_value"]) == 2000.00

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_metrics_not_found(self, mock_service, mock_api_key, 
                                     mock_user_id, client, mock_portfolio):
        """Test pie metrics retrieval for non-existent pie."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/non-existent-pie-id/metrics")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestPiePositionsEndpoints:
    """Test pie positions endpoints."""

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_positions_success(self, mock_service, mock_api_key, 
                                     mock_user_id, client, mock_portfolio):
        """Test successful pie positions retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/positions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_positions_with_sorting(self, mock_service, mock_api_key, 
                                          mock_user_id, client, mock_portfolio):
        """Test pie positions with sorting parameters."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/positions?limit=10&sort_by=symbol&sort_order=asc")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_top_holdings_success(self, mock_service, mock_api_key, 
                                        mock_user_id, client, mock_portfolio):
        """Test successful pie top holdings retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/top-holdings?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


class TestPieAllocationEndpoints:
    """Test pie allocation endpoints."""

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_allocation_by_position(self, mock_service, mock_api_key, 
                                          mock_user_id, client, mock_portfolio):
        """Test pie allocation by position."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/allocation?breakdown_type=position")
        
        assert response.status_code == 200
        data = response.json()
        assert data["pie_id"] == "test-pie-id"
        assert data["breakdown_type"] == "position"
        assert "allocations" in data
        assert "total_value" in data

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_allocation_by_sector(self, mock_service, mock_api_key, 
                                        mock_user_id, client, mock_portfolio):
        """Test pie allocation by sector."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/allocation?breakdown_type=sector")
        
        assert response.status_code == 200
        data = response.json()
        assert data["breakdown_type"] == "sector"
        assert "allocations" in data

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_allocation_invalid_type(self, mock_service, mock_api_key, 
                                           mock_user_id, client, mock_portfolio):
        """Test pie allocation with invalid breakdown type."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        response = client.get("/api/v1/pies/test-pie-id/allocation?breakdown_type=invalid")
        
        assert response.status_code == 422  # Validation error


class TestPieComparisonEndpoints:
    """Test pie comparison endpoints."""

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_compare_pies_success(self, mock_service, mock_api_key, 
                                mock_user_id, client, mock_portfolio):
        """Test successful pie comparison."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/compare?metric=total_return_pct&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["comparison_metric"] == "total_return_pct"
        assert "pies" in data
        assert "total_pies" in data

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_compare_specific_pies(self, mock_service, mock_api_key, 
                                 mock_user_id, client, mock_portfolio):
        """Test comparison of specific pies."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/compare?pie_ids=test-pie-id&metric=total_return_pct")
        
        assert response.status_code == 200
        data = response.json()
        assert "pies" in data

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_ranking_success(self, mock_service, mock_api_key, 
                                   mock_user_id, client, mock_portfolio):
        """Test successful pie ranking."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/ranking?rank_by=total_return_pct&order=desc")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ranking_metric"] == "total_return_pct"
        assert data["ranking_order"] == "desc"
        assert "rankings" in data
        assert "total_pies" in data

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_get_pie_ranking_ascending(self, mock_service, mock_api_key, 
                                     mock_user_id, client, mock_portfolio):
        """Test pie ranking in ascending order."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/ranking?rank_by=volatility&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ranking_order"] == "asc"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_pie_id_format(self, client):
        """Test endpoints with invalid pie ID format."""
        # Test with empty pie ID
        response = client.get("/api/v1/pies//metrics")
        assert response.status_code == 404

    def test_invalid_query_parameters(self, client):
        """Test endpoints with invalid query parameters."""
        # Test invalid limit
        response = client.get("/api/v1/pies/test-pie-id/positions?limit=0")
        assert response.status_code == 422
        
        # Test invalid sort order
        response = client.get("/api/v1/pies/test-pie-id/positions?sort_order=invalid")
        assert response.status_code == 422
        
        # Test invalid breakdown type
        response = client.get("/api/v1/pies/test-pie-id/allocation?breakdown_type=invalid")
        assert response.status_code == 422

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_trading212_api_error_handling(self, mock_service, mock_api_key, 
                                         mock_user_id, client):
        """Test handling of Trading 212 API errors."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.side_effect = Trading212APIError("API Error")
        
        response = client.get("/api/v1/pies/test-pie-id")
        
        assert response.status_code == 400
        assert "Trading 212 API error" in response.json()["detail"]

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_general_exception_handling(self, mock_service, mock_api_key, 
                                      mock_user_id, client):
        """Test handling of general exceptions."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.side_effect = Exception("General error")
        
        response = client.get("/api/v1/pies/test-pie-id")
        
        assert response.status_code == 500
        assert "Failed to fetch pie details" in response.json()["detail"]


class TestPieAllocationCalculations:
    """Test pie allocation calculation logic."""

    @patch('app.api.v1.endpoints.pies.get_current_user_id')
    @patch('app.api.v1.endpoints.pies.get_trading212_api_key')
    @patch('app.api.v1.endpoints.pies.Trading212Service')
    def test_pie_allocation_calculations(self, mock_service, mock_api_key, 
                                       mock_user_id, client, mock_portfolio):
        """Test that pie allocation calculations are correct."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/pies/test-pie-id/allocation?breakdown_type=position")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that allocations add up to 100% (within rounding tolerance)
        total_percentage = sum(allocation["percentage"] for allocation in data["allocations"])
        assert abs(total_percentage - 100.0) < 0.01  # Allow for rounding errors
        
        # Check that values match the pie's total value
        total_value = sum(allocation["value"] for allocation in data["allocations"])
        assert abs(total_value - float(data["total_value"])) < 0.01


if __name__ == "__main__":
    pytest.main([__file__])