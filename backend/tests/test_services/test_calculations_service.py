"""
Tests for the financial calculations service.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np

from app.services.calculations_service import CalculationsService
from app.models.position import Position
from app.models.dividend import Dividend
from app.models.historical import HistoricalData, PricePoint
from app.models.enums import AssetType, DividendType


class TestCalculationsService:
    """Test cases for CalculationsService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calc_service = CalculationsService()
        
        # Sample positions
        self.positions = [
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=Decimal('10'),
                average_price=Decimal('150.00'),
                current_price=Decimal('160.00'),
                market_value=Decimal('1600.00'),
                unrealized_pnl=Decimal('100.00'),
                unrealized_pnl_pct=Decimal('6.67'),
                sector="Technology",
                industry="Consumer Electronics",
                country="US",
                asset_type=AssetType.STOCK
            ),
            Position(
                symbol="MSFT",
                name="Microsoft Corporation",
                quantity=Decimal('5'),
                average_price=Decimal('300.00'),
                current_price=Decimal('320.00'),
                market_value=Decimal('1600.00'),
                unrealized_pnl=Decimal('100.00'),
                unrealized_pnl_pct=Decimal('6.67'),
                sector="Technology",
                industry="Software",
                country="US",
                asset_type=AssetType.STOCK
            ),
            Position(
                symbol="SPY",
                name="SPDR S&P 500 ETF",
                quantity=Decimal('20'),
                average_price=Decimal('400.00'),
                current_price=Decimal('420.00'),
                market_value=Decimal('8400.00'),
                unrealized_pnl=Decimal('400.00'),
                unrealized_pnl_pct=Decimal('5.00'),
                sector="Diversified",
                industry="ETF",
                country="US",
                asset_type=AssetType.ETF
            )
        ]
        
        # Sample dividends
        self.dividends = [
            Dividend(
                symbol="AAPL",
                security_name="Apple Inc.",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal('0.88'),
                total_amount=Decimal('8.80'),
                shares_held=Decimal('10'),
                ex_dividend_date=date.today() - timedelta(days=30),
                payment_date=date.today() - timedelta(days=15),
                gross_amount=Decimal('8.80'),
                tax_withheld=Decimal('0.00'),
                net_amount=Decimal('8.80'),
                is_reinvested=False
            ),
            Dividend(
                symbol="MSFT",
                security_name="Microsoft Corporation",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal('2.72'),
                total_amount=Decimal('13.60'),
                shares_held=Decimal('5'),
                ex_dividend_date=date.today() - timedelta(days=60),
                payment_date=date.today() - timedelta(days=45),
                gross_amount=Decimal('13.60'),
                tax_withheld=Decimal('0.00'),
                net_amount=Decimal('13.60'),
                is_reinvested=True
            )
        ]
    
    def test_calculate_sector_allocation(self):
        """Test sector allocation calculation."""
        allocation = self.calc_service._calculate_sector_allocation(self.positions)
        
        # Total value is 11,600 (1600 + 1600 + 8400)
        # Technology: 3200 / 11600 = 27.59%
        # Diversified: 8400 / 11600 = 72.41%
        
        assert "Technology" in allocation
        assert "Diversified" in allocation
        assert abs(allocation["Technology"] - Decimal('27.59')) < Decimal('0.1')
        assert abs(allocation["Diversified"] - Decimal('72.41')) < Decimal('0.1')
    
    def test_calculate_country_allocation(self):
        """Test country allocation calculation."""
        allocation = self.calc_service._calculate_country_allocation(self.positions)
        
        # All positions are US
        assert "US" in allocation
        assert allocation["US"] == Decimal('100')
    
    def test_calculate_asset_type_allocation(self):
        """Test asset type allocation calculation."""
        allocation = self.calc_service._calculate_asset_type_allocation(self.positions)
        
        # STOCK: 3200 / 11600 = 27.59%
        # ETF: 8400 / 11600 = 72.41%
        
        assert "STOCK" in allocation
        assert "ETF" in allocation
        assert abs(allocation["STOCK"] - Decimal('27.59')) < Decimal('0.1')
        assert abs(allocation["ETF"] - Decimal('72.41')) < Decimal('0.1')
    
    def test_calculate_diversification_metrics(self):
        """Test diversification metrics calculation."""
        div_score, conc_risk, top_10_weight = self.calc_service._calculate_diversification_metrics(self.positions)
        
        # With 3 positions, should have some diversification
        assert div_score > Decimal('0')
        assert conc_risk > Decimal('0')
        assert top_10_weight == Decimal('100')  # Only 3 positions, so top 10 is 100%
    
    def test_calculate_dividend_metrics(self):
        """Test dividend metrics calculation."""
        total_value = Decimal('11600')  # Sum of position values
        metrics = self.calc_service._calculate_dividend_metrics(self.dividends, total_value)
        
        assert metrics['total_dividends'] == Decimal('22.40')  # 8.80 + 13.60
        assert metrics['dividend_yield'] > Decimal('0')
        assert metrics['annual_projection'] >= Decimal('0')
        assert metrics['monthly_avg'] >= Decimal('0')
    
    def test_calculate_concentration_analysis(self):
        """Test concentration analysis."""
        analysis = self.calc_service.calculate_concentration_analysis(self.positions)
        
        assert 'herfindahl_index' in analysis
        assert 'concentration_level' in analysis
        assert 'top_holdings' in analysis
        assert 'concentration_buckets' in analysis
        
        # Should have 3 holdings in top holdings
        assert len(analysis['top_holdings']) == 3
        
        # Check that top holding is SPY (largest position)
        assert analysis['top_holdings'][0]['symbol'] == 'SPY'
    
    def test_calculate_diversification_score(self):
        """Test diversification score calculation."""
        scores = self.calc_service.calculate_diversification_score(self.positions)
        
        assert 'overall_score' in scores
        assert 'sector_diversification' in scores
        assert 'geographical_diversification' in scores
        assert 'asset_type_diversification' in scores
        assert 'position_count_score' in scores
        
        # All scores should be between 0 and 100
        for score in scores.values():
            assert Decimal('0') <= score <= Decimal('100')
    
    def test_comprehensive_dividend_analysis(self):
        """Test comprehensive dividend analysis."""
        analysis = self.calc_service.calculate_comprehensive_dividend_analysis(
            self.dividends, self.positions
        )
        
        assert 'total_dividends' in analysis
        assert 'reinvestment_rate' in analysis
        assert 'current_yield' in analysis
        assert 'monthly_analysis' in analysis
        assert 'security_analysis' in analysis
        assert 'projections' in analysis
        assert 'growth_analysis' in analysis
        
        # Check that we have the expected dividend total
        assert analysis['total_dividends'] == Decimal('22.40')
        
        # Check that reinvestment rate is calculated correctly
        # MSFT dividend (13.60) was reinvested, AAPL (8.80) was not
        expected_reinvestment_rate = Decimal('13.60') / Decimal('22.40') * 100
        assert abs(analysis['reinvestment_rate'] - expected_reinvestment_rate) < Decimal('0.1')
    
    def test_empty_positions_handling(self):
        """Test handling of empty positions list."""
        empty_positions = []
        
        # Should not raise errors and return sensible defaults
        allocation = self.calc_service._calculate_sector_allocation(empty_positions)
        assert allocation == {}
        
        div_score, conc_risk, top_10_weight = self.calc_service._calculate_diversification_metrics(empty_positions)
        assert div_score == Decimal('0')
        assert conc_risk == Decimal('0')
        assert top_10_weight == Decimal('0')
    
    def test_empty_dividends_handling(self):
        """Test handling of empty dividends list."""
        empty_dividends = []
        
        analysis = self.calc_service.calculate_comprehensive_dividend_analysis(
            empty_dividends, self.positions
        )
        
        # Should return default analysis structure
        assert analysis['total_dividends'] == Decimal('0')
        assert analysis['current_yield'] == Decimal('0')
        assert analysis['reinvestment_rate'] == Decimal('0')
    
    def test_portfolio_metrics_calculation(self):
        """Test portfolio metrics calculation."""
        metrics = self.calc_service.calculate_portfolio_metrics(self.positions)
        
        # Check basic calculations
        expected_total_value = Decimal('11600')  # 1600 + 1600 + 8400
        expected_total_invested = Decimal('11000')  # 1500 + 1500 + 8000
        expected_total_return = expected_total_value - expected_total_invested
        
        assert metrics.total_value == expected_total_value
        assert metrics.total_invested == expected_total_invested
        assert metrics.total_return == expected_total_return
        
        # Check that allocations are calculated
        assert len(metrics.sector_allocation) > 0
        assert len(metrics.asset_type_allocation) > 0
        
        # Check diversification metrics
        assert metrics.diversification_score >= Decimal('0')
        assert metrics.concentration_risk >= Decimal('0')