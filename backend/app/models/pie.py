"""
Pie models for Trading 212 pie investments.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from .position import Position
from .risk import RiskMetrics


class PieMetrics(BaseModel):
    """Performance and risk metrics for a pie."""
    
    # Value metrics
    total_value: Decimal = Field(..., ge=0, description="Current total value of the pie")
    invested_amount: Decimal = Field(..., ge=0, description="Total amount invested in the pie")
    cash_balance: Decimal = Field(default=Decimal('0'), ge=0, description="Uninvested cash in pie")
    
    # Return metrics
    total_return: Decimal = Field(..., description="Total return amount")
    total_return_pct: Decimal = Field(..., description="Total return percentage")
    annualized_return: Optional[Decimal] = Field(None, description="Annualized return percentage")
    time_weighted_return: Optional[Decimal] = Field(None, description="Time-weighted return")
    
    # Performance attribution
    portfolio_contribution: Decimal = Field(default=Decimal('0'), description="Contribution to total portfolio return")
    portfolio_weight: Decimal = Field(..., ge=0, le=100, description="Weight in total portfolio")
    
    # Dividend metrics
    total_dividends: Decimal = Field(default=Decimal('0'), ge=0, description="Total dividends received")
    dividend_yield: Decimal = Field(default=Decimal('0'), ge=0, description="Current dividend yield")
    monthly_dividend_avg: Decimal = Field(default=Decimal('0'), ge=0, description="Average monthly dividends")
    
    # Risk metrics
    risk_metrics: Optional[RiskMetrics] = Field(None, description="Risk analysis for the pie")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True


class Pie(BaseModel):
    """Represents a Trading 212 pie investment."""
    
    # Basic identification
    id: str = Field(..., description="Unique pie identifier from Trading 212")
    name: str = Field(..., description="Name of the pie")
    description: Optional[str] = Field(None, description="Pie description")
    
    # Holdings
    positions: List[Position] = Field(default_factory=list, description="Positions within the pie")
    
    # Metrics
    metrics: PieMetrics = Field(..., description="Performance and risk metrics")
    
    # Configuration
    auto_invest: bool = Field(default=False, description="Whether auto-invest is enabled")
    target_allocation: Optional[Decimal] = Field(None, ge=0, le=100, description="Target allocation in portfolio")
    
    # Metadata
    created_at: datetime = Field(..., description="Pie creation date")
    last_rebalanced: Optional[datetime] = Field(None, description="Last rebalancing date")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('positions')
    def validate_positions(cls, v):
        """Ensure positions list is valid."""
        if not isinstance(v, list):
            raise ValueError("Positions must be a list")
        return v
    
    @property
    def position_count(self) -> int:
        """Number of positions in the pie."""
        return len(self.positions)
    
    @property
    def top_holdings(self) -> List[Position]:
        """Top 10 holdings by market value."""
        return sorted(self.positions, key=lambda p: p.market_value, reverse=True)[:10]
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True