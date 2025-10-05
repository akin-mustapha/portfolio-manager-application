"""
Financial calculations service for portfolio and pie metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple, Any
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.pie import Pie, PieMetrics
from app.models.position import Position
from app.models.historical import HistoricalData, PricePoint
from app.models.risk import RiskMetrics, RiskCategory
from app.models.benchmark import BenchmarkComparison
from app.models.dividend import Dividend


class CalculationsService:
    """Service for financial calculations and metrics."""
    
    def __init__(self):
        """Initialize the calculations service."""
        self.risk_free_rate = Decimal('0.02')  # 2% default risk-free rate
    
    def calculate_portfolio_metrics(
        self, 
        positions: List[Position],
        historical_data: Optional[Dict[str, HistoricalData]] = None,
        dividends: Optional[List[Dividend]] = None,
        benchmark_data: Optional[HistoricalData] = None
    ) -> PortfolioMetrics:
        """
        Calculate comprehensive portfolio-level metrics.
        
        Args:
            positions: List of current positions
            historical_data: Historical price data for positions
            dividends: Dividend history
            benchmark_data: Benchmark historical data for beta calculation
            
        Returns:
            PortfolioMetrics with all calculated metrics
        """
        # Basic value calculations
        total_value = sum(pos.market_value for pos in positions)
        total_invested = sum(pos.quantity * pos.average_price for pos in positions)
        total_return = total_value - total_invested
        total_return_pct = (total_return / total_invested * 100) if total_invested > 0 else Decimal('0')
        
        # Dividend calculations
        dividend_metrics = self._calculate_dividend_metrics(dividends, total_value) if dividends else {}
        
        # Allocation calculations
        sector_allocation = self._calculate_sector_allocation(positions)
        industry_allocation = self._calculate_industry_allocation(positions)
        country_allocation = self._calculate_country_allocation(positions)
        asset_type_allocation = self._calculate_asset_type_allocation(positions)
        
        # Diversification calculations
        diversification_score, concentration_risk, top_10_weight = self._calculate_diversification_metrics(positions)
        
        # Risk calculations (if historical data available)
        risk_metrics = None
        annualized_return = None
        time_weighted_return = None
        
        if historical_data:
            portfolio_returns = self._calculate_portfolio_returns(positions, historical_data)
            if len(portfolio_returns) > 0:
                risk_metrics = self._calculate_risk_metrics(portfolio_returns, benchmark_data)
                annualized_return = self._calculate_annualized_return(portfolio_returns)
                time_weighted_return = self._calculate_time_weighted_return(portfolio_returns)
        
        return PortfolioMetrics(
            total_value=total_value,
            total_invested=total_invested,
            total_return=total_return,
            total_return_pct=total_return_pct,
            annualized_return=annualized_return,
            time_weighted_return=time_weighted_return,
            total_dividends=dividend_metrics.get('total_dividends', Decimal('0')),
            dividend_yield=dividend_metrics.get('dividend_yield', Decimal('0')),
            annual_dividend_projection=dividend_metrics.get('annual_projection', Decimal('0')),
            monthly_dividend_avg=dividend_metrics.get('monthly_avg', Decimal('0')),
            reinvested_dividends=dividend_metrics.get('reinvested_dividends', Decimal('0')),
            withdrawn_dividends=dividend_metrics.get('withdrawn_dividends', Decimal('0')),
            reinvestment_rate=dividend_metrics.get('reinvestment_rate', Decimal('0')),
            trailing_12m_dividends=dividend_metrics.get('trailing_12m_dividends', Decimal('0')),
            dividend_growth_rate=dividend_metrics.get('dividend_growth_rate', Decimal('0')),
            sector_allocation=sector_allocation,
            industry_allocation=industry_allocation,
            country_allocation=country_allocation,
            asset_type_allocation=asset_type_allocation,
            diversification_score=diversification_score,
            concentration_risk=concentration_risk,
            top_10_weight=top_10_weight,
            risk_metrics=risk_metrics
        )
    
    def _calculate_sector_allocation(self, positions: List[Position]) -> Dict[str, Decimal]:
        """Calculate allocation by sector."""
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {}
        
        sector_values = {}
        for pos in positions:
            sector = pos.sector or "Unknown"
            sector_values[sector] = sector_values.get(sector, Decimal('0')) + pos.market_value
        
        return {
            sector: (value / total_value * 100) 
            for sector, value in sector_values.items()
        }
    
    def _calculate_industry_allocation(self, positions: List[Position]) -> Dict[str, Decimal]:
        """Calculate allocation by industry."""
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {}
        
        industry_values = {}
        for pos in positions:
            industry = pos.industry or "Unknown"
            industry_values[industry] = industry_values.get(industry, Decimal('0')) + pos.market_value
        
        return {
            industry: (value / total_value * 100) 
            for industry, value in industry_values.items()
        }
    
    def _calculate_country_allocation(self, positions: List[Position]) -> Dict[str, Decimal]:
        """Calculate allocation by country."""
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {}
        
        country_values = {}
        for pos in positions:
            country = pos.country or "Unknown"
            country_values[country] = country_values.get(country, Decimal('0')) + pos.market_value
        
        return {
            country: (value / total_value * 100) 
            for country, value in country_values.items()
        }
    
    def _calculate_asset_type_allocation(self, positions: List[Position]) -> Dict[str, Decimal]:
        """Calculate allocation by asset type."""
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {}
        
        asset_type_values = {}
        for pos in positions:
            asset_type = pos.asset_type.value
            asset_type_values[asset_type] = asset_type_values.get(asset_type, Decimal('0')) + pos.market_value
        
        return {
            asset_type: (value / total_value * 100) 
            for asset_type, value in asset_type_values.items()
        }
    
    def _calculate_diversification_metrics(self, positions: List[Position]) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate diversification score, concentration risk, and top 10 weight.
        
        Returns:
            Tuple of (diversification_score, concentration_risk, top_10_weight)
        """
        if not positions:
            return Decimal('0'), Decimal('0'), Decimal('0')
        
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return Decimal('0'), Decimal('0'), Decimal('0')
        
        # Calculate weights
        weights = [pos.market_value / total_value for pos in positions]
        
        # Herfindahl-Hirschman Index for concentration
        hhi = sum(w ** 2 for w in weights)
        
        # Diversification score (inverse of concentration, scaled 0-100)
        diversification_score = Decimal(str((1 - hhi) * 100))
        
        # Concentration risk (HHI scaled 0-100)
        concentration_risk = Decimal(str(hhi * 100))
        
        # Top 10 holdings weight
        sorted_positions = sorted(positions, key=lambda p: p.market_value, reverse=True)
        top_10_value = sum(pos.market_value for pos in sorted_positions[:10])
        top_10_weight = (top_10_value / total_value * 100) if total_value > 0 else Decimal('0')
        
        return diversification_score, concentration_risk, top_10_weight
    
    def _calculate_dividend_metrics(self, dividends: List[Dividend], total_value: Decimal) -> Dict[str, Decimal]:
        """Calculate comprehensive dividend-related metrics."""
        if not dividends:
            return {
                'total_dividends': Decimal('0'),
                'dividend_yield': Decimal('0'),
                'annual_projection': Decimal('0'),
                'monthly_avg': Decimal('0'),
                'reinvested_dividends': Decimal('0'),
                'withdrawn_dividends': Decimal('0'),
                'reinvestment_rate': Decimal('0'),
                'trailing_12m_dividends': Decimal('0'),
                'dividend_growth_rate': Decimal('0')
            }
        
        # Total dividends received
        total_dividends = sum(div.total_amount for div in dividends)
        
        # Separate reinvested vs withdrawn dividends
        reinvested_dividends = sum(div.total_amount for div in dividends if div.is_reinvested)
        withdrawn_dividends = sum(div.total_amount for div in dividends if not div.is_reinvested)
        
        # Calculate reinvestment rate
        reinvestment_rate = (reinvested_dividends / total_dividends * 100) if total_dividends > 0 else Decimal('0')
        
        # Current dividend yield based on total value
        dividend_yield = (total_dividends / total_value * 100) if total_value > 0 else Decimal('0')
        
        # Calculate trailing 12 months metrics
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_dividends = [
            div for div in dividends 
            if div.payment_date and div.payment_date >= one_year_ago.date()
        ]
        
        trailing_12m_dividends = sum(div.total_amount for div in recent_dividends)
        monthly_avg = trailing_12m_dividends / 12 if recent_dividends else Decimal('0')
        annual_projection = trailing_12m_dividends
        
        # Calculate dividend growth rate (comparing last 12 months to previous 12 months)
        two_years_ago = datetime.now() - timedelta(days=730)
        previous_year_dividends = [
            div for div in dividends 
            if div.payment_date and two_years_ago.date() <= div.payment_date < one_year_ago.date()
        ]
        
        previous_12m_total = sum(div.total_amount for div in previous_year_dividends)
        dividend_growth_rate = Decimal('0')
        if previous_12m_total > 0 and trailing_12m_dividends > 0:
            dividend_growth_rate = ((trailing_12m_dividends - previous_12m_total) / previous_12m_total * 100)
        
        return {
            'total_dividends': total_dividends,
            'dividend_yield': dividend_yield,
            'annual_projection': annual_projection,
            'monthly_avg': monthly_avg,
            'reinvested_dividends': reinvested_dividends,
            'withdrawn_dividends': withdrawn_dividends,
            'reinvestment_rate': reinvestment_rate,
            'trailing_12m_dividends': trailing_12m_dividends,
            'dividend_growth_rate': dividend_growth_rate
        }
    
    def calculate_dividend_income_analysis(
        self, 
        dividends: List[Dividend], 
        positions: List[Position],
        pie_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive dividend and income analysis.
        
        Args:
            dividends: List of dividend records
            positions: Current positions for yield calculations
            pie_id: Optional pie ID to filter dividends
            
        Returns:
            Comprehensive dividend analysis dictionary
        """
        if pie_id:
            # Filter dividends for specific pie
            dividends = [div for div in dividends if div.pie_id == pie_id]
            # Filter positions for specific pie (would need pie context)
        
        if not dividends:
            return self._get_empty_dividend_analysis()
        
        # Basic metrics
        total_value = sum(pos.market_value for pos in positions)
        dividend_metrics = self._calculate_dividend_metrics(dividends, total_value)
        
        # Monthly dividend history and trends
        monthly_history = self._calculate_monthly_dividend_history(dividends)
        
        # Dividend by security analysis
        dividend_by_security = self._calculate_dividend_by_security(dividends, positions)
        
        # Reinvestment analysis
        reinvestment_analysis = self._calculate_reinvestment_analysis(dividends)
        
        # Income projections
        income_projections = self._calculate_income_projections(dividends, positions)
        
        # Tax analysis
        tax_analysis = self._calculate_dividend_tax_analysis(dividends)
        
        return {
            'summary': dividend_metrics,
            'monthly_history': monthly_history,
            'by_security': dividend_by_security,
            'reinvestment_analysis': reinvestment_analysis,
            'income_projections': income_projections,
            'tax_analysis': tax_analysis,
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    def _calculate_monthly_dividend_history(self, dividends: List[Dividend]) -> List[Dict[str, Any]]:
        """Calculate monthly dividend history for trend analysis."""
        if not dividends:
            return []
        
        # Group dividends by month
        monthly_data = {}
        for dividend in dividends:
            if dividend.payment_date:
                month_key = dividend.payment_date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'total_amount': Decimal('0'),
                        'reinvested_amount': Decimal('0'),
                        'withdrawn_amount': Decimal('0'),
                        'dividend_count': 0,
                        'securities_count': set()
                    }
                
                monthly_data[month_key]['total_amount'] += dividend.total_amount
                monthly_data[month_key]['dividend_count'] += 1
                monthly_data[month_key]['securities_count'].add(dividend.symbol)
                
                if dividend.is_reinvested:
                    monthly_data[month_key]['reinvested_amount'] += dividend.total_amount
                else:
                    monthly_data[month_key]['withdrawn_amount'] += dividend.total_amount
        
        # Convert to list and calculate additional metrics
        monthly_history = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            monthly_history.append({
                'month': month_key,
                'total_amount': float(data['total_amount']),
                'reinvested_amount': float(data['reinvested_amount']),
                'withdrawn_amount': float(data['withdrawn_amount']),
                'dividend_count': data['dividend_count'],
                'securities_count': len(data['securities_count']),
                'reinvestment_rate': float(data['reinvested_amount'] / data['total_amount'] * 100) if data['total_amount'] > 0 else 0
            })
        
        # Add trend analysis
        if len(monthly_history) >= 2:
            for i in range(1, len(monthly_history)):
                current = monthly_history[i]['total_amount']
                previous = monthly_history[i-1]['total_amount']
                if previous > 0:
                    monthly_history[i]['month_over_month_change'] = (current - previous) / previous * 100
                else:
                    monthly_history[i]['month_over_month_change'] = 0
        
        return monthly_history
    
    def _calculate_dividend_by_security(
        self, 
        dividends: List[Dividend], 
        positions: List[Position]
    ) -> List[Dict[str, Any]]:
        """Calculate dividend analysis by individual security."""
        if not dividends:
            return []
        
        # Group dividends by security
        security_data = {}
        position_map = {pos.symbol: pos for pos in positions}
        
        for dividend in dividends:
            symbol = dividend.symbol
            if symbol not in security_data:
                security_data[symbol] = {
                    'symbol': symbol,
                    'security_name': dividend.security_name,
                    'total_dividends': Decimal('0'),
                    'reinvested_dividends': Decimal('0'),
                    'withdrawn_dividends': Decimal('0'),
                    'dividend_count': 0,
                    'last_dividend_date': None,
                    'last_dividend_amount': Decimal('0'),
                    'current_position_value': Decimal('0'),
                    'current_yield': Decimal('0'),
                    'trailing_12m_dividends': Decimal('0')
                }
            
            data = security_data[symbol]
            data['total_dividends'] += dividend.total_amount
            data['dividend_count'] += 1
            
            if dividend.is_reinvested:
                data['reinvested_dividends'] += dividend.total_amount
            else:
                data['withdrawn_dividends'] += dividend.total_amount
            
            # Track most recent dividend
            if not data['last_dividend_date'] or dividend.payment_date > data['last_dividend_date']:
                data['last_dividend_date'] = dividend.payment_date
                data['last_dividend_amount'] = dividend.total_amount
            
            # Calculate trailing 12 months dividends
            one_year_ago = datetime.now() - timedelta(days=365)
            if dividend.payment_date and dividend.payment_date >= one_year_ago.date():
                data['trailing_12m_dividends'] += dividend.total_amount
        
        # Add current position data and calculate yields
        security_analysis = []
        for symbol, data in security_data.items():
            if symbol in position_map:
                position = position_map[symbol]
                data['current_position_value'] = position.market_value
                data['current_shares'] = position.quantity
                
                # Calculate current yield based on trailing 12 months
                if position.market_value > 0:
                    data['current_yield'] = data['trailing_12m_dividends'] / position.market_value * 100
            
            # Calculate reinvestment rate
            reinvestment_rate = Decimal('0')
            if data['total_dividends'] > 0:
                reinvestment_rate = data['reinvested_dividends'] / data['total_dividends'] * 100
            
            security_analysis.append({
                'symbol': data['symbol'],
                'security_name': data['security_name'],
                'total_dividends': float(data['total_dividends']),
                'reinvested_dividends': float(data['reinvested_dividends']),
                'withdrawn_dividends': float(data['withdrawn_dividends']),
                'reinvestment_rate': float(reinvestment_rate),
                'dividend_count': data['dividend_count'],
                'last_dividend_date': data['last_dividend_date'].isoformat() if data['last_dividend_date'] else None,
                'last_dividend_amount': float(data['last_dividend_amount']),
                'current_position_value': float(data['current_position_value']),
                'current_shares': float(data.get('current_shares', 0)),
                'current_yield': float(data['current_yield']),
                'trailing_12m_dividends': float(data['trailing_12m_dividends'])
            })
        
        # Sort by total dividends descending
        return sorted(security_analysis, key=lambda x: x['total_dividends'], reverse=True)
    
    def _calculate_reinvestment_analysis(self, dividends: List[Dividend]) -> Dict[str, Any]:
        """Calculate detailed reinvestment analysis."""
        if not dividends:
            return {
                'total_reinvested': 0,
                'total_withdrawn': 0,
                'overall_reinvestment_rate': 0,
                'reinvested_shares_acquired': 0,
                'average_reinvestment_price': 0,
                'reinvestment_by_security': []
            }
        
        total_reinvested = sum(div.total_amount for div in dividends if div.is_reinvested)
        total_withdrawn = sum(div.total_amount for div in dividends if not div.is_reinvested)
        total_dividends = total_reinvested + total_withdrawn
        
        overall_reinvestment_rate = (total_reinvested / total_dividends * 100) if total_dividends > 0 else Decimal('0')
        
        # Calculate reinvested shares and average prices
        total_reinvested_shares = sum(
            div.reinvested_shares for div in dividends 
            if div.is_reinvested and div.reinvested_shares
        )
        
        # Calculate weighted average reinvestment price
        total_reinvestment_value = Decimal('0')
        total_shares = Decimal('0')
        for div in dividends:
            if div.is_reinvested and div.reinvested_shares and div.reinvestment_price:
                value = div.reinvested_shares * div.reinvestment_price
                total_reinvestment_value += value
                total_shares += div.reinvested_shares
        
        average_reinvestment_price = (total_reinvestment_value / total_shares) if total_shares > 0 else Decimal('0')
        
        # Reinvestment by security
        security_reinvestment = {}
        for div in dividends:
            symbol = div.symbol
            if symbol not in security_reinvestment:
                security_reinvestment[symbol] = {
                    'symbol': symbol,
                    'security_name': div.security_name,
                    'total_dividends': Decimal('0'),
                    'reinvested_amount': Decimal('0'),
                    'withdrawn_amount': Decimal('0'),
                    'reinvested_shares': Decimal('0')
                }
            
            data = security_reinvestment[symbol]
            data['total_dividends'] += div.total_amount
            
            if div.is_reinvested:
                data['reinvested_amount'] += div.total_amount
                if div.reinvested_shares:
                    data['reinvested_shares'] += div.reinvested_shares
            else:
                data['withdrawn_amount'] += div.total_amount
        
        reinvestment_by_security = []
        for symbol, data in security_reinvestment.items():
            reinvestment_rate = (data['reinvested_amount'] / data['total_dividends'] * 100) if data['total_dividends'] > 0 else Decimal('0')
            reinvestment_by_security.append({
                'symbol': data['symbol'],
                'security_name': data['security_name'],
                'total_dividends': float(data['total_dividends']),
                'reinvested_amount': float(data['reinvested_amount']),
                'withdrawn_amount': float(data['withdrawn_amount']),
                'reinvestment_rate': float(reinvestment_rate),
                'reinvested_shares': float(data['reinvested_shares'])
            })
        
        return {
            'total_reinvested': float(total_reinvested),
            'total_withdrawn': float(total_withdrawn),
            'overall_reinvestment_rate': float(overall_reinvestment_rate),
            'reinvested_shares_acquired': float(total_reinvested_shares),
            'average_reinvestment_price': float(average_reinvestment_price),
            'reinvestment_by_security': sorted(reinvestment_by_security, key=lambda x: x['reinvested_amount'], reverse=True)
        }
    
    def _calculate_income_projections(
        self, 
        dividends: List[Dividend], 
        positions: List[Position]
    ) -> Dict[str, Any]:
        """Calculate income projections based on historical data and current positions."""
        if not dividends or not positions:
            return {
                'annual_projection': 0,
                'quarterly_projection': 0,
                'monthly_projection': 0,
                'next_12_months_projection': 0,
                'projection_by_security': [],
                'confidence_level': 'low'
            }
        
        # Calculate trailing 12 months for baseline projection
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_dividends = [
            div for div in dividends 
            if div.payment_date and div.payment_date >= one_year_ago.date()
        ]
        
        trailing_12m_total = sum(div.total_amount for div in recent_dividends)
        
        # Basic projections
        annual_projection = trailing_12m_total
        quarterly_projection = trailing_12m_total / 4
        monthly_projection = trailing_12m_total / 12
        
        # Calculate projection by security based on current positions
        position_map = {pos.symbol: pos for pos in positions}
        security_projections = {}
        
        for div in recent_dividends:
            symbol = div.symbol
            if symbol not in security_projections:
                security_projections[symbol] = {
                    'symbol': symbol,
                    'security_name': div.security_name,
                    'trailing_12m_dividends': Decimal('0'),
                    'current_position_value': Decimal('0'),
                    'current_shares': Decimal('0'),
                    'projected_annual_income': Decimal('0'),
                    'current_yield': Decimal('0')
                }
            
            security_projections[symbol]['trailing_12m_dividends'] += div.total_amount
        
        # Add current position data and calculate projections
        projection_by_security = []
        for symbol, data in security_projections.items():
            if symbol in position_map:
                position = position_map[symbol]
                data['current_position_value'] = position.market_value
                data['current_shares'] = position.quantity
                
                # Project based on current yield
                if position.market_value > 0:
                    data['current_yield'] = data['trailing_12m_dividends'] / position.market_value * 100
                    data['projected_annual_income'] = data['trailing_12m_dividends']  # Assume same rate
            
            projection_by_security.append({
                'symbol': data['symbol'],
                'security_name': data['security_name'],
                'trailing_12m_dividends': float(data['trailing_12m_dividends']),
                'current_position_value': float(data['current_position_value']),
                'current_shares': float(data['current_shares']),
                'projected_annual_income': float(data['projected_annual_income']),
                'current_yield': float(data['current_yield'])
            })
        
        # Determine confidence level based on data availability
        confidence_level = 'low'
        if len(recent_dividends) >= 4:  # At least quarterly data
            confidence_level = 'medium'
        if len(recent_dividends) >= 12:  # Monthly data available
            confidence_level = 'high'
        
        return {
            'annual_projection': float(annual_projection),
            'quarterly_projection': float(quarterly_projection),
            'monthly_projection': float(monthly_projection),
            'next_12_months_projection': float(annual_projection),
            'projection_by_security': sorted(projection_by_security, key=lambda x: x['projected_annual_income'], reverse=True),
            'confidence_level': confidence_level,
            'data_points_used': len(recent_dividends)
        }
    
    def _calculate_dividend_tax_analysis(self, dividends: List[Dividend]) -> Dict[str, Any]:
        """Calculate tax-related dividend analysis."""
        if not dividends:
            return {
                'total_gross_dividends': 0,
                'total_tax_withheld': 0,
                'total_net_dividends': 0,
                'effective_tax_rate': 0,
                'tax_by_country': [],
                'tax_by_security': []
            }
        
        total_gross = sum(div.gross_amount for div in dividends)
        total_tax_withheld = sum(div.tax_withheld for div in dividends)
        total_net = sum(div.net_amount for div in dividends)
        
        effective_tax_rate = (total_tax_withheld / total_gross * 100) if total_gross > 0 else Decimal('0')
        
        # Tax analysis by country (would need country data in dividend model)
        # For now, return basic structure
        tax_by_country = []
        
        # Tax analysis by security
        security_tax = {}
        for div in dividends:
            symbol = div.symbol
            if symbol not in security_tax:
                security_tax[symbol] = {
                    'symbol': symbol,
                    'security_name': div.security_name,
                    'gross_dividends': Decimal('0'),
                    'tax_withheld': Decimal('0'),
                    'net_dividends': Decimal('0')
                }
            
            data = security_tax[symbol]
            data['gross_dividends'] += div.gross_amount
            data['tax_withheld'] += div.tax_withheld
            data['net_dividends'] += div.net_amount
        
        tax_by_security = []
        for symbol, data in security_tax.items():
            effective_rate = (data['tax_withheld'] / data['gross_dividends'] * 100) if data['gross_dividends'] > 0 else Decimal('0')
            tax_by_security.append({
                'symbol': data['symbol'],
                'security_name': data['security_name'],
                'gross_dividends': float(data['gross_dividends']),
                'tax_withheld': float(data['tax_withheld']),
                'net_dividends': float(data['net_dividends']),
                'effective_tax_rate': float(effective_rate)
            })
        
        return {
            'total_gross_dividends': float(total_gross),
            'total_tax_withheld': float(total_tax_withheld),
            'total_net_dividends': float(total_net),
            'effective_tax_rate': float(effective_tax_rate),
            'tax_by_country': tax_by_country,
            'tax_by_security': sorted(tax_by_security, key=lambda x: x['tax_withheld'], reverse=True)
        }
    
    def _get_empty_dividend_analysis(self) -> Dict[str, Any]:
        """Return empty dividend analysis structure."""
        return {
            'summary': {
                'total_dividends': 0,
                'dividend_yield': 0,
                'annual_projection': 0,
                'monthly_avg': 0,
                'reinvested_dividends': 0,
                'withdrawn_dividends': 0,
                'reinvestment_rate': 0,
                'trailing_12m_dividends': 0,
                'dividend_growth_rate': 0
            },
            'monthly_history': [],
            'by_security': [],
            'reinvestment_analysis': {
                'total_reinvested': 0,
                'total_withdrawn': 0,
                'overall_reinvestment_rate': 0,
                'reinvested_shares_acquired': 0,
                'average_reinvestment_price': 0,
                'reinvestment_by_security': []
            },
            'income_projections': {
                'annual_projection': 0,
                'quarterly_projection': 0,
                'monthly_projection': 0,
                'next_12_months_projection': 0,
                'projection_by_security': [],
                'confidence_level': 'low'
            },
            'tax_analysis': {
                'total_gross_dividends': 0,
                'total_tax_withheld': 0,
                'total_net_dividends': 0,
                'effective_tax_rate': 0,
                'tax_by_country': [],
                'tax_by_security': []
            },
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    def _calculate_portfolio_returns(
        self, 
        positions: List[Position], 
        historical_data: Dict[str, HistoricalData]
    ) -> pd.Series:
        """
        Calculate portfolio returns time series.
        
        Args:
            positions: Current positions
            historical_data: Historical price data for each symbol
            
        Returns:
            pandas Series of portfolio returns
        """
        if not positions or not historical_data:
            return pd.Series(dtype=float)
        
        # Get all available dates
        all_dates = set()
        for symbol, data in historical_data.items():
            all_dates.update(point.price_date for point in data.price_history)
        
        if not all_dates:
            return pd.Series(dtype=float)
        
        all_dates = sorted(all_dates)
        
        # Calculate portfolio value for each date
        portfolio_values = []
        total_value = sum(pos.market_value for pos in positions)
        
        for date in all_dates:
            daily_value = Decimal('0')
            
            for pos in positions:
                if pos.symbol in historical_data:
                    # Find price for this date
                    price_data = historical_data[pos.symbol]
                    price_point = next(
                        (p for p in price_data.price_history if p.price_date == date),
                        None
                    )
                    
                    if price_point:
                        # Calculate position weight based on current allocation
                        position_weight = pos.market_value / total_value if total_value > 0 else Decimal('0')
                        daily_value += position_weight * price_point.close_price
            
            portfolio_values.append(float(daily_value))
        
        # Convert to pandas Series and calculate returns
        portfolio_series = pd.Series(portfolio_values, index=all_dates)
        returns = portfolio_series.pct_change().dropna()
        
        return returns
    
    def _calculate_risk_metrics(
        self, 
        returns: pd.Series, 
        benchmark_data: Optional[HistoricalData] = None
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            returns: Portfolio returns time series
            benchmark_data: Benchmark data for beta calculation
            
        Returns:
            RiskMetrics object with all risk calculations
        """
        if len(returns) == 0:
            return self._default_risk_metrics()
        
        # Convert to numpy for calculations
        returns_array = returns.values
        
        # Volatility (annualized)
        volatility = Decimal(str(np.std(returns_array) * np.sqrt(252)))
        
        # Sharpe ratio
        excess_returns = returns_array - float(self.risk_free_rate) / 252
        sharpe_ratio = Decimal(str(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252))) if np.std(excess_returns) > 0 else None
        
        # Sortino ratio (downside deviation)
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) > 0:
            downside_deviation = np.std(downside_returns) * np.sqrt(252)
            sortino_ratio = Decimal(str(np.mean(excess_returns) / downside_deviation)) if downside_deviation > 0 else None
        else:
            sortino_ratio = None
        
        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = Decimal(str(abs(drawdowns.min()) * 100))
        current_drawdown = Decimal(str(abs(drawdowns.iloc[-1]) * 100))
        
        # Beta calculation (if benchmark data available)
        beta = None
        alpha = None
        correlation = None
        tracking_error = None
        
        if benchmark_data and len(benchmark_data.price_history) > 1:
            benchmark_returns = self._calculate_benchmark_returns(benchmark_data)
            if len(benchmark_returns) > 0:
                # Align returns
                aligned_portfolio, aligned_benchmark = self._align_returns(returns, benchmark_returns)
                
                if len(aligned_portfolio) > 1 and len(aligned_benchmark) > 1:
                    # Beta
                    covariance = np.cov(aligned_portfolio, aligned_benchmark)[0, 1]
                    benchmark_variance = np.var(aligned_benchmark)
                    beta = Decimal(str(covariance / benchmark_variance)) if benchmark_variance > 0 else None
                    
                    # Alpha (annualized)
                    if beta is not None:
                        portfolio_return = np.mean(aligned_portfolio) * 252
                        benchmark_return = np.mean(aligned_benchmark) * 252
                        alpha = Decimal(str((portfolio_return - float(self.risk_free_rate) - float(beta) * (benchmark_return - float(self.risk_free_rate))) * 100))
                    
                    # Correlation
                    correlation = Decimal(str(np.corrcoef(aligned_portfolio, aligned_benchmark)[0, 1]))
                    
                    # Tracking error
                    tracking_error = Decimal(str(np.std(aligned_portfolio - aligned_benchmark) * np.sqrt(252) * 100))
        
        # Value at Risk (VaR)
        var_95 = Decimal(str(np.percentile(returns_array, 5) * 100)) if len(returns_array) > 0 else None
        var_99 = Decimal(str(np.percentile(returns_array, 1) * 100)) if len(returns_array) > 0 else None
        
        # Conditional VaR (Expected Shortfall)
        if var_95 is not None:
            var_95_threshold = float(var_95) / 100
            tail_returns = returns_array[returns_array <= var_95_threshold]
            cvar_95 = Decimal(str(np.mean(tail_returns) * 100)) if len(tail_returns) > 0 else None
        else:
            cvar_95 = None
        
        # Risk categorization
        risk_category, risk_score = self._categorize_risk(volatility, max_drawdown, sharpe_ratio)
        
        return RiskMetrics(
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            current_drawdown=current_drawdown,
            beta=beta,
            alpha=alpha,
            correlation=correlation,
            tracking_error=tracking_error,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            risk_category=risk_category,
            risk_score=risk_score
        )
    
    def _calculate_benchmark_returns(self, benchmark_data: HistoricalData) -> pd.Series:
        """Calculate benchmark returns from historical data."""
        if not benchmark_data.price_history or len(benchmark_data.price_history) < 2:
            return pd.Series(dtype=float)
        
        prices = [float(point.close_price) for point in benchmark_data.price_history]
        dates = [point.price_date for point in benchmark_data.price_history]
        
        price_series = pd.Series(prices, index=dates)
        returns = price_series.pct_change().dropna()
        
        return returns
    
    def _align_returns(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Align portfolio and benchmark returns by date."""
        # Find common dates
        common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
        
        if len(common_dates) == 0:
            return np.array([]), np.array([])
        
        aligned_portfolio = portfolio_returns.loc[common_dates].values
        aligned_benchmark = benchmark_returns.loc[common_dates].values
        
        return aligned_portfolio, aligned_benchmark
    
    def _calculate_annualized_return(self, returns: pd.Series) -> Optional[Decimal]:
        """Calculate annualized return from returns series."""
        if len(returns) == 0:
            return None
        
        # Geometric mean return annualized
        total_return = (1 + returns).prod() - 1
        years = len(returns) / 252  # Assuming daily returns
        
        if years > 0:
            annualized = (1 + total_return) ** (1 / years) - 1
            return Decimal(str(annualized * 100))
        
        return None
    
    def _calculate_time_weighted_return(self, returns: pd.Series) -> Optional[Decimal]:
        """Calculate time-weighted return."""
        if len(returns) == 0:
            return None
        
        # Time-weighted return is the geometric mean of period returns
        total_return = (1 + returns).prod() - 1
        return Decimal(str(total_return * 100))
    
    def _categorize_risk(
        self, 
        volatility: Decimal, 
        max_drawdown: Decimal, 
        sharpe_ratio: Optional[Decimal]
    ) -> Tuple[RiskCategory, Decimal]:
        """
        Categorize risk level and calculate risk score.
        
        Returns:
            Tuple of (risk_category, risk_score)
        """
        # Risk score based on volatility, max drawdown, and Sharpe ratio
        vol_score = min(float(volatility) * 2, 50)  # Cap at 50
        drawdown_score = min(float(max_drawdown), 30)  # Cap at 30
        sharpe_score = max(0, 20 - (float(sharpe_ratio) * 10 if sharpe_ratio else 0))  # Lower is better
        
        risk_score = Decimal(str(vol_score + drawdown_score + sharpe_score))
        
        # Categorize based on risk score
        if risk_score <= 30:
            risk_category = RiskCategory.LOW
        elif risk_score <= 60:
            risk_category = RiskCategory.MEDIUM
        else:
            risk_category = RiskCategory.HIGH
        
        return risk_category, min(risk_score, Decimal('100'))
    
    def _default_risk_metrics(self) -> RiskMetrics:
        """Return default risk metrics when calculation is not possible."""
        return RiskMetrics(
            volatility=Decimal('0'),
            max_drawdown=Decimal('0'),
            risk_category=RiskCategory.LOW,
            risk_score=Decimal('0')
        )
    
    def calculate_pie_metrics(
        self,
        pie: Pie,
        portfolio_total_value: Decimal,
        historical_data: Optional[Dict[str, HistoricalData]] = None,
        dividends: Optional[List[Dividend]] = None,
        portfolio_returns: Optional[pd.Series] = None
    ) -> PieMetrics:
        """
        Calculate comprehensive pie-level metrics.
        
        Args:
            pie: Pie object with positions
            portfolio_total_value: Total portfolio value for contribution calculations
            historical_data: Historical price data for positions
            dividends: Dividend history for pie positions
            portfolio_returns: Portfolio returns for beta calculation
            
        Returns:
            PieMetrics with all calculated metrics
        """
        # Basic value calculations
        pie_value = sum(pos.market_value for pos in pie.positions)
        pie_invested = sum(pos.quantity * pos.average_price for pos in pie.positions)
        pie_return = pie_value - pie_invested
        pie_return_pct = (pie_return / pie_invested * 100) if pie_invested > 0 else Decimal('0')
        
        # Portfolio contribution calculations
        portfolio_contribution = self._calculate_pie_portfolio_contribution(
            pie_return, portfolio_total_value, pie_value
        )
        portfolio_weight = (pie_value / portfolio_total_value * 100) if portfolio_total_value > 0 else Decimal('0')
        
        # Dividend calculations for pie
        pie_dividends = []
        if dividends:
            pie_symbols = {pos.symbol for pos in pie.positions}
            pie_dividends = [div for div in dividends if div.symbol in pie_symbols]
        
        dividend_metrics = self._calculate_dividend_metrics(pie_dividends, pie_value)
        
        # Allocation calculations
        sector_allocation = self._calculate_sector_allocation(pie.positions)
        industry_allocation = self._calculate_industry_allocation(pie.positions)
        country_allocation = self._calculate_country_allocation(pie.positions)
        asset_type_allocation = self._calculate_asset_type_allocation(pie.positions)
        
        # Advanced performance and risk calculations
        risk_metrics = None
        annualized_return = None
        time_weighted_return = None
        beta_vs_portfolio = None
        
        if historical_data:
            pie_returns = self._calculate_pie_returns(pie.positions, historical_data)
            if len(pie_returns) > 0:
                # Enhanced risk metrics calculation for pie
                risk_metrics = self._calculate_pie_risk_metrics(pie_returns)
                
                # Enhanced time-weighted return calculation
                time_weighted_return = self._calculate_pie_time_weighted_return(pie_returns)
                
                # Annualized return
                annualized_return = self._calculate_annualized_return(pie_returns)
                
                # Beta vs portfolio with enhanced calculation
                if portfolio_returns is not None and len(portfolio_returns) > 0:
                    beta_vs_portfolio = self._calculate_enhanced_pie_beta(pie_returns, portfolio_returns)
        
        # Top holdings for pie
        top_holdings = sorted(pie.positions, key=lambda p: p.market_value, reverse=True)[:5]
        
        return PieMetrics(
            total_value=pie_value,
            total_invested=pie_invested,
            total_return=pie_return,
            total_return_pct=pie_return_pct,
            annualized_return=annualized_return,
            time_weighted_return=time_weighted_return,
            portfolio_weight=portfolio_weight,
            portfolio_contribution=portfolio_contribution,
            total_dividends=dividend_metrics.get('total_dividends', Decimal('0')),
            dividend_yield=dividend_metrics.get('dividend_yield', Decimal('0')),
            annual_dividend_projection=dividend_metrics.get('annual_projection', Decimal('0')),
            monthly_dividend_avg=dividend_metrics.get('monthly_avg', Decimal('0')),
            reinvested_dividends=dividend_metrics.get('reinvested_dividends', Decimal('0')),
            withdrawn_dividends=dividend_metrics.get('withdrawn_dividends', Decimal('0')),
            reinvestment_rate=dividend_metrics.get('reinvestment_rate', Decimal('0')),
            trailing_12m_dividends=dividend_metrics.get('trailing_12m_dividends', Decimal('0')),
            dividend_growth_rate=dividend_metrics.get('dividend_growth_rate', Decimal('0')),
            sector_allocation=sector_allocation,
            industry_allocation=industry_allocation,
            country_allocation=country_allocation,
            asset_type_allocation=asset_type_allocation,
            risk_metrics=risk_metrics,
            beta_vs_portfolio=beta_vs_portfolio,
            top_holdings=[pos.symbol for pos in top_holdings]
        )
    
    def _calculate_pie_returns(
        self, 
        positions: List[Position], 
        historical_data: Dict[str, HistoricalData]
    ) -> pd.Series:
        """
        Calculate enhanced pie returns time series with proper weighting.
        
        Args:
            positions: Pie positions
            historical_data: Historical price data for each symbol
            
        Returns:
            pandas Series of pie returns
        """
        if not positions or not historical_data:
            return pd.Series(dtype=float)
        
        # Get all available dates for pie positions
        pie_symbols = {pos.symbol for pos in positions}
        all_dates = set()
        
        for symbol, data in historical_data.items():
            if symbol in pie_symbols:
                all_dates.update(point.price_date for point in data.price_history)
        
        if not all_dates:
            return pd.Series(dtype=float)
        
        all_dates = sorted(all_dates)
        
        # Calculate current total value for weighting
        current_total_value = sum(pos.market_value for pos in positions)
        
        if current_total_value == 0:
            return pd.Series(dtype=float)
        
        # Build position weights based on current market values
        position_weights = {
            pos.symbol: pos.market_value / current_total_value 
            for pos in positions
        }
        
        # Calculate weighted pie value for each date
        pie_values = []
        valid_dates = []
        
        for date in all_dates:
            daily_weighted_value = Decimal('0')
            has_data = False
            
            for pos in positions:
                if pos.symbol in historical_data:
                    price_data = historical_data[pos.symbol]
                    price_point = next(
                        (p for p in price_data.price_history if p.price_date == date),
                        None
                    )
                    
                    if price_point:
                        weight = position_weights[pos.symbol]
                        # Use normalized price (price relative to current price for proper weighting)
                        normalized_price = price_point.close_price / pos.current_price if pos.current_price > 0 else Decimal('1')
                        daily_weighted_value += weight * normalized_price
                        has_data = True
            
            # Only include dates where we have at least some price data
            if has_data and daily_weighted_value > 0:
                pie_values.append(float(daily_weighted_value))
                valid_dates.append(date)
        
        if len(pie_values) < 2:
            return pd.Series(dtype=float)
        
        # Convert to pandas Series and calculate returns
        pie_series = pd.Series(pie_values, index=valid_dates)
        returns = pie_series.pct_change().dropna()
        
        return returns
    
    def _calculate_pie_portfolio_contribution(
        self,
        pie_return: Decimal,
        portfolio_total_value: Decimal,
        pie_value: Decimal
    ) -> Decimal:
        """
        Calculate pie's contribution to total portfolio return.
        
        Args:
            pie_return: Absolute return of the pie
            portfolio_total_value: Total portfolio value
            pie_value: Current pie value
            
        Returns:
            Pie's contribution to portfolio return as percentage
        """
        if portfolio_total_value <= 0:
            return Decimal('0')
        
        # Contribution = (pie_return / portfolio_total_value) * 100
        contribution = (pie_return / portfolio_total_value * 100)
        return contribution
    
    def _calculate_pie_time_weighted_return(self, pie_returns: pd.Series) -> Optional[Decimal]:
        """
        Calculate enhanced time-weighted return for pie with proper handling of cash flows.
        
        Args:
            pie_returns: Pie returns time series
            
        Returns:
            Time-weighted return percentage
        """
        if len(pie_returns) == 0:
            return None
        
        # Time-weighted return calculation using geometric linking
        # TWR = [(1 + R1) × (1 + R2) × ... × (1 + Rn)] - 1
        cumulative_return = (1 + pie_returns).prod() - 1
        
        # Convert to percentage
        return Decimal(str(cumulative_return * 100))
    
    def _calculate_pie_risk_metrics(self, pie_returns: pd.Series) -> RiskMetrics:
        """
        Calculate enhanced risk metrics specifically for pie-level analysis.
        
        Args:
            pie_returns: Pie returns time series
            
        Returns:
            RiskMetrics with pie-specific calculations
        """
        if len(pie_returns) == 0:
            return self._default_risk_metrics()
        
        returns_array = pie_returns.values
        
        # Enhanced volatility calculation (annualized)
        volatility = Decimal(str(np.std(returns_array) * np.sqrt(252)))
        
        # Enhanced Sharpe ratio calculation
        excess_returns = returns_array - float(self.risk_free_rate) / 252
        if np.std(excess_returns) > 0:
            sharpe_ratio = Decimal(str(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)))
        else:
            sharpe_ratio = None
        
        # Sortino ratio (downside deviation only)
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) > 0:
            downside_deviation = np.std(downside_returns) * np.sqrt(252)
            sortino_ratio = Decimal(str(np.mean(excess_returns) / downside_deviation)) if downside_deviation > 0 else None
        else:
            sortino_ratio = None
        
        # Maximum drawdown calculation
        cumulative_returns = (1 + pie_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = Decimal(str(abs(drawdowns.min()) * 100))
        current_drawdown = Decimal(str(abs(drawdowns.iloc[-1]) * 100))
        
        # Value at Risk calculations
        var_95 = Decimal(str(np.percentile(returns_array, 5) * 100)) if len(returns_array) > 0 else None
        var_99 = Decimal(str(np.percentile(returns_array, 1) * 100)) if len(returns_array) > 0 else None
        
        # Conditional VaR (Expected Shortfall)
        if var_95 is not None:
            var_95_threshold = float(var_95) / 100
            tail_returns = returns_array[returns_array <= var_95_threshold]
            cvar_95 = Decimal(str(np.mean(tail_returns) * 100)) if len(tail_returns) > 0 else None
        else:
            cvar_95 = None
        
        # Risk categorization
        risk_category, risk_score = self._categorize_risk(volatility, max_drawdown, sharpe_ratio)
        
        return RiskMetrics(
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            current_drawdown=current_drawdown,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            risk_category=risk_category,
            risk_score=risk_score
        )
    
    def _calculate_enhanced_pie_beta(
        self, 
        pie_returns: pd.Series, 
        portfolio_returns: pd.Series
    ) -> Optional[Decimal]:
        """
        Calculate enhanced pie beta vs portfolio with improved statistical methods.
        
        Args:
            pie_returns: Pie returns time series
            portfolio_returns: Portfolio returns time series
            
        Returns:
            Enhanced beta coefficient or None if calculation not possible
        """
        # Align returns
        aligned_pie, aligned_portfolio = self._align_returns(pie_returns, portfolio_returns)
        
        if len(aligned_pie) < 10:  # Require minimum 10 observations for statistical significance
            return None
        
        # Calculate beta using covariance method
        covariance = np.cov(aligned_pie, aligned_portfolio)[0, 1]
        portfolio_variance = np.var(aligned_portfolio)
        
        if portfolio_variance > 0:
            beta = covariance / portfolio_variance
            
            # Apply bounds to prevent extreme beta values
            beta = max(-3.0, min(3.0, beta))  # Bound beta between -3 and 3
            
            return Decimal(str(beta))
        
        return None
    
    def _calculate_pie_beta_vs_portfolio(
        self, 
        pie_returns: pd.Series, 
        portfolio_returns: pd.Series
    ) -> Optional[Decimal]:
        """
        Calculate pie beta vs portfolio.
        
        Args:
            pie_returns: Pie returns time series
            portfolio_returns: Portfolio returns time series
            
        Returns:
            Beta coefficient or None if calculation not possible
        """
        # Use the enhanced beta calculation
        return self._calculate_enhanced_pie_beta(pie_returns, portfolio_returns)
    
    def calculate_allocation_drift(
        self,
        current_allocation: Dict[str, Decimal],
        target_allocation: Dict[str, Decimal],
        tolerance: Decimal = Decimal('5.0')
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate allocation drift from target weights.
        
        Args:
            current_allocation: Current allocation percentages
            target_allocation: Target allocation percentages
            tolerance: Tolerance threshold for drift detection
            
        Returns:
            Dictionary with drift analysis for each category
        """
        drift_analysis = {}
        
        all_categories = set(current_allocation.keys()) | set(target_allocation.keys())
        
        for category in all_categories:
            current = current_allocation.get(category, Decimal('0'))
            target = target_allocation.get(category, Decimal('0'))
            drift = current - target
            drift_pct = (abs(drift) / target * 100) if target > 0 else Decimal('100')
            
            needs_rebalancing = abs(drift) > tolerance
            
            drift_analysis[category] = {
                'current': current,
                'target': target,
                'drift': drift,
                'drift_pct': drift_pct,
                'needs_rebalancing': needs_rebalancing
            }
        
        return drift_analysis
    
    def calculate_pie_performance_comparison(
        self,
        pies: List[Pie],
        portfolio_total_value: Decimal,
        historical_data: Optional[Dict[str, HistoricalData]] = None,
        dividends: Optional[List[Dividend]] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate performance comparison metrics across all pies.
        
        Args:
            pies: List of pies to compare
            portfolio_total_value: Total portfolio value
            historical_data: Historical price data
            dividends: Dividend history
            
        Returns:
            Dictionary with comparison metrics for each pie
        """
        if not pies:
            return {}
        
        comparison_metrics = {}
        
        # Calculate portfolio returns for beta calculations
        all_positions = []
        for pie in pies:
            all_positions.extend(pie.positions)
        
        portfolio_returns = None
        if historical_data:
            portfolio_returns = self._calculate_portfolio_returns(all_positions, historical_data)
        
        for pie in pies:
            pie_metrics = self.calculate_pie_metrics(
                pie, portfolio_total_value, historical_data, dividends, portfolio_returns
            )
            
            comparison_metrics[pie.id] = {
                'name': pie.name,
                'total_return_pct': pie_metrics.total_return_pct,
                'annualized_return': pie_metrics.annualized_return or Decimal('0'),
                'time_weighted_return': pie_metrics.time_weighted_return or Decimal('0'),
                'portfolio_weight': pie_metrics.portfolio_weight,
                'portfolio_contribution': pie_metrics.portfolio_contribution,
                'volatility': pie_metrics.risk_metrics.volatility if pie_metrics.risk_metrics else Decimal('0'),
                'sharpe_ratio': pie_metrics.risk_metrics.sharpe_ratio if pie_metrics.risk_metrics and pie_metrics.risk_metrics.sharpe_ratio else Decimal('0'),
                'max_drawdown': pie_metrics.risk_metrics.max_drawdown if pie_metrics.risk_metrics else Decimal('0'),
                'beta_vs_portfolio': pie_metrics.beta_vs_portfolio or Decimal('1'),
                'dividend_yield': pie_metrics.dividend_yield
            }
        
        return comparison_metrics
    
    def calculate_benchmark_comparison(
        self,
        entity_returns: pd.Series,
        benchmark_returns: pd.Series,
        entity_name: str,
        benchmark_name: str,
        entity_type: str = "portfolio"
    ) -> BenchmarkComparison:
        """
        Calculate comprehensive benchmark comparison metrics.
        
        Args:
            entity_returns: Portfolio or pie returns
            benchmark_returns: Benchmark returns
            entity_name: Name of the entity being compared
            benchmark_name: Name of the benchmark
            entity_type: Type of entity (portfolio or pie)
            
        Returns:
            BenchmarkComparison with all comparison metrics
        """
        # Align returns
        aligned_entity, aligned_benchmark = self._align_returns(entity_returns, benchmark_returns)
        
        if len(aligned_entity) == 0 or len(aligned_benchmark) == 0:
            # Return default comparison if no aligned data
            return self._default_benchmark_comparison(entity_name, benchmark_name, entity_type)
        
        # Calculate returns
        entity_total_return = (np.prod(1 + aligned_entity) - 1) * 100
        benchmark_total_return = (np.prod(1 + aligned_benchmark) - 1) * 100
        
        # Alpha and Beta
        covariance = np.cov(aligned_entity, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        entity_mean_return = np.mean(aligned_entity) * 252  # Annualized
        benchmark_mean_return = np.mean(aligned_benchmark) * 252  # Annualized
        alpha = (entity_mean_return - float(self.risk_free_rate) - beta * (benchmark_mean_return - float(self.risk_free_rate))) * 100
        
        # Risk metrics
        tracking_error = np.std(aligned_entity - aligned_benchmark) * np.sqrt(252) * 100
        correlation = np.corrcoef(aligned_entity, aligned_benchmark)[0, 1]
        
        # R-squared
        r_squared = correlation ** 2
        
        # Information ratio
        excess_returns = aligned_entity - aligned_benchmark
        information_ratio = (np.mean(excess_returns) * 252) / (np.std(excess_returns) * np.sqrt(252)) if np.std(excess_returns) > 0 else 0
        
        # Up/Down capture ratios
        up_periods = aligned_benchmark > 0
        down_periods = aligned_benchmark < 0
        
        up_capture = None
        down_capture = None
        
        if np.any(up_periods):
            up_entity = np.mean(aligned_entity[up_periods])
            up_benchmark = np.mean(aligned_benchmark[up_periods])
            up_capture = (up_entity / up_benchmark) * 100 if up_benchmark != 0 else 0
        
        if np.any(down_periods):
            down_entity = np.mean(aligned_entity[down_periods])
            down_benchmark = np.mean(aligned_benchmark[down_periods])
            down_capture = (down_entity / down_benchmark) * 100 if down_benchmark != 0 else 0
        
        # Summary
        outperforming = entity_total_return > benchmark_total_return
        outperformance_amount = entity_total_return - benchmark_total_return
        
        return BenchmarkComparison(
            entity_type=entity_type,
            entity_id="",  # To be filled by caller
            entity_name=entity_name,
            benchmark_symbol="",  # To be filled by caller
            benchmark_name=benchmark_name,
            period="",  # To be filled by caller
            start_date=datetime.now(),  # To be filled by caller
            end_date=datetime.now(),  # To be filled by caller
            entity_return_pct=Decimal(str(entity_total_return)),
            benchmark_return_pct=Decimal(str(benchmark_total_return)),
            alpha=Decimal(str(alpha)),
            beta=Decimal(str(beta)),
            tracking_error=Decimal(str(tracking_error)),
            correlation=Decimal(str(correlation)),
            r_squared=Decimal(str(r_squared)),
            information_ratio=Decimal(str(information_ratio)) if information_ratio else None,
            up_capture=Decimal(str(up_capture)) if up_capture is not None else None,
            down_capture=Decimal(str(down_capture)) if down_capture is not None else None,
            outperforming=outperforming,
            outperformance_amount=Decimal(str(outperformance_amount))
        )
    
    def _default_benchmark_comparison(
        self, 
        entity_name: str, 
        benchmark_name: str, 
        entity_type: str
    ) -> BenchmarkComparison:
        """Return default benchmark comparison when calculation is not possible."""
        return BenchmarkComparison(
            entity_type=entity_type,
            entity_id="",
            entity_name=entity_name,
            benchmark_symbol="",
            benchmark_name=benchmark_name,
            period="",
            start_date=datetime.now(),
            end_date=datetime.now(),
            entity_return_pct=Decimal('0'),
            benchmark_return_pct=Decimal('0'),
            alpha=Decimal('0'),
            beta=Decimal('1'),
            tracking_error=Decimal('0'),
            correlation=Decimal('0'),
            r_squared=Decimal('0'),
            outperforming=False,
            outperformance_amount=Decimal('0')
        )    

    def calculate_sector_breakdown(self, positions: List[Position]) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate detailed sector breakdown with industry sub-categories.
        
        Args:
            positions: List of positions to analyze
            
        Returns:
            Dictionary with sector breakdown including industries
        """
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {}
        
        sector_breakdown = {}
        
        for pos in positions:
            sector = pos.sector or "Unknown"
            industry = pos.industry or "Unknown"
            
            if sector not in sector_breakdown:
                sector_breakdown[sector] = {
                    'total_value': Decimal('0'),
                    'percentage': Decimal('0'),
                    'industries': {}
                }
            
            # Add to sector total
            sector_breakdown[sector]['total_value'] += pos.market_value
            
            # Add to industry within sector
            if industry not in sector_breakdown[sector]['industries']:
                sector_breakdown[sector]['industries'][industry] = {
                    'total_value': Decimal('0'),
                    'percentage': Decimal('0'),
                    'positions': []
                }
            
            sector_breakdown[sector]['industries'][industry]['total_value'] += pos.market_value
            sector_breakdown[sector]['industries'][industry]['positions'].append({
                'symbol': pos.symbol,
                'name': pos.name,
                'value': pos.market_value,
                'percentage': (pos.market_value / total_value * 100)
            })
        
        # Calculate percentages
        for sector, data in sector_breakdown.items():
            data['percentage'] = (data['total_value'] / total_value * 100)
            
            for industry, industry_data in data['industries'].items():
                industry_data['percentage'] = (industry_data['total_value'] / total_value * 100)
        
        return sector_breakdown
    
    def calculate_geographical_breakdown(self, positions: List[Position]) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate geographical breakdown by country and region.
        
        Args:
            positions: List of positions to analyze
            
        Returns:
            Dictionary with geographical breakdown
        """
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {}
        
        # Country mapping to regions (simplified)
        country_to_region = {
            'US': 'North America',
            'CA': 'North America',
            'GB': 'Europe',
            'DE': 'Europe',
            'FR': 'Europe',
            'IT': 'Europe',
            'ES': 'Europe',
            'NL': 'Europe',
            'CH': 'Europe',
            'JP': 'Asia Pacific',
            'CN': 'Asia Pacific',
            'HK': 'Asia Pacific',
            'SG': 'Asia Pacific',
            'AU': 'Asia Pacific',
            'BR': 'Latin America',
            'MX': 'Latin America',
            'ZA': 'Africa',
            'Unknown': 'Unknown'
        }
        
        geographical_breakdown = {}
        
        for pos in positions:
            country = pos.country or "Unknown"
            region = country_to_region.get(country, "Other")
            
            if region not in geographical_breakdown:
                geographical_breakdown[region] = {
                    'total_value': Decimal('0'),
                    'percentage': Decimal('0'),
                    'countries': {}
                }
            
            if country not in geographical_breakdown[region]['countries']:
                geographical_breakdown[region]['countries'][country] = {
                    'total_value': Decimal('0'),
                    'percentage': Decimal('0'),
                    'positions': []
                }
            
            # Add to region and country totals
            geographical_breakdown[region]['total_value'] += pos.market_value
            geographical_breakdown[region]['countries'][country]['total_value'] += pos.market_value
            geographical_breakdown[region]['countries'][country]['positions'].append({
                'symbol': pos.symbol,
                'name': pos.name,
                'value': pos.market_value,
                'percentage': (pos.market_value / total_value * 100)
            })
        
        # Calculate percentages
        for region, data in geographical_breakdown.items():
            data['percentage'] = (data['total_value'] / total_value * 100)
            
            for country, country_data in data['countries'].items():
                country_data['percentage'] = (country_data['total_value'] / total_value * 100)
        
        return geographical_breakdown
    
    def calculate_concentration_analysis(self, positions: List[Position]) -> Dict[str, any]:
        """
        Calculate concentration risk analysis including top holdings and HHI.
        
        Args:
            positions: List of positions to analyze
            
        Returns:
            Dictionary with concentration analysis
        """
        if not positions:
            return {
                'herfindahl_index': Decimal('0'),
                'concentration_level': 'Low',
                'top_holdings': [],
                'concentration_buckets': {}
            }
        
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {
                'herfindahl_index': Decimal('0'),
                'concentration_level': 'Low',
                'top_holdings': [],
                'concentration_buckets': {}
            }
        
        # Calculate weights and sort by value
        sorted_positions = sorted(positions, key=lambda p: p.market_value, reverse=True)
        weights = [pos.market_value / total_value for pos in sorted_positions]
        
        # Herfindahl-Hirschman Index
        hhi = sum(w ** 2 for w in weights)
        hhi_decimal = Decimal(str(hhi))
        
        # Concentration level
        if hhi < 0.15:
            concentration_level = 'Low'
        elif hhi < 0.25:
            concentration_level = 'Moderate'
        else:
            concentration_level = 'High'
        
        # Top holdings analysis
        top_holdings = []
        for i, pos in enumerate(sorted_positions[:20]):  # Top 20
            weight = pos.market_value / total_value * 100
            top_holdings.append({
                'rank': i + 1,
                'symbol': pos.symbol,
                'name': pos.name,
                'value': pos.market_value,
                'weight': Decimal(str(weight)),
                'sector': pos.sector,
                'country': pos.country
            })
        
        # Concentration buckets
        concentration_buckets = {
            'top_1': sum(weights[:1]) * 100 if len(weights) >= 1 else 0,
            'top_5': sum(weights[:5]) * 100 if len(weights) >= 5 else sum(weights) * 100,
            'top_10': sum(weights[:10]) * 100 if len(weights) >= 10 else sum(weights) * 100,
            'top_20': sum(weights[:20]) * 100 if len(weights) >= 20 else sum(weights) * 100,
            'remaining': sum(weights[20:]) * 100 if len(weights) > 20 else 0
        }
        
        return {
            'herfindahl_index': hhi_decimal,
            'concentration_level': concentration_level,
            'top_holdings': top_holdings,
            'concentration_buckets': {k: Decimal(str(v)) for k, v in concentration_buckets.items()}
        }
    
    def calculate_diversification_score(self, positions: List[Position]) -> Dict[str, Decimal]:
        """
        Calculate comprehensive diversification score across multiple dimensions.
        
        Args:
            positions: List of positions to analyze
            
        Returns:
            Dictionary with diversification scores
        """
        if not positions:
            return {
                'overall_score': Decimal('0'),
                'sector_diversification': Decimal('0'),
                'industry_diversification': Decimal('0'),
                'geographical_diversification': Decimal('0'),
                'asset_type_diversification': Decimal('0'),
                'position_count_score': Decimal('0')
            }
        
        total_value = sum(pos.market_value for pos in positions)
        if total_value == 0:
            return {
                'overall_score': Decimal('0'),
                'sector_diversification': Decimal('0'),
                'industry_diversification': Decimal('0'),
                'geographical_diversification': Decimal('0'),
                'asset_type_diversification': Decimal('0'),
                'position_count_score': Decimal('0')
            }
        
        # Sector diversification
        sector_weights = {}
        for pos in positions:
            sector = pos.sector or "Unknown"
            sector_weights[sector] = sector_weights.get(sector, Decimal('0')) + (pos.market_value / total_value)
        
        sector_hhi = sum(w ** 2 for w in sector_weights.values())
        sector_diversification = Decimal(str((1 - sector_hhi) * 100))
        
        # Industry diversification
        industry_weights = {}
        for pos in positions:
            industry = pos.industry or "Unknown"
            industry_weights[industry] = industry_weights.get(industry, Decimal('0')) + (pos.market_value / total_value)
        
        industry_hhi = sum(w ** 2 for w in industry_weights.values())
        industry_diversification = Decimal(str((1 - industry_hhi) * 100))
        
        # Geographical diversification
        country_weights = {}
        for pos in positions:
            country = pos.country or "Unknown"
            country_weights[country] = country_weights.get(country, Decimal('0')) + (pos.market_value / total_value)
        
        geo_hhi = sum(w ** 2 for w in country_weights.values())
        geographical_diversification = Decimal(str((1 - geo_hhi) * 100))
        
        # Asset type diversification
        asset_type_weights = {}
        for pos in positions:
            asset_type = pos.asset_type.value
            asset_type_weights[asset_type] = asset_type_weights.get(asset_type, Decimal('0')) + (pos.market_value / total_value)
        
        asset_hhi = sum(w ** 2 for w in asset_type_weights.values())
        asset_type_diversification = Decimal(str((1 - asset_hhi) * 100))
        
        # Position count score (more positions = better diversification, up to a point)
        position_count = len(positions)
        if position_count <= 5:
            position_count_score = Decimal(str(position_count * 10))  # 0-50
        elif position_count <= 20:
            position_count_score = Decimal(str(50 + (position_count - 5) * 2))  # 50-80
        else:
            position_count_score = Decimal('80')  # Cap at 80
        
        # Overall score (weighted average)
        overall_score = (
            sector_diversification * Decimal('0.25') +
            industry_diversification * Decimal('0.2') +
            geographical_diversification * Decimal('0.25') +
            asset_type_diversification * Decimal('0.15') +
            position_count_score * Decimal('0.15')
        )
        
        return {
            'overall_score': min(overall_score, Decimal('100')),
            'sector_diversification': sector_diversification,
            'industry_diversification': industry_diversification,
            'geographical_diversification': geographical_diversification,
            'asset_type_diversification': asset_type_diversification,
            'position_count_score': position_count_score
        }
    
    def detect_allocation_drift(
        self,
        current_positions: List[Position],
        target_allocations: Dict[str, Dict[str, Decimal]],
        tolerance_pct: Decimal = Decimal('5.0')
    ) -> Dict[str, any]:
        """
        Detect allocation drift from target allocations.
        
        Args:
            current_positions: Current portfolio positions
            target_allocations: Target allocations by category
            tolerance_pct: Tolerance percentage for drift detection
            
        Returns:
            Dictionary with drift analysis and rebalancing recommendations
        """
        total_value = sum(pos.market_value for pos in current_positions)
        if total_value == 0:
            return {'drift_detected': False, 'recommendations': []}
        
        # Calculate current allocations
        current_sector = self._calculate_sector_allocation(current_positions)
        current_industry = self._calculate_industry_allocation(current_positions)
        current_country = self._calculate_country_allocation(current_positions)
        current_asset_type = self._calculate_asset_type_allocation(current_positions)
        
        drift_analysis = {
            'drift_detected': False,
            'total_drift_score': Decimal('0'),
            'category_drifts': {},
            'recommendations': []
        }
        
        # Check sector drift
        if 'sector' in target_allocations:
            sector_drift = self.calculate_allocation_drift(
                current_sector, 
                target_allocations['sector'], 
                tolerance_pct
            )
            drift_analysis['category_drifts']['sector'] = sector_drift
            
            # Check if any sector needs rebalancing
            for category, drift_data in sector_drift.items():
                if drift_data['needs_rebalancing']:
                    drift_analysis['drift_detected'] = True
                    drift_analysis['recommendations'].append({
                        'type': 'sector_rebalancing',
                        'category': category,
                        'current': drift_data['current'],
                        'target': drift_data['target'],
                        'action': 'increase' if drift_data['drift'] < 0 else 'decrease'
                    })
        
        # Check industry drift
        if 'industry' in target_allocations:
            industry_drift = self.calculate_allocation_drift(
                current_industry, 
                target_allocations['industry'], 
                tolerance_pct
            )
            drift_analysis['category_drifts']['industry'] = industry_drift
            
            for category, drift_data in industry_drift.items():
                if drift_data['needs_rebalancing']:
                    drift_analysis['drift_detected'] = True
                    drift_analysis['recommendations'].append({
                        'type': 'industry_rebalancing',
                        'category': category,
                        'current': drift_data['current'],
                        'target': drift_data['target'],
                        'action': 'increase' if drift_data['drift'] < 0 else 'decrease'
                    })
        
        # Check country drift
        if 'country' in target_allocations:
            country_drift = self.calculate_allocation_drift(
                current_country, 
                target_allocations['country'], 
                tolerance_pct
            )
            drift_analysis['category_drifts']['country'] = country_drift
            
            for category, drift_data in country_drift.items():
                if drift_data['needs_rebalancing']:
                    drift_analysis['drift_detected'] = True
                    drift_analysis['recommendations'].append({
                        'type': 'country_rebalancing',
                        'category': category,
                        'current': drift_data['current'],
                        'target': drift_data['target'],
                        'action': 'increase' if drift_data['drift'] < 0 else 'decrease'
                    })
        
        # Check asset type drift
        if 'asset_type' in target_allocations:
            asset_type_drift = self.calculate_allocation_drift(
                current_asset_type, 
                target_allocations['asset_type'], 
                tolerance_pct
            )
            drift_analysis['category_drifts']['asset_type'] = asset_type_drift
            
            for category, drift_data in asset_type_drift.items():
                if drift_data['needs_rebalancing']:
                    drift_analysis['drift_detected'] = True
                    drift_analysis['recommendations'].append({
                        'type': 'asset_type_rebalancing',
                        'category': category,
                        'current': drift_data['current'],
                        'target': drift_data['target'],
                        'action': 'increase' if drift_data['drift'] < 0 else 'decrease'
                    })
        
        # Calculate total drift score
        total_drift = Decimal('0')
        drift_count = 0
        
        for category_drifts in drift_analysis['category_drifts'].values():
            for drift_data in category_drifts.values():
                total_drift += abs(drift_data['drift'])
                drift_count += 1
        
        if drift_count > 0:
            drift_analysis['total_drift_score'] = total_drift / drift_count
        
        return drift_analysis
    
    def calculate_comprehensive_allocation_analysis(
        self,
        positions: List[Position],
        target_allocations: Optional[Dict[str, Dict[str, Decimal]]] = None,
        tolerance_pct: Decimal = Decimal('5.0')
    ) -> Dict[str, any]:
        """
        Calculate comprehensive allocation and diversification analysis.
        
        Args:
            positions: List of positions to analyze
            target_allocations: Optional target allocations for drift detection
            tolerance_pct: Tolerance percentage for drift detection
            
        Returns:
            Dictionary with comprehensive allocation analysis
        """
        if not positions:
            return {
                'allocations': {},
                'diversification': {},
                'concentration': {},
                'top_holdings': [],
                'drift_analysis': None
            }
        
        # Calculate all allocation breakdowns
        allocations = {
            'sector': self._calculate_sector_allocation(positions),
            'industry': self._calculate_industry_allocation(positions),
            'country': self._calculate_country_allocation(positions),
            'asset_type': self._calculate_asset_type_allocation(positions)
        }
        
        # Calculate diversification scores
        diversification = self.calculate_diversification_score(positions)
        
        # Calculate concentration analysis
        concentration = self.calculate_concentration_analysis(positions)
        
        # Get top holdings with enhanced details
        total_value = sum(pos.market_value for pos in positions)
        sorted_positions = sorted(positions, key=lambda p: p.market_value, reverse=True)
        
        top_holdings = []
        for i, pos in enumerate(sorted_positions[:20]):  # Top 20 holdings
            weight = (pos.market_value / total_value * 100) if total_value > 0 else Decimal('0')
            top_holdings.append({
                'rank': i + 1,
                'symbol': pos.symbol,
                'name': pos.name,
                'sector': pos.sector,
                'industry': pos.industry,
                'country': pos.country,
                'asset_type': pos.asset_type.value,
                'market_value': pos.market_value,
                'weight': weight,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_pct': pos.unrealized_pnl_pct
            })
        
        # Calculate drift analysis if target allocations provided
        drift_analysis = None
        if target_allocations:
            drift_analysis = self.detect_allocation_drift(
                positions, target_allocations, tolerance_pct
            )
        
        return {
            'allocations': allocations,
            'diversification': diversification,
            'concentration': concentration,
            'top_holdings': top_holdings,
            'drift_analysis': drift_analysis,
            'summary': {
                'total_positions': len(positions),
                'total_value': total_value,
                'diversification_score': diversification['overall_score'],
                'concentration_level': concentration['concentration_level'],
                'top_10_weight': concentration['concentration_buckets']['top_10']
            }
        }
  
    def calculate_comprehensive_dividend_analysis(
        self,
        dividends: List[Dividend],
        positions: List[Position],
        analysis_period_months: int = 12
    ) -> Dict[str, any]:
        """
        Calculate comprehensive dividend and income analysis.
        
        Args:
            dividends: List of dividend payments
            positions: Current positions for yield calculations
            analysis_period_months: Period for analysis in months
            
        Returns:
            Dictionary with comprehensive dividend analysis
        """
        if not dividends:
            return self._default_dividend_analysis()
        
        # Filter dividends to analysis period
        cutoff_date = datetime.now() - timedelta(days=analysis_period_months * 30)
        period_dividends = [
            div for div in dividends 
            if div.payment_date >= cutoff_date.date()
        ]
        
        total_portfolio_value = sum(pos.market_value for pos in positions)
        
        # Basic dividend metrics
        total_dividends = sum(div.net_amount for div in period_dividends)
        gross_dividends = sum(div.gross_amount for div in period_dividends)
        taxes_withheld = sum(div.tax_withheld for div in period_dividends)
        
        # Reinvestment analysis
        reinvested_dividends = sum(
            div.net_amount for div in period_dividends if div.is_reinvested
        )
        cash_dividends = sum(
            div.net_amount for div in period_dividends if not div.is_reinvested
        )
        reinvestment_rate = (reinvested_dividends / total_dividends * 100) if total_dividends > 0 else Decimal('0')
        
        # Yield calculations
        current_yield = (total_dividends / total_portfolio_value * 100) if total_portfolio_value > 0 else Decimal('0')
        
        # Monthly analysis
        monthly_analysis = self._calculate_monthly_dividend_analysis(period_dividends)
        
        # Security-level analysis
        security_analysis = self._calculate_security_dividend_analysis(period_dividends, positions)
        
        # Projections
        projections = self._calculate_dividend_projections(period_dividends, positions)
        
        # Dividend growth analysis
        growth_analysis = self._calculate_dividend_growth_analysis(dividends)
        
        return {
            'period_months': analysis_period_months,
            'total_dividends': total_dividends,
            'gross_dividends': gross_dividends,
            'taxes_withheld': taxes_withheld,
            'reinvested_dividends': reinvested_dividends,
            'cash_dividends': cash_dividends,
            'reinvestment_rate': reinvestment_rate,
            'current_yield': current_yield,
            'monthly_analysis': monthly_analysis,
            'security_analysis': security_analysis,
            'projections': projections,
            'growth_analysis': growth_analysis
        }
    
    def _calculate_monthly_dividend_analysis(self, dividends: List[Dividend]) -> Dict[str, any]:
        """Calculate monthly dividend breakdown and trends."""
        monthly_data = {}
        
        for div in dividends:
            month_key = div.payment_date.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'total_amount': Decimal('0'),
                    'gross_amount': Decimal('0'),
                    'tax_withheld': Decimal('0'),
                    'reinvested_amount': Decimal('0'),
                    'cash_amount': Decimal('0'),
                    'payment_count': 0,
                    'securities': set()
                }
            
            monthly_data[month_key]['total_amount'] += div.net_amount
            monthly_data[month_key]['gross_amount'] += div.gross_amount
            monthly_data[month_key]['tax_withheld'] += div.tax_withheld
            monthly_data[month_key]['payment_count'] += 1
            monthly_data[month_key]['securities'].add(div.symbol)
            
            if div.is_reinvested:
                monthly_data[month_key]['reinvested_amount'] += div.net_amount
            else:
                monthly_data[month_key]['cash_amount'] += div.net_amount
        
        # Convert sets to counts and calculate averages
        for month_data in monthly_data.values():
            month_data['unique_securities'] = len(month_data['securities'])
            month_data['securities'] = list(month_data['securities'])
        
        # Calculate trends
        sorted_months = sorted(monthly_data.keys())
        if len(sorted_months) >= 2:
            recent_avg = sum(monthly_data[month]['total_amount'] for month in sorted_months[-3:]) / min(3, len(sorted_months))
            earlier_avg = sum(monthly_data[month]['total_amount'] for month in sorted_months[:3]) / min(3, len(sorted_months))
            trend = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else Decimal('0')
        else:
            trend = Decimal('0')
        
        return {
            'monthly_breakdown': monthly_data,
            'trend_percentage': trend,
            'average_monthly': sum(data['total_amount'] for data in monthly_data.values()) / len(monthly_data) if monthly_data else Decimal('0'),
            'highest_month': max(monthly_data.items(), key=lambda x: x[1]['total_amount']) if monthly_data else None,
            'lowest_month': min(monthly_data.items(), key=lambda x: x[1]['total_amount']) if monthly_data else None
        }
    
    def _calculate_security_dividend_analysis(
        self, 
        dividends: List[Dividend], 
        positions: List[Position]
    ) -> Dict[str, any]:
        """Calculate dividend analysis by security."""
        security_data = {}
        position_map = {pos.symbol: pos for pos in positions}
        
        for div in dividends:
            symbol = div.symbol
            
            if symbol not in security_data:
                security_data[symbol] = {
                    'security_name': div.security_name,
                    'total_dividends': Decimal('0'),
                    'payment_count': 0,
                    'average_payment': Decimal('0'),
                    'reinvested_amount': Decimal('0'),
                    'cash_amount': Decimal('0'),
                    'current_yield': Decimal('0'),
                    'payments': []
                }
            
            security_data[symbol]['total_dividends'] += div.net_amount
            security_data[symbol]['payment_count'] += 1
            security_data[symbol]['payments'].append({
                'date': div.payment_date,
                'amount': div.net_amount,
                'amount_per_share': div.amount_per_share,
                'is_reinvested': div.is_reinvested
            })
            
            if div.is_reinvested:
                security_data[symbol]['reinvested_amount'] += div.net_amount
            else:
                security_data[symbol]['cash_amount'] += div.net_amount
        
        # Calculate additional metrics
        for symbol, data in security_data.items():
            data['average_payment'] = data['total_dividends'] / data['payment_count'] if data['payment_count'] > 0 else Decimal('0')
            
            # Current yield calculation
            if symbol in position_map:
                position = position_map[symbol]
                annual_dividend = data['total_dividends']  # Assuming 12-month period
                data['current_yield'] = (annual_dividend / position.market_value * 100) if position.market_value > 0 else Decimal('0')
                data['current_position_value'] = position.market_value
                data['current_shares'] = position.quantity
            else:
                data['current_yield'] = Decimal('0')
                data['current_position_value'] = Decimal('0')
                data['current_shares'] = Decimal('0')
        
        # Sort by total dividends
        sorted_securities = sorted(
            security_data.items(), 
            key=lambda x: x[1]['total_dividends'], 
            reverse=True
        )
        
        return {
            'security_breakdown': dict(sorted_securities),
            'top_dividend_payers': sorted_securities[:10],
            'total_securities': len(security_data),
            'average_payments_per_security': sum(data['payment_count'] for data in security_data.values()) / len(security_data) if security_data else 0
        }
    
    def _calculate_dividend_projections(
        self, 
        dividends: List[Dividend], 
        positions: List[Position]
    ) -> Dict[str, Decimal]:
        """Calculate dividend income projections."""
        if not dividends:
            return {
                'annual_projection': Decimal('0'),
                'quarterly_projection': Decimal('0'),
                'monthly_projection': Decimal('0')
            }
        
        # Calculate based on last 12 months
        total_annual = sum(div.net_amount for div in dividends)
        
        # Forward-looking projection based on current positions and historical yields
        position_map = {pos.symbol: pos for pos in positions}
        projected_annual = Decimal('0')
        
        # Group dividends by security to calculate yields
        security_dividends = {}
        for div in dividends:
            if div.symbol not in security_dividends:
                security_dividends[div.symbol] = []
            security_dividends[div.symbol].append(div)
        
        # Project based on current holdings and historical yields
        for symbol, pos in position_map.items():
            if symbol in security_dividends:
                # Calculate annual dividend per share from historical data
                annual_per_share = sum(div.amount_per_share for div in security_dividends[symbol])
                projected_dividend = annual_per_share * pos.quantity
                projected_annual += projected_dividend
        
        return {
            'annual_projection': projected_annual,
            'quarterly_projection': projected_annual / 4,
            'monthly_projection': projected_annual / 12
        }
    
    def _calculate_dividend_growth_analysis(self, dividends: List[Dividend]) -> Dict[str, any]:
        """Calculate dividend growth trends over time."""
        if len(dividends) < 2:
            return {
                'growth_rate': Decimal('0'),
                'trend': 'Insufficient data',
                'consistency_score': Decimal('0')
            }
        
        # Group dividends by year and security
        yearly_data = {}
        for div in dividends:
            year = div.payment_date.year
            symbol = div.symbol
            
            if year not in yearly_data:
                yearly_data[year] = {}
            
            if symbol not in yearly_data[year]:
                yearly_data[year][symbol] = Decimal('0')
            
            yearly_data[year][symbol] += div.net_amount
        
        # Calculate year-over-year growth for each security
        security_growth_rates = {}
        for symbol in set(div.symbol for div in dividends):
            symbol_years = []
            for year in sorted(yearly_data.keys()):
                if symbol in yearly_data[year]:
                    symbol_years.append((year, yearly_data[year][symbol]))
            
            if len(symbol_years) >= 2:
                # Calculate compound annual growth rate
                first_year_amount = symbol_years[0][1]
                last_year_amount = symbol_years[-1][1]
                years_diff = symbol_years[-1][0] - symbol_years[0][0]
                
                if first_year_amount > 0 and years_diff > 0:
                    cagr = ((last_year_amount / first_year_amount) ** (1 / years_diff) - 1) * 100
                    security_growth_rates[symbol] = Decimal(str(cagr))
        
        # Overall portfolio dividend growth
        if len(yearly_data) >= 2:
            sorted_years = sorted(yearly_data.keys())
            total_first_year = sum(yearly_data[sorted_years[0]].values())
            total_last_year = sum(yearly_data[sorted_years[-1]].values())
            years_diff = sorted_years[-1] - sorted_years[0]
            
            if total_first_year > 0 and years_diff > 0:
                overall_growth = ((total_last_year / total_first_year) ** (1 / years_diff) - 1) * 100
            else:
                overall_growth = Decimal('0')
        else:
            overall_growth = Decimal('0')
        
        # Consistency score (lower standard deviation = higher consistency)
        if security_growth_rates:
            growth_values = list(security_growth_rates.values())
            mean_growth = sum(growth_values) / len(growth_values)
            variance = sum((rate - mean_growth) ** 2 for rate in growth_values) / len(growth_values)
            std_dev = Decimal(str(variance ** 0.5))
            consistency_score = max(Decimal('0'), Decimal('100') - std_dev)
        else:
            consistency_score = Decimal('0')
        
        # Determine trend
        if overall_growth > 5:
            trend = 'Growing'
        elif overall_growth > 0:
            trend = 'Stable'
        elif overall_growth > -5:
            trend = 'Declining'
        else:
            trend = 'Significantly Declining'
        
        return {
            'growth_rate': overall_growth,
            'trend': trend,
            'consistency_score': consistency_score,
            'security_growth_rates': security_growth_rates,
            'yearly_totals': {year: sum(securities.values()) for year, securities in yearly_data.items()}
        }
    
    def calculate_pie_dividend_analysis(
        self,
        pie: Pie,
        dividends: List[Dividend],
        analysis_period_months: int = 12
    ) -> Dict[str, any]:
        """
        Calculate dividend analysis specific to a pie.
        
        Args:
            pie: Pie object
            dividends: All dividend payments
            analysis_period_months: Analysis period in months
            
        Returns:
            Dictionary with pie-specific dividend analysis
        """
        # Filter dividends for this pie's positions
        pie_symbols = {pos.symbol for pos in pie.positions}
        pie_dividends = [
            div for div in dividends 
            if div.symbol in pie_symbols and 
            (div.pie_id == pie.id if div.pie_id else True)
        ]
        
        if not pie_dividends:
            return self._default_dividend_analysis()
        
        # Filter to analysis period
        cutoff_date = datetime.now() - timedelta(days=analysis_period_months * 30)
        period_dividends = [
            div for div in pie_dividends 
            if div.payment_date >= cutoff_date.date()
        ]
        
        # Calculate pie-specific metrics
        pie_value = sum(pos.market_value for pos in pie.positions)
        total_dividends = sum(div.net_amount for div in period_dividends)
        
        # Pie dividend yield
        pie_yield = (total_dividends / pie_value * 100) if pie_value > 0 else Decimal('0')
        
        # Contribution to total portfolio dividends (if provided)
        # This would need total portfolio dividends to calculate
        
        # Monthly breakdown for pie
        monthly_analysis = self._calculate_monthly_dividend_analysis(period_dividends)
        
        # Security analysis within pie
        security_analysis = self._calculate_security_dividend_analysis(period_dividends, pie.positions)
        
        return {
            'pie_id': pie.id,
            'pie_name': pie.name,
            'pie_value': pie_value,
            'total_dividends': total_dividends,
            'pie_yield': pie_yield,
            'dividend_count': len(period_dividends),
            'monthly_analysis': monthly_analysis,
            'security_analysis': security_analysis,
            'reinvestment_rate': (
                sum(div.net_amount for div in period_dividends if div.is_reinvested) / 
                total_dividends * 100
            ) if total_dividends > 0 else Decimal('0')
        }
    
    def _default_dividend_analysis(self) -> Dict[str, any]:
        """Return default dividend analysis when no data is available."""
        return {
            'total_dividends': Decimal('0'),
            'gross_dividends': Decimal('0'),
            'taxes_withheld': Decimal('0'),
            'reinvested_dividends': Decimal('0'),
            'cash_dividends': Decimal('0'),
            'reinvestment_rate': Decimal('0'),
            'current_yield': Decimal('0'),
            'monthly_analysis': {
                'monthly_breakdown': {},
                'trend_percentage': Decimal('0'),
                'average_monthly': Decimal('0')
            },
            'security_analysis': {
                'security_breakdown': {},
                'top_dividend_payers': [],
                'total_securities': 0
            },
            'projections': {
                'annual_projection': Decimal('0'),
                'quarterly_projection': Decimal('0'),
                'monthly_projection': Decimal('0')
            },
            'growth_analysis': {
                'growth_rate': Decimal('0'),
                'trend': 'No data',
                'consistency_score': Decimal('0')
            }
        }