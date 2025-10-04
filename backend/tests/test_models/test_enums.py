"""
Tests for enum models.
"""

import pytest
from app.models.enums import AssetType, RiskCategory, DividendType, TransactionType


class TestAssetType:
    """Test AssetType enum."""
    
    def test_asset_type_values(self):
        """Test that all expected asset types are available."""
        expected_values = {"STOCK", "ETF", "CRYPTO", "BOND", "COMMODITY", "CASH"}
        actual_values = {asset_type.value for asset_type in AssetType}
        assert actual_values == expected_values
    
    def test_asset_type_string_representation(self):
        """Test string representation of asset types."""
        assert AssetType.STOCK.value == "STOCK"
        assert AssetType.ETF.value == "ETF"
        assert AssetType.CRYPTO.value == "CRYPTO"
    
    def test_asset_type_equality(self):
        """Test asset type equality comparisons."""
        assert AssetType.STOCK == "STOCK"
        assert AssetType.ETF == "ETF"
        assert AssetType.STOCK != AssetType.ETF


class TestRiskCategory:
    """Test RiskCategory enum."""
    
    def test_risk_category_values(self):
        """Test that all expected risk categories are available."""
        expected_values = {"LOW", "MEDIUM", "HIGH", "VERY_HIGH"}
        actual_values = {risk_cat.value for risk_cat in RiskCategory}
        assert actual_values == expected_values
    
    def test_risk_category_string_representation(self):
        """Test string representation of risk categories."""
        assert RiskCategory.LOW.value == "LOW"
        assert RiskCategory.MEDIUM.value == "MEDIUM"
        assert RiskCategory.HIGH.value == "HIGH"
        assert RiskCategory.VERY_HIGH.value == "VERY_HIGH"
    
    def test_risk_category_equality(self):
        """Test risk category equality comparisons."""
        assert RiskCategory.LOW == "LOW"
        assert RiskCategory.MEDIUM == "MEDIUM"
        assert RiskCategory.LOW != RiskCategory.HIGH


class TestDividendType:
    """Test DividendType enum."""
    
    def test_dividend_type_values(self):
        """Test that all expected dividend types are available."""
        expected_values = {"CASH", "STOCK", "REINVESTED"}
        actual_values = {div_type.value for div_type in DividendType}
        assert actual_values == expected_values
    
    def test_dividend_type_string_representation(self):
        """Test string representation of dividend types."""
        assert str(DividendType.CASH) == "CASH"
        assert str(DividendType.STOCK) == "STOCK"
        assert str(DividendType.REINVESTED) == "REINVESTED"


class TestTransactionType:
    """Test TransactionType enum."""
    
    def test_transaction_type_values(self):
        """Test that all expected transaction types are available."""
        expected_values = {"BUY", "SELL", "DIVIDEND", "FEE"}
        actual_values = {trans_type.value for trans_type in TransactionType}
        assert actual_values == expected_values
    
    def test_transaction_type_string_representation(self):
        """Test string representation of transaction types."""
        assert str(TransactionType.BUY) == "BUY"
        assert str(TransactionType.SELL) == "SELL"
        assert str(TransactionType.DIVIDEND) == "DIVIDEND"
        assert str(TransactionType.FEE) == "FEE"