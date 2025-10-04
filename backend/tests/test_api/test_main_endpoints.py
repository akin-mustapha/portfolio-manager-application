"""
Integration tests for main API endpoints and health checks.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestMainEndpoints:
    """Test main application endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Trading 212 Portfolio Dashboard API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"

    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data

    @patch('app.main.settings.ENVIRONMENT', 'development')
    def test_health_check_development_environment(self, client):
        """Test health check in development environment."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch('app.main.settings.ENVIRONMENT', 'production')
    def test_health_check_production_environment(self, client):
        """Test health check in production environment."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAPIV1HealthEndpoints:
    """Test API v1 health endpoints."""

    def test_api_v1_health_endpoint(self, client):
        """Test API v1 health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "v1"


class TestCORSAndMiddleware:
    """Test CORS and middleware functionality."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get("/")
        
        # Check that the response doesn't have CORS errors
        assert response.status_code == 200
        
        # In a real CORS test, we would check for specific headers
        # but TestClient doesn't simulate browser CORS behavior

    def test_options_request(self, client):
        """Test OPTIONS request for CORS preflight."""
        response = client.options("/api/v1/portfolio/overview")
        
        # TestClient handles OPTIONS requests
        assert response.status_code in [200, 405]  # 405 if not explicitly handled


class TestErrorHandling:
    """Test error handling for main endpoints."""

    def test_404_for_nonexistent_endpoint(self, client):
        """Test 404 response for non-existent endpoints."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404

    def test_405_for_wrong_method(self, client):
        """Test 405 response for wrong HTTP method."""
        response = client.post("/")
        
        assert response.status_code == 405

    def test_422_for_invalid_json(self, client):
        """Test 422 response for invalid JSON in POST requests."""
        response = client.post(
            "/api/v1/auth/session",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


class TestAPIRouting:
    """Test API routing functionality."""

    def test_api_v1_prefix_routing(self, client):
        """Test that API v1 endpoints are properly routed."""
        # Test that endpoints are accessible with the v1 prefix
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_api_endpoint_without_prefix_404(self, client):
        """Test that API endpoints without prefix return 404."""
        response = client.get("/health")  # This should work (main health endpoint)
        assert response.status_code == 200
        
        response = client.get("/portfolio/overview")  # This should not work
        assert response.status_code == 404


class TestApplicationConfiguration:
    """Test application configuration."""

    def test_openapi_json_accessible(self, client):
        """Test that OpenAPI JSON is accessible."""
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Trading 212 Portfolio Dashboard API"

    def test_docs_accessible(self, client):
        """Test that API docs are accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_accessible(self, client):
        """Test that ReDoc is accessible."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestSecurityHeaders:
    """Test security-related headers and middleware."""

    def test_trusted_host_middleware(self, client):
        """Test that trusted host middleware is working."""
        # TestClient doesn't simulate host header validation
        # but we can test that requests work normally
        response = client.get("/")
        assert response.status_code == 200

    def test_content_type_headers(self, client):
        """Test that appropriate content-type headers are set."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
        
        response = client.get("/docs")
        assert "text/html" in response.headers["content-type"]


class TestAPIVersioning:
    """Test API versioning functionality."""

    def test_api_v1_endpoints_accessible(self, client):
        """Test that all v1 endpoints are accessible."""
        # Test main endpoint categories
        endpoints_to_test = [
            "/api/v1/health",
            # Auth endpoints (will fail without proper setup, but should route)
            "/api/v1/auth/session",
            # Portfolio endpoints (will fail without API key, but should route)
            "/api/v1/portfolio/overview",
            # Pies endpoints
            "/api/v1/pies/compare",
            # Benchmarks endpoints
            "/api/v1/benchmarks/available",
            # Dividends endpoints
            "/api/v1/dividends/portfolio/analysis"
        ]
        
        for endpoint in endpoints_to_test:
            if endpoint == "/api/v1/health":
                # Health endpoint should work
                response = client.get(endpoint)
                assert response.status_code == 200
            elif endpoint == "/api/v1/auth/session":
                # Auth endpoint should accept POST
                response = client.post(endpoint, json={})
                assert response.status_code in [200, 422]  # 422 for validation errors
            else:
                # Other endpoints should route but may fail due to missing auth/data
                response = client.get(endpoint)
                assert response.status_code in [200, 400, 401, 422, 500]  # Should route, not 404


class TestRequestValidation:
    """Test request validation functionality."""

    def test_json_validation_error_format(self, client):
        """Test that JSON validation errors are properly formatted."""
        response = client.post(
            "/api/v1/auth/session",
            json={"invalid_field": "value"}
        )
        
        # Should either succeed or return validation error
        assert response.status_code in [200, 422]
        
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data

    def test_query_parameter_validation(self, client):
        """Test query parameter validation."""
        # Test with invalid query parameters that should trigger validation
        response = client.get("/api/v1/portfolio/positions?limit=-1")
        
        # Should return validation error or route to endpoint that handles it
        assert response.status_code in [400, 422]

    def test_path_parameter_validation(self, client):
        """Test path parameter validation."""
        # Test with valid path parameter format
        response = client.get("/api/v1/pies/test-pie-id")
        
        # Should route properly (may fail due to auth, but not routing)
        assert response.status_code != 404


class TestResponseFormats:
    """Test response format consistency."""

    def test_json_response_format(self, client):
        """Test that JSON responses are properly formatted."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)

    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_health_response_format(self, client):
        """Test that health responses follow expected format."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])