"""
Tests for Dividend model.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from pydantic import ValidationError

from app.models.dividend import Dividend
from app.models.enums import DividendType


class TestDividend:
    """Test Dividend model validation and functionality."""
    
    def test_valid_dividend_creation(self, sample_dividend_data):
        """Test creating a valid dividend."""
        dividend = Dividend(**sample_dividend_data)
        
        assert dividend.symbol == "AAPL"
        assert dividend.security_name == "Apple Inc."
        assert dividend.dividend_type == DividendType.CASH
        assert dividend.amount_per_share == Decimal("0.25")
        assert dividend.total_amount == Decimal("2.50")
        assert dividend.shares_held == Decimal("10")
        assert dividend.ex_dividend_date == date(2024, 1, 10)
        assert dividend.payment_date == date(2024, 1, 25)
        assert dividend.is_reinvested is False
    
    def test_negative_amount_per_share_validation(self):
        """Test that negative amount per share raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("-0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_total_amount_validation(self):
        """Test that negative total amount raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("-2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_shares_held_validation(self):
        """Test that negative shares held raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("-10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_gross_amount_validation(self):
        """Test that negative gross amount raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("-2.50"),
                net_amount=Decimal("2.50")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_tax_withheld_validation(self):
        """Test that negative tax withheld raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                tax_withheld=Decimal("-0.25"),
                net_amount=Decimal("2.25")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_net_amount_validation(self):
        """Test that negative net amount raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("-2.25")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_zero_exchange_rate_validation(self):
        """Test that zero exchange rate raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50"),
                exchange_rate=Decimal("0")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_negative_reinvested_shares_validation(self):
        """Test that negative reinvested shares raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.REINVESTED,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50"),
                is_reinvested=True,
                reinvested_shares=Decimal("-0.5")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_zero_reinvestment_price_validation(self):
        """Test that zero reinvestment price raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.REINVESTED,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50"),
                is_reinvested=True,
                reinvestment_price=Decimal("0")
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend()
        
        error_messages = str(exc_info.value)
        assert "symbol" in error_messages
        assert "security_name" in error_messages
        assert "dividend_type" in error_messages
        assert "amount_per_share" in error_messages
        assert "total_amount" in error_messages
        assert "shares_held" in error_messages
        assert "ex_dividend_date" in error_messages
        assert "payment_date" in error_messages
        assert "gross_amount" in error_messages
        assert "net_amount" in error_messages
    
    def test_invalid_dividend_type(self):
        """Test that invalid dividend type raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type="INVALID_TYPE",
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50")
            )
        
        assert "Input should be" in str(exc_info.value)
    
    def test_default_values(self):
        """Test default values for optional fields."""
        dividend = Dividend(
            symbol="AAPL",
            security_name="Apple Inc.",
            dividend_type=DividendType.CASH,
            amount_per_share=Decimal("0.25"),
            total_amount=Decimal("2.50"),
            shares_held=Decimal("10"),
            ex_dividend_date=date(2024, 1, 10),
            payment_date=date(2024, 1, 25),
            gross_amount=Decimal("2.50"),
            net_amount=Decimal("2.50")
        )
        
        assert dividend.currency == "USD"
        assert dividend.tax_withheld == Decimal('0')
        assert dividend.is_reinvested is False
        assert isinstance(dividend.created_at, datetime)
    
    def test_json_serialization(self, sample_dividend_data):
        """Test JSON serialization of dividend."""
        dividend = Dividend(**sample_dividend_data)
        json_data = dividend.model_dump()
        
        assert json_data["symbol"] == "AAPL"
        assert json_data["dividend_type"] == "CASH"
        assert str(json_data["ex_dividend_date"]) == "2024-01-10"
        assert str(json_data["payment_date"]) == "2024-01-25"
        assert isinstance(json_data["created_at"], datetime)
    
    def test_all_dividend_types(self):
        """Test that all dividend types work correctly."""
        for div_type in DividendType:
            dividend = Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=div_type,
                amount_per_share=Decimal("0.25"),
                total_amount=Decimal("2.50"),
                shares_held=Decimal("10"),
                ex_dividend_date=date(2024, 1, 10),
                payment_date=date(2024, 1, 25),
                gross_amount=Decimal("2.50"),
                net_amount=Decimal("2.50")
            )
            assert dividend.dividend_type == div_type
    
    def test_reinvested_dividend(self):
        """Test reinvested dividend with all fields."""
        dividend = Dividend(
            symbol="AAPL",
            security_name="Apple Inc.",
            dividend_type=DividendType.REINVESTED,
            amount_per_share=Decimal("0.25"),
            total_amount=Decimal("2.50"),
            shares_held=Decimal("10"),
            ex_dividend_date=date(2024, 1, 10),
            payment_date=date(2024, 1, 25),
            gross_amount=Decimal("2.50"),
            net_amount=Decimal("2.50"),
            is_reinvested=True,
            reinvested_shares=Decimal("0.016"),
            reinvestment_price=Decimal("156.25")
        )
        
        assert dividend.is_reinvested is True
        assert dividend.reinvested_shares == Decimal("0.016")
        assert dividend.reinvestment_price == Decimal("156.25")