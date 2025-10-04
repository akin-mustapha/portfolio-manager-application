"""
Position model for individual holdings within portfolios and pies.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator
from .enums import AssetType


class Position(BaseModel):
    """Represents a single position/holding in a portfolio or pie."""
    
    symbol: str = Field(..., description="Stock/ETF symbol (e.g., AAPL, SPY)")
    name: str = Field(..., description="Full name of the security")
    quantity: Decimal = Field(..., ge=0, description="Number of shares/units held")
    average_price: Decimal = Field(..., ge=0, description="Average purchase price per share")
    current_price: Decimal = Field(..., ge=0, description="Current market price per share")
    market_value: Decimal = Field(..., ge=0, description="Current market value (quantity * current_price)")
    unrealized_pnl: Decimal = Field(..., description="Unrealized profit/loss")
    unrealized_pnl_pct: Decimal = Field(..., description="Unrealized P&L as percentage")
    
    # Classification fields
    sector: Optional[str] = Field(None, description="Sector classification (e.g., Technology)")
    industry: Optional[str] = Field(None, description="Industry classification (e.g., Software)")
    country: Optional[str] = Field(None, description="Country of domicile")
    currency: str = Field(default="USD", description="Currency of the position")
    asset_type: AssetType = Field(..., description="Type of asset")
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('market_value', always=True)
    def calculate_market_value(cls, v, values):
        """Calculate market value from quantity and current price."""
        if 'quantity' in values and 'current_price' in values:
            return values['quantity'] * values['current_price']
        return v
    
    @validator('unrealized_pnl', always=True)
    def calculate_unrealized_pnl(cls, v, values):
        """Calculate unrealized P&L."""
        if all(key in values for key in ['quantity', 'current_price', 'average_price']):
            return values['quantity'] * (values['current_price'] - values['average_price'])
        return v
    
    @validator('unrealized_pnl_pct', always=True)
    def calculate_unrealized_pnl_pct(cls, v, values):
        """Calculate unrealized P&L percentage."""
        if 'current_price' in values and 'average_price' in values and values['average_price'] > 0:
            return ((values['current_price'] - values['average_price']) / values['average_price']) * 100
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True