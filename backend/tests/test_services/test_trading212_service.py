"""
Integration tests for Trading 212 API service.

Tests authentication, data fetching, error handling, and rate limiting scenarios.
"""

import json
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

import httpx
import redis.asyncio as redis
from cryptography.fernet import Fernet

from app.services.trading212_service import (
    Trading212Service,
    Trading212APIError,
    AuthResult
)
from app.models.enums import AssetType


class TestTrading212ServiceAuthentication:
    """Test authentication functionality."""
    
    @pytest_asyncio.fixture
    async def service(self):
        """Create Trading212Service instance for testing."""
        service = Trading212Service(use_demo=True)
        await service._init_session()
        yield service
        await service._close_session()
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = True
        return mock_redis
    
    @pytest.fixture
    def valid_api_key(self):
        """Valid API key for testing."""
        return "test_api_key_12345"
    
    @pytest.fixture
    def mock_account_info_response(self):
        """Mock successful account info response."""
        return {
            "id": "test_account_123",
            "currencyCode": "USD",
            "cash": {"free": 1000.0, "total": 1000.0}
        }
    
    @pytest.mark.asyncio
    async def test_successful_authentication(self, service, valid_api_key, mock_account_info_response):
        """Test successful authentication with valid API key."""
        # Mock the HTTP request
        with patch.object(service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_account_info_response
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test authentication
            result = await service.authenticate(valid_api_key)
            
            # Verify result
            assert result.success is True
            assert result.message == "Authentication successful"
            assert result.expires_at is not None
            assert service.api_key == valid_api_key
            
            # Verify API call was made
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'GET'
            assert '/equity/account/info' in call_args[1]['url']
            assert call_args[1]['headers']['Authorization'] == valid_api_key
    
    @pytest.mark.asyncio
    async def test_authentication_with_invalid_credentials(self, service):
        """Test authentication failure with invalid API key."""
        invalid_key = "invalid_api_key"
        
        # Mock 401 response
        with patch.object(service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Invalid API key"}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test authentication
            result = await service.authenticate(invalid_key)
            
            # Verify result
            assert result.success is False
            assert "Authentication failed" in result.message
            assert result.expires_at is None
            assert service.api_key is None
    
    @pytest.mark.asyncio
    async def test_authentication_network_error(self, service, valid_api_key):
        """Test authentication failure due to network error."""
        # Mock network error
        with patch.object(service.session, 'request') as mock_request:
            mock_request.side_effect = httpx.RequestError("Network error")
            
            # Test authentication
            result = await service.authenticate(valid_api_key)
            
            # Verify result
            assert result.success is False
            assert "Network error" in result.message
            assert service.api_key is None
    
    @pytest.mark.asyncio
    async def test_authentication_with_redis_caching(self, service, valid_api_key, mock_account_info_response, mock_redis):
        """Test authentication with Redis caching enabled."""
        service.redis_client = mock_redis
        
        # Mock successful HTTP response
        with patch.object(service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_account_info_response
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test authentication
            result = await service.authenticate(valid_api_key)
            
            # Verify result
            assert result.success is True
            
            # Verify Redis caching was attempted
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args[0]
            assert call_args[0] == "trading212:encrypted_api_key"
            assert call_args[1] == 86400  # 24 hours
    
    @pytest.mark.asyncio
    async def test_load_stored_credentials(self, service, mock_redis):
        """Test loading previously stored credentials from Redis."""
        service.redis_client = mock_redis
        
        # Mock encrypted API key in Redis
        test_key = "test_api_key"
        encrypted_key = service._encrypt_api_key(test_key)
        mock_redis.get.return_value = encrypted_key.encode()
        
        # Test loading credentials
        result = await service.load_stored_credentials()
        
        # Verify result
        assert result is True
        assert service.api_key == test_key
        mock_redis.get.assert_called_once_with("trading212:encrypted_api_key")
    
    @pytest.mark.asyncio
    async def test_load_stored_credentials_not_found(self, service, mock_redis):
        """Test loading credentials when none are stored."""
        service.redis_client = mock_redis
        mock_redis.get.return_value = None
        
        # Test loading credentials
        result = await service.load_stored_credentials()
        
        # Verify result
        assert result is False
        assert service.api_key is None
    
    @pytest.mark.asyncio
    async def test_clear_credentials(self, service, mock_redis):
        """Test clearing stored credentials."""
        service.redis_client = mock_redis
        service.api_key = "test_key"
        
        # Test clearing credentials
        await service.clear_credentials()
        
        # Verify result
        assert service.api_key is None
        mock_redis.delete.assert_called_once_with("trading212:encrypted_api_key")


class TestTrading212ServiceDataFetching:
    """Test data fetching functionality."""
    
    @pytest_asyncio.fixture
    async def authenticated_service(self, mock_redis):
        """Create authenticated Trading212Service instance."""
        service = Trading212Service(use_demo=True)
        await service._init_session()
        service.redis_client = mock_redis
        service.api_key = "test_api_key"
        yield service
        await service._close_session()
    
    @pytest.fixture
    def mock_portfolio_response(self):
        """Mock portfolio data response."""
        return [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "quantity": 10.5,
                "averagePrice": 150.25,
                "currentPrice": 155.75,
                "marketValue": 1635.38,
                "ppl": 57.75,
                "pplPercent": 3.66,
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "country": "US",
                "currency": "USD",
                "type": "STOCK"
            }
        ]
    
    @pytest.fixture
    def mock_pies_response(self):
        """Mock pies data response."""
        return [
            {
                "id": "pie_123",
                "name": "Tech Growth",
                "description": "Technology growth stocks",
                "creationTime": "2024-01-01T00:00:00Z",
                "autoInvest": True,
                "instruments": ["AAPL", "GOOGL", "MSFT"]
            }
        ]
    
    @pytest.fixture
    def mock_dividends_response(self):
        """Mock dividends data response."""
        return {
            "items": [
                {
                    "ticker": "AAPL",
                    "amount": 2.50,
                    "amountInEuro": {"amount": 2.30, "currency": "EUR"},
                    "paidOn": "2024-01-15T00:00:00Z",
                    "type": "ORDINARY",
                    "quantity": 10,
                    "grossAmountPerShare": 0.25,
                    "withholdingTax": 0.0
                }
            ],
            "nextPagePath": None
        }
    
    @pytest.mark.asyncio
    async def test_get_account_info_success(self, authenticated_service, mock_redis):
        """Test successful account info retrieval."""
        mock_response_data = {
            "id": "account_123",
            "currencyCode": "USD",
            "cash": {"free": 1000.0}
        }
        
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test account info retrieval
            result = await authenticated_service.get_account_info()
            
            # Verify result
            assert result == mock_response_data
            assert result["id"] == "account_123"
            assert result["currencyCode"] == "USD"
    
    @pytest.mark.asyncio
    async def test_get_positions_success(self, authenticated_service, mock_portfolio_response):
        """Test successful positions retrieval."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_portfolio_response
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test positions retrieval
            result = await authenticated_service.get_positions()
            
            # Verify result
            assert result == mock_portfolio_response
            assert len(result) == 1
            assert result[0]["ticker"] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_get_pies_success(self, authenticated_service, mock_pies_response):
        """Test successful pies retrieval."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_pies_response
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test pies retrieval
            result = await authenticated_service.get_pies()
            
            # Verify result
            assert result == mock_pies_response
            assert len(result) == 1
            assert result[0]["id"] == "pie_123"
    
    @pytest.mark.asyncio
    async def test_get_dividends_success(self, authenticated_service, mock_dividends_response):
        """Test successful dividends retrieval."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_dividends_response
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Test dividends retrieval
            result = await authenticated_service.get_dividends()
            
            # Verify result
            assert result == mock_dividends_response
            assert len(result["items"]) == 1
            assert result["items"][0]["ticker"] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, authenticated_service, mock_redis):
        """Test Redis caching behavior for GET requests."""
        mock_response_data = {"test": "data"}
        cache_key = "trading212:/equity/account/info:2546219878"  # hash of None params
        
        # First request - cache miss
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # Mock cache miss
            mock_redis.get.return_value = None
            
            result = await authenticated_service.get_account_info()
            
            # Verify API was called and cache was written
            mock_request.assert_called_once()
            mock_redis.setex.assert_called_once()
        
        # Second request - cache hit
        mock_redis.reset_mock()
        mock_redis.get.return_value = json.dumps(mock_response_data).encode()
        
        with patch.object(authenticated_service.session, 'request') as mock_request:
            result = await authenticated_service.get_account_info()
            
            # Verify API was not called but cache was read
            mock_request.assert_not_called()
            mock_redis.get.assert_called_once()
            assert result == mock_response_data


class TestTrading212ServiceErrorHandling:
    """Test error handling scenarios."""
    
    @pytest_asyncio.fixture
    async def authenticated_service(self):
        """Create authenticated Trading212Service instance."""
        service = Trading212Service(use_demo=True)
        await service._init_session()
        service.api_key = "test_api_key"
        yield service
        await service._close_session()
    
    @pytest.mark.asyncio
    async def test_unauthenticated_request_error(self, authenticated_service):
        """Test error when making request without API key."""
        authenticated_service.api_key = None
        
        with pytest.raises(Trading212APIError) as exc_info:
            await authenticated_service.get_account_info()
        
        assert exc_info.value.error_type == "authentication_failure"
        assert "API key not set" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_401_authentication_error(self, authenticated_service):
        """Test handling of 401 authentication error."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Invalid API key"}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            with pytest.raises(Trading212APIError) as exc_info:
                await authenticated_service.get_account_info()
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.error_type == "authentication_failure"
            assert "Authentication failed" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_429_rate_limit_error(self, authenticated_service):
        """Test handling of 429 rate limit error."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int((datetime.utcnow() + timedelta(minutes=1)).timestamp()))
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(Trading212APIError) as exc_info:
                await authenticated_service.get_account_info()
            
            assert exc_info.value.status_code == 429
            assert exc_info.value.error_type == "rate_limit_exceeded"
            assert "Rate limit exceeded" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_503_service_unavailable_error(self, authenticated_service):
        """Test handling of 503 service unavailable error."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            with pytest.raises(Trading212APIError) as exc_info:
                await authenticated_service.get_account_info()
            
            assert exc_info.value.status_code == 503
            assert exc_info.value.error_type == "api_unavailable"
            assert "temporarily unavailable" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_generic_api_error(self, authenticated_service):
        """Test handling of generic API errors."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"message": "Bad request"}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            with pytest.raises(Trading212APIError) as exc_info:
                await authenticated_service.get_account_info()
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.error_type == "api_error"
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, authenticated_service):
        """Test handling of network errors."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_request.side_effect = httpx.RequestError("Connection failed")
            
            with pytest.raises(Trading212APIError) as exc_info:
                await authenticated_service.get_account_info()
            
            assert exc_info.value.error_type == "network_error"
            assert "Network error" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, authenticated_service):
        """Test handling of invalid JSON responses."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            # The service should handle JSON decode errors gracefully
            with pytest.raises((Trading212APIError, json.JSONDecodeError)):
                await authenticated_service.get_account_info()


class TestTrading212ServiceRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest_asyncio.fixture
    async def authenticated_service(self):
        """Create authenticated Trading212Service instance."""
        service = Trading212Service(use_demo=True)
        await service._init_session()
        service.api_key = "test_api_key"
        yield service
        await service._close_session()
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers_processing(self, authenticated_service):
        """Test processing of rate limit headers."""
        reset_time = datetime.utcnow() + timedelta(minutes=5)
        
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_response.headers = {
                "X-RateLimit-Remaining": "45",
                "X-RateLimit-Reset": str(int(reset_time.timestamp()))
            }
            mock_request.return_value = mock_response
            
            await authenticated_service.get_account_info()
            
            # Verify rate limit info was updated
            assert authenticated_service._requests_remaining == 45
            assert authenticated_service._rate_limit_reset is not None
    
    @pytest.mark.asyncio
    async def test_rate_limit_wait_behavior(self, authenticated_service):
        """Test waiting behavior when rate limit is exceeded."""
        # Set up rate limit exceeded state
        authenticated_service._requests_remaining = 0
        authenticated_service._rate_limit_reset = datetime.utcnow() + timedelta(seconds=1)
        
        with patch('asyncio.sleep') as mock_sleep:
            with patch.object(authenticated_service.session, 'request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"test": "data"}
                mock_response.headers = {}
                mock_request.return_value = mock_response
                
                await authenticated_service.get_account_info()
                
                # Verify sleep was called
                mock_sleep.assert_called_once()
                sleep_time = mock_sleep.call_args[0][0]
                assert 0 < sleep_time <= 1


class TestTrading212ServiceDataTransformation:
    """Test data transformation functionality."""
    
    @pytest_asyncio.fixture
    async def service(self):
        """Create Trading212Service instance."""
        service = Trading212Service(use_demo=True)
        await service._init_session()
        yield service
        await service._close_session()
    
    def test_transform_position_data_success(self, service):
        """Test successful position data transformation."""
        raw_position = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "quantity": 10.5,
            "averagePrice": 150.25,
            "currentPrice": 155.75,
            "marketValue": 1635.38,
            "ppl": 57.75,
            "pplPercent": 3.66,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "US",
            "currency": "USD",
            "type": "STOCK"
        }
        
        position = service._transform_position_data(raw_position)
        
        # Verify transformation
        assert position.symbol == "AAPL"
        assert position.name == "Apple Inc."
        assert position.quantity == Decimal("10.5")
        assert position.average_price == Decimal("150.25")
        assert position.current_price == Decimal("155.75")
        # Market value is calculated: quantity * current_price = 10.5 * 155.75 = 1635.375
        assert position.market_value == Decimal("1635.375")
        assert position.unrealized_pnl == Decimal("57.75")
        assert position.sector == "Technology"
        assert position.asset_type == AssetType.STOCK
    
    def test_transform_position_data_invalid(self, service):
        """Test position data transformation with invalid data."""
        raw_position = {
            "ticker": "AAPL",
            # Missing required fields like quantity, prices, etc.
            "name": "Apple Inc."
        }
        
        # The transformation should handle missing fields gracefully by using defaults
        # or raise an error - let's check what actually happens
        try:
            position = service._transform_position_data(raw_position)
            # If it succeeds, verify it has default values
            assert position.symbol == "AAPL"
            assert position.quantity == Decimal("0")  # Default value
        except Trading212APIError as e:
            assert "Invalid position data" in e.message
    
    def test_map_asset_type(self, service):
        """Test asset type mapping."""
        assert service._map_asset_type("STOCK") == AssetType.STOCK
        assert service._map_asset_type("ETF") == AssetType.ETF
        assert service._map_asset_type("CRYPTO") == AssetType.CRYPTO
        assert service._map_asset_type("UNKNOWN") == AssetType.STOCK  # Default
    
    def test_transform_dividend_data_success(self, service):
        """Test successful dividend data transformation."""
        raw_dividend = {
            "ticker": "AAPL",
            "amount": 2.50,
            "amountInEuro": {"amount": 2.30, "currency": "EUR"},
            "paidOn": "2024-01-15T00:00:00Z",
            "type": "ORDINARY",
            "quantity": 10,
            "grossAmountPerShare": 0.25,
            "withholdingTax": 0.0,
            "name": "Apple Inc."
        }
        
        dividend = service._transform_dividend_data(raw_dividend)
        
        # Verify transformation
        assert dividend.symbol == "AAPL"
        assert dividend.security_name == "Apple Inc."
        assert dividend.total_amount == Decimal("2.50")
        assert dividend.shares_held == Decimal("10")
        assert dividend.amount_per_share == Decimal("0.25")  # total_amount / shares_held
        assert dividend.gross_amount == Decimal("2.50")  # grossAmountPerShare * shares_held
        assert dividend.tax_withheld == Decimal("0.0")
        assert dividend.net_amount == Decimal("2.50")  # gross_amount - tax_withheld
        assert dividend.currency == "USD"  # Default currency
        assert dividend.base_currency_amount == Decimal("2.30")  # From amountInEuro
        assert dividend.is_reinvested is False
        assert dividend.payment_date.year == 2024
        assert dividend.payment_date.month == 1
        assert dividend.payment_date.day == 15


class TestTrading212ServiceHealthCheck:
    """Test health check functionality."""
    
    @pytest_asyncio.fixture
    async def authenticated_service(self):
        """Create authenticated Trading212Service instance."""
        service = Trading212Service(use_demo=True)
        await service._init_session()
        service.api_key = "test_api_key"
        yield service
        await service._close_session()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, authenticated_service):
        """Test successful health check."""
        with patch.object(authenticated_service.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "test_account"}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            result = await authenticated_service.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, authenticated_service):
        """Test health check failure."""
        with patch.object(authenticated_service, 'get_account_info') as mock_get_account:
            mock_get_account.side_effect = Trading212APIError("API error")
            
            result = await authenticated_service.health_check()
            
            assert result is False


class TestTrading212ServiceContextManager:
    """Test async context manager functionality."""
    
    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self):
        """Test proper initialization and cleanup in context manager."""
        async with Trading212Service(use_demo=True) as service:
            # Verify service is initialized
            assert service.session is not None
            assert isinstance(service.session, httpx.AsyncClient)
        
        # After context exit, session should be closed
        # Note: We can't directly test if session is closed, but we can verify
        # that the context manager completed without errors
    
    @pytest.mark.asyncio
    async def test_manual_session_management(self):
        """Test manual session initialization and cleanup."""
        service = Trading212Service(use_demo=True)
        
        # Initially no session
        assert service.session is None
        
        # Initialize session
        await service._init_session()
        assert service.session is not None
        
        # Close session
        await service._close_session()
        # Session object still exists but should be closed
        assert service.session is not None


# Integration test fixtures for mock data
@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.keys.return_value = []
    return mock_redis