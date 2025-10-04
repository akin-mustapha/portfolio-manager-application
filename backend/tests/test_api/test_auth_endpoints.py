"""
Integration tests for authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import redis

from app.main import app
from app.models.auth import (
    SessionCreate, SessionResponse, TokenRefresh, TokenResponse,
    Trading212APISetup, Trading212APIResponse, SessionInfo, APIKeyValidation
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.hset.return_value = True
    mock_redis.expire.return_value = True
    mock_redis.exists.return_value = True
    mock_redis.hgetall.return_value = {
        "session_id": "test-session-id",
        "created_at": "2024-01-15T10:30:00",
        "last_activity": "2024-01-15T10:30:00",
        "session_name": "Test Session",
        "trading212_connected": "false"
    }
    mock_redis.delete.return_value = True
    mock_redis.hdel.return_value = True
    return mock_redis


class TestSessionEndpoints:
    """Test session management endpoints."""

    @patch('app.api.v1.endpoints.auth.get_redis')
    @patch('app.api.v1.endpoints.auth.generate_session_id')
    @patch('app.api.v1.endpoints.auth.create_access_token')
    @patch('app.api.v1.endpoints.auth.create_refresh_token')
    def test_create_session_success(self, mock_refresh_token, mock_access_token, 
                                  mock_session_id, mock_get_redis, client, mock_redis):
        """Test successful session creation."""
        # Setup mocks
        mock_get_redis.return_value = mock_redis
        mock_session_id.return_value = "test-session-id"
        mock_access_token.return_value = "test-access-token"
        mock_refresh_token.return_value = "test-refresh-token"
        
        # Test data
        session_data = {
            "session_name": "Test Session"
        }
        
        response = client.post("/api/v1/auth/session", json=session_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-id"
        assert data["access_token"] == "test-access-token"
        assert data["refresh_token"] == "test-refresh-token"
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "created_at" in data
        
        # Verify Redis calls
        mock_redis.hset.assert_called()
        mock_redis.expire.assert_called()

    @patch('app.api.v1.endpoints.auth.get_redis')
    @patch('app.api.v1.endpoints.auth.verify_refresh_token')
    @patch('app.api.v1.endpoints.auth.create_access_token')
    def test_refresh_token_success(self, mock_access_token, mock_verify_token, 
                                 mock_get_redis, client, mock_redis):
        """Test successful token refresh."""
        # Setup mocks
        mock_get_redis.return_value = mock_redis
        mock_verify_token.return_value = "test-session-id"
        mock_access_token.return_value = "new-access-token"
        
        # Test data
        token_data = {
            "refresh_token": "valid-refresh-token"
        }
        
        response = client.post("/api/v1/auth/refresh", json=token_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new-access-token"
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        
        # Verify Redis calls
        mock_redis.exists.assert_called()
        mock_redis.hset.assert_called()

    @patch('app.api.v1.endpoints.auth.get_redis')
    @patch('app.api.v1.endpoints.auth.verify_refresh_token')
    def test_refresh_token_invalid(self, mock_verify_token, mock_get_redis, client):
        """Test token refresh with invalid token."""
        mock_verify_token.return_value = None
        
        token_data = {
            "refresh_token": "invalid-refresh-token"
        }
        
        response = client.post("/api/v1/auth/refresh", json=token_data)
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    @patch('app.api.v1.endpoints.auth.get_current_session')
    def test_get_session_info_success(self, mock_get_session, client):
        """Test getting session info."""
        # Setup mock
        mock_get_session.return_value = {
            "session_id": "test-session-id",
            "created_at": "2024-01-15T10:30:00",
            "last_activity": "2024-01-15T10:30:00",
            "session_name": "Test Session",
            "trading212_connected": "true"
        }
        
        response = client.get("/api/v1/auth/session/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-id"
        assert data["trading212_connected"] is True
        assert data["session_name"] == "Test Session"

    @patch('app.api.v1.endpoints.auth.get_current_user_id')
    @patch('app.api.v1.endpoints.auth.get_redis')
    def test_update_session_info(self, mock_get_redis, mock_user_id, client, mock_redis):
        """Test updating session info."""
        # Setup mocks
        mock_user_id.return_value = "test-user-id"
        mock_get_redis.return_value = mock_redis
        
        update_data = {
            "session_name": "Updated Session Name"
        }
        
        response = client.put("/api/v1/auth/session/info", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "created_at" in data
        assert "last_activity" in data
        
        # Verify Redis calls
        mock_redis.hset.assert_called()

    @patch('app.api.v1.endpoints.auth.get_current_user_id')
    @patch('app.api.v1.endpoints.auth.get_redis')
    def test_delete_session(self, mock_get_redis, mock_user_id, client, mock_redis):
        """Test session deletion."""
        # Setup mocks
        mock_user_id.return_value = "test-user-id"
        mock_get_redis.return_value = mock_redis
        
        response = client.delete("/api/v1/auth/session")
        
        assert response.status_code == 200
        assert "Session deleted successfully" in response.json()["message"]
        
        # Verify Redis calls
        mock_redis.delete.assert_called()


class TestTrading212APIEndpoints:
    """Test Trading 212 API setup endpoints."""

    @patch('app.api.v1.endpoints.auth.get_current_user_id')
    @patch('app.api.v1.endpoints.auth.get_redis')
    @patch('app.api.v1.endpoints.auth.validate_trading212_api_key')
    @patch('app.api.v1.endpoints.auth.encrypt_api_key')
    def test_setup_trading212_api_success(self, mock_encrypt, mock_validate, 
                                        mock_get_redis, mock_user_id, client, mock_redis):
        """Test successful Trading 212 API setup."""
        # Setup mocks
        mock_user_id.return_value = "test-user-id"
        mock_get_redis.return_value = mock_redis
        mock_encrypt.return_value = "encrypted-api-key"
        mock_validate.return_value = APIKeyValidation(
            is_valid=True,
            account_id="test-account-id",
            account_type="equity",
            error_message=None
        )
        
        api_setup = {
            "api_key": "test-api-key",
            "validate_connection": True
        }
        
        response = client.post("/api/v1/auth/trading212/setup", json=api_setup)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Trading 212 API key configured successfully" in data["message"]
        assert data["account_info"]["account_id"] == "test-account-id"
        
        # Verify Redis calls
        mock_redis.hset.assert_called()

    @patch('app.api.v1.endpoints.auth.get_current_user_id')
    @patch('app.api.v1.endpoints.auth.get_redis')
    @patch('app.api.v1.endpoints.auth.validate_trading212_api_key')
    def test_setup_trading212_api_invalid_key(self, mock_validate, mock_get_redis, 
                                            mock_user_id, client):
        """Test Trading 212 API setup with invalid key."""
        # Setup mocks
        mock_user_id.return_value = "test-user-id"
        mock_validate.return_value = APIKeyValidation(
            is_valid=False,
            error_message="Invalid API key"
        )
        
        api_setup = {
            "api_key": "invalid-api-key",
            "validate_connection": True
        }
        
        response = client.post("/api/v1/auth/trading212/setup", json=api_setup)
        
        assert response.status_code == 400
        assert "Invalid Trading 212 API key" in response.json()["detail"]

    @patch('app.api.v1.endpoints.auth.validate_trading212_api_key')
    def test_validate_trading212_connection_success(self, mock_validate, client):
        """Test Trading 212 API validation."""
        # Setup mock
        mock_validate.return_value = APIKeyValidation(
            is_valid=True,
            account_id="test-account-id",
            account_type="equity",
            error_message=None
        )
        
        api_setup = {
            "api_key": "test-api-key"
        }
        
        response = client.post("/api/v1/auth/trading212/validate", json=api_setup)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["account_id"] == "test-account-id"
        assert data["account_type"] == "equity"

    @patch('app.api.v1.endpoints.auth.validate_trading212_api_key')
    def test_validate_trading212_connection_failure(self, mock_validate, client):
        """Test Trading 212 API validation failure."""
        # Setup mock
        mock_validate.return_value = APIKeyValidation(
            is_valid=False,
            error_message="Connection timeout"
        )
        
        api_setup = {
            "api_key": "test-api-key"
        }
        
        response = client.post("/api/v1/auth/trading212/validate", json=api_setup)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert data["error_message"] == "Connection timeout"

    @patch('app.api.v1.endpoints.auth.get_current_user_id')
    @patch('app.api.v1.endpoints.auth.get_redis')
    def test_remove_trading212_api(self, mock_get_redis, mock_user_id, client, mock_redis):
        """Test removing Trading 212 API key."""
        # Setup mocks
        mock_user_id.return_value = "test-user-id"
        mock_get_redis.return_value = mock_redis
        
        response = client.delete("/api/v1/auth/trading212/setup")
        
        assert response.status_code == 200
        assert "Trading 212 API key removed successfully" in response.json()["message"]
        
        # Verify Redis calls
        mock_redis.hdel.assert_called()
        mock_redis.hset.assert_called()


class TestAPIValidationFunction:
    """Test the Trading 212 API validation function."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.auth.httpx.AsyncClient')
    async def test_validate_trading212_api_key_success(self, mock_client):
        """Test successful API key validation."""
        from app.api.v1.endpoints.auth import validate_trading212_api_key
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test-account-id"}
        
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await validate_trading212_api_key("test-api-key")
        
        assert result.is_valid is True
        assert result.account_id == "test-account-id"
        assert result.account_type == "equity"
        assert result.error_message is None

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.auth.httpx.AsyncClient')
    async def test_validate_trading212_api_key_unauthorized(self, mock_client):
        """Test API key validation with unauthorized response."""
        from app.api.v1.endpoints.auth import validate_trading212_api_key
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await validate_trading212_api_key("invalid-api-key")
        
        assert result.is_valid is False
        assert "Invalid API key or unauthorized access" in result.error_message

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.auth.httpx.AsyncClient')
    async def test_validate_trading212_api_key_timeout(self, mock_client):
        """Test API key validation with timeout."""
        from app.api.v1.endpoints.auth import validate_trading212_api_key
        import httpx
        
        # Setup mock to raise timeout
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await validate_trading212_api_key("test-api-key")
        
        assert result.is_valid is False
        assert "Connection timeout" in result.error_message


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_create_session_missing_data(self, client):
        """Test session creation with missing data."""
        response = client.post("/api/v1/auth/session", json={})
        
        # Should still work as session_name is optional
        assert response.status_code in [200, 422]  # 422 if validation fails

    def test_refresh_token_missing_data(self, client):
        """Test token refresh with missing data."""
        response = client.post("/api/v1/auth/refresh", json={})
        
        assert response.status_code == 422  # Validation error

    def test_setup_trading212_missing_api_key(self, client):
        """Test Trading 212 setup with missing API key."""
        response = client.post("/api/v1/auth/trading212/setup", json={})
        
        assert response.status_code == 422  # Validation error

    def test_validate_trading212_missing_api_key(self, client):
        """Test Trading 212 validation with missing API key."""
        response = client.post("/api/v1/auth/trading212/validate", json={})
        
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__])