# globalmoo/models/result.py
from datetime import datetime
from typing import Optional
from pydantic import Field, ConfigDict
from .base import GlobalMooModel
from ..enums.objective_type import ObjectiveType

class Result(GlobalMooModel):
    """Model representing a result from an inverse optimization step."""
    model_config = ConfigDict(frozen=True)  # Make it explicit that instances are immutable

    id: int
    created_at: datetime
    updated_at: datetime 
    disabled_at: Optional[datetime] = None
    number: int = Field(ge=0)
    objective: float = 0.0
    objective_type: ObjectiveType = ObjectiveType.EXACT
    minimum_bound: float = 0.0
    maximum_bound: float = 0.0
    output: float = 0.0
    error: float = 0.0
    detail: Optional[str] = None
    satisfied: bool = True

    def get_objective_formatted(self) -> str:
        """Get formatted objective value."""
        return self._format_value(self.objective)

    def get_minimum_bound_formatted(self) -> str:
        """Get formatted minimum bound."""
        return self._format_value(self.minimum_bound)

    def get_maximum_bound_formatted(self) -> str:
        """Get formatted maximum bound."""
        return self._format_value(self.maximum_bound)

    def get_output_formatted(self) -> str:
        """Get formatted output value."""
        return self._format_value(self.output)

    def get_error_formatted(self) -> str:
        """Get formatted error value."""
        return self._format_value(self.error)

    def _format_value(self, value: float) -> str:
        """Format a value based on objective type."""
        if self.objective_type.is_percent():
            return f"{value:.6f}%"
        return f"{value:.6f}"

    def with_satisfied_detail(self, detail: str) -> 'Result':
        """Create new instance with satisfied status and detail."""
        return self.model_copy(update={"satisfied": True, "detail": detail})

    def with_unsatisfied_detail(self, detail: str) -> 'Result':
        """Create new instance with unsatisfied status and detail."""
        return self.model_copy(update={"satisfied": False, "detail": detail})
