"""
Tests for pie-level performance calculations.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
import pandas as pd
import numpy as np
from unittest.mock import Mock

from app.services.calculations_service import CalculationsService
from app.models.pie import Pie, PieMetrics
from app.models.position import Position, AssetType
from app.models.historical import HistoricalData, PricePoint
from app.models.dividend import Dividend, DividendType
from app.models.risk import RiskCategory


class TestPieCalculations:
    """Test pie-level performance calculations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calc_service = CalculationsService()
    
    def test_calculate_pie_portfolio_contribution_basic(self):
        """Test basic pie portfolio contribution calculation."""
        portfolio_total_value = Decimal('10000.00')
        pie_return = Decimal('200.00')
        pie_value = Decimal('3200.00')
        
        contribution = self.calc_service._calculate_pie_portfolio_contribution(
            pie_return, portfolio_total_value, pie_value
        )
        
        assert contribution == Decimal('2.00')  # 200/10000 * 100
        
    def test_calculate_pie_portfolio_contribution_edge_cases(self):
        """Test pie portfolio contribution with edge cases."""
        # Zero portfolio value
        contribution = self.calc_service._calculate_pie_portfolio_contribution(
            Decimal('100.00'), Decimal('0'), Decimal('1000.00')
        )
        assert contribution == Decimal('0')
        
        # Negative return
        contribution = self.calc_service._calculate_pie_portfolio_contribution(
            Decimal('-50.00'), Decimal('10000.00'), Decimal('1000.00')
        )
        assert contribution == Decimal('-0.50')
    
    def test_calculate_pie_time_weighted_return(self):
        """Test time-weighted return calculation."""
        # Create sample returns
        returns = pd.Series([0.02, 0.01, -0.005, 0.015, 0.008])
        
        twr = self.calc_service._calculate_pie_time_weighted_return(returns)
        
        # Calculate expected TWR: (1.02 * 1.01 * 0.995 * 1.015 * 1.008) - 1
        expected = (1.02 * 1.01 * 0.995 * 1.015 * 1.008 - 1) * 100
        
        assert abs(float(twr) - expected) < 0.01
        
    def test_calculate_pie_risk_metrics(self):
        """Test pie risk metrics calculation."""
        # Create sample returns with some volatility
        returns = pd.Series([0.02, -0.01, 0.015, -0.008, 0.012, 0.005, -0.003])
        
        risk_metrics = self.calc_service._calculate_pie_risk_metrics(returns)
        
        assert risk_metrics.volatility > 0
        assert risk_metrics.max_drawdown >= 0
        assert risk_metrics.risk_category in [RiskCategory.LOW, RiskCategory.MEDIUM, RiskCategory.HIGH]
        assert risk_metrics.var_95 is not None
        
    def test_calculate_enhanced_pie_beta(self):
        """Test enhanced pie beta calculation."""
        # Create correlated returns with enough observations (minimum 10)
        portfolio_returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.008, 0.005, -0.003, 0.012, 0.007, -0.002, 0.009, 0.004])
        pie_returns = pd.Series([0.015, 0.025, -0.008, 0.018, 0.012, 0.008, -0.001, 0.016, 0.010, 0.001, 0.013, 0.006])  # Higher volatility
        
        beta = self.calc_service._calculate_enhanced_pie_beta(pie_returns, portfolio_returns)
        
        assert beta is not None
        assert float(beta) > 0  # Should be positive correlation
        assert -3.0 <= float(beta) <= 3.0  # Should be within bounds
        
    def test_calculate_enhanced_pie_beta_insufficient_data(self):
        """Test enhanced pie beta calculation with insufficient data."""
        # Create returns with less than 10 observations
        portfolio_returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.008])
        pie_returns = pd.Series([0.015, 0.025, -0.008, 0.018, 0.012])
        
        beta = self.calc_service._calculate_enhanced_pie_beta(pie_returns, portfolio_returns)
        
        assert beta is None  # Should return None for insufficient data
        
    def test_time_weighted_return_edge_cases(self):
        """Test time-weighted return with edge cases."""
        # Empty returns
        empty_returns = pd.Series(dtype=float)
        twr = self.calc_service._calculate_pie_time_weighted_return(empty_returns)
        assert twr is None
        
        # Single return
        single_return = pd.Series([0.05])
        twr = self.calc_service._calculate_pie_time_weighted_return(single_return)
        assert abs(float(twr) - 5.0) < 0.01