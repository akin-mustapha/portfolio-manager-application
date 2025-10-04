"""
SQLAlchemy database models for the Trading 212 Portfolio Dashboard.
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Numeric, Boolean, 
    Text, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base


class AssetTypeEnum(enum.Enum):
    """Asset type enumeration for database."""
    STOCK = "STOCK"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    BOND = "BOND"
    COMMODITY = "COMMODITY"
    CASH = "CASH"


class RiskCategoryEnum(enum.Enum):
    """Risk category enumeration for database."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DividendTypeEnum(enum.Enum):
    """Dividend type enumeration for database."""
    CASH = "CASH"
    STOCK = "STOCK"
    REINVESTED = "REINVESTED"


class PortfolioTable(Base):
    """Portfolio database table."""
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, default="Main Portfolio")
    base_currency = Column(String, nullable=False, default="USD")
    benchmark_symbol = Column(String, nullable=True)
    
    # Metrics (stored as JSON for flexibility)
    total_value = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    total_invested = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    cash_balance = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    total_return = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    total_return_pct = Column(Numeric(precision=8, scale=4), nullable=False, default=0)
    annualized_return = Column(Numeric(precision=8, scale=4), nullable=True)
    
    # Dividend metrics
    total_dividends = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    dividend_yield = Column(Numeric(precision=8, scale=4), nullable=False, default=0)
    annual_dividend_projection = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    
    # Allocation data (stored as JSON)
    sector_allocation = Column(JSON, nullable=True)
    country_allocation = Column(JSON, nullable=True)
    asset_type_allocation = Column(JSON, nullable=True)
    
    # Risk metrics
    volatility = Column(Numeric(precision=8, scale=4), nullable=True)
    sharpe_ratio = Column(Numeric(precision=8, scale=4), nullable=True)
    max_drawdown = Column(Numeric(precision=8, scale=4), nullable=True)
    beta = Column(Numeric(precision=8, scale=4), nullable=True)
    risk_category = Column(SQLEnum(RiskCategoryEnum), nullable=True)
    risk_score = Column(Numeric(precision=5, scale=2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    last_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    last_sync = Column(DateTime, nullable=True)
    
    # Relationships
    pies = relationship("PieTable", back_populates="portfolio", cascade="all, delete-orphan")
    individual_positions = relationship("PositionTable", 
                                      foreign_keys="PositionTable.portfolio_id",
                                      back_populates="portfolio", 
                                      cascade="all, delete-orphan")
    dividends = relationship("DividendTable", back_populates="portfolio", cascade="all, delete-orphan")
    performance_snapshots = relationship("PerformanceSnapshotTable", 
                                       foreign_keys="PerformanceSnapshotTable.portfolio_id",
                                       back_populates="portfolio", 
                                       cascade="all, delete-orphan")


class PieTable(Base):
    """Pie database table."""
    __tablename__ = "pies"
    
    id = Column(String, primary_key=True, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    auto_invest = Column(Boolean, nullable=False, default=False)
    target_allocation = Column(Numeric(precision=5, scale=2), nullable=True)
    
    # Metrics
    total_value = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    invested_amount = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    cash_balance = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    total_return = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    total_return_pct = Column(Numeric(precision=8, scale=4), nullable=False, default=0)
    annualized_return = Column(Numeric(precision=8, scale=4), nullable=True)
    time_weighted_return = Column(Numeric(precision=8, scale=4), nullable=True)
    
    # Portfolio attribution
    portfolio_contribution = Column(Numeric(precision=8, scale=4), nullable=False, default=0)
    portfolio_weight = Column(Numeric(precision=5, scale=2), nullable=False, default=0)
    
    # Dividend metrics
    total_dividends = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    dividend_yield = Column(Numeric(precision=8, scale=4), nullable=False, default=0)
    monthly_dividend_avg = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    
    # Risk metrics
    volatility = Column(Numeric(precision=8, scale=4), nullable=True)
    sharpe_ratio = Column(Numeric(precision=8, scale=4), nullable=True)
    max_drawdown = Column(Numeric(precision=8, scale=4), nullable=True)
    beta = Column(Numeric(precision=8, scale=4), nullable=True)
    risk_category = Column(SQLEnum(RiskCategoryEnum), nullable=True)
    risk_score = Column(Numeric(precision=5, scale=2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    last_rebalanced = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("PortfolioTable", back_populates="pies")
    positions = relationship("PositionTable", 
                           foreign_keys="PositionTable.pie_id",
                           back_populates="pie", 
                           cascade="all, delete-orphan")
    dividends = relationship("DividendTable", back_populates="pie", cascade="all, delete-orphan")
    performance_snapshots = relationship("PerformanceSnapshotTable", 
                                       foreign_keys="PerformanceSnapshotTable.pie_id",
                                       back_populates="pie", 
                                       cascade="all, delete-orphan")


class PositionTable(Base):
    """Position database table."""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=True, index=True)
    pie_id = Column(String, ForeignKey("pies.id"), nullable=True, index=True)
    
    # Security identification
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    # Position data
    quantity = Column(Numeric(precision=15, scale=6), nullable=False)
    average_price = Column(Numeric(precision=15, scale=6), nullable=False)
    current_price = Column(Numeric(precision=15, scale=6), nullable=False)
    market_value = Column(Numeric(precision=15, scale=2), nullable=False)
    unrealized_pnl = Column(Numeric(precision=15, scale=2), nullable=False)
    unrealized_pnl_pct = Column(Numeric(precision=8, scale=4), nullable=False)
    
    # Classification
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)
    currency = Column(String, nullable=False, default="USD")
    asset_type = Column(SQLEnum(AssetTypeEnum), nullable=False)
    
    # Timestamps
    last_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("PortfolioTable", 
                           foreign_keys=[portfolio_id],
                           back_populates="individual_positions")
    pie = relationship("PieTable", 
                      foreign_keys=[pie_id],
                      back_populates="positions")


class DividendTable(Base):
    """Dividend database table."""
    __tablename__ = "dividends"
    
    id = Column(String, primary_key=True, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    pie_id = Column(String, ForeignKey("pies.id"), nullable=True, index=True)
    
    # Security identification
    symbol = Column(String, nullable=False, index=True)
    security_name = Column(String, nullable=False)
    
    # Dividend details
    dividend_type = Column(SQLEnum(DividendTypeEnum), nullable=False)
    amount_per_share = Column(Numeric(precision=15, scale=6), nullable=False)
    total_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    shares_held = Column(Numeric(precision=15, scale=6), nullable=False)
    
    # Dates
    ex_dividend_date = Column(Date, nullable=False)
    record_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=False)
    
    # Tax information
    gross_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    tax_withheld = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    net_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    
    # Currency
    currency = Column(String, nullable=False, default="USD")
    exchange_rate = Column(Numeric(precision=15, scale=6), nullable=True)
    base_currency_amount = Column(Numeric(precision=15, scale=2), nullable=True)
    
    # Reinvestment
    is_reinvested = Column(Boolean, nullable=False, default=False)
    reinvested_shares = Column(Numeric(precision=15, scale=6), nullable=True)
    reinvestment_price = Column(Numeric(precision=15, scale=6), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    portfolio = relationship("PortfolioTable", back_populates="dividends")
    pie = relationship("PieTable", back_populates="dividends")


class HistoricalDataTable(Base):
    """Historical price data table."""
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    price_date = Column(Date, nullable=False, index=True)
    
    # Price data
    open_price = Column(Numeric(precision=15, scale=6), nullable=True)
    high_price = Column(Numeric(precision=15, scale=6), nullable=True)
    low_price = Column(Numeric(precision=15, scale=6), nullable=True)
    close_price = Column(Numeric(precision=15, scale=6), nullable=False)
    adjusted_close = Column(Numeric(precision=15, scale=6), nullable=True)
    volume = Column(Integer, nullable=True)
    
    # Metadata
    currency = Column(String, nullable=False, default="USD")
    data_source = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Unique constraint on symbol and date
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class PerformanceSnapshotTable(Base):
    """Performance snapshot table for historical tracking."""
    __tablename__ = "performance_snapshots"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=True, index=True)
    pie_id = Column(String, ForeignKey("pies.id"), nullable=True, index=True)
    entity_type = Column(String, nullable=False)  # 'portfolio' or 'pie'
    
    # Time period
    snapshot_date = Column(Date, nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Performance metrics
    start_value = Column(Numeric(precision=15, scale=2), nullable=False)
    end_value = Column(Numeric(precision=15, scale=2), nullable=False)
    total_return = Column(Numeric(precision=15, scale=2), nullable=False)
    total_return_pct = Column(Numeric(precision=8, scale=4), nullable=False)
    
    # Cash flows
    dividends_received = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    contributions = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    withdrawals = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    portfolio = relationship("PortfolioTable", 
                           foreign_keys=[portfolio_id],
                           back_populates="performance_snapshots")
    pie = relationship("PieTable", 
                      foreign_keys=[pie_id],
                      back_populates="performance_snapshots")