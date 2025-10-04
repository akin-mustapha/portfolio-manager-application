"""
Database session configuration.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base

# Database URL from environment variable or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./portfolio_dashboard.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)