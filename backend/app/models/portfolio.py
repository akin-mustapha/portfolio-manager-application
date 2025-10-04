"""
Portfolio models for the main portfolio container.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator
from .pie import Pie
from .position import Position
from .risk import RiskMetrics


class PortfolioMetrics(BaseModel):
    """Comprehensive metrics for the entire portfolio."""
    
    # Value metrics
    total_value: Decimal = Field(..., ge=0, description="Total portfolio market value")
    total_invested: Decimal = Field(..., ge=0, description="Total amount invested")
    cash_balance: Decimal = Field(default=Decimal('0'), ge=0, description="Uninvested cash balance")
    
    # Return metrics
    total_return: Decimal = Field(..., description="Total return amount")
    total_return_pct: Decimal = Field(..., description="Total return percentage")
    annualized_return: Optional[Decimal] = Field(None, description="Annualized return percentage")
    time_weighted_return: Optional[Decimal] = Field(None, description="Time-weighted return")
    
    # Dividend metrics
    total_dividends: Decimal = Field(default=Decimal('0'), ge=0, description="Total dividends received")
    dividend_yield: Decimal = Field(default=Decimal('0'), ge=0, description="Portfolio dividend yield")
    annual_dividend_projection: Decimal = Field(default=Decimal('0'), ge=0, description="Projected annual dividends")
    monthly_dividend_avg: Decimal = Field(default=Decimal('0'), ge=0, description="Average monthly dividends")
    
    # Allocation metrics
    sector_allocation: Dict[str, Decimal] = Field(default_factory=dict, description="Allocation by sector")
    country_allocation: Dict[str, Decimal] = Field(default_factory=dict, description="Allocation by country")
    asset_type_allocation: Dict[str, Decimal] = Field(default_factory=dict, description="Allocation by asset type")
    
    # Diversification metrics
    diversification_score: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Diversification score")
    concentration_risk: Decimal = Field(default=Decimal('0'), ge=0, description="Concentration risk metric")
    top_10_weight: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Weight of top 10 holdings")
    
    # Risk metrics
    risk_metrics: Optional[RiskMetrics] = Field(None, description="Portfolio risk analysis")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True


class Portfolio(BaseModel):
    """Main portfolio model containing all pies and individual positions."""
    
    # Basic identification
    id: str = Field(..., description="Unique portfolio identifier")
    user_id: str = Field(..., description="User identifier")
    name: str = Field(default="Main Portfolio", description="Portfolio name")
    
    # Holdings
    pies: List[Pie] = Field(default_factory=list, description="List of pies in the portfolio")
    individual_positions: List[Position] = Field(default_factory=list, description="Individual positions outside pies")
    
    # Metrics
    metrics: PortfolioMetrics = Field(..., description="Portfolio performance and risk metrics")
    
    # Configuration
    base_currency: str = Field(default="USD", description="Base currency for calculations")
    benchmark_symbol: Optional[str] = Field(None, description="Benchmark symbol for comparison")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Portfolio creation date")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_sync: Optional[datetime] = Field(None, description="Last sync with Trading 212")
    
    @validator('pies')
    def validate_pies(cls, v):
        """Ensure pies list is valid."""
        if not isinstance(v, list):
            raise ValueError("Pies must be a list")
        return v
    
    @validator('individual_positions')
    def validate_individual_positions(cls, v):
        """Ensure individual positions list is valid."""
        if not isinstance(v, list):
            raise ValueError("Individual positions must be a list")
        return v
    
    @property
    def total_positions(self) -> int:
        """Total number of positions across all pies and individual holdings."""
        pie_positions = sum(len(pie.positions) for pie in self.pies)
        return pie_positions + len(self.individual_positions)
    
    @property
    def all_positions(self) -> List[Position]:
        """All positions from pies and individual holdings combined."""
        all_pos = []
        for pie in self.pies:
            all_pos.extend(pie.positions)
        all_pos.extend(self.individual_positions)
        return all_pos
    
    @property
    def top_holdings(self) -> List[Position]:
        """Top 10 holdings across entire portfolio by market value."""
        return sorted(self.all_positions, key=lambda p: p.market_value, reverse=True)[:10]
    
    @property
    def pie_count(self) -> int:
        """Number of pies in the portfolio."""
        return len(self.pies)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True