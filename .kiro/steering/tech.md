# Technology Stack

## Backend
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Authentication**: JWT with python-jose
- **Data Processing**: Pandas, NumPy
- **Migration**: Alembic
- **ASGI Server**: Uvicorn

## Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Data Fetching**: TanStack React Query (v4)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Build Tool**: Create React App

## Development Environment
- **Containerization**: Docker with Docker Compose
- **Database**: PostgreSQL 15
- **Cache**: Redis 7

## Code Quality Tools

### Backend
- **Formatting**: Black (line length 88)
- **Import Sorting**: isort (black profile)
- **Linting**: Flake8
- **Type Checking**: MyPy
- **Testing**: Pytest with pytest-asyncio

### Frontend
- **Testing**: Jest with React Testing Library
- **Type Checking**: TypeScript 4.9+

## Common Commands

### Development Setup
```bash
# Start full development environment
docker-compose up --build

# Backend only (local development)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend only (local development)  
cd frontend
npm install
npm start
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend formatting and linting
cd backend
black .
isort .
flake8 .
mypy .

# Frontend type checking
cd frontend
npx tsc --noEmit
```

## Environment Configuration
- Backend: `.env` file with database, Redis, and API key settings
- Frontend: `.env` file with API URL configuration
- Development ports: Frontend (3000), Backend (8000), PostgreSQL (5432), Redis (6379)