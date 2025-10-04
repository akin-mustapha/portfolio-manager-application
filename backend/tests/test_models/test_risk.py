"""
Tests for RiskMetrics model.
"""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.models.risk import RiskMetrics
from app.models.enums import RiskCategory


class TestRiskMetrics:
    """Test RiskMetrics model validation and functionality."""
    
    def test_valid_risk_metrics_creation(self, sample_risk_metrics_data):
        """Test creating valid risk metrics."""
        risk_metrics = RiskMetrics(**sample_risk_metrics_data)
        
        assert risk_metrics.volatility == Decimal("15.25")
        assert risk_metrics.sharpe_ratio == Decimal("1.45")
        assert risk_metrics.max_drawdown == Decimal("-8.75")
        assert risk_metrics.beta == Decimal("1.15")
        assert risk_metrics.risk_category == RiskCategory.MEDIUM
        assert risk_metrics.risk_score == Decimal("65.5")
    
    def test_negative_volatility_validation(self):
        """Test that negative volatility raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("-5.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.LOW,
                risk_score=Decimal("50.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_risk_score_range_validation(self):
        """Test that risk score must be between 0 and 100."""
        # Test risk score too high
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.HIGH,
                risk_score=Decimal("150.0")
            )
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)
        
        # Test risk score too low
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.LOW,
                risk_score=Decimal("-10.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_correlation_range_validation(self):
        """Test that correlation must be between -1 and 1."""
        # Test correlation too high
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.MEDIUM,
                risk_score=Decimal("50.0"),
                correlation=Decimal("1.5")
            )
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
        
        # Test correlation too low
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.MEDIUM,
                risk_score=Decimal("50.0"),
                correlation=Decimal("-1.5")
            )
        
        assert "Input should be greater than or equal to -1" in str(exc_info.value)
    
    def test_negative_tracking_error_validation(self):
        """Test that negative tracking error raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.MEDIUM,
                risk_score=Decimal("50.0"),
                tracking_error=Decimal("-2.0")
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_negative_max_drawdown_duration_validation(self):
        """Test that negative max drawdown duration raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=RiskCategory.MEDIUM,
                risk_score=Decimal("50.0"),
                max_drawdown_duration=-5
            )
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics()
        
        error_messages = str(exc_info.value)
        assert "volatility" in error_messages
        assert "max_drawdown" in error_messages
        assert "risk_category" in error_messages
        assert "risk_score" in error_messages
    
    def test_invalid_risk_category(self):
        """Test that invalid risk category raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category="INVALID_CATEGORY",
                risk_score=Decimal("50.0")
            )
        
        assert "Input should be" in str(exc_info.value)
    
    def test_optional_fields_default_values(self):
        """Test that optional fields can be None and have proper defaults."""
        risk_metrics = RiskMetrics(
            volatility=Decimal("15.0"),
            max_drawdown=Decimal("-10.0"),
            risk_category=RiskCategory.MEDIUM,
            risk_score=Decimal("50.0")
        )
        
        assert risk_metrics.volatility_30d is None
        assert risk_metrics.volatility_90d is None
        assert risk_metrics.sharpe_ratio is None
        assert risk_metrics.sortino_ratio is None
        assert risk_metrics.beta is None
        assert risk_metrics.alpha is None
        assert risk_metrics.correlation is None
        assert risk_metrics.tracking_error is None
        assert risk_metrics.var_95 is None
        assert risk_metrics.var_99 is None
        assert risk_metrics.cvar_95 is None
        assert risk_metrics.max_drawdown_duration is None
        assert risk_metrics.current_drawdown == Decimal('0')
    
    def test_json_serialization(self, sample_risk_metrics_data):
        """Test JSON serialization of risk metrics."""
        risk_metrics = RiskMetrics(**sample_risk_metrics_data)
        json_data = risk_metrics.model_dump()
        
        assert json_data["volatility"] == 15.25
        assert json_data["risk_category"] == "MEDIUM"
        assert json_data["risk_score"] == 65.5
    
    def test_all_risk_categories(self):
        """Test that all risk categories work correctly."""
        for risk_cat in RiskCategory:
            risk_metrics = RiskMetrics(
                volatility=Decimal("15.0"),
                max_drawdown=Decimal("-10.0"),
                risk_category=risk_cat,
                risk_score=Decimal("50.0")
            )
            assert risk_metrics.risk_category == risk_cat
    
    def test_edge_case_values(self):
        """Test edge case values for risk metrics."""
        # Test minimum values
        risk_metrics = RiskMetrics(
            volatility=Decimal("0"),
            max_drawdown=Decimal("0"),
            risk_category=RiskCategory.LOW,
            risk_score=Decimal("0"),
            correlation=Decimal("-1"),
            tracking_error=Decimal("0"),
            max_drawdown_duration=0
        )
        
        assert risk_metrics.volatility == Decimal("0")
        assert risk_metrics.risk_score == Decimal("0")
        assert risk_metrics.correlation == Decimal("-1")
        
        # Test maximum values
        risk_metrics = RiskMetrics(
            volatility=Decimal("100"),
            max_drawdown=Decimal("-100"),
            risk_category=RiskCategory.VERY_HIGH,
            risk_score=Decimal("100"),
            correlation=Decimal("1"),
            tracking_error=Decimal("50")
        )
        
        assert risk_metrics.risk_score == Decimal("100")
        assert risk_metrics.correlation == Decimal("1")