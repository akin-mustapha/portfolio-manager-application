"""
Enums for the Trading 212 Portfolio Dashboard models.
"""

from enum import Enum


class AssetType(str, Enum):
    """Asset type classification for positions."""
    STOCK = "STOCK"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    BOND = "BOND"
    COMMODITY = "COMMODITY"
    CASH = "CASH"


class RiskCategory(str, Enum):
    """Risk category classification for portfolios and pies."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DividendType(str, Enum):
    """Type of dividend payment."""
    ORDINARY = "ORDINARY"
    SPECIAL = "SPECIAL"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
    STOCK = "STOCK"
    REINVESTED = "REINVESTED"
    CASH = "CASH"  # Backward compatibility


class TransactionType(str, Enum):
    """Type of transaction."""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    FEE = "FEE"