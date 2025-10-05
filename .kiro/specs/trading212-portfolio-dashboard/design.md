# Design Document

## Overview

The Trading 212 Portfolio Manager Dashboard is a modern web application built with React/TypeScript frontend and Python FastAPI backend. The system integrates with Trading 212's REST API to fetch real-time portfolio data and provides comprehensive analytics through interactive visualizations. The architecture follows a microservices pattern with clear separation between data fetching, processing, and presentation layers.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Dashboard UI]
        Charts[Chart.js/D3 Visualizations]
        State[Redux/Zustand State Management]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server]
        Auth[Authentication Service]
        Cache[Redis Cache Layer]
    end
    
    subgraph "Data Layer"
        T212[Trading 212 API]
        Market[Market Data APIs]
        DB[(SQLite/PostgreSQL)]
    end
    
    subgraph "Processing Layer"
        Calc[Financial Calculations Engine]
        Risk[Risk Analytics Module]
        Bench[Benchmark Comparison Service]
    end
    
    UI --> API
    Charts --> State
    State --> UI
    API --> Auth
    API --> Cache
    API --> T212
    API --> Market
    API --> DB
    API --> Calc
    Calc --> Risk
    Calc --> Bench
```

### Technology Stack

**Frontend:**
- React 18 with TypeScript for type safety
- Tailwind CSS for responsive styling with modern design system
- Framer Motion for smooth animations and micro-interactions
- Lucide React for consistent iconography
- Chart.js or Recharts for financial visualizations
- React Query for data fetching and caching
- React Router for navigation

**Backend:**
- Python with FastAPI framework
- Pydantic for data validation and type safety
- Redis for caching API responses
- SQLite for development, PostgreSQL for production
- JWT for session management

**External APIs:**
- Trading 212 API for portfolio data
- Alpha Vantage or Yahoo Finance for benchmark data
- Market data APIs for real-time pricing

## Modern UI Design System

### Design Principles
- **Smooth Animations**: All interactions use Framer Motion for fluid, spring-based animations
- **Backdrop Blur Effects**: Modern glassmorphism with backdrop-blur for depth and sophistication
- **Micro-interactions**: Subtle hover states, scale transforms, and transition effects
- **Gradient Accents**: Strategic use of gradients for visual hierarchy and modern appeal
- **Consistent Iconography**: Lucide React icons for clean, consistent visual language
- **Responsive Animations**: Animations that adapt to screen size and user preferences

### Animation Patterns
```typescript
type AnimationStyle = 
  | "from-bottom" | "from-center" | "from-top" 
  | "from-left" | "from-right" | "fade"
  | "top-in-bottom-out" | "left-in-right-out"

interface AnimationConfig {
  initial: MotionProps;
  animate: MotionProps;
  exit: MotionProps;
  transition: {
    type: "spring";
    damping: number;
    stiffness: number;
  };
}

// Standard animation variants for consistency
const standardAnimations = {
  cardHover: { scale: 1.02, y: -2 },
  buttonHover: { scale: 1.05 },
  iconHover: { scale: 1.1, rotate: 5 },
  backdropBlur: "backdrop-blur-md",
  shadowLevels: ["shadow-sm", "shadow-md", "shadow-lg", "shadow-xl"]
}
```

### Color System & Gradients
```typescript
interface ColorSystem {
  primary: {
    gradient: "from-primary/30 to-primary";
    background: "bg-primary/10";
    text: "text-primary";
    border: "border-primary/20";
  };
  
  neutral: {
    glass: "bg-neutral-900/50 dark:bg-neutral-100/50";
    backdrop: "bg-black/50";
    border: "border-neutral-200 dark:border-neutral-800";
  };
  
  interactive: {
    hover: "group-hover:brightness-[0.8]";
    focus: "focus:ring-2 focus:ring-primary/50";
    active: "active:scale-95";
  };
}
```

### Icon System with Lucide React
```typescript
// Financial Dashboard Icon Mapping
interface FinancialIcons {
  // Performance & Trends
  TrendingUp: LucideIcon;      // Positive performance
  TrendingDown: LucideIcon;    // Negative performance
  Activity: LucideIcon;        // Volatility/Activity
  BarChart: LucideIcon;        // Charts/Analytics
  PieChart: LucideIcon;        // Allocation views
  LineChart: LucideIcon;       // Time series
  
  // Financial
  DollarSign: LucideIcon;      // Currency/Value
  Percent: LucideIcon;         // Percentages
  Calculator: LucideIcon;      // Calculations
  Target: LucideIcon;          // Goals/Targets
  
  // UI Controls (matching snippet style)
  Play: LucideIcon;            // Play actions
  X: LucideIcon;               // Close (XIcon in snippet)
  Menu: LucideIcon;            // Navigation
  Settings: LucideIcon;        // Configuration
  Refresh: LucideIcon;         // Data refresh
  Eye: LucideIcon;             // Show/visibility
  EyeOff: LucideIcon;          // Hide
  
  // Status & Alerts
  CheckCircle: LucideIcon;     // Success states
  AlertTriangle: LucideIcon;   // Warnings
  Info: LucideIcon;            // Information
  AlertCircle: LucideIcon;     // Errors
}

interface IconWrapper {
  icon: LucideIcon;
  size?: "sm" | "md" | "lg" | "xl";
  variant?: "default" | "hover" | "active" | "disabled";
  animation?: "none" | "spin" | "pulse" | "bounce";
  className?: string;
}
```

## Components and Interfaces

### Frontend Components

#### Core Layout Components
```typescript
interface DashboardLayout {
  header: HeaderComponent;
  sidebar: NavigationSidebar;
  main: MainContent;
  footer?: FooterComponent;
}

interface HeaderComponent {
  logo: string;
  userProfile: UserProfile;
  apiStatus: ConnectionStatus;
  refreshButton: RefreshControl;
}
```

#### Portfolio Overview Components
```typescript
interface PortfolioOverview {
  totalValue: AnimatedMetricCard;
  totalReturn: AnimatedMetricCard;
  pieChart: InteractiveConsolidatedPieChart;
  pieList: AnimatedPieListComponent;
}

interface AnimatedMetricCard {
  title: string;
  value: number | string;
  change?: PercentageChange;
  trend?: TrendIndicator;
  animationDelay?: number;
  hoverEffect?: boolean;
  gradient?: boolean;
}

interface InteractiveElement {
  hoverScale?: number;
  clickAnimation?: AnimationStyle;
  backdropBlur?: boolean;
  shadowEffect?: boolean;
}
```

#### Pie Analysis Components
```typescript
interface PieAnalysisView {
  pieSelector: PieSelector;
  performanceMetrics: PiePerformanceCard;
  riskMetrics: PieRiskCard;
  allocationChart: PieAllocationChart;
  holdingsTable: TopHoldingsTable;
}
```

#### Financial Visualization Components
```typescript
interface ChartComponents {
  performanceChart: AnimatedTimeSeriesChart;
  allocationPieChart: InteractivePieChart;
  sectorBreakdownChart: AnimatedDonutChart;
  benchmarkComparisonChart: InteractiveLineChart;
  riskReturnScatterPlot: AnimatedScatterChart;
}

interface AnimatedChart extends InteractiveElement {
  enterAnimation: AnimationStyle;
  dataUpdateAnimation: AnimationStyle;
  tooltipAnimation: AnimationStyle;
  loadingState: SkeletonLoader;
}

interface ModernUIElements {
  backdropBlur: boolean;
  gradientBackgrounds: boolean;
  shadowEffects: boolean;
  hoverTransitions: boolean;
  microInteractions: boolean;
}
```

### Backend API Interfaces

#### Trading 212 Integration Service
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Trading212Service:
    async def authenticate(self, api_key: str) -> AuthResult:
        pass
    
    async def get_account_info(self) -> AccountInfo:
        pass
    
    async def get_pies(self) -> List[Pie]:
        pass
    
    async def get_positions(self) -> List[Position]:
        pass
    
    async def get_historical_data(self, symbol: str, period: str) -> HistoricalData:
        pass
    
    async def get_dividends(self) -> List[Dividend]:
        pass

class Pie(BaseModel):
    id: str
    name: str
    total_value: float
    invested_amount: float
    return_pct: float
    positions: List[Position]
    created_at: datetime
    updated_at: datetime
```

#### Financial Calculations Service
```python
import pandas as pd
import numpy as np
from typing import List

class CalculationsService:
    def calculate_portfolio_metrics(self, positions: List[Position]) -> PortfolioMetrics:
        pass
    
    def calculate_pie_metrics(self, pie: Pie) -> PieMetrics:
        pass
    
    def calculate_risk_metrics(self, returns: pd.Series) -> RiskMetrics:
        pass
    
    def calculate_benchmark_comparison(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> BenchmarkComparison:
        pass

class PortfolioMetrics(BaseModel):
    total_value: float
    total_invested: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
```

### Data Models

#### Core Data Models
```python
from enum import Enum
from typing import List, Optional

class AssetType(str, Enum):
    STOCK = "STOCK"
    ETF = "ETF"
    CRYPTO = "CRYPTO"

class RiskCategory(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Portfolio(BaseModel):
    id: str
    user_id: str
    total_value: float
    total_invested: float
    pies: List[Pie]
    positions: List[Position]
    metrics: PortfolioMetrics
    last_updated: datetime

class Position(BaseModel):
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    sector: str
    industry: str
    country: str
    asset_type: AssetType

class RiskMetrics(BaseModel):
    volatility: float
    beta: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float  # Value at Risk
    risk_category: RiskCategory
```

## Error Handling

### API Error Handling Strategy
```python
from fastapi import HTTPException
from enum import Enum

class ErrorType(str, Enum):
    AUTHENTICATION_FAILURE = "authentication_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    API_UNAVAILABLE = "api_unavailable"
    INVALID_REQUEST = "invalid_request"
    INSUFFICIENT_DATA = "insufficient_data"
    CALCULATION_ERROR = "calculation_error"

class APIError(HTTPException):
    def __init__(self, error_type: ErrorType, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)
        self.error_type = error_type

# Error handlers for different scenarios
async def handle_trading212_errors(error_type: ErrorType, detail: str):
    if error_type == ErrorType.AUTHENTICATION_FAILURE:
        raise APIError(error_type, detail, 401)
    elif error_type == ErrorType.RATE_LIMIT_EXCEEDED:
        raise APIError(error_type, detail, 429)
    # ... other error handling
```

### Error Recovery Mechanisms
- **Retry Logic:** Exponential backoff for API calls with circuit breaker pattern
- **Fallback Data:** Cache previous successful responses for offline viewing
- **Graceful Degradation:** Show partial data when some services are unavailable
- **User Feedback:** Clear error messages with suggested actions

## Testing Strategy

### Frontend Testing
```typescript
interface FrontendTesting {
  unitTests: {
    components: 'React Testing Library + Jest';
    utilities: 'Jest for calculation functions';
    hooks: 'React Hooks Testing Library';
  };
  
  integrationTests: {
    apiIntegration: 'MSW for API mocking';
    userFlows: 'Cypress for E2E testing';
    visualRegression: 'Percy or Chromatic';
  };
}
```

### Backend Testing
```python
# Testing framework configuration
backend_testing = {
    "unit_tests": {
        "services": "pytest for business logic",
        "calculations": "pytest with financial test cases using pandas/numpy",
        "utilities": "pytest for helper functions"
    },
    
    "integration_tests": {
        "api_endpoints": "pytest with FastAPI TestClient",
        "database_operations": "pytest with test database fixtures",
        "external_apis": "httpx_mock for API mocking"
    }
}

# Example test structure
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

@pytest.fixture
def test_client():
    return TestClient(app)

def test_portfolio_metrics_calculation():
    # Test financial calculations with known data
    pass
```

### Performance Testing
- **Load Testing:** Locust for Python-based API endpoint performance testing
- **Frontend Performance:** Lighthouse CI for Core Web Vitals
- **Memory Profiling:** Python memory_profiler and cProfile for performance analysis
- **Database Performance:** SQLAlchemy query analysis and indexing optimization
- **Financial Calculations:** Benchmark pandas/numpy operations for large datasets

## Security Considerations

### API Security
```typescript
interface SecurityMeasures {
  authentication: {
    jwtTokens: 'Short-lived access tokens';
    refreshTokens: 'Secure refresh mechanism';
    apiKeyEncryption: 'AES-256 encryption for Trading 212 keys';
  };
  
  dataProtection: {
    encryption: 'Encrypt sensitive data at rest';
    transmission: 'HTTPS/TLS for all communications';
    sanitization: 'Input validation and sanitization';
  };
  
  accessControl: {
    rateLimiting: 'Prevent API abuse';
    cors: 'Restrict cross-origin requests';
    headers: 'Security headers (CSP, HSTS, etc.)';
  };
}
```

### Data Privacy
- **Local Storage:** Minimize sensitive data in browser storage
- **API Keys:** Never expose Trading 212 API keys in frontend code
- **Audit Logging:** Track access to sensitive financial data
- **Data Retention:** Implement data cleanup policies

## Performance Optimization

### Frontend Optimization
```typescript
interface PerformanceOptimization {
  rendering: {
    lazyLoading: 'React.lazy for route-based code splitting';
    memoization: 'React.memo for expensive components';
    virtualization: 'React Window for large lists';
    animationOptimization: 'Framer Motion layout animations with will-change';
  };
  
  dataFetching: {
    caching: 'React Query with stale-while-revalidate';
    prefetching: 'Prefetch critical data on route change';
    pagination: 'Paginate large datasets';
    optimisticUpdates: 'Immediate UI feedback with rollback';
  };
  
  bundleOptimization: {
    treeshaking: 'Remove unused code';
    compression: 'Gzip/Brotli compression';
    cdn: 'CDN for static assets';
    motionOptimization: 'Tree-shake unused Framer Motion features';
  };
  
  userExperience: {
    skeletonLoaders: 'Animated loading states for all components';
    errorBoundaries: 'Graceful error handling with recovery options';
    accessibilityAnimations: 'Respect prefers-reduced-motion';
    responsiveAnimations: 'Adaptive animations for different screen sizes';
  };
}
```

### Backend Optimization
- **Caching Strategy:** Redis for frequently accessed calculations
- **Database Indexing:** Optimize queries for portfolio and position lookups
- **API Response Compression:** Gzip compression for large JSON responses
- **Connection Pooling:** Efficient database connection management

## Deployment Architecture

### Development Environment
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - REACT_APP_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=sqlite:///./dev.db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports: ["6379:6379"]
```

### Production Deployment
- **Frontend:** Static hosting on Vercel/Netlify with CDN
- **Backend:** Python FastAPI app on Railway/Render with Gunicorn/Uvicorn
- **Database:** Managed PostgreSQL instance
- **Caching:** Redis Cloud or managed Redis service
- **Monitoring:** Application performance monitoring with Sentry
- **Python Dependencies:** Poetry or pip-tools for dependency management

## Data Flow Architecture

### Real-time Data Updates
```mermaid
sequenceDiagram
    participant UI as Frontend UI
    participant API as Backend API
    participant Cache as Redis Cache
    participant T212 as Trading 212 API
    participant Calc as Calculations Engine
    
    UI->>API: Request portfolio data
    API->>Cache: Check cached data
    alt Cache hit
        Cache->>API: Return cached data
    else Cache miss
        API->>T212: Fetch fresh data
        T212->>API: Return portfolio data
        API->>Calc: Process calculations
        Calc->>API: Return metrics
        API->>Cache: Store processed data
    end
    API->>UI: Return complete portfolio data
    UI->>UI: Update visualizations
```

### Batch Processing for Historical Analysis
- **Daily Jobs:** Update historical performance data
- **Weekly Jobs:** Recalculate risk metrics and benchmarks
- **Monthly Jobs:** Generate portfolio reports and analytics
- **Real-time Updates:** Live price updates during market hours

## Logging and Monitoring Design

### Logging Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        API[FastAPI Application]
        Service[Trading212 Service]
        Auth[Authentication Service]
        Calc[Calculations Service]
    end
    
    subgraph "Logging Layer"
        Logger[Python Logger]
        Formatter[Log Formatter]
        Filter[Sensitive Data Filter]
    end
    
    subgraph "Storage Layer"
        Local[Local Log Files]
        Central[Centralized Log Server]
        Metrics[Metrics Collection]
    end
    
    API --> Logger
    Service --> Logger
    Auth --> Logger
    Calc --> Logger
    Logger --> Formatter
    Formatter --> Filter
    Filter --> Local
    Filter --> Central
    Filter --> Metrics
```

### Logging Configuration

```python
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
from contextlib import contextmanager

class SecurityFilter(logging.Filter):
    """Filter to remove sensitive data from logs"""
    
    SENSITIVE_KEYS = {
        'password', 'api_key', 'token', 'secret', 'authorization',
        'trading212_api_key', 'encrypted_key', 'refresh_token', 'access_token'
    }
    
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, 'msg') and isinstance(record.msg, dict):
            record.msg = self._sanitize_dict(record.msg)
        elif hasattr(record, 'args') and record.args:
            record.args = tuple(self._sanitize_value(arg) for arg in record.args)
        return True
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive keys from dictionary"""
        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            else:
                sanitized[key] = self._sanitize_value(value)
        return sanitized
    
    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize individual values"""
        if isinstance(value, str) and len(value) > 20:
            # Potentially sensitive string, mask middle part
            return f"{value[:4]}...{value[-4:]}"
        return value

class ContextualFormatter(logging.Formatter):
    """Custom formatter that includes request context"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            record.request_context = {
                'request_id': record.request_id,
                'user_id': getattr(record, 'user_id', None),
                'endpoint': getattr(record, 'endpoint', None),
                'method': getattr(record, 'method', None)
            }
        
        # Format as JSON for structured logging
        log_data = {
            'timestamp': record.timestamp,
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'request_context'):
            log_data['request_context'] = record.request_context
        
        if hasattr(record, 'extra_data'):
            log_data['extra_data'] = record.extra_data
        
        return json.dumps(log_data, default=str)

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'contextual': {
            '()': ContextualFormatter,
        },
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'filters': {
        'security_filter': {
            '()': SecurityFilter,
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/application.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'contextual',
            'filters': ['security_filter']
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['security_filter']
        },
        'centralized': {
            'level': 'WARNING',
            'class': 'logging.handlers.HTTPHandler',
            'host': 'logs.example.com',
            'url': '/api/logs',
            'method': 'POST',
            'formatter': 'contextual',
            'filters': ['security_filter']
        }
    },
    'loggers': {
        'app': {
            'handlers': ['file', 'console', 'centralized'],
            'level': 'DEBUG',
            'propagate': False
        },
        'trading212_service': {
            'handlers': ['file', 'console', 'centralized'],
            'level': 'INFO',
            'propagate': False
        },
        'auth_service': {
            'handlers': ['file', 'console', 'centralized'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

### Request Context Middleware

```python
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id')
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context to logs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user ID from JWT token if available
        user_id = self._extract_user_id(request)
        if user_id:
            user_id_var.set(user_id)
        
        # Log request start
        logger = logging.getLogger('app.requests')
        logger.info(
            "Request started",
            extra={
                'request_id': request_id,
                'user_id': user_id,
                'endpoint': str(request.url.path),
                'method': request.method,
                'user_agent': request.headers.get('user-agent'),
                'ip_address': request.client.host if request.client else None
            }
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful request
            duration = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    'request_id': request_id,
                    'user_id': user_id,
                    'endpoint': str(request.url.path),
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2)
                }
            )
            
            return response
            
        except Exception as e:
            # Log request error
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    'request_id': request_id,
                    'user_id': user_id,
                    'endpoint': str(request.url.path),
                    'method': request.method,
                    'error': str(e),
                    'duration_ms': round(duration * 1000, 2)
                },
                exc_info=True
            )
            raise
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token"""
        try:
            auth_header = request.headers.get('authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                # Decode JWT token to get user ID
                # Implementation depends on your JWT library
                return self._decode_jwt_user_id(token)
        except Exception:
            pass
        return None

# Context-aware logger helper
class ContextLogger:
    """Logger that automatically includes request context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _get_extra_context(self, extra: Optional[Dict] = None) -> Dict:
        """Get current request context"""
        context = {}
        
        try:
            context['request_id'] = request_id_var.get()
        except LookupError:
            pass
        
        try:
            context['user_id'] = user_id_var.get()
        except LookupError:
            pass
        
        if extra:
            context.update(extra)
        
        return context
    
    def info(self, message: str, extra: Optional[Dict] = None):
        self.logger.info(message, extra=self._get_extra_context(extra))
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        self.logger.warning(message, extra=self._get_extra_context(extra))
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        self.logger.error(message, extra=self._get_extra_context(extra), exc_info=exc_info)
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        self.logger.debug(message, extra=self._get_extra_context(extra))
```

### Service-Specific Logging

```python
# Trading 212 Service Logging
class Trading212Service:
    def __init__(self):
        self.logger = ContextLogger('trading212_service')
    
    async def authenticate(self, api_key: str) -> AuthResult:
        self.logger.info("Trading 212 authentication attempt started")
        
        try:
            # Authentication logic here
            result = await self._make_auth_request(api_key)
            
            if result.success:
                self.logger.info(
                    "Trading 212 authentication successful",
                    extra={'account_id': result.account_id}
                )
            else:
                self.logger.warning(
                    "Trading 212 authentication failed",
                    extra={'reason': result.message}
                )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Trading 212 authentication error",
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            raise
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        self.logger.debug(
            "Trading 212 API request",
            extra={
                'method': method,
                'endpoint': endpoint,
                'rate_limit_remaining': self._requests_remaining
            }
        )
        
        try:
            response = await self._execute_request(method, endpoint, **kwargs)
            
            self.logger.info(
                "Trading 212 API request successful",
                extra={
                    'method': method,
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'rate_limit_remaining': self._requests_remaining
                }
            )
            
            return response
            
        except Trading212APIError as e:
            if e.error_type == "rate_limit_exceeded":
                self.logger.warning(
                    "Trading 212 rate limit exceeded",
                    extra={
                        'endpoint': endpoint,
                        'reset_time': self._rate_limit_reset,
                        'requests_remaining': self._requests_remaining
                    }
                )
            else:
                self.logger.error(
                    "Trading 212 API error",
                    extra={
                        'endpoint': endpoint,
                        'error_type': e.error_type,
                        'status_code': e.status_code
                    }
                )
            raise

# Authentication Service Logging
class AuthService:
    def __init__(self):
        self.logger = ContextLogger('auth_service')
    
    async def create_session(self, session_data: SessionCreate):
        self.logger.info(
            "Session creation started",
            extra={'session_name': session_data.session_name}
        )
        
        try:
            session = await self._create_session_logic(session_data)
            
            self.logger.info(
                "Session created successfully",
                extra={
                    'session_id': session.session_id,
                    'expires_in': session.expires_in
                }
            )
            
            return session
            
        except Exception as e:
            self.logger.error(
                "Session creation failed",
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            raise
```

### Monitoring and Alerting

```python
from typing import Dict, Any
import time
from dataclasses import dataclass

@dataclass
class MetricEvent:
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class MetricsCollector:
    """Collect application metrics for monitoring"""
    
    def __init__(self):
        self.logger = ContextLogger('metrics')
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Record API call metrics"""
        self.logger.info(
            "API call metric",
            extra={
                'metric_type': 'api_call',
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'duration_ms': duration_ms
            }
        )
    
    def record_trading212_rate_limit(self, remaining: int, reset_time: datetime):
        """Record Trading 212 rate limit status"""
        self.logger.info(
            "Trading 212 rate limit status",
            extra={
                'metric_type': 'rate_limit',
                'requests_remaining': remaining,
                'reset_time': reset_time.isoformat()
            }
        )
    
    def record_error(self, error_type: str, endpoint: str = None):
        """Record error occurrence"""
        self.logger.warning(
            "Error metric",
            extra={
                'metric_type': 'error',
                'error_type': error_type,
                'endpoint': endpoint
            }
        )
    
    def record_user_action(self, action: str, user_id: str):
        """Record user action for analytics"""
        self.logger.info(
            "User action metric",
            extra={
                'metric_type': 'user_action',
                'action': action,
                'user_id': user_id
            }
        )

# Global metrics collector instance
metrics = MetricsCollector()
```

### Log Analysis and Alerting Rules

```yaml
# Example alerting rules for log monitoring
alerting_rules:
  - name: "High Error Rate"
    condition: "error_rate > 5% over 5 minutes"
    severity: "warning"
    notification: "slack"
    
  - name: "Trading 212 API Failures"
    condition: "trading212_api_errors > 10 over 10 minutes"
    severity: "critical"
    notification: "email, slack"
    
  - name: "Authentication Failures"
    condition: "auth_failures > 20 over 5 minutes"
    severity: "warning"
    notification: "slack"
    
  - name: "Rate Limit Exceeded"
    condition: "rate_limit_exceeded > 0"
    severity: "info"
    notification: "slack"

log_retention:
  local_files: "30 days"
  centralized_logs: "90 days"
  metrics: "1 year"
```