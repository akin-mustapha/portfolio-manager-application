"""
Dividend and income analysis endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user_id
from app.services.calculations_service import CalculationsService
from app.services.trading212_service import Trading212Service

router = APIRouter()


@router.get("/portfolio/analysis")
async def get_portfolio_dividend_analysis(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive dividend and income analysis for the entire portfolio.
    
    Returns detailed dividend metrics, monthly history, reinvestment analysis,
    income projections, and tax analysis.
    """
    try:
        # Initialize services
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            # Load stored credentials
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch portfolio data
            portfolio = await trading212_service.fetch_portfolio_data()
            
            # Fetch dividend data
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate comprehensive dividend analysis
            dividend_analysis = calculations_service.calculate_dividend_income_analysis(
                dividends=dividends,
                positions=portfolio.all_positions
            )
            
            return {
                "status": "success",
                "data": dividend_analysis
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze dividends: {str(e)}")


@router.get("/portfolio/monthly-history")
async def get_monthly_dividend_history(
    months: int = Query(default=12, ge=1, le=60, description="Number of months to retrieve"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get monthly dividend history with trend analysis.
    
    Args:
        months: Number of months to retrieve (1-60)
    
    Returns:
        Monthly dividend history with trends and statistics
    """
    try:
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch dividend data
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate monthly history
            monthly_history = calculations_service._calculate_monthly_dividend_history(dividends)
            
            # Limit to requested months
            if len(monthly_history) > months:
                monthly_history = monthly_history[-months:]
            
            # Calculate summary statistics
            if monthly_history:
                total_amount = sum(month['total_amount'] for month in monthly_history)
                avg_monthly = total_amount / len(monthly_history)
                max_month = max(monthly_history, key=lambda x: x['total_amount'])
                min_month = min(monthly_history, key=lambda x: x['total_amount'])
                
                summary = {
                    'total_amount': total_amount,
                    'average_monthly': avg_monthly,
                    'highest_month': {
                        'month': max_month['month'],
                        'amount': max_month['total_amount']
                    },
                    'lowest_month': {
                        'month': min_month['month'],
                        'amount': min_month['total_amount']
                    },
                    'months_with_dividends': len([m for m in monthly_history if m['total_amount'] > 0])
                }
            else:
                summary = {
                    'total_amount': 0,
                    'average_monthly': 0,
                    'highest_month': None,
                    'lowest_month': None,
                    'months_with_dividends': 0
                }
            
            return {
                "status": "success",
                "data": {
                    "monthly_history": monthly_history,
                    "summary": summary,
                    "period_months": months
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monthly history: {str(e)}")


@router.get("/portfolio/by-security")
async def get_dividend_by_security(
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of securities to return"),
    sort_by: str = Query(default="total_dividends", description="Sort field: total_dividends, current_yield, dividend_count"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get dividend analysis by individual security.
    
    Args:
        limit: Maximum number of securities to return
        sort_by: Field to sort by (total_dividends, current_yield, dividend_count)
    
    Returns:
        Dividend analysis for each security with current positions
    """
    try:
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch data
            portfolio = await trading212_service.fetch_portfolio_data()
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate dividend by security
            dividend_by_security = calculations_service._calculate_dividend_by_security(
                dividends, portfolio.all_positions
            )
            
            # Sort by requested field
            valid_sort_fields = ['total_dividends', 'current_yield', 'dividend_count', 'trailing_12m_dividends']
            if sort_by not in valid_sort_fields:
                sort_by = 'total_dividends'
            
            dividend_by_security.sort(key=lambda x: x[sort_by], reverse=True)
            
            # Limit results
            dividend_by_security = dividend_by_security[:limit]
            
            # Calculate summary
            total_securities = len(dividend_by_security)
            total_dividends = sum(sec['total_dividends'] for sec in dividend_by_security)
            avg_yield = sum(sec['current_yield'] for sec in dividend_by_security) / total_securities if total_securities > 0 else 0
            
            return {
                "status": "success",
                "data": {
                    "securities": dividend_by_security,
                    "summary": {
                        "total_securities": total_securities,
                        "total_dividends": total_dividends,
                        "average_yield": avg_yield
                    },
                    "sort_by": sort_by,
                    "limit": limit
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dividend by security: {str(e)}")


@router.get("/portfolio/reinvestment-analysis")
async def get_reinvestment_analysis(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get detailed reinvestment analysis showing reinvested vs withdrawn dividends.
    
    Returns:
        Comprehensive reinvestment analysis with rates and share acquisition data
    """
    try:
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch dividend data
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate reinvestment analysis
            reinvestment_analysis = calculations_service._calculate_reinvestment_analysis(dividends)
            
            return {
                "status": "success",
                "data": reinvestment_analysis
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze reinvestment: {str(e)}")


@router.get("/portfolio/income-projections")
async def get_income_projections(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get income projections based on historical dividend data and current positions.
    
    Returns:
        Annual, quarterly, and monthly income projections with confidence levels
    """
    try:
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch data
            portfolio = await trading212_service.fetch_portfolio_data()
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate income projections
            income_projections = calculations_service._calculate_income_projections(
                dividends, portfolio.all_positions
            )
            
            return {
                "status": "success",
                "data": income_projections
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate projections: {str(e)}")


@router.get("/portfolio/tax-analysis")
async def get_tax_analysis(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get tax analysis for dividend income including withholding taxes.
    
    Returns:
        Tax analysis with gross/net amounts and effective tax rates
    """
    try:
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch dividend data
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate tax analysis
            tax_analysis = calculations_service._calculate_dividend_tax_analysis(dividends)
            
            return {
                "status": "success",
                "data": tax_analysis
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze taxes: {str(e)}")


@router.get("/pie/{pie_id}/analysis")
async def get_pie_dividend_analysis(
    pie_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive dividend and income analysis for a specific pie.
    
    Args:
        pie_id: Unique pie identifier
    
    Returns:
        Detailed dividend analysis for the specified pie
    """
    try:
        calculations_service = CalculationsService()
        
        async with Trading212Service() as trading212_service:
            if not await trading212_service.load_stored_credentials():
                raise HTTPException(
                    status_code=401,
                    detail="Trading 212 credentials not found. Please authenticate first."
                )
            
            # Fetch portfolio data to get pie
            portfolio = await trading212_service.fetch_portfolio_data()
            
            # Find the specific pie
            target_pie = None
            for pie in portfolio.pies:
                if pie.id == pie_id:
                    target_pie = pie
                    break
            
            if not target_pie:
                raise HTTPException(status_code=404, detail=f"Pie with ID {pie_id} not found")
            
            # Fetch dividend data
            dividends = await trading212_service.fetch_all_dividends()
            
            # Calculate pie-specific dividend analysis
            dividend_analysis = calculations_service.calculate_dividend_income_analysis(
                dividends=dividends,
                positions=target_pie.positions,
                pie_id=pie_id
            )
            
            # Add pie context
            dividend_analysis['pie_info'] = {
                'id': target_pie.id,
                'name': target_pie.name,
                'description': target_pie.description,
                'position_count': target_pie.position_count,
                'total_value': float(target_pie.metrics.total_value),
                'portfolio_weight': float(target_pie.metrics.portfolio_weight)
            }
            
            return {
                "status": "success",
                "data": dividend_analysis
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze pie dividends: {str(e)}")