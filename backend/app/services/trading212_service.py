"""
Trading 212 API integration service.

This service handles authentication, data fetching, and transformation
from Trading 212 API to internal data models.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

import httpx
import redis.asyncio as redis
from cryptography.fernet import Fernet
from pydantic import BaseModel, ValidationError

from ..core.config import settings
from ..models.portfolio import Portfolio, PortfolioMetrics
from ..models.pie import Pie, PieMetrics
from ..models.position import Position
from ..models.dividend import Dividend
from ..models.historical import HistoricalData
from ..models.enums import AssetType


logger = logging.getLogger(__name__)


class AuthResult(BaseModel):
    """Result of authentication attempt."""
    success: bool
    message: str
    expires_at: Optional[datetime] = None


class Trading212APIError(Exception):
    """Custom exception for Trading 212 API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_type: str = "api_error"):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)


class Trading212Service:
    """
    Service for interacting with Trading 212 API.
    
    Handles authentication, data fetching, caching, and error handling.
    """
    
    BASE_URL = "https://live.trading212.com/api/v0"
    DEMO_BASE_URL = "https://demo.trading212.com/api/v0"
    
    def __init__(self, use_demo: bool = False):
        self.base_url = self.DEMO_BASE_URL if use_demo else self.BASE_URL
        self.session: Optional[httpx.AsyncClient] = None
        self.api_key: Optional[str] = None
        self.redis_client: Optional[redis.Redis] = None
        self.cipher_suite: Optional[Fernet] = None
        self._rate_limit_reset: Optional[datetime] = None
        self._requests_remaining: int = 60  # Default rate limit
        
        # Initialize encryption for API key storage
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption for secure API key storage."""
        try:
            # Use a key derived from the secret key for encryption
            key = Fernet.generate_key()  # In production, derive from settings.SECRET_KEY
            self.cipher_suite = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise Trading212APIError("Failed to initialize secure storage")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
    
    async def _init_session(self):
        """Initialize HTTP session and Redis connection."""
        # Initialize HTTP client
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": "Trading212-Portfolio-Dashboard/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def _close_session(self):
        """Close HTTP session and Redis connection."""
        if self.session:
            await self.session.aclose()
        if self.redis_client:
            await self.redis_client.close()
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for secure storage."""
        if not self.cipher_suite:
            raise Trading212APIError("Encryption not initialized")
        return self.cipher_suite.encrypt(api_key.encode()).decode()
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key from storage."""
        if not self.cipher_suite:
            raise Trading212APIError("Encryption not initialized")
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
    
    async def _check_rate_limit(self):
        """Check and handle rate limiting."""
        if self._rate_limit_reset and datetime.utcnow() < self._rate_limit_reset:
            if self._requests_remaining <= 0:
                wait_time = (self._rate_limit_reset - datetime.utcnow()).total_seconds()
                logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Trading 212 API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            use_cache: Whether to use Redis caching
            cache_ttl: Cache time-to-live in seconds
            
        Returns:
            API response data
            
        Raises:
            Trading212APIError: On API errors or authentication failures
        """
        if not self.session:
            raise Trading212APIError("Session not initialized")
        
        if not self.api_key:
            raise Trading212APIError("API key not set", error_type="authentication_failure")
        
        # Check rate limiting
        await self._check_rate_limit()
        
        # Check cache for GET requests
        cache_key = None
        if use_cache and method.upper() == "GET" and self.redis_client:
            cache_key = f"trading212:{endpoint}:{hash(str(params))}"
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache hit for {endpoint}")
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        # Prepare request
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": self.api_key}
        
        try:
            response = await self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            
            # Update rate limit info from headers
            if "X-RateLimit-Remaining" in response.headers:
                self._requests_remaining = int(response.headers["X-RateLimit-Remaining"])
            if "X-RateLimit-Reset" in response.headers:
                reset_timestamp = int(response.headers["X-RateLimit-Reset"])
                self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            
            # Handle different response status codes
            if response.status_code == 200:
                response_data = response.json()
                
                # Cache successful GET responses
                if use_cache and method.upper() == "GET" and self.redis_client and cache_key:
                    try:
                        await self.redis_client.setex(
                            cache_key, 
                            cache_ttl, 
                            json.dumps(response_data, default=str)
                        )
                    except Exception as e:
                        logger.warning(f"Cache write error: {e}")
                
                return response_data
                
            elif response.status_code == 401:
                raise Trading212APIError(
                    "Authentication failed. Please check your API key.",
                    status_code=401,
                    error_type="authentication_failure"
                )
            elif response.status_code == 429:
                raise Trading212APIError(
                    "Rate limit exceeded. Please try again later.",
                    status_code=429,
                    error_type="rate_limit_exceeded"
                )
            elif response.status_code == 503:
                raise Trading212APIError(
                    "Trading 212 API is temporarily unavailable.",
                    status_code=503,
                    error_type="api_unavailable"
                )
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                except:
                    pass
                
                raise Trading212APIError(
                    error_msg,
                    status_code=response.status_code,
                    error_type="api_error"
                )
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Trading212APIError(
                f"Network error: {str(e)}",
                error_type="network_error"
            )
    
    async def authenticate(self, api_key: str) -> AuthResult:
        """
        Authenticate with Trading 212 API and validate credentials.
        
        Args:
            api_key: Trading 212 API key
            
        Returns:
            AuthResult with success status and message
        """
        try:
            # Store the API key temporarily for testing
            self.api_key = api_key
            
            # Test authentication by fetching account info
            await self._make_request("GET", "/equity/account/info", use_cache=False)
            
            # If successful, encrypt and store the API key
            encrypted_key = self._encrypt_api_key(api_key)
            
            # Store in Redis if available
            if self.redis_client:
                try:
                    await self.redis_client.setex(
                        "trading212:encrypted_api_key",
                        86400,  # 24 hours
                        encrypted_key
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache API key: {e}")
            
            logger.info("Trading 212 authentication successful")
            return AuthResult(
                success=True,
                message="Authentication successful",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
        except Trading212APIError as e:
            logger.error(f"Authentication failed: {e.message}")
            self.api_key = None
            return AuthResult(
                success=False,
                message=e.message
            )
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            self.api_key = None
            return AuthResult(
                success=False,
                message="Unexpected authentication error"
            )
    
    async def load_stored_credentials(self) -> bool:
        """
        Load previously stored API credentials from cache.
        
        Returns:
            True if credentials were loaded successfully, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            encrypted_key = await self.redis_client.get("trading212:encrypted_api_key")
            if encrypted_key:
                self.api_key = self._decrypt_api_key(encrypted_key.decode())
                logger.info("Loaded stored API credentials")
                return True
        except Exception as e:
            logger.error(f"Failed to load stored credentials: {e}")
        
        return False
    
    async def clear_credentials(self):
        """Clear stored API credentials."""
        self.api_key = None
        if self.redis_client:
            try:
                await self.redis_client.delete("trading212:encrypted_api_key")
            except Exception as e:
                logger.warning(f"Failed to clear cached credentials: {e}")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Fetch account information from Trading 212.
        
        Returns:
            Account information dictionary
        """
        return await self._make_request("GET", "/equity/account/info")
    
    async def health_check(self) -> bool:
        """
        Check if the service is healthy and can connect to Trading 212.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            await self.get_account_info()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # Portfolio Data Fetching Methods
    
    async def get_pies(self) -> List[Dict[str, Any]]:
        """
        Fetch all pies from Trading 212.
        
        Returns:
            List of pie data dictionaries
        """
        return await self._make_request("GET", "/equity/pies", cache_ttl=300)
    
    async def get_pie_details(self, pie_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific pie.
        
        Args:
            pie_id: Unique pie identifier
            
        Returns:
            Detailed pie information
        """
        return await self._make_request("GET", f"/equity/pies/{pie_id}", cache_ttl=300)
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Fetch all equity positions from Trading 212.
        
        Returns:
            List of position data dictionaries
        """
        return await self._make_request("GET", "/equity/portfolio", cache_ttl=60)
    
    async def get_cash_balance(self) -> Dict[str, Any]:
        """
        Fetch cash balance information.
        
        Returns:
            Cash balance data
        """
        return await self._make_request("GET", "/equity/account/cash", cache_ttl=60)
    
    async def get_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent orders.
        
        Args:
            limit: Maximum number of orders to fetch
            
        Returns:
            List of order data
        """
        params = {"limit": limit}
        return await self._make_request("GET", "/equity/orders", params=params, cache_ttl=300)
    
    # Data Transformation Methods
    
    def _transform_position_data(self, raw_position: Dict[str, Any]) -> Position:
        """
        Transform Trading 212 position data to internal Position model.
        
        Args:
            raw_position: Raw position data from Trading 212 API
            
        Returns:
            Position model instance
        """
        try:
            # Map Trading 212 fields to internal model
            return Position(
                symbol=raw_position.get("ticker", ""),
                name=raw_position.get("name", ""),
                quantity=Decimal(str(raw_position.get("quantity", 0))),
                average_price=Decimal(str(raw_position.get("averagePrice", 0))),
                current_price=Decimal(str(raw_position.get("currentPrice", 0))),
                market_value=Decimal(str(raw_position.get("marketValue", 0))),
                unrealized_pnl=Decimal(str(raw_position.get("ppl", 0))),
                unrealized_pnl_pct=Decimal(str(raw_position.get("pplPercent", 0))),
                sector=raw_position.get("sector"),
                industry=raw_position.get("industry"),
                country=raw_position.get("country"),
                currency=raw_position.get("currency", "USD"),
                asset_type=self._map_asset_type(raw_position.get("type", "STOCK")),
                last_updated=datetime.utcnow()
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to transform position data: {e}")
            raise Trading212APIError(f"Invalid position data: {e}")
    
    def _map_asset_type(self, trading212_type: str) -> AssetType:
        """
        Map Trading 212 asset type to internal AssetType enum.
        
        Args:
            trading212_type: Asset type from Trading 212
            
        Returns:
            Internal AssetType enum value
        """
        type_mapping = {
            "STOCK": AssetType.STOCK,
            "ETF": AssetType.ETF,
            "CRYPTO": AssetType.CRYPTO,
        }
        return type_mapping.get(trading212_type.upper(), AssetType.STOCK)
    
    def _transform_pie_data(self, raw_pie: Dict[str, Any], positions: List[Position]) -> Pie:
        """
        Transform Trading 212 pie data to internal Pie model.
        
        Args:
            raw_pie: Raw pie data from Trading 212 API
            positions: List of positions in the pie
            
        Returns:
            Pie model instance
        """
        try:
            # Calculate basic metrics
            total_value = sum(pos.market_value for pos in positions)
            invested_amount = sum(pos.quantity * pos.average_price for pos in positions)
            total_return = total_value - invested_amount
            total_return_pct = (total_return / invested_amount * 100) if invested_amount > 0 else Decimal('0')
            
            pie_metrics = PieMetrics(
                total_value=total_value,
                invested_amount=invested_amount,
                total_return=total_return,
                total_return_pct=total_return_pct,
                portfolio_weight=Decimal('0'),  # Will be calculated at portfolio level
                portfolio_contribution=Decimal('0')  # Will be calculated at portfolio level
            )
            
            return Pie(
                id=raw_pie.get("id", ""),
                name=raw_pie.get("name", ""),
                description=raw_pie.get("description"),
                positions=positions,
                metrics=pie_metrics,
                auto_invest=raw_pie.get("autoInvest", False),
                created_at=datetime.fromisoformat(raw_pie.get("creationTime", datetime.utcnow().isoformat())),
                last_updated=datetime.utcnow()
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to transform pie data: {e}")
            raise Trading212APIError(f"Invalid pie data: {e}")
    
    async def fetch_portfolio_data(self) -> Portfolio:
        """
        Fetch and transform complete portfolio data from Trading 212.
        
        Returns:
            Complete Portfolio model with all pies and positions
        """
        try:
            # Fetch all required data concurrently
            account_info, pies_data, positions_data, cash_data = await asyncio.gather(
                self.get_account_info(),
                self.get_pies(),
                self.get_positions(),
                self.get_cash_balance(),
                return_exceptions=True
            )
            
            # Handle any exceptions from concurrent requests
            for result in [account_info, pies_data, positions_data, cash_data]:
                if isinstance(result, Exception):
                    raise result
            
            # Transform positions data
            all_positions = []
            for raw_pos in positions_data:
                try:
                    position = self._transform_position_data(raw_pos)
                    all_positions.append(position)
                except Exception as e:
                    logger.warning(f"Skipping invalid position: {e}")
            
            # Group positions by pie
            pie_positions_map = {}
            individual_positions = []
            
            # Fetch detailed pie information and group positions
            pies = []
            for raw_pie in pies_data:
                try:
                    pie_id = raw_pie.get("id")
                    if pie_id:
                        # Get positions for this pie (this would need pie-specific API call)
                        # For now, we'll use a simplified approach
                        pie_positions = [pos for pos in all_positions if pos.symbol in raw_pie.get("instruments", [])]
                        pie = self._transform_pie_data(raw_pie, pie_positions)
                        pies.append(pie)
                        
                        # Track which positions are in pies
                        for pos in pie_positions:
                            pie_positions_map[pos.symbol] = pie_id
                except Exception as e:
                    logger.warning(f"Skipping invalid pie: {e}")
            
            # Identify individual positions (not in any pie)
            individual_positions = [
                pos for pos in all_positions 
                if pos.symbol not in pie_positions_map
            ]
            
            # Calculate portfolio-level metrics
            total_value = sum(pos.market_value for pos in all_positions)
            total_invested = sum(pos.quantity * pos.average_price for pos in all_positions)
            cash_balance = Decimal(str(cash_data.get("free", 0)))
            
            portfolio_metrics = PortfolioMetrics(
                total_value=total_value,
                total_invested=total_invested,
                cash_balance=cash_balance,
                total_return=total_value - total_invested,
                total_return_pct=(total_value - total_invested) / total_invested * 100 if total_invested > 0 else Decimal('0')
            )
            
            # Update pie portfolio weights
            for pie in pies:
                if total_value > 0:
                    pie.metrics.portfolio_weight = pie.metrics.total_value / total_value * 100
                    pie.metrics.portfolio_contribution = pie.metrics.total_return / total_value * 100 if total_value > 0 else Decimal('0')
            
            # Create portfolio
            portfolio = Portfolio(
                id=account_info.get("id", "default"),
                user_id=account_info.get("id", "default"),
                name="Trading 212 Portfolio",
                pies=pies,
                individual_positions=individual_positions,
                metrics=portfolio_metrics,
                base_currency=account_info.get("currencyCode", "USD"),
                last_sync=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            logger.info(f"Successfully fetched portfolio with {len(pies)} pies and {len(individual_positions)} individual positions")
            return portfolio
            
        except Exception as e:
            logger.error(f"Failed to fetch portfolio data: {e}")
            raise Trading212APIError(f"Portfolio data fetch failed: {str(e)}")
    
    async def refresh_portfolio_data(self, portfolio_id: str) -> Portfolio:
        """
        Refresh portfolio data with latest information from Trading 212.
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            Updated Portfolio model
        """
        # Clear relevant caches
        if self.redis_client:
            try:
                cache_keys = await self.redis_client.keys("trading212:/equity/*")
                if cache_keys:
                    await self.redis_client.delete(*cache_keys)
                logger.info("Cleared portfolio data cache")
            except Exception as e:
                logger.warning(f"Failed to clear cache: {e}")
        
        return await self.fetch_portfolio_data()