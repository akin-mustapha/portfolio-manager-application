"""
Integration tests for portfolio API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
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
def mock_risk_metrics():
    """Create mock risk metrics."""
    return RiskMetrics(
        volatility=Decimal('15.25'),
        sharpe_ratio=Decimal('1.45'),
        max_drawdown=Decimal('-8.75'),
        beta=Decimal('1.15'),
        alpha=Decimal('2.35'),
        correlation=Decimal('0.85'),
        tracking_error=Decimal('3.25'),
        var_95=Decimal('-5.25'),
        risk_category=RiskCategory.MEDIUM,
        risk_score=Decimal('65.5')
    )


@pytest.fixture
def mock_portfolio_metrics(mock_risk_metrics):
    """Create mock portfolio metrics."""
    return PortfolioMetrics(
        total_value=Decimal('5000.00'),
        total_invested=Decimal('4800.00'),
        total_return=Decimal('200.00'),
        total_return_pct=Decimal('4.17'),
        annualized_return=Decimal('5.2'),
        risk_metrics=mock_risk_metrics,
        sector_allocation={
            "Technology": Decimal('60.0'),
            "Healthcare": Decimal('40.0')
        },
        industry_allocation={
            "Consumer Electronics": Decimal('60.0'),
            "Pharmaceuticals": Decimal('40.0')
        },
        country_allocation={
            "US": Decimal('100.0')
        },
        asset_type_allocation={
            "STOCK": Decimal('100.0')
        },
        diversification_score=Decimal('75.0'),
        concentration_risk=Decimal('25.0'),
        top_10_weight=Decimal('100.0'),
        dividend_yield=Decimal('2.5')
    )


@pytest.fixture
def mock_portfolio(mock_position, mock_portfolio_metrics):
    """Create mock portfolio."""
    return Portfolio(
        id="test-portfolio",
        user_id="test-user",
        name="Test Portfolio",
        pies=[],
        individual_positions=[mock_position],
        metrics=mock_portfolio_metrics,
        last_updated=datetime.utcnow()
    )


class TestPortfolioOverviewEndpoints:
    """Test portfolio overview endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.get_redis')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_overview_success(self, mock_service, mock_redis, 
                                          mock_api_key, mock_user_id, client, mock_portfolio):
        """Test successful portfolio overview retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-portfolio"
        assert data["user_id"] == "test-user"
        assert "metrics" in data
        assert "individual_positions" in data

    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    def test_get_portfolio_overview_no_api_key(self, mock_api_key, client):
        """Test portfolio overview without API key."""
        mock_api_key.return_value = None
        
        response = client.get("/api/v1/portfolio/overview")
        
        assert response.status_code == 400
        assert "API key not configured" in response.json()["detail"]

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_overview_auth_failure(self, mock_service, mock_api_key, 
                                                mock_user_id, client):
        """Test portfolio overview with authentication failure."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "invalid-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(
            success=False, 
            message="Invalid API key"
        )
        
        response = client.get("/api/v1/portfolio/overview")
        
        assert response.status_code == 401
        assert "Trading 212 authentication failed" in response.json()["detail"]

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_overview_api_error(self, mock_service, mock_api_key, 
                                            mock_user_id, client):
        """Test portfolio overview with Trading 212 API error."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.side_effect = Trading212APIError("API Error")
        
        response = client.get("/api/v1/portfolio/overview")
        
        assert response.status_code == 400
        assert "Trading 212 API error" in response.json()["detail"]


class TestPortfolioMetricsEndpoints:
    """Test portfolio metrics endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_metrics_success(self, mock_service, mock_api_key, 
                                         mock_user_id, client, mock_portfolio):
        """Test successful portfolio metrics retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "total_return_pct" in data
        assert "risk_metrics" in data
        assert float(data["total_value"]) == 5000.00


class TestPortfolioPositionsEndpoints:
    """Test portfolio positions endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_positions_success(self, mock_service, mock_api_key, 
                                           mock_user_id, client, mock_portfolio):
        """Test successful portfolio positions retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/positions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_positions_with_pagination(self, mock_service, mock_api_key, 
                                                   mock_user_id, client, mock_portfolio):
        """Test portfolio positions with pagination parameters."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/positions?limit=10&offset=0&sort_by=symbol&sort_order=asc")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_top_holdings_success(self, mock_service, mock_api_key, 
                                    mock_user_id, client, mock_portfolio):
        """Test successful top holdings retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/top-holdings?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


class TestPortfolioAllocationEndpoints:
    """Test portfolio allocation endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_allocation_sector(self, mock_service, mock_api_key, 
                                           mock_user_id, client, mock_portfolio):
        """Test portfolio allocation by sector."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/allocation?breakdown_type=sector")
        
        assert response.status_code == 200
        data = response.json()
        assert data["breakdown_type"] == "sector"
        assert "allocations" in data
        assert "total_value" in data

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_allocation_invalid_type(self, mock_service, mock_api_key, 
                                                  mock_user_id, client, mock_portfolio):
        """Test portfolio allocation with invalid breakdown type."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        response = client.get("/api/v1/portfolio/allocation?breakdown_type=invalid")
        
        assert response.status_code == 422  # Validation error


class TestPortfolioHistoricalEndpoints:
    """Test portfolio historical data endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_historical_data(self, mock_service, mock_api_key, 
                                         mock_user_id, client, mock_portfolio):
        """Test portfolio historical data retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/historical?period=1y&data_type=value")
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "1y"
        assert data["data_type"] == "value"
        assert "current_value" in data


class TestPortfolioRefreshEndpoints:
    """Test portfolio refresh endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.get_redis')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_refresh_portfolio_data_success(self, mock_service, mock_redis, 
                                          mock_api_key, mock_user_id, client, mock_portfolio):
        """Test successful portfolio data refresh."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.refresh_portfolio_data.return_value = mock_portfolio
        
        response = client.post("/api/v1/portfolio/refresh")
        
        assert response.status_code == 200
        data = response.json()
        assert "Portfolio data refreshed successfully" in data["message"]
        assert "last_updated" in data
        assert "total_value" in data


class TestPortfolioPiesEndpoints:
    """Test portfolio pies endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_pies_success(self, mock_service, mock_api_key, 
                                      mock_user_id, client, mock_portfolio):
        """Test successful portfolio pies retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/pies")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_get_portfolio_pies_exclude_positions(self, mock_service, mock_api_key, 
                                                mock_user_id, client, mock_portfolio):
        """Test portfolio pies retrieval excluding positions."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/portfolio/pies?include_positions=false")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPortfolioAnalysisEndpoints:
    """Test portfolio analysis endpoints."""

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    @patch('app.api.v1.endpoints.portfolio.CalculationsService')
    def test_get_diversification_analysis(self, mock_calc_service, mock_service, 
                                        mock_api_key, mock_user_id, client, mock_portfolio):
        """Test diversification analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance.calculate_diversification_score.return_value = {
            "overall_score": 75.0,
            "sector_diversification": 60.0,
            "industry_diversification": 65.0
        }
        
        response = client.get("/api/v1/portfolio/diversification")
        
        assert response.status_code == 200
        data = response.json()
        assert "diversification_scores" in data
        assert "total_positions" in data

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    @patch('app.api.v1.endpoints.portfolio.CalculationsService')
    def test_get_concentration_analysis(self, mock_calc_service, mock_service, 
                                      mock_api_key, mock_user_id, client, mock_portfolio):
        """Test concentration analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance.calculate_concentration_analysis.return_value = {
            "herfindahl_index": 0.25,
            "concentration_level": "Medium",
            "top_holdings": []
        }
        
        response = client.get("/api/v1/portfolio/concentration")
        
        assert response.status_code == 200
        data = response.json()
        assert "herfindahl_index" in data
        assert "concentration_level" in data

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    @patch('app.api.v1.endpoints.portfolio.CalculationsService')
    def test_detect_allocation_drift(self, mock_calc_service, mock_service, 
                                   mock_api_key, mock_user_id, client, mock_portfolio):
        """Test allocation drift detection."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance.detect_allocation_drift.return_value = {
            "drift_detected": True,
            "category_drifts": {},
            "recommendations": []
        }
        
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


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_query_parameters(self, client):
        """Test endpoints with invalid query parameters."""
        # Test invalid limit
        response = client.get("/api/v1/portfolio/positions?limit=0")
        assert response.status_code == 422
        
        # Test invalid sort order
        response = client.get("/api/v1/portfolio/positions?sort_order=invalid")
        assert response.status_code == 422
        
        # Test invalid period
        response = client.get("/api/v1/portfolio/historical?period=invalid")
        assert response.status_code == 422

    @patch('app.api.v1.endpoints.portfolio.get_current_user_id')
    @patch('app.api.v1.endpoints.portfolio.get_trading212_api_key')
    @patch('app.api.v1.endpoints.portfolio.Trading212Service')
    def test_service_exception_handling(self, mock_service, mock_api_key, 
                                      mock_user_id, client):
        """Test handling of service exceptions."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.authenticate.return_value = Mock(success=True)
        mock_service_instance.fetch_portfolio_data.side_effect = Exception("Service error")
        
        response = client.get("/api/v1/portfolio/overview")
        
        assert response.status_code == 500
        assert "Failed to fetch portfolio data" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__])