# Project Structure

## Root Level
```
├── backend/           # Python FastAPI backend
├── frontend/          # React TypeScript frontend  
├── docs/              # Documentation
├── docker-compose.yml # Development environment
└── README.md          # Project documentation
```

## Backend Structure (`backend/`)
```
backend/
├── app/
│   ├── api/v1/           # API routes (versioned)
│   │   ├── api.py        # Main API router
│   │   └── endpoints/    # Individual endpoint modules
│   ├── core/             # Core configuration and dependencies
│   │   ├── config.py     # Settings and configuration
│   │   ├── deps.py       # Dependency injection
│   │   └── security.py   # Authentication logic
│   ├── db/               # Database configuration
│   │   ├── base.py       # Base model imports
│   │   ├── models.py     # SQLAlchemy models
│   │   └── session.py    # Database session
│   ├── models/           # Pydantic models (schemas)
│   ├── services/         # Business logic layer
│   └── main.py           # FastAPI application entry point
├── alembic/              # Database migrations
├── tests/                # Test suite
│   ├── test_api/         # API endpoint tests
│   ├── test_db/          # Database tests
│   ├── test_models/      # Model tests
│   └── test_services/    # Service layer tests
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Poetry configuration
```

## Frontend Structure (`frontend/`)
```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   │   └── __tests__/    # Component tests
│   ├── pages/            # Page-level components
│   │   └── __tests__/    # Page tests
│   ├── contexts/         # React context providers
│   ├── hooks/            # Custom React hooks
│   │   └── __tests__/    # Hook tests
│   ├── services/         # API service layer
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Main application component
│   └── index.tsx         # Application entry point
├── public/               # Static assets
├── package.json          # Node.js dependencies
└── tsconfig.json         # TypeScript configuration
```

## Architecture Patterns

### Backend Patterns
- **Layered Architecture**: API → Services → Database
- **Dependency Injection**: Core dependencies in `app/core/deps.py`
- **Repository Pattern**: Database access through SQLAlchemy models
- **Service Layer**: Business logic isolated in `app/services/`
- **API Versioning**: Routes organized under `/api/v1/`

### Frontend Patterns
- **Component-Based**: Reusable components in `components/`
- **Page-Based Routing**: Route components in `pages/`
- **Context Pattern**: Global state management via React Context
- **Custom Hooks**: Reusable logic in `hooks/`
- **Service Layer**: API calls abstracted in `services/`

## Naming Conventions

### Backend
- **Files**: Snake_case (e.g., `portfolio_service.py`)
- **Classes**: PascalCase (e.g., `PortfolioService`)
- **Functions/Variables**: Snake_case (e.g., `get_portfolio_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_V1_STR`)

### Frontend
- **Files**: PascalCase for components (e.g., `Dashboard.tsx`), camelCase for utilities
- **Components**: PascalCase (e.g., `MetricCard`)
- **Functions/Variables**: camelCase (e.g., `fetchPortfolioData`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

## Testing Structure
- **Backend**: Tests mirror source structure in `tests/`
- **Frontend**: Tests co-located in `__tests__/` directories
- **Fixtures**: Centralized in `backend/tests/conftest.py`
- **Test Data**: Sample data fixtures for consistent testing