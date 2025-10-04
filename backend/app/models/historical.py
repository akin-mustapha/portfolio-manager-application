"""
Historical data models for price history and performance tracking.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    """Single price data point."""
    
    price_date: date = Field(..., description="Date of the price point")
    open_price: Optional[Decimal] = Field(None, gt=0, description="Opening price")
    high_price: Optional[Decimal] = Field(None, gt=0, description="High price")
    low_price: Optional[Decimal] = Field(None, gt=0, description="Low price")
    close_price: Decimal = Field(..., gt=0, description="Closing price")
    volume: Optional[int] = Field(None, ge=0, description="Trading volume")
    adjusted_close: Optional[Decimal] = Field(None, gt=0, description="Adjusted closing price")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class HistoricalData(BaseModel):
    """Historical price and performance data for a security or portfolio."""
    
    # Basic identification
    symbol: str = Field(..., description="Symbol or identifier")
    name: Optional[str] = Field(None, description="Name of the security/portfolio")
    
    # Data points
    price_history: List[PricePoint] = Field(..., description="Historical price data points")
    
    # Data metadata
    start_date: date = Field(..., description="Start date of the data")
    end_date: date = Field(..., description="End date of the data")
    frequency: str = Field(default="daily", description="Data frequency (daily, weekly, monthly)")
    currency: str = Field(default="USD", description="Currency of the price data")
    
    # Data source
    data_source: Optional[str] = Field(None, description="Source of the historical data")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @property
    def data_points_count(self) -> int:
        """Number of data points in the history."""
        return len(self.price_history)
    
    @property
    def latest_price(self) -> Optional[Decimal]:
        """Most recent closing price."""
        if self.price_history:
            return self.price_history[-1].close_price
        return None
    
    @property
    def earliest_price(self) -> Optional[Decimal]:
        """Earliest closing price."""
        if self.price_history:
            return self.price_history[0].close_price
        return None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True


class PerformanceSnapshot(BaseModel):
    """Performance snapshot for a specific time period."""
    
    # Identification
    entity_id: str = Field(..., description="Portfolio or pie identifier")
    entity_type: str = Field(..., description="Type of entity (portfolio, pie)")
    
    # Time period
    snapshot_date: date = Field(..., description="Date of the snapshot")
    period_start: date = Field(..., description="Start date of the performance period")
    period_end: date = Field(..., description="End date of the performance period")
    
    # Performance metrics
    start_value: Decimal = Field(..., ge=0, description="Value at period start")
    end_value: Decimal = Field(..., ge=0, description="Value at period end")
    total_return: Decimal = Field(..., description="Total return for the period")
    total_return_pct: Decimal = Field(..., description="Total return percentage")
    
    # Additional metrics
    dividends_received: Decimal = Field(default=Decimal('0'), ge=0, description="Dividends received during period")
    contributions: Decimal = Field(default=Decimal('0'), description="Net contributions during period")
    withdrawals: Decimal = Field(default=Decimal('0'), ge=0, description="Withdrawals during period")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Snapshot creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True