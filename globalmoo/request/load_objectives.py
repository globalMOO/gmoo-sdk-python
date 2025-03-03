# globalmoo/request/load_objectives.py
from typing import List, Union, Type
from .base import BaseRequest
from ..models.objective import Objective
from ..models.inverse import Inverse
from ..enums.objective_type import ObjectiveType


class LoadObjectives(BaseRequest):
    """Request to load objectives for a trial."""
    
    def __init__(
        self,
        trial_id: int,
        objectives: List[Union[int, float]],
        objective_types: List[ObjectiveType],
        initial_input: List[Union[int, float]],
        initial_output: List[Union[int, float]],
        desired_l1_norm: float = None,
        minimum_bounds: List[Union[int, float]] = None,
        maximum_bounds: List[Union[int, float]] = None,
    ):
        """Initialize the request."""
        self.trial_id = trial_id
        self.objectives = objectives
        
        # Convert strings to ObjectiveType if needed
        self.objective_types = [ot if isinstance(ot, ObjectiveType) else ObjectiveType(ot)
                              for ot in objective_types]
        
        self.initial_input = initial_input
        self.initial_output = initial_output

        # Set defaults for bounds if not provided and using all EXACT types
        if all(ot == ObjectiveType.EXACT for ot in self.objective_types):
            self.minimum_bounds = [0.0] * len(objectives) if minimum_bounds is None else minimum_bounds
            self.maximum_bounds = [0.0] * len(objectives) if maximum_bounds is None else maximum_bounds
        else:
            self.minimum_bounds = minimum_bounds
            self.maximum_bounds = maximum_bounds

        # Default l1_norm to 0 if not provided
        self.desired_l1_norm = 0.0 if desired_l1_norm is None else desired_l1_norm

    def _get_path(self) -> str:
        return f"trials/{self.trial_id}/objectives"

    def get_response_type(self) -> Type[Objective]:
        return Objective

    def to_dict(self) -> dict:
        return {
            "desiredL1Norm": self.desired_l1_norm,
            "objectives": self.objectives,
            "objectiveTypes": [ot.value for ot in self.objective_types],
            "initialInput": self.initial_input,
            "initialOutput": self.initial_output,
            "minimumBounds": self.minimum_bounds,
            "maximumBounds": self.maximum_bounds,
        }