# tests/test_result.py
from datetime import datetime
from pydantic import BaseModel
from globalmoo.models.result import Result
from globalmoo.enums.objective_type import ObjectiveType

class TestResult:
    """Tests for Result model."""

    def test_basic_initialization(self):
        """Should initialize with minimum required fields."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=1.0,
            objective_type=ObjectiveType.EXACT,
            minimum_bound=0.0,
            maximum_bound=2.0,
            output=1.5,
            error=0.5,
            detail="Test detail",
            satisfied=True
        )
        assert result.id == 1
        assert result.number == 0
        assert result.objective == 1.0
        assert result.objective_type == ObjectiveType.EXACT
        assert result.minimum_bound == 0.0
        assert result.maximum_bound == 2.0
        assert result.output == 1.5
        assert result.error == 0.5
        assert result.detail == "Test detail"
        assert result.satisfied is True

    def test_number_validation(self):
        """Should ensure number is non-negative."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=1.0,
            objective_type=ObjectiveType.EXACT,
            minimum_bound=0.0,
            maximum_bound=1.0,
            output=0.5,
            error=0.5
        )
        assert result.number >= 0

    def test_default_values(self):
        """Should use correct default values."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=1.0
        )
        assert result.objective_type == ObjectiveType.EXACT
        assert result.minimum_bound == 0.0
        assert result.maximum_bound == 0.0
        assert result.output == 0.0
        assert result.error == 0.0
        assert result.detail is None
        assert result.satisfied is True
        assert result.disabled_at is None

    def test_formatted_values_exact(self):
        """Should format exact values correctly."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=1.23456789,
            objective_type=ObjectiveType.EXACT,
            minimum_bound=0.98765432,
            maximum_bound=1.56789012,
            output=1.34567890,
            error=0.11111111
        )
        assert result.get_objective_formatted() == "1.234568"
        assert result.get_minimum_bound_formatted() == "0.987654"
        assert result.get_maximum_bound_formatted() == "1.567890"
        assert result.get_output_formatted() == "1.345679"
        assert result.get_error_formatted() == "0.111111"

    def test_formatted_values_percent(self):
        """Should format percentage values correctly."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=12.3456789,
            objective_type=ObjectiveType.PERCENT,
            minimum_bound=9.8765432,
            maximum_bound=15.6789012,
            output=13.4567890,
            error=1.1111111
        )
        assert result.get_objective_formatted() == "12.345679%"
        assert result.get_minimum_bound_formatted() == "9.876543%"
        assert result.get_maximum_bound_formatted() == "15.678901%"
        assert result.get_output_formatted() == "13.456789%"
        assert result.get_error_formatted() == "1.111111%"

    def test_satisfaction_methods(self):
        """Should create new instances with updated satisfaction status."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=1.0
        )
        
        # Test satisfied case
        satisfied_result = result.with_satisfied_detail("Test satisfied")
        assert satisfied_result.satisfied is True
        assert satisfied_result.detail == "Test satisfied"
        # Original should be unchanged
        assert result.satisfied is True
        assert result.detail is None
        
        # Test unsatisfied case
        unsatisfied_result = result.with_unsatisfied_detail("Test unsatisfied")
        assert unsatisfied_result.satisfied is False
        assert unsatisfied_result.detail == "Test unsatisfied"
        # Original should be unchanged
        assert result.satisfied is True
        assert result.detail is None

    def test_model_copy(self):
        """Should support model copying with updates."""
        result = Result(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number=0,
            objective=1.0
        )
        
        copied = result.model_copy(update={"detail": "New detail", "satisfied": False})
        assert copied.detail == "New detail"
        assert copied.satisfied is False
        # Original should be unchanged
        assert result.detail is None
        assert result.satisfied is True