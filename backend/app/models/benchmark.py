"""
Benchmark comparison models for portfolio performance analysis.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from .historical import HistoricalData


class BenchmarkData(BaseModel):
    """Benchmark index data and metadata."""
    
    # Basic identification
    symbol: str = Field(..., description="Benchmark symbol (e.g., SPY, VTI)")
    name: str = Field(..., description="Benchmark name (e.g., S&P 500)")
    description: Optional[str] = Field(None, description="Benchmark description")
    
    # Historical data
    historical_data: HistoricalData = Field(..., description="Historical price data")
    
    # Benchmark characteristics
    asset_class: str = Field(..., description="Primary asset class (equity, bond, etc.)")
    geography: str = Field(..., description="Geographic focus (US, International, Global)")
    market_cap: Optional[str] = Field(None, description="Market cap focus (Large, Mid, Small)")
    
    # Metadata
    data_provider: Optional[str] = Field(None, description="Data provider for benchmark")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class BenchmarkComparison(BaseModel):
    """Comparison metrics between portfolio/pie and benchmark."""
    
    # Identification
    portfolio_id: Optional[str] = Field(None, description="Portfolio identifier")
    pie_id: Optional[str] = Field(None, description="Pie identifier")
    benchmark_symbol: str = Field(..., description="Benchmark symbol used for comparison")
    
    # Time period
    start_date: date = Field(..., description="Start date of comparison period")
    end_date: date = Field(..., description="End date of comparison period")
    
    # Return comparison
    portfolio_return: Decimal = Field(..., description="Portfolio/pie return for the period")
    benchmark_return: Decimal = Field(..., description="Benchmark return for the period")
    excess_return: Decimal = Field(..., description="Excess return vs benchmark")
    
    # Risk-adjusted metrics
    alpha: Optional[Decimal] = Field(None, description="Alpha (excess return adjusted for risk)")
    beta: Optional[Decimal] = Field(None, description="Beta (sensitivity to benchmark)")
    correlation: Optional[Decimal] = Field(None, ge=-1, le=1, description="Correlation with benchmark")
    tracking_error: Optional[Decimal] = Field(None, ge=0, description="Tracking error (volatility of excess returns)")
    information_ratio: Optional[Decimal] = Field(None, description="Information ratio (excess return / tracking error)")
    
    # Performance attribution
    outperformance_periods: int = Field(default=0, ge=0, description="Number of periods outperforming benchmark")
    total_periods: int = Field(..., gt=0, description="Total number of periods analyzed")
    win_rate: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Percentage of periods outperforming")
    
    # Drawdown comparison
    max_drawdown_portfolio: Decimal = Field(..., description="Maximum drawdown of portfolio/pie")
    max_drawdown_benchmark: Decimal = Field(..., description="Maximum drawdown of benchmark")
    drawdown_difference: Decimal = Field(..., description="Difference in maximum drawdowns")
    
    # Volatility comparison
    volatility_portfolio: Decimal = Field(..., ge=0, description="Portfolio/pie volatility")
    volatility_benchmark: Decimal = Field(..., ge=0, description="Benchmark volatility")
    volatility_ratio: Decimal = Field(..., gt=0, description="Ratio of portfolio to benchmark volatility")
    
    # Metadata
    calculation_date: datetime = Field(default_factory=datetime.utcnow, description="Date of calculation")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True