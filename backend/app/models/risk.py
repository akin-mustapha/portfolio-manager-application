"""
Risk metrics models for portfolio and pie risk analysis.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from .enums import RiskCategory


class RiskMetrics(BaseModel):
    """Risk metrics for portfolios and pies."""
    
    # Volatility metrics
    volatility: Decimal = Field(..., ge=0, description="Annualized volatility (standard deviation)")
    volatility_30d: Optional[Decimal] = Field(None, ge=0, description="30-day rolling volatility")
    volatility_90d: Optional[Decimal] = Field(None, ge=0, description="90-day rolling volatility")
    
    # Risk-adjusted returns
    sharpe_ratio: Optional[Decimal] = Field(None, description="Sharpe ratio (risk-adjusted return)")
    sortino_ratio: Optional[Decimal] = Field(None, description="Sortino ratio (downside risk-adjusted)")
    
    # Drawdown metrics
    max_drawdown: Decimal = Field(..., description="Maximum drawdown percentage")
    max_drawdown_duration: Optional[int] = Field(None, ge=0, description="Max drawdown duration in days")
    current_drawdown: Decimal = Field(default=Decimal('0'), description="Current drawdown from peak")
    
    # Market risk metrics
    beta: Optional[Decimal] = Field(None, description="Beta vs benchmark (market sensitivity)")
    alpha: Optional[Decimal] = Field(None, description="Alpha vs benchmark (excess return)")
    correlation: Optional[Decimal] = Field(None, ge=-1, le=1, description="Correlation with benchmark")
    tracking_error: Optional[Decimal] = Field(None, ge=0, description="Tracking error vs benchmark")
    
    # Value at Risk
    var_95: Optional[Decimal] = Field(None, description="Value at Risk (95% confidence)")
    var_99: Optional[Decimal] = Field(None, description="Value at Risk (99% confidence)")
    cvar_95: Optional[Decimal] = Field(None, description="Conditional VaR (95% confidence)")
    
    # Risk categorization
    risk_category: RiskCategory = Field(..., description="Overall risk category")
    risk_score: Decimal = Field(..., ge=0, le=100, description="Risk score (0-100)")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        validate_assignment = True