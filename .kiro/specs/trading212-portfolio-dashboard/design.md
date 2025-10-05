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
- Tailwind CSS for responsive styling
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
  totalValue: MetricCard;
  totalReturn: MetricCard;
  pieChart: ConsolidatedPieChart;
  pieList: PieListComponent;
}

interface MetricCard {
  title: string;
  value: number | string;
  change?: PercentageChange;
  trend?: TrendIndicator;
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
  performanceChart: TimeSeriesChart;
  allocationPieChart: PieChart;
  sectorBreakdownChart: DonutChart;
  benchmarkComparisonChart: LineChart;
  riskReturnScatterPlot: ScatterChart;
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
  };
  
  dataFetching: {
    caching: 'React Query with stale-while-revalidate';
    prefetching: 'Prefetch critical data on route change';
    pagination: 'Paginate large datasets';
  };
  
  bundleOptimization: {
    treeshaking: 'Remove unused code';
    compression: 'Gzip/Brotli compression';
    cdn: 'CDN for static assets';
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