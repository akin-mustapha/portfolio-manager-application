"""
Dividend models for tracking dividend payments and income.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from .enums import DividendType


class Dividend(BaseModel):
    """Represents a dividend payment."""
    
    # Basic identification
    id: Optional[str] = Field(None, description="Unique dividend record identifier")
    symbol: str = Field(..., description="Symbol of the dividend-paying security")
    security_name: str = Field(..., description="Name of the dividend-paying security")
    
    # Dividend details
    dividend_type: DividendType = Field(..., description="Type of dividend payment")
    amount_per_share: Decimal = Field(..., ge=0, description="Dividend amount per share")
    total_amount: Decimal = Field(..., ge=0, description="Total dividend amount received")
    shares_held: Decimal = Field(..., ge=0, description="Number of shares held at record date")
    
    # Dates
    ex_dividend_date: date = Field(..., description="Ex-dividend date")
    record_date: Optional[date] = Field(None, description="Record date")
    payment_date: date = Field(..., description="Payment date")
    
    # Tax information
    gross_amount: Decimal = Field(..., ge=0, description="Gross dividend amount before taxes")
    tax_withheld: Decimal = Field(default=Decimal('0'), ge=0, description="Tax withheld amount")
    net_amount: Decimal = Field(..., ge=0, description="Net dividend amount after taxes")
    
    # Currency and conversion
    currency: str = Field(default="USD", description="Currency of the dividend")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate if currency conversion applied")
    base_currency_amount: Optional[Decimal] = Field(None, description="Amount in portfolio base currency")
    
    # Reinvestment
    is_reinvested: bool = Field(default=False, description="Whether dividend was reinvested")
    reinvested_shares: Optional[Decimal] = Field(None, ge=0, description="Number of shares purchased via reinvestment")
    reinvestment_price: Optional[Decimal] = Field(None, gt=0, description="Price per share for reinvestment")
    
    # Portfolio context
    portfolio_id: Optional[str] = Field(None, description="Portfolio identifier")
    pie_id: Optional[str] = Field(None, description="Pie identifier if dividend from pie holding")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        validate_assignment = True