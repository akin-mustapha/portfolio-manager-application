"""
Integration tests for benchmarks API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime

from app.main import app
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.benchmark import BenchmarkData, BenchmarkComparison, BenchmarkInfo
from app.services.benchmark_service import BenchmarkAPIError
from app.services.trading212_service import Trading212APIError


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_benchmark_info():
    """Create mock benchmark info."""
    return BenchmarkInfo(
        symbol="SPY",
        name="SPDR S&P 500 ETF Trust",
        description="Tracks the S&P 500 index",
        category="US Large Cap"
    )


@pytest.fixture
def mock_benchmark_data():
    """Create mock benchmark data."""
    return BenchmarkData(
        symbol="SPY",
        name="SPDR S&P 500 ETF Trust",
        data_points=[
            {"date": "2024-01-01", "value": 100.0},
            {"date": "2024-01-02", "value": 101.0},
            {"date": "2024-01-03", "value": 102.0}
        ],
        period="1y",
        last_updated=datetime.utcnow()
    )


@pytest.fixture
def mock_benchmark_comparison():
    """Create mock benchmark comparison."""
    return BenchmarkComparison(
        entity_name="Test Portfolio",
        benchmark_name="SPDR S&P 500 ETF Trust",
        period="1y",
        alpha=Decimal('2.5'),
        beta=Decimal('1.1'),
        correlation=Decimal('0.85'),
        tracking_error=Decimal('3.2'),
        outperforming=True,
        entity_return=Decimal('12.5'),
        benchmark_return=Decimal('10.0'),
        excess_return=Decimal('2.5')
    )


@pytest.fixture
def mock_portfolio():
    """Create mock portfolio."""
    return Portfolio(
        id="test-portfolio",
        user_id="test-user",
        name="Test Portfolio",
        pies=[],
        individual_positions=[],
        metrics=PortfolioMetrics(
            total_value=Decimal('10000.00'),
            total_invested=Decimal('9500.00'),
            total_return=Decimal('500.00'),
            total_return_pct=Decimal('5.26'),
            annualized_return=Decimal('6.2'),
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


class TestBenchmarkAvailabilityEndpoints:
    """Test benchmark availability endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_available_benchmarks_success(self, mock_service, client, mock_benchmark_info):
        """Test successful retrieval of available benchmarks."""
        # Setup mock
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.get_supported_benchmarks.return_value = {
            "SPY": mock_benchmark_info
        }
        
        response = client.get("/api/v1/benchmarks/available")
        
        assert response.status_code == 200
        data = response.json()
        assert "benchmarks" in data
        assert "total_count" in data
        assert len(data["benchmarks"]) == 1
        assert data["benchmarks"][0]["symbol"] == "SPY"

    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_available_benchmarks_service_error(self, mock_service, client):
        """Test available benchmarks with service error."""
        # Setup mock to raise exception
        mock_service.return_value.__aenter__.side_effect = Exception("Service error")
        
        response = client.get("/api/v1/benchmarks/available")
        
        assert response.status_code == 500
        assert "Failed to get available benchmarks" in response.json()["detail"]


class TestBenchmarkDataEndpoints:
    """Test benchmark data endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_benchmark_data_success(self, mock_service, mock_user_id, 
                                      client, mock_benchmark_info, mock_benchmark_data):
        """Test successful benchmark data retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.get_benchmark_info.return_value = mock_benchmark_info
        mock_service_instance.fetch_benchmark_data.return_value = mock_benchmark_data
        
        response = client.get("/api/v1/benchmarks/SPY/data?period=1y")
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "SPY"
        assert data["period"] == "1y"
        assert "data_points" in data

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_benchmark_data_not_found(self, mock_service, mock_user_id, client):
        """Test benchmark data retrieval for unsupported benchmark."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.get_benchmark_info.return_value = None
        
        response = client.get("/api/v1/benchmarks/INVALID/data")
        
        assert response.status_code == 404
        assert "not available" in response.json()["detail"]

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_benchmark_data_service_unavailable(self, mock_service, mock_user_id, 
                                                   client, mock_benchmark_info):
        """Test benchmark data retrieval when service is unavailable."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.get_benchmark_info.return_value = mock_benchmark_info
        mock_service_instance.fetch_benchmark_data.return_value = None
        
        response = client.get("/api/v1/benchmarks/SPY/data")
        
        assert response.status_code == 503
        assert "Failed to fetch data" in response.json()["detail"]

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_benchmark_data_api_error(self, mock_service, mock_user_id, client):
        """Test benchmark data retrieval with API error."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.get_benchmark_info.side_effect = BenchmarkAPIError("API Error")
        
        response = client.get("/api/v1/benchmarks/SPY/data")
        
        assert response.status_code == 400
        assert "Benchmark API error" in response.json()["detail"]


class TestBenchmarkComparisonEndpoints:
    """Test benchmark comparison endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_compare_portfolio_to_benchmark_success(self, mock_benchmark_service, mock_trading_service,
                                                   mock_api_key, mock_user_id, client, 
                                                   mock_portfolio, mock_benchmark_comparison):
        """Test successful portfolio to benchmark comparison."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(success=True)
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        # Benchmark service mock
        mock_benchmark_instance = Mock()
        mock_benchmark_service.return_value.__aenter__.return_value = mock_benchmark_instance
        mock_benchmark_instance.compare_portfolio_to_benchmark.return_value = mock_benchmark_comparison
        
        response = client.post("/api/v1/benchmarks/compare?benchmark_symbol=SPY&period=1y")
        
        assert response.status_code == 200
        data = response.json()
        assert data["entity_name"] == "Test Portfolio"
        assert data["benchmark_name"] == "SPDR S&P 500 ETF Trust"
        assert data["outperforming"] is True

    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    def test_compare_portfolio_to_benchmark_no_api_key(self, mock_api_key, client):
        """Test portfolio comparison without API key."""
        mock_api_key.return_value = None
        
        response = client.post("/api/v1/benchmarks/compare?benchmark_symbol=SPY")
        
        assert response.status_code == 400
        assert "API key not configured" in response.json()["detail"]

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    def test_compare_portfolio_to_benchmark_auth_failure(self, mock_trading_service, 
                                                        mock_api_key, mock_user_id, client):
        """Test portfolio comparison with authentication failure."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "invalid-api-key"
        
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(
            success=False, 
            message="Invalid API key"
        )
        
        response = client.post("/api/v1/benchmarks/compare?benchmark_symbol=SPY")
        
        assert response.status_code == 401
        assert "Trading 212 authentication failed" in response.json()["detail"]


class TestPieBenchmarkComparisonEndpoints:
    """Test pie benchmark comparison endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_compare_pies_to_benchmark_success(self, mock_benchmark_service, mock_trading_service,
                                             mock_api_key, mock_user_id, client, mock_portfolio):
        """Test successful pies to benchmark comparison."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(success=True)
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        # Benchmark service mock
        mock_benchmark_instance = Mock()
        mock_benchmark_service.return_value.__aenter__.return_value = mock_benchmark_instance
        mock_benchmark_instance.compare_pie_to_benchmark.return_value = BenchmarkComparison(
            entity_name="Test Pie",
            benchmark_name="SPDR S&P 500 ETF Trust",
            period="1y",
            alpha=Decimal('1.5'),
            beta=Decimal('1.0'),
            correlation=Decimal('0.9'),
            tracking_error=Decimal('2.5'),
            outperforming=True,
            entity_return=Decimal('11.5'),
            benchmark_return=Decimal('10.0'),
            excess_return=Decimal('1.5')
        )
        mock_benchmark_instance.get_benchmark_info.return_value = BenchmarkInfo(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            description="Tracks the S&P 500 index",
            category="US Large Cap"
        )
        
        response = client.post("/api/v1/benchmarks/compare/pies?benchmark_symbol=SPY&period=1y")
        
        assert response.status_code == 200
        data = response.json()
        assert data["comparison_period"] == "1y"
        assert "benchmark" in data
        assert "pie_comparisons" in data
        assert "summary" in data

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_compare_specific_pies_to_benchmark(self, mock_benchmark_service, mock_trading_service,
                                              mock_api_key, mock_user_id, client, mock_portfolio):
        """Test comparison of specific pies to benchmark."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(success=True)
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        # Benchmark service mock
        mock_benchmark_instance = Mock()
        mock_benchmark_service.return_value.__aenter__.return_value = mock_benchmark_instance
        mock_benchmark_instance.get_benchmark_info.return_value = BenchmarkInfo(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            description="Tracks the S&P 500 index",
            category="US Large Cap"
        )
        
        response = client.post("/api/v1/benchmarks/compare/pies?benchmark_symbol=SPY&pie_ids=pie1,pie2")
        
        assert response.status_code == 200
        data = response.json()
        assert "pie_comparisons" in data


class TestCustomBenchmarkEndpoints:
    """Test custom benchmark endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_create_custom_benchmark_success(self, mock_service, mock_user_id, client):
        """Test successful custom benchmark creation."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.create_custom_benchmark.return_value = Mock(
            dict=Mock(return_value={
                "id": "custom-benchmark-id",
                "name": "Custom Benchmark",
                "components": [
                    {"symbol": "SPY", "weight": 60.0},
                    {"symbol": "AGG", "weight": 40.0}
                ]
            })
        )
        
        response = client.post(
            "/api/v1/benchmarks/custom/create?name=Custom Benchmark&symbols=SPY:60,AGG:40"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Custom Benchmark"
        assert len(data["components"]) == 2

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_create_custom_benchmark_equal_weights(self, mock_service, mock_user_id, client):
        """Test custom benchmark creation with equal weights."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.create_custom_benchmark.return_value = Mock(
            dict=Mock(return_value={
                "id": "custom-benchmark-id",
                "name": "Equal Weight Benchmark",
                "components": [
                    {"symbol": "SPY", "weight": 50.0},
                    {"symbol": "AGG", "weight": 50.0}
                ]
            })
        )
        
        response = client.post(
            "/api/v1/benchmarks/custom/create?name=Equal Weight Benchmark&symbols=SPY,AGG"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["components"]) == 2

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_create_custom_benchmark_invalid_weights(self, mock_service, mock_user_id, client):
        """Test custom benchmark creation with invalid weights."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.create_custom_benchmark.side_effect = ValueError("Invalid weight")
        
        response = client.post(
            "/api/v1/benchmarks/custom/create?name=Invalid Benchmark&symbols=SPY:invalid"
        )
        
        assert response.status_code == 400
        assert "Invalid weight format" in response.json()["detail"]


class TestBenchmarkAnalysisEndpoints:
    """Test benchmark analysis endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_comprehensive_benchmark_analysis(self, mock_benchmark_service, mock_trading_service,
                                                 mock_api_key, mock_user_id, client, mock_portfolio):
        """Test comprehensive benchmark analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(success=True)
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        # Benchmark service mock
        mock_benchmark_instance = Mock()
        mock_benchmark_service.return_value.__aenter__.return_value = mock_benchmark_instance
        mock_benchmark_instance.compare_multiple_entities_to_benchmark.return_value = Mock(
            dict=Mock(return_value={
                "portfolio_comparison": {},
                "pie_comparisons": [],
                "summary": {}
            })
        )
        
        response = client.post("/api/v1/benchmarks/analysis/comprehensive?benchmark_symbol=SPY")
        
        assert response.status_code == 200
        data = response.json()
        assert "portfolio_comparison" in data
        assert "pie_comparisons" in data
        assert "summary" in data

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_get_benchmark_recommendations(self, mock_benchmark_service, mock_trading_service,
                                         mock_api_key, mock_user_id, client, mock_portfolio):
        """Test benchmark recommendations."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(success=True)
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        # Benchmark service mock
        mock_benchmark_instance = Mock()
        mock_benchmark_service.return_value.__aenter__.return_value = mock_benchmark_instance
        mock_benchmark_instance.get_benchmark_selection_recommendations.return_value = [
            Mock(dict=Mock(return_value={
                "symbol": "SPY",
                "name": "SPDR S&P 500 ETF Trust",
                "reason": "Good match for US equity exposure",
                "confidence": 0.9
            }))
        ]
        
        response = client.get("/api/v1/benchmarks/recommendations")
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "total_count" in data
        assert "portfolio_summary" in data


class TestBenchmarkSearchEndpoints:
    """Test benchmark search endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_search_benchmarks_success(self, mock_service, mock_user_id, client):
        """Test successful benchmark search."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.search_benchmarks.return_value = [
            Mock(dict=Mock(return_value={
                "symbol": "SPY",
                "name": "SPDR S&P 500 ETF Trust",
                "description": "Tracks the S&P 500 index",
                "category": "US Large Cap"
            }))
        ]
        
        response = client.get("/api/v1/benchmarks/search?query=S&P 500")
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "total_count" in data
        assert data["query"] == "S&P 500"

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_search_benchmarks_service_error(self, mock_service, mock_user_id, client):
        """Test benchmark search with service error."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service.return_value.__aenter__.side_effect = Exception("Search error")
        
        response = client.get("/api/v1/benchmarks/search?query=test")
        
        assert response.status_code == 500
        assert "Failed to search benchmarks" in response.json()["detail"]


class TestBenchmarkCacheEndpoints:
    """Test benchmark cache endpoints."""

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_clear_benchmark_cache_all(self, mock_service, mock_user_id, client):
        """Test clearing all benchmark cache."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.clear_benchmark_cache = AsyncMock()
        
        response = client.delete("/api/v1/benchmarks/cache")
        
        assert response.status_code == 200
        data = response.json()
        assert "Cache cleared for all benchmarks" in data["message"]
        assert data["cleared_symbol"] is None

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_clear_benchmark_cache_specific(self, mock_service, mock_user_id, client):
        """Test clearing specific benchmark cache."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_service_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_service_instance
        mock_service_instance.clear_benchmark_cache = AsyncMock()
        
        response = client.delete("/api/v1/benchmarks/cache?symbol=SPY")
        
        assert response.status_code == 200
        data = response.json()
        assert "Cache cleared for SPY" in data["message"]
        assert data["cleared_symbol"] == "SPY"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_query_parameters(self, client):
        """Test endpoints with invalid query parameters."""
        # Test invalid period
        response = client.get("/api/v1/benchmarks/SPY/data?period=invalid")
        assert response.status_code == 422
        
        # Test missing benchmark symbol
        response = client.post("/api/v1/benchmarks/compare")
        assert response.status_code == 422

    def test_missing_required_parameters(self, client):
        """Test endpoints with missing required parameters."""
        # Test custom benchmark creation without name
        response = client.post("/api/v1/benchmarks/custom/create?symbols=SPY,AGG")
        assert response.status_code == 422
        
        # Test search without query
        response = client.get("/api/v1/benchmarks/search")
        assert response.status_code == 422

    @patch('app.api.v1.endpoints.benchmarks.get_current_user_id')
    @patch('app.api.v1.endpoints.benchmarks.get_trading212_api_key')
    @patch('app.api.v1.endpoints.benchmarks.Trading212Service')
    @patch('app.api.v1.endpoints.benchmarks.BenchmarkService')
    def test_service_error_handling(self, mock_benchmark_service, mock_trading_service,
                                  mock_api_key, mock_user_id, client):
        """Test handling of service errors."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        mock_api_key.return_value = "test-api-key"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.authenticate.return_value = Mock(success=True)
        mock_trading_instance.fetch_portfolio_data.side_effect = Trading212APIError("API Error")
        
        response = client.post("/api/v1/benchmarks/compare?benchmark_symbol=SPY")
        
        assert response.status_code == 400
        assert "Trading 212 API error" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__])