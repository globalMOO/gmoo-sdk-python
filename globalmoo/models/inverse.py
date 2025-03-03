# globalmoo/models/inverse.py
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from pydantic import field_validator
from .base import GlobalMooModel
from .result import Result
from ..enums.stop_reason import StopReason
from ..enums.objective_type import ObjectiveType

class Inverse(GlobalMooModel):
    """Model representing an inverse optimization step."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    loaded_at: Optional[datetime] = None
    satisfied_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    exhausted_at: Optional[datetime] = None
    iteration: int
    l1_norm: float = 0.0
    suggest_time: int = 0  # Time in nanoseconds for suggestion
    compute_time: int = 0  # Time in nanoseconds for computation
    input: List[Union[int, float]]
    output: Optional[List[Union[int, float]]] = None
    errors: Optional[List[Union[int, float]]] = None
    results: Optional[List[Result]] = None

    @field_validator('results', mode='before')
    def validate_results(cls, v: Optional[List[Dict[str, Any]]]) -> Optional[List[Result]]:
        """Convert result dictionaries to Result objects."""
        if v is None:
            return None
        return [Result.model_validate(result) for result in v]

    def get_result_details(self) -> List[str]:
        """Get the satisfaction details for each objective."""
        if not self.results:
            return []
        return [result.detail or '' for result in self.results]

    def get_satisfaction_status(self) -> List[bool]:
        """Get the satisfaction status for each objective."""
        if not self.results:
            return []
        return [result.satisfied for result in self.results]

    def get_objective_errors(self) -> List[float]:
        """Get the error values for each objective."""
        if not self.results:
            return []
        return [result.error for result in self.results]

    def get_stop_reason(self) -> StopReason:
        """Get the reason why the optimization stopped (if it has)."""
        if self.satisfied_at is not None:
            return StopReason.SATISFIED
        elif self.stopped_at is not None:
            return StopReason.STOPPED
        elif self.exhausted_at is not None:
            return StopReason.EXHAUSTED
        return StopReason.RUNNING

    def get_objective_errors(self) -> List[float]:
        """Get the error values for each objective."""
        if not self.results:
            return []
        return [result.error for result in self.results]

    def should_stop(self) -> bool:
        """Determine if the optimization should stop."""
        return self.get_stop_reason() != StopReason.RUNNING