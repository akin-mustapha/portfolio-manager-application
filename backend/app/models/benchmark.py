from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class BenchmarkInfo(BaseModel):
    """Basic information about a benchmark index"""
    symbol: str = Field(..., description="Benchmark symbol (e.g., SPY, QQQ)")
    name: str = Field(..., description="Full name of the benchmark")
    description: str = Field(..., description="Description of what the benchmark tracks")
    category: str = Field(..., description="Category (e.g., US Equity, International Equity)")


class BenchmarkDataPoint(BaseModel):
    """Single data point for benchmark historical data"""
    date: datetime = Field(..., description="Date of the data point")
    price: Decimal = Field(..., ge=0, description="Price at this date")
    return_pct: Optional[Decimal] = Field(None, description="Return percentage from previous period")
    volume: Optional[int] = Field(None, description="Trading volume")


class BenchmarkData(BaseModel):
    """Historical data for a benchmark index"""
    symbol: str = Field(..., description="Benchmark symbol")
    name: str = Field(..., description="Benchmark name")
    period: str = Field(..., description="Time period of the data")
    start_date: datetime = Field(..., description="Start date of the data")
    end_date: datetime = Field(..., description="End date of the data")
    data_points: List[BenchmarkDataPoint] = Field(..., description="Historical data points")
    
    # Summary statistics
    total_return_pct: Decimal = Field(..., description="Total return over the period")
    annualized_return_pct: Optional[Decimal] = Field(None, description="Annualized return")
    volatility: Optional[Decimal] = Field(None, description="Volatility (standard deviation)")
    max_drawdown: Optional[Decimal] = Field(None, description="Maximum drawdown")
    sharpe_ratio: Optional[Decimal] = Field(None, description="Sharpe ratio")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class BenchmarkComparison(BaseModel):
    """Comparison between portfolio/pie and benchmark"""
    entity_type: str = Field(..., description="Type of entity being compared (portfolio or pie)")
    entity_id: str = Field(..., description="ID of the entity")
    entity_name: str = Field(..., description="Name of the entity")
    
    benchmark_symbol: str = Field(..., description="Benchmark symbol")
    benchmark_name: str = Field(..., description="Benchmark name")
    
    period: str = Field(..., description="Comparison period")
    start_date: datetime = Field(..., description="Start date of comparison")
    end_date: datetime = Field(..., description="End date of comparison")
    
    # Performance metrics
    entity_return_pct: Decimal = Field(..., description="Entity return percentage")
    benchmark_return_pct: Decimal = Field(..., description="Benchmark return percentage")
    alpha: Decimal = Field(..., description="Alpha (excess return over benchmark)")
    beta: Decimal = Field(..., description="Beta (sensitivity to benchmark)")
    
    # Risk metrics
    tracking_error: Decimal = Field(..., description="Tracking error")
    correlation: Decimal = Field(..., ge=-1, le=1, description="Correlation coefficient")
    r_squared: Decimal = Field(..., ge=0, le=1, description="R-squared (coefficient of determination)")
    
    # Additional metrics
    information_ratio: Optional[Decimal] = Field(None, description="Information ratio")
    up_capture: Optional[Decimal] = Field(None, description="Up capture ratio")
    down_capture: Optional[Decimal] = Field(None, description="Down capture ratio")
    
    # Summary
    outperforming: bool = Field(..., description="Whether entity is outperforming benchmark")
    outperformance_amount: Decimal = Field(..., description="Amount of outperformance")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class CustomBenchmark(BaseModel):
    """Custom benchmark composed of multiple indices"""
    id: str = Field(..., description="Unique custom benchmark ID")
    name: str = Field(..., description="Custom benchmark name")
    description: Optional[str] = Field(None, description="Description of the custom benchmark")
    
    components: List[Dict[str, Any]] = Field(..., description="Benchmark components with weights")
    total_weight: Decimal = Field(..., description="Total weight (should be 100)")
    
    created_by: str = Field(..., description="User ID who created the benchmark")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class BenchmarkAnalysis(BaseModel):
    """Comprehensive benchmark analysis results"""
    analysis_type: str = Field(..., description="Type of analysis performed")
    period: str = Field(..., description="Analysis period")
    benchmark_symbol: str = Field(..., description="Benchmark used for analysis")
    
    portfolio_analysis: Optional[BenchmarkComparison] = Field(None, description="Portfolio vs benchmark")
    pie_analyses: List[BenchmarkComparison] = Field(default_factory=list, description="Pie vs benchmark analyses")
    
    summary_stats: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }