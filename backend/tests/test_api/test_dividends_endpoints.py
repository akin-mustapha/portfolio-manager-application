"""
Integration tests for dividends API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime, date

from app.main import app
from app.models.portfolio import Portfolio, PortfolioMetrics
from app.models.position import Position
from app.models.pie import Pie, PieMetrics
from app.models.dividend import Dividend
from app.models.enums import AssetType, DividendType
from app.services.trading212_service import Trading212APIError


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_dividend():
    """Create mock dividend."""
    return Dividend(
        symbol="AAPL",
        security_name="Apple Inc.",
        dividend_type=DividendType.CASH,
        amount_per_share=Decimal('0.25'),
        total_amount=Decimal('2.50'),
        shares_held=Decimal('10'),
        ex_dividend_date=date(2024, 1, 10),
        payment_date=date(2024, 1, 25),
        gross_amount=Decimal('2.50'),
        tax_withheld=Decimal('0.00'),
        net_amount=Decimal('2.50'),
        currency="USD",
        is_reinvested=False
    )


@pytest.fixture
def mock_position():
    """Create mock position."""
    return Position(
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
    )


@pytest.fixture
def mock_pie(mock_position):
    """Create mock pie."""
    return Pie(
        id="test-pie-id",
        name="Test Pie",
        description="Test pie description",
        positions=[mock_position],
        metrics=PieMetrics(
            total_value=Decimal('1600.00'),
            invested_amount=Decimal('1500.00'),
            total_return=Decimal('100.00'),
            total_return_pct=Decimal('6.67'),
            portfolio_weight=Decimal('32.0'),
            portfolio_contribution=Decimal('2.0'),
            dividend_yield=Decimal('2.5')
        ),
        last_updated=datetime.utcnow()
    )


@pytest.fixture
def mock_portfolio(mock_position, mock_pie):
    """Create mock portfolio."""
    return Portfolio(
        id="test-portfolio",
        user_id="test-user",
        name="Test Portfolio",
        pies=[mock_pie],
        individual_positions=[mock_position],
        metrics=PortfolioMetrics(
            total_value=Decimal('5000.00'),
            total_invested=Decimal('4800.00'),
            total_return=Decimal('200.00'),
            total_return_pct=Decimal('4.17'),
            annualized_return=Decimal('5.2'),
            sector_allocation={},
            industry_allocation={},
            country_allocation={},
            asset_type_allocation={},
            diversification_score=Decimal('75.0'),
            concentration_risk=Decimal('25.0'),
            top_10_weight=Decimal('100.0'),
            dividend_yield=Decimal('2.5')
        ),
        last_updated=datetime.utcnow()
    )


class TestPortfolioDividendAnalysisEndpoints:
    """Test portfolio dividend analysis endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_portfolio_dividend_analysis_success(self, mock_calc_service, mock_trading_service,
                                                   mock_user_id, client, mock_portfolio, mock_dividend):
        """Test successful portfolio dividend analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance.calculate_dividend_income_analysis.return_value = {
            "total_dividends": 125.50,
            "annual_dividend_yield": 2.5,
            "monthly_average": 10.46,
            "reinvestment_rate": 75.0,
            "tax_efficiency": 85.0,
            "income_growth_rate": 5.2,
            "projected_annual_income": 130.0
        }
        
        response = client.get("/api/v1/dividends/portfolio/analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        dividend_data = data["data"]
        assert "total_dividends" in dividend_data
        assert "annual_dividend_yield" in dividend_data
        assert dividend_data["total_dividends"] == 125.50

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    def test_get_portfolio_dividend_analysis_no_credentials(self, mock_trading_service, mock_user_id, client):
        """Test portfolio dividend analysis without credentials."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = False
        
        response = client.get("/api/v1/dividends/portfolio/analysis")
        
        assert response.status_code == 401
        assert "Trading 212 credentials not found" in response.json()["detail"]

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    def test_get_portfolio_dividend_analysis_service_error(self, mock_trading_service, mock_user_id, client):
        """Test portfolio dividend analysis with service error."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.side_effect = Exception("Service error")
        
        response = client.get("/api/v1/dividends/portfolio/analysis")
        
        assert response.status_code == 500
        assert "Failed to analyze dividends" in response.json()["detail"]


class TestMonthlyDividendHistoryEndpoints:
    """Test monthly dividend history endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_monthly_dividend_history_success(self, mock_calc_service, mock_trading_service,
                                                 mock_user_id, client, mock_dividend):
        """Test successful monthly dividend history retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_monthly_dividend_history.return_value = [
            {"month": "2024-01", "total_amount": 25.50, "dividend_count": 3},
            {"month": "2024-02", "total_amount": 30.25, "dividend_count": 4},
            {"month": "2024-03", "total_amount": 22.75, "dividend_count": 2}
        ]
        
        response = client.get("/api/v1/dividends/portfolio/monthly-history?months=12")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        history_data = data["data"]
        assert "monthly_history" in history_data
        assert "summary" in history_data
        assert history_data["period_months"] == 12
        assert len(history_data["monthly_history"]) == 3

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_monthly_dividend_history_with_limit(self, mock_calc_service, mock_trading_service,
                                                    mock_user_id, client, mock_dividend):
        """Test monthly dividend history with month limit."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock - return more months than requested
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_monthly_dividend_history.return_value = [
            {"month": f"2024-{i:02d}", "total_amount": 25.0 + i, "dividend_count": i}
            for i in range(1, 25)  # 24 months
        ]
        
        response = client.get("/api/v1/dividends/portfolio/monthly-history?months=6")
        
        assert response.status_code == 200
        data = response.json()
        history_data = data["data"]
        # Should only return the last 6 months
        assert len(history_data["monthly_history"]) == 6

    def test_get_monthly_dividend_history_invalid_months(self, client):
        """Test monthly dividend history with invalid months parameter."""
        # Test months too low
        response = client.get("/api/v1/dividends/portfolio/monthly-history?months=0")
        assert response.status_code == 422
        
        # Test months too high
        response = client.get("/api/v1/dividends/portfolio/monthly-history?months=100")
        assert response.status_code == 422


class TestDividendBySecurityEndpoints:
    """Test dividend by security endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_dividend_by_security_success(self, mock_calc_service, mock_trading_service,
                                            mock_user_id, client, mock_portfolio, mock_dividend):
        """Test successful dividend by security retrieval."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_dividend_by_security.return_value = [
            {
                "symbol": "AAPL",
                "security_name": "Apple Inc.",
                "total_dividends": 125.50,
                "current_yield": 2.5,
                "dividend_count": 12,
                "trailing_12m_dividends": 125.50,
                "average_dividend": 10.46
            }
        ]
        
        response = client.get("/api/v1/dividends/portfolio/by-security?limit=50&sort_by=total_dividends")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        security_data = data["data"]
        assert "securities" in security_data
        assert "summary" in security_data
        assert security_data["sort_by"] == "total_dividends"
        assert security_data["limit"] == 50

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_dividend_by_security_different_sort(self, mock_calc_service, mock_trading_service,
                                                   mock_user_id, client, mock_portfolio, mock_dividend):
        """Test dividend by security with different sort field."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_dividend_by_security.return_value = []
        
        response = client.get("/api/v1/dividends/portfolio/by-security?sort_by=current_yield")
        
        assert response.status_code == 200
        data = response.json()
        security_data = data["data"]
        assert security_data["sort_by"] == "current_yield"

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_dividend_by_security_invalid_sort(self, mock_calc_service, mock_trading_service,
                                                  mock_user_id, client, mock_portfolio, mock_dividend):
        """Test dividend by security with invalid sort field."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_dividend_by_security.return_value = []
        
        response = client.get("/api/v1/dividends/portfolio/by-security?sort_by=invalid_field")
        
        assert response.status_code == 200
        data = response.json()
        security_data = data["data"]
        # Should default to total_dividends
        assert security_data["sort_by"] == "total_dividends"

    def test_get_dividend_by_security_invalid_limit(self, client):
        """Test dividend by security with invalid limit."""
        # Test limit too low
        response = client.get("/api/v1/dividends/portfolio/by-security?limit=0")
        assert response.status_code == 422
        
        # Test limit too high
        response = client.get("/api/v1/dividends/portfolio/by-security?limit=300")
        assert response.status_code == 422


class TestReinvestmentAnalysisEndpoints:
    """Test reinvestment analysis endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_reinvestment_analysis_success(self, mock_calc_service, mock_trading_service,
                                             mock_user_id, client, mock_dividend):
        """Test successful reinvestment analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_reinvestment_analysis.return_value = {
            "total_dividends": 500.0,
            "reinvested_amount": 375.0,
            "withdrawn_amount": 125.0,
            "reinvestment_rate": 75.0,
            "shares_acquired_through_reinvestment": 25.5,
            "reinvestment_impact_on_returns": 2.3
        }
        
        response = client.get("/api/v1/dividends/portfolio/reinvestment-analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        reinvestment_data = data["data"]
        assert "total_dividends" in reinvestment_data
        assert "reinvestment_rate" in reinvestment_data
        assert reinvestment_data["reinvestment_rate"] == 75.0


class TestIncomeProjectionsEndpoints:
    """Test income projections endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_income_projections_success(self, mock_calc_service, mock_trading_service,
                                          mock_user_id, client, mock_portfolio, mock_dividend):
        """Test successful income projections."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_income_projections.return_value = {
            "annual_projection": 650.0,
            "quarterly_projection": 162.5,
            "monthly_projection": 54.17,
            "confidence_level": 85.0,
            "growth_rate": 5.2,
            "projection_basis": "12-month trailing average"
        }
        
        response = client.get("/api/v1/dividends/portfolio/income-projections")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        projection_data = data["data"]
        assert "annual_projection" in projection_data
        assert "confidence_level" in projection_data
        assert projection_data["annual_projection"] == 650.0


class TestTaxAnalysisEndpoints:
    """Test tax analysis endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_tax_analysis_success(self, mock_calc_service, mock_trading_service,
                                    mock_user_id, client, mock_dividend):
        """Test successful tax analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_dividend_tax_analysis.return_value = {
            "gross_dividends": 500.0,
            "tax_withheld": 75.0,
            "net_dividends": 425.0,
            "effective_tax_rate": 15.0,
            "tax_by_country": {
                "US": {"gross": 300.0, "tax": 45.0, "net": 255.0},
                "UK": {"gross": 200.0, "tax": 30.0, "net": 170.0}
            }
        }
        
        response = client.get("/api/v1/dividends/portfolio/tax-analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        tax_data = data["data"]
        assert "gross_dividends" in tax_data
        assert "effective_tax_rate" in tax_data
        assert tax_data["effective_tax_rate"] == 15.0


class TestPieDividendAnalysisEndpoints:
    """Test pie dividend analysis endpoints."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_get_pie_dividend_analysis_success(self, mock_calc_service, mock_trading_service,
                                             mock_user_id, client, mock_portfolio, mock_dividend):
        """Test successful pie dividend analysis."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance.calculate_dividend_income_analysis.return_value = {
            "total_dividends": 50.0,
            "annual_dividend_yield": 3.1,
            "monthly_average": 4.17,
            "pie_contribution_to_portfolio_dividends": 20.0
        }
        
        response = client.get("/api/v1/dividends/pie/test-pie-id/analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        pie_data = data["data"]
        assert "total_dividends" in pie_data
        assert "pie_info" in pie_data
        assert pie_data["pie_info"]["id"] == "test-pie-id"

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    def test_get_pie_dividend_analysis_pie_not_found(self, mock_trading_service, mock_user_id, 
                                                    client, mock_portfolio):
        """Test pie dividend analysis for non-existent pie."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.return_value = mock_portfolio
        
        response = client.get("/api/v1/dividends/pie/non-existent-pie-id/analysis")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_query_parameters(self, client):
        """Test endpoints with invalid query parameters."""
        # Test invalid months range
        response = client.get("/api/v1/dividends/portfolio/monthly-history?months=0")
        assert response.status_code == 422
        
        response = client.get("/api/v1/dividends/portfolio/monthly-history?months=100")
        assert response.status_code == 422
        
        # Test invalid limit range
        response = client.get("/api/v1/dividends/portfolio/by-security?limit=0")
        assert response.status_code == 422
        
        response = client.get("/api/v1/dividends/portfolio/by-security?limit=300")
        assert response.status_code == 422

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    def test_service_exception_handling(self, mock_trading_service, mock_user_id, client):
        """Test handling of service exceptions."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_portfolio_data.side_effect = Exception("Service error")
        
        response = client.get("/api/v1/dividends/portfolio/analysis")
        
        assert response.status_code == 500
        assert "Failed to analyze dividends" in response.json()["detail"]

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    def test_credentials_not_found_handling(self, mock_trading_service, mock_user_id, client):
        """Test handling when credentials are not found."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = False
        
        response = client.get("/api/v1/dividends/portfolio/analysis")
        
        assert response.status_code == 401
        assert "Trading 212 credentials not found" in response.json()["detail"]


class TestDividendCalculations:
    """Test dividend calculation logic."""

    @patch('app.api.v1.endpoints.dividends.get_current_user_id')
    @patch('app.api.v1.endpoints.dividends.Trading212Service')
    @patch('app.api.v1.endpoints.dividends.CalculationsService')
    def test_monthly_history_summary_calculations(self, mock_calc_service, mock_trading_service,
                                                 mock_user_id, client, mock_dividend):
        """Test that monthly history summary calculations are correct."""
        # Setup mocks
        mock_user_id.return_value = "test-user"
        
        # Trading 212 service mock
        mock_trading_instance = Mock()
        mock_trading_service.return_value.__aenter__.return_value = mock_trading_instance
        mock_trading_instance.load_stored_credentials.return_value = True
        mock_trading_instance.fetch_all_dividends.return_value = [mock_dividend]
        
        # Calculations service mock with specific data
        mock_calc_instance = Mock()
        mock_calc_service.return_value = mock_calc_instance
        mock_calc_instance._calculate_monthly_dividend_history.return_value = [
            {"month": "2024-01", "total_amount": 100.0, "dividend_count": 5},
            {"month": "2024-02", "total_amount": 150.0, "dividend_count": 7},
            {"month": "2024-03", "total_amount": 0.0, "dividend_count": 0}  # No dividends month
        ]
        
        response = client.get("/api/v1/dividends/portfolio/monthly-history")
        
        assert response.status_code == 200
        data = response.json()
        summary = data["data"]["summary"]
        
        # Check summary calculations
        assert summary["total_amount"] == 250.0  # 100 + 150 + 0
        assert summary["average_monthly"] == 250.0 / 3  # Total / 3 months
        assert summary["highest_month"]["amount"] == 150.0
        assert summary["lowest_month"]["amount"] == 0.0
        assert summary["months_with_dividends"] == 2  # Only Jan and Feb had dividends


if __name__ == "__main__":
    pytest.main([__file__])