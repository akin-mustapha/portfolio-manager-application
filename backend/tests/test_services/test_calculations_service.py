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
from app.models.enums import AssetType, DividendType, RiskCategory
from app.models.pie import Pie


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
        
        # Sample historical data for risk calculations
        self.historical_data = self._create_sample_historical_data()
        
        # Sample benchmark data
        self.benchmark_data = self._create_sample_benchmark_data()
    
    def _create_sample_historical_data(self) -> dict:
        """Create sample historical data for testing."""
        base_date = date.today() - timedelta(days=252)  # 1 year of data
        end_date = date.today() - timedelta(days=1)
        
        # AAPL historical data with known volatility pattern
        aapl_prices = []
        price = 150.0
        for i in range(252):
            # Simulate daily returns with known volatility (~20% annual)
            daily_return = np.random.normal(0.0008, 0.0127)  # ~20% annual volatility
            price *= (1 + daily_return)
            aapl_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i),
                open_price=Decimal(str(price * 0.999)),
                high_price=Decimal(str(price * 1.002)),
                low_price=Decimal(str(price * 0.998)),
                close_price=Decimal(str(price)),
                volume=1000000
            ))
        
        # MSFT historical data
        msft_prices = []
        price = 300.0
        for i in range(252):
            daily_return = np.random.normal(0.0008, 0.0110)  # ~17% annual volatility
            price *= (1 + daily_return)
            msft_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i),
                open_price=Decimal(str(price * 0.999)),
                high_price=Decimal(str(price * 1.002)),
                low_price=Decimal(str(price * 0.998)),
                close_price=Decimal(str(price)),
                volume=800000
            ))
        
        # SPY historical data (lower volatility)
        spy_prices = []
        price = 400.0
        for i in range(252):
            daily_return = np.random.normal(0.0008, 0.0079)  # ~12.5% annual volatility
            price *= (1 + daily_return)
            spy_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i),
                open_price=Decimal(str(price * 0.999)),
                high_price=Decimal(str(price * 1.002)),
                low_price=Decimal(str(price * 0.998)),
                close_price=Decimal(str(price)),
                volume=50000000
            ))
        
        return {
            "AAPL": HistoricalData(
                symbol="AAPL", 
                price_history=aapl_prices,
                start_date=base_date,
                end_date=end_date
            ),
            "MSFT": HistoricalData(
                symbol="MSFT", 
                price_history=msft_prices,
                start_date=base_date,
                end_date=end_date
            ),
            "SPY": HistoricalData(
                symbol="SPY", 
                price_history=spy_prices,
                start_date=base_date,
                end_date=end_date
            )
        }
    
    def _create_sample_benchmark_data(self) -> HistoricalData:
        """Create sample benchmark data for testing."""
        base_date = date.today() - timedelta(days=252)
        end_date = date.today() - timedelta(days=1)
        benchmark_prices = []
        price = 4000.0  # S&P 500 index level
        
        for i in range(252):
            daily_return = np.random.normal(0.0008, 0.0079)  # Market return pattern
            price *= (1 + daily_return)
            benchmark_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i),
                open_price=Decimal(str(price * 0.999)),
                high_price=Decimal(str(price * 1.002)),
                low_price=Decimal(str(price * 0.998)),
                close_price=Decimal(str(price)),
                volume=0
            ))
        
        return HistoricalData(
            symbol="SPX", 
            price_history=benchmark_prices,
            start_date=base_date,
            end_date=end_date
        )
    
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


class TestFinancialCalculationsAccuracy:
    """Test financial calculations accuracy with known datasets."""
    
    def setup_method(self):
        """Set up test fixtures with known financial data."""
        self.calc_service = CalculationsService()
        
        # Create positions with known values for precise testing
        self.test_positions = [
            Position(
                symbol="TEST1",
                name="Test Stock 1",
                quantity=Decimal('100'),
                average_price=Decimal('50.00'),
                current_price=Decimal('55.00'),
                market_value=Decimal('5500.00'),
                unrealized_pnl=Decimal('500.00'),
                unrealized_pnl_pct=Decimal('10.00'),
                sector="Technology",
                industry="Software",
                country="US",
                asset_type=AssetType.STOCK
            ),
            Position(
                symbol="TEST2",
                name="Test Stock 2",
                quantity=Decimal('50'),
                average_price=Decimal('100.00'),
                current_price=Decimal('90.00'),
                market_value=Decimal('4500.00'),
                unrealized_pnl=Decimal('-500.00'),
                unrealized_pnl_pct=Decimal('-10.00'),
                sector="Healthcare",
                industry="Pharmaceuticals",
                country="US",
                asset_type=AssetType.STOCK
            )
        ]
        
        # Create known historical data for precise volatility testing
        self.known_historical_data = self._create_known_historical_data()
    
    def _create_known_historical_data(self) -> dict:
        """Create historical data with known statistical properties."""
        base_date = date.today() - timedelta(days=100)
        
        # Create TEST1 data with exactly 20% annual volatility
        test1_prices = []
        prices = [50.0, 51.0, 49.5, 52.0, 50.5, 53.0, 51.5, 54.0, 52.0, 55.0]  # Known price series
        
        for i, price in enumerate(prices):
            test1_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i*10),
                open_price=Decimal(str(price)),
                high_price=Decimal(str(price * 1.01)),
                low_price=Decimal(str(price * 0.99)),
                close_price=Decimal(str(price)),
                volume=100000
            ))
        
        # Create TEST2 data with known negative trend
        test2_prices = []
        prices = [100.0, 98.0, 96.0, 94.0, 92.0, 90.0, 88.0, 86.0, 88.0, 90.0]  # Known declining series
        
        for i, price in enumerate(prices):
            test2_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i*10),
                open_price=Decimal(str(price)),
                high_price=Decimal(str(price * 1.01)),
                low_price=Decimal(str(price * 0.99)),
                close_price=Decimal(str(price)),
                volume=80000
            ))
        
        return {
            "TEST1": HistoricalData(
                symbol="TEST1", 
                price_history=test1_prices,
                start_date=base_date,
                end_date=base_date + timedelta(days=90)
            ),
            "TEST2": HistoricalData(
                symbol="TEST2", 
                price_history=test2_prices,
                start_date=base_date,
                end_date=base_date + timedelta(days=90)
            )
        }
    
    def test_portfolio_returns_calculation_accuracy(self):
        """Test portfolio returns calculation with known data."""
        returns = self.calc_service._calculate_portfolio_returns(
            self.test_positions, self.known_historical_data
        )
        
        # Should have returns data
        assert len(returns) > 0
        assert isinstance(returns, pd.Series)
        
        # Returns should be reasonable (between -50% and +50% daily)
        assert all(returns.between(-0.5, 0.5))
    
    def test_risk_metrics_calculation_accuracy(self):
        """Test risk metrics calculation accuracy."""
        returns = self.calc_service._calculate_portfolio_returns(
            self.test_positions, self.known_historical_data
        )
        
        if len(returns) > 0:
            risk_metrics = self.calc_service._calculate_risk_metrics(returns)
            
            # Volatility should be positive
            assert risk_metrics.volatility > Decimal('0')
            
            # Max drawdown should be non-negative
            assert risk_metrics.max_drawdown >= Decimal('0')
            
            # Risk category should be valid
            assert risk_metrics.risk_category in [RiskCategory.LOW, RiskCategory.MEDIUM, RiskCategory.HIGH]
            
            # Risk score should be between 0 and 100
            assert Decimal('0') <= risk_metrics.risk_score <= Decimal('100')
    
    def test_annualized_return_calculation(self):
        """Test annualized return calculation accuracy."""
        # Create known returns series: 1% daily for 252 days = ~1200% annual
        daily_returns = pd.Series([0.01] * 252)
        
        annualized = self.calc_service._calculate_annualized_return(daily_returns)
        
        # Should be approximately 1200% (compound growth)
        expected = (1.01 ** 252 - 1) * 100
        assert abs(float(annualized) - expected) < 1.0  # Within 1% tolerance
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation with known data."""
        # Create returns with known mean and std
        np.random.seed(42)  # For reproducible results
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))  # 0.1% daily mean, 2% daily std
        
        risk_metrics = self.calc_service._calculate_risk_metrics(returns)
        
        # Sharpe ratio should be calculated
        assert risk_metrics.sharpe_ratio is not None
        
        # Should be reasonable value (typically between -3 and 3)
        assert -3 <= float(risk_metrics.sharpe_ratio) <= 3
    
    def test_beta_calculation_accuracy(self):
        """Test beta calculation with known correlation."""
        # Create correlated returns
        np.random.seed(42)
        market_returns = pd.Series(np.random.normal(0.0008, 0.01, 100))
        
        # Create portfolio returns with beta = 1.5
        portfolio_returns = 1.5 * market_returns + pd.Series(np.random.normal(0, 0.005, 100))
        
        # Create benchmark data from market returns
        base_date = date.today() - timedelta(days=100)
        benchmark_prices = []
        price = 1000.0
        
        for i, ret in enumerate(market_returns):
            price *= (1 + ret)
            benchmark_prices.append(PricePoint(
                price_date=base_date + timedelta(days=i),
                open_price=Decimal(str(price)),
                high_price=Decimal(str(price)),
                low_price=Decimal(str(price)),
                close_price=Decimal(str(price)),
                volume=0
            ))
        
        benchmark_data = HistoricalData(
            symbol="BENCH", 
            price_history=benchmark_prices,
            start_date=base_date,
            end_date=base_date + timedelta(days=99)
        )
        risk_metrics = self.calc_service._calculate_risk_metrics(portfolio_returns, benchmark_data)
        
        # Beta should be approximately 1.5
        if risk_metrics.beta:
            assert abs(float(risk_metrics.beta) - 1.5) < 0.3  # Within 0.3 tolerance
    
    def test_dividend_yield_calculation_accuracy(self):
        """Test dividend yield calculation with known values."""
        # Create dividends with known total
        test_dividends = [
            Dividend(
                symbol="TEST1",
                security_name="Test Stock 1",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal('1.00'),
                total_amount=Decimal('100.00'),  # 100 shares * $1.00
                shares_held=Decimal('100'),
                ex_dividend_date=date.today() - timedelta(days=90),
                payment_date=date.today() - timedelta(days=75),
                gross_amount=Decimal('100.00'),
                tax_withheld=Decimal('0.00'),
                net_amount=Decimal('100.00'),
                is_reinvested=False
            ),
            Dividend(
                symbol="TEST1",
                security_name="Test Stock 1",
                dividend_type=DividendType.CASH,
                amount_per_share=Decimal('1.00'),
                total_amount=Decimal('100.00'),
                shares_held=Decimal('100'),
                ex_dividend_date=date.today() - timedelta(days=180),
                payment_date=date.today() - timedelta(days=165),
                gross_amount=Decimal('100.00'),
                tax_withheld=Decimal('0.00'),
                net_amount=Decimal('100.00'),
                is_reinvested=False
            )
        ]
        
        total_value = Decimal('5500.00')  # TEST1 market value
        metrics = self.calc_service._calculate_dividend_metrics(test_dividends, total_value)
        
        # Total dividends should be $200
        assert metrics['total_dividends'] == Decimal('200.00')
        
        # Dividend yield should be 200/5500 * 100 = 3.636%
        expected_yield = Decimal('200.00') / total_value * 100
        assert abs(metrics['dividend_yield'] - expected_yield) < Decimal('0.01')
    
    def test_allocation_calculation_precision(self):
        """Test allocation calculations with precise values."""
        # Total value: 5500 + 4500 = 10000
        sector_allocation = self.calc_service._calculate_sector_allocation(self.test_positions)
        
        # Technology: 5500/10000 = 55%
        # Healthcare: 4500/10000 = 45%
        assert sector_allocation["Technology"] == Decimal('55.00')
        assert sector_allocation["Healthcare"] == Decimal('45.00')
        
        # Should sum to 100%
        total_allocation = sum(sector_allocation.values())
        assert abs(total_allocation - Decimal('100.00')) < Decimal('0.01')


class TestFinancialCalculationsEdgeCases:
    """Test edge cases for financial calculations."""
    
    def setup_method(self):
        """Set up test fixtures for edge cases."""
        self.calc_service = CalculationsService()
    
    def test_zero_positions_handling(self):
        """Test handling of zero positions."""
        empty_positions = []
        
        # Portfolio metrics with empty positions
        metrics = self.calc_service.calculate_portfolio_metrics(empty_positions)
        assert metrics.total_value == Decimal('0')
        assert metrics.total_invested == Decimal('0')
        assert metrics.total_return == Decimal('0')
        assert metrics.sector_allocation == {}
        
        # Allocation calculations
        allocation = self.calc_service._calculate_sector_allocation(empty_positions)
        assert allocation == {}
        
        # Diversification metrics
        div_score, conc_risk, top_10_weight = self.calc_service._calculate_diversification_metrics(empty_positions)
        assert div_score == Decimal('0')
        assert conc_risk == Decimal('0')
        assert top_10_weight == Decimal('0')
    
    def test_zero_market_value_positions(self):
        """Test positions with zero market value."""
        zero_value_positions = [
            Position(
                symbol="ZERO1",
                name="Zero Value Stock",
                quantity=Decimal('100'),
                average_price=Decimal('10.00'),
                current_price=Decimal('0.00'),
                market_value=Decimal('0.00'),
                unrealized_pnl=Decimal('-1000.00'),
                unrealized_pnl_pct=Decimal('-100.00'),
                sector="Technology",
                industry="Software",
                country="US",
                asset_type=AssetType.STOCK
            )
        ]
        
        metrics = self.calc_service.calculate_portfolio_metrics(zero_value_positions)
        assert metrics.total_value == Decimal('0')
        assert metrics.total_invested == Decimal('1000.00')
        assert metrics.total_return == Decimal('-1000.00')
        assert metrics.total_return_pct == Decimal('-100.00')
    
    def test_negative_returns_handling(self):
        """Test handling of negative returns."""
        # Create returns series with significant negative returns
        negative_returns = pd.Series([-0.05, -0.03, -0.08, -0.02, -0.10, 0.01, -0.04])
        
        risk_metrics = self.calc_service._calculate_risk_metrics(negative_returns)
        
        # Should handle negative returns without errors
        assert risk_metrics.volatility > Decimal('0')
        assert risk_metrics.max_drawdown > Decimal('0')
        
        # VaR should be negative (representing losses)
        if risk_metrics.var_95:
            assert risk_metrics.var_95 < Decimal('0')
    
    def test_missing_historical_data(self):
        """Test handling of missing historical data."""
        positions = [
            Position(
                symbol="MISSING",
                name="Missing Data Stock",
                quantity=Decimal('100'),
                average_price=Decimal('50.00'),
                current_price=Decimal('55.00'),
                market_value=Decimal('5500.00'),
                unrealized_pnl=Decimal('500.00'),
                unrealized_pnl_pct=Decimal('10.00'),
                sector="Technology",
                industry="Software",
                country="US",
                asset_type=AssetType.STOCK
            )
        ]
        
        # Empty historical data
        empty_historical = {}
        
        returns = self.calc_service._calculate_portfolio_returns(positions, empty_historical)
        assert len(returns) == 0
        
        # Portfolio metrics should still work without historical data
        metrics = self.calc_service.calculate_portfolio_metrics(positions, empty_historical)
        assert metrics.total_value == Decimal('5500.00')
        assert metrics.annualized_return is None
        assert metrics.risk_metrics is None
    
    def test_single_data_point_historical(self):
        """Test handling of historical data with single data point."""
        single_point_data = {
            "TEST": HistoricalData(
                symbol="TEST",
                price_history=[
                    PricePoint(
                        price_date=date.today(),
                        open_price=Decimal('100.00'),
                        high_price=Decimal('100.00'),
                        low_price=Decimal('100.00'),
                        close_price=Decimal('100.00'),
                        volume=1000
                    )
                ],
                start_date=date.today(),
                end_date=date.today()
            )
        }
        
        positions = [
            Position(
                symbol="TEST",
                name="Test Stock",
                quantity=Decimal('10'),
                average_price=Decimal('100.00'),
                current_price=Decimal('100.00'),
                market_value=Decimal('1000.00'),
                unrealized_pnl=Decimal('0.00'),
                unrealized_pnl_pct=Decimal('0.00'),
                sector="Technology",
                industry="Software",
                country="US",
                asset_type=AssetType.STOCK
            )
        ]
        
        returns = self.calc_service._calculate_portfolio_returns(positions, single_point_data)
        # Should return empty series (can't calculate returns from single point)
        assert len(returns) == 0
    
    def test_extreme_volatility_handling(self):
        """Test handling of extreme volatility scenarios."""
        # Create extremely volatile returns (daily swings of ±50%)
        extreme_returns = pd.Series([0.5, -0.5, 0.5, -0.5, 0.5, -0.5] * 10)
        
        risk_metrics = self.calc_service._calculate_risk_metrics(extreme_returns)
        
        # Should handle extreme volatility (volatility is annualized, so ~8% daily = ~127% annual)
        assert risk_metrics.volatility > Decimal('5')  # High volatility
        assert risk_metrics.risk_category == RiskCategory.HIGH
        assert risk_metrics.max_drawdown > Decimal('40')  # High drawdown expected
    
    def test_zero_dividend_handling(self):
        """Test handling of zero dividends."""
        empty_dividends = []
        total_value = Decimal('10000.00')
        
        metrics = self.calc_service._calculate_dividend_metrics(empty_dividends, total_value)
        
        assert metrics['total_dividends'] == Decimal('0')
        assert metrics['dividend_yield'] == Decimal('0')
        assert metrics['annual_projection'] == Decimal('0')
        assert metrics['monthly_avg'] == Decimal('0')
        assert metrics['reinvestment_rate'] == Decimal('0')
    
    def test_division_by_zero_protection(self):
        """Test protection against division by zero in calculations."""
        # Test with zero total invested
        zero_invested_position = Position(
            symbol="FREE",
            name="Free Stock",
            quantity=Decimal('100'),
            average_price=Decimal('0.00'),  # Free stock
            current_price=Decimal('10.00'),
            market_value=Decimal('1000.00'),
            unrealized_pnl=Decimal('1000.00'),
            unrealized_pnl_pct=Decimal('0.00'),  # Can't calculate percentage
            sector="Technology",
            industry="Software",
            country="US",
            asset_type=AssetType.STOCK
        )
        
        metrics = self.calc_service.calculate_portfolio_metrics([zero_invested_position])
        
        # Should handle zero invested amount gracefully
        assert metrics.total_value == Decimal('1000.00')
        assert metrics.total_invested == Decimal('0.00')
        # Return percentage should be 0 when invested amount is 0
        assert metrics.total_return_pct == Decimal('0')
    
    def test_very_small_numbers_precision(self):
        """Test precision with very small numbers."""
        tiny_position = Position(
            symbol="TINY",
            name="Tiny Stock",
            quantity=Decimal('0.001'),
            average_price=Decimal('0.01'),
            current_price=Decimal('0.02'),
            market_value=Decimal('0.00002'),
            unrealized_pnl=Decimal('0.00001'),
            unrealized_pnl_pct=Decimal('100.00'),
            sector="Technology",
            industry="Software",
            country="US",
            asset_type=AssetType.STOCK
        )
        
        metrics = self.calc_service.calculate_portfolio_metrics([tiny_position])
        
        # Should handle very small numbers without precision loss
        assert metrics.total_value == Decimal('0.00002')
        assert metrics.total_invested == Decimal('0.00001')
        assert metrics.total_return == Decimal('0.00001')
    
    def test_large_numbers_handling(self):
        """Test handling of very large numbers."""
        large_position = Position(
            symbol="LARGE",
            name="Large Stock",
            quantity=Decimal('1000000'),
            average_price=Decimal('1000.00'),
            current_price=Decimal('1100.00'),
            market_value=Decimal('1100000000.00'),  # 1.1 billion
            unrealized_pnl=Decimal('100000000.00'),  # 100 million
            unrealized_pnl_pct=Decimal('10.00'),
            sector="Technology",
            industry="Software",
            country="US",
            asset_type=AssetType.STOCK
        )
        
        metrics = self.calc_service.calculate_portfolio_metrics([large_position])
        
        # Should handle large numbers correctly
        assert metrics.total_value == Decimal('1100000000.00')
        assert metrics.total_invested == Decimal('1000000000.00')
        assert metrics.total_return == Decimal('100000000.00')
        assert metrics.total_return_pct == Decimal('10.00')