from datetime import datetime
from typing import List, Optional, Union
from .base import GlobalMooModel
from .inverse import Inverse
from ..enums.stop_reason import StopReason
from ..enums.objective_type import ObjectiveType


class Objective(GlobalMooModel):
    """Model representing an optimization objective."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    optimal_inverse: Optional[Inverse] = None
    attempt_count: int = 0
    stop_reason: StopReason
    desired_l1_norm: float
    objectives: List[Union[int, float]]
    objective_types: List[ObjectiveType]
    minimum_bounds: List[Union[int, float]]
    maximum_bounds: List[Union[int, float]]
    inverses: List[Inverse] = []

    @property
    def iteration_count(self) -> int:
        """Get the total number of iterations."""
        return len(self.inverses)

    @property
    def last_inverse(self) -> Optional[Inverse]:
        """Get the last inverse if any exist."""
        if not self.inverses:
            return None
        return self.inverses[-1]
