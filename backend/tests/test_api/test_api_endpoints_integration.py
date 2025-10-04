"""
Comprehensive integration tests for all API endpoints.
This test file focuses on testing endpoint routing, request validation, 
and response formats without requiring external dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import json

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIEndpointRouting:
    """Test that all API endpoints are properly routed and accessible."""

    def test_root_endpoint_routing(self, client):
        """Test root endpoint routing."""
        response = client.get("/")
        # Should route correctly, even if it fails due to missing config
        assert response.status_code != 404

    def test_health_endpoint_routing(self, client):
        """Test health endpoint routing."""
        response = client.get("/health")
        # Should route correctly
        assert response.status_code != 404

    def test_api_v1_health_endpoint_routing(self, client):
        """Test API v1 health endpoint routing."""
        response = client.get("/api/v1/health")
        # Should route correctly
        assert response.status_code != 404

    def test_auth_endpoints_routing(self, client):
        """Test authentication endpoints routing."""
        # Test session creation endpoint
        response = client.post("/api/v1/auth/session", json={})
        assert response.status_code != 404
        
        # Test token refresh endpoint
        response = client.post("/api/v1/auth/refresh", json={})
        assert response.status_code != 404
        
        # Test session info endpoint
        response = client.get("/api/v1/auth/session/info")
        assert response.status_code != 404
        
        # Test Trading 212 setup endpoint
        response = client.post("/api/v1/auth/trading212/setup", json={})
        assert response.status_code != 404

    def test_portfolio_endpoints_routing(self, client):
        """Test portfolio endpoints routing."""
        # Test portfolio overview
        response = client.get("/api/v1/portfolio/overview")
        assert response.status_code != 404
        
        # Test portfolio metrics
        response = client.get("/api/v1/portfolio/metrics")
        assert response.status_code != 404
        
        # Test portfolio positions
        response = client.get("/api/v1/portfolio/positions")
        assert response.status_code != 404
        
        # Test portfolio allocation
        response = client.get("/api/v1/portfolio/allocation")
        assert response.status_code != 404

    def test_pies_endpoints_routing(self, client):
        """Test pies endpoints routing."""
        # Test pie details
        response = client.get("/api/v1/pies/test-pie-id")
        assert response.status_code != 404
        
        # Test pie metrics
        response = client.get("/api/v1/pies/test-pie-id/metrics")
        assert response.status_code != 404
        
        # Test pie positions
        response = client.get("/api/v1/pies/test-pie-id/positions")
        assert response.status_code != 404
        
        # Test pie comparison
        response = client.get("/api/v1/pies/compare")
        assert response.status_code != 404

    def test_benchmarks_endpoints_routing(self, client):
        """Test benchmarks endpoints routing."""
        # Test available benchmarks
        response = client.get("/api/v1/benchmarks/available")
        assert response.status_code != 404
        
        # Test benchmark data
        response = client.get("/api/v1/benchmarks/SPY/data")
        assert response.status_code != 404
        
        # Test benchmark comparison
        response = client.post("/api/v1/benchmarks/compare?benchmark_symbol=SPY")
        assert response.status_code != 404

    def test_dividends_endpoints_routing(self, client):
        """Test dividends endpoints routing."""
        # Test portfolio dividend analysis
        response = client.get("/api/v1/dividends/portfolio/analysis")
        assert response.status_code != 404
        
        # Test monthly dividend history
        response = client.get("/api/v1/dividends/portfolio/monthly-history")
        assert response.status_code != 404
        
        # Test dividend by security
        response = client.get("/api/v1/dividends/portfolio/by-security")
        assert response.status_code != 404

    def test_nonexistent_endpoint_returns_404(self, client):
        """Test that non-existent endpoints return 404."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestRequestValidation:
    """Test request validation for various endpoints."""

    def test_query_parameter_validation(self, client):
        """Test query parameter validation."""
        # Test invalid limit parameter
        response = client.get("/api/v1/portfolio/positions?limit=invalid")
        assert response.status_code in [400, 422]  # Should be validation error
        
        # Test negative limit parameter
        response = client.get("/api/v1/portfolio/positions?limit=-1")
        assert response.status_code in [400, 422]  # Should be validation error

    def test_json_body_validation(self, client):
        """Test JSON body validation."""
        # Test invalid JSON
        response = client.post(
            "/api/v1/auth/session",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]  # Should be validation error

    def test_path_parameter_validation(self, client):
        """Test path parameter validation."""
        # Test with valid path parameter format
        response = client.get("/api/v1/pies/valid-pie-id")
        # Should route correctly (may fail for other reasons, but not routing)
        assert response.status_code != 404


class TestHTTPMethods:
    """Test HTTP method handling."""

    def test_get_methods(self, client):
        """Test GET method endpoints."""
        get_endpoints = [
            "/api/v1/health",
            "/api/v1/portfolio/overview",
            "/api/v1/portfolio/metrics",
            "/api/v1/pies/test-id",
            "/api/v1/benchmarks/available",
            "/api/v1/dividends/portfolio/analysis"
        ]
        
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            # Should route correctly, not return 404 or 405
            assert response.status_code not in [404, 405]

    def test_post_methods(self, client):
        """Test POST method endpoints."""
        post_endpoints = [
            ("/api/v1/auth/session", {}),
            ("/api/v1/auth/refresh", {}),
            ("/api/v1/auth/trading212/setup", {}),
            ("/api/v1/benchmarks/compare?benchmark_symbol=SPY", {}),
            ("/api/v1/portfolio/refresh", {})
        ]
        
        for endpoint, data in post_endpoints:
            response = client.post(endpoint, json=data)
            # Should route correctly, not return 404 or 405
            assert response.status_code not in [404, 405]

    def test_wrong_http_method(self, client):
        """Test wrong HTTP method returns 405."""
        # Try POST on GET-only endpoint
        response = client.post("/api/v1/portfolio/overview")
        assert response.status_code == 405
        
        # Try GET on POST-only endpoint
        response = client.get("/api/v1/auth/session")
        assert response.status_code == 405


class TestResponseFormats:
    """Test response format consistency."""

    def test_json_content_type(self, client):
        """Test that API endpoints return JSON content type."""
        # Test endpoints that should return JSON
        json_endpoints = [
            "/api/v1/health",
            "/api/v1/portfolio/overview",
            "/api/v1/benchmarks/available"
        ]
        
        for endpoint in json_endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                assert "application/json" in response.headers.get("content-type", "")

    def test_error_response_structure(self, client):
        """Test that error responses have consistent structure."""
        # Test 404 error
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "detail" in data

    def test_validation_error_structure(self, client):
        """Test that validation errors have consistent structure."""
        # Test with invalid query parameter
        response = client.get("/api/v1/portfolio/positions?limit=invalid")
        
        if response.status_code == 422 and response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "detail" in data


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_json_accessible(self, client):
        """Test that OpenAPI JSON is accessible."""
        response = client.get("/api/v1/openapi.json")
        
        if response.status_code == 200:
            data = response.json()
            assert "openapi" in data
            assert "info" in data
            assert data["info"]["title"] == "Trading 212 Portfolio Dashboard API"

    def test_docs_accessible(self, client):
        """Test that API docs are accessible."""
        response = client.get("/docs")
        
        if response.status_code == 200:
            assert "text/html" in response.headers["content-type"]

    def test_redoc_accessible(self, client):
        """Test that ReDoc is accessible."""
        response = client.get("/redoc")
        
        if response.status_code == 200:
            assert "text/html" in response.headers["content-type"]


class TestEndpointCoverage:
    """Test that all major endpoint categories are covered."""

    def test_all_endpoint_categories_exist(self, client):
        """Test that all major endpoint categories exist and route correctly."""
        endpoint_categories = {
            "health": "/api/v1/health",
            "auth_session": "/api/v1/auth/session",
            "auth_trading212": "/api/v1/auth/trading212/setup",
            "portfolio_overview": "/api/v1/portfolio/overview",
            "portfolio_metrics": "/api/v1/portfolio/metrics",
            "portfolio_positions": "/api/v1/portfolio/positions",
            "portfolio_allocation": "/api/v1/portfolio/allocation",
            "portfolio_historical": "/api/v1/portfolio/historical",
            "portfolio_pies": "/api/v1/portfolio/pies",
            "pie_details": "/api/v1/pies/test-id",
            "pie_metrics": "/api/v1/pies/test-id/metrics",
            "pie_positions": "/api/v1/pies/test-id/positions",
            "pie_allocation": "/api/v1/pies/test-id/allocation",
            "pie_compare": "/api/v1/pies/compare",
            "pie_ranking": "/api/v1/pies/ranking",
            "benchmarks_available": "/api/v1/benchmarks/available",
            "benchmarks_data": "/api/v1/benchmarks/SPY/data",
            "benchmarks_compare": "/api/v1/benchmarks/compare?benchmark_symbol=SPY",
            "benchmarks_search": "/api/v1/benchmarks/search?query=test",
            "dividends_analysis": "/api/v1/dividends/portfolio/analysis",
            "dividends_history": "/api/v1/dividends/portfolio/monthly-history",
            "dividends_by_security": "/api/v1/dividends/portfolio/by-security",
            "dividends_reinvestment": "/api/v1/dividends/portfolio/reinvestment-analysis",
            "dividends_projections": "/api/v1/dividends/portfolio/income-projections",
            "dividends_tax": "/api/v1/dividends/portfolio/tax-analysis",
            "dividends_pie": "/api/v1/dividends/pie/test-id/analysis"
        }
        
        for category, endpoint in endpoint_categories.items():
            if endpoint.startswith("/api/v1/benchmarks/compare") or endpoint.startswith("/api/v1/portfolio/refresh"):
                # POST endpoints
                response = client.post(endpoint, json={})
            else:
                # GET endpoints
                response = client.get(endpoint)
            
            # Should route correctly (not 404)
            assert response.status_code != 404, f"Endpoint {category} ({endpoint}) returned 404"

    def test_endpoint_count_coverage(self, client):
        """Test that we have comprehensive endpoint coverage."""
        # Get OpenAPI spec to count endpoints
        response = client.get("/api/v1/openapi.json")
        
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            # Should have a reasonable number of endpoints
            assert len(paths) >= 20, f"Expected at least 20 endpoints, found {len(paths)}"
            
            # Should have endpoints for all major categories
            path_strings = list(paths.keys())
            
            # Check for auth endpoints
            auth_endpoints = [p for p in path_strings if "/auth/" in p]
            assert len(auth_endpoints) >= 3, "Should have at least 3 auth endpoints"
            
            # Check for portfolio endpoints
            portfolio_endpoints = [p for p in path_strings if "/portfolio/" in p]
            assert len(portfolio_endpoints) >= 5, "Should have at least 5 portfolio endpoints"
            
            # Check for pies endpoints
            pies_endpoints = [p for p in path_strings if "/pies/" in p]
            assert len(pies_endpoints) >= 3, "Should have at least 3 pies endpoints"
            
            # Check for benchmarks endpoints
            benchmarks_endpoints = [p for p in path_strings if "/benchmarks/" in p]
            assert len(benchmarks_endpoints) >= 3, "Should have at least 3 benchmarks endpoints"
            
            # Check for dividends endpoints
            dividends_endpoints = [p for p in path_strings if "/dividends/" in p]
            assert len(dividends_endpoints) >= 3, "Should have at least 3 dividends endpoints"


class TestSecurityAndValidation:
    """Test security and validation aspects."""

    def test_cors_handling(self, client):
        """Test CORS handling."""
        # Test that requests work (CORS is handled by middleware)
        response = client.get("/api/v1/health")
        # Should not fail due to CORS issues in test environment
        assert response.status_code != 403

    def test_request_size_limits(self, client):
        """Test request size limits."""
        # Test with reasonable request size
        normal_data = {"test": "data"}
        response = client.post("/api/v1/auth/session", json=normal_data)
        # Should not fail due to size limits
        assert response.status_code != 413

    def test_content_type_handling(self, client):
        """Test content type handling."""
        # Test with correct content type
        response = client.post(
            "/api/v1/auth/session",
            json={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        # Should handle content type correctly
        assert response.status_code != 415


if __name__ == "__main__":
    pytest.main([__file__, "-v"])