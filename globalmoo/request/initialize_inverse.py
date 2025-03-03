# globalmoo/request/initialize_inverse.py
from typing import List, Union, Type

from ..models.trial import Trial
from ..enums.objective_type import ObjectiveType
from .base import BaseRequest

class InitializeInverse(BaseRequest):
    """Request to initialize inverse optimization."""
    
    def __init__(
        self,
        trial_id: int,
        convergence: float,
        objectives: List[Union[int, float]],
        objective_types: List[ObjectiveType],
        initial_input: List[Union[int, float]],
        initial_output: List[Union[int, float]],
        uncertain_min: List[Union[int, float]],
        uncertain_max: List[Union[int, float]]
    ) -> None:
        self.trial_id = trial_id
        self.convergence = convergence
        self.objectives = objectives
        self.objective_types = objective_types
        self.initial_input = initial_input
        self.initial_output = initial_output
        self.uncertain_min = uncertain_min
        self.uncertain_max = uncertain_max
    
    def get_url(self) -> str:
        return f"trials/{self.trial_id}/initialize-inverse"
    
    def get_response_type(self) -> Type[Trial]:
        return Trial
    
    def to_dict(self) -> dict:
        return {
            "convergence": self.convergence,
            "objectives": self.objectives,
            "objectiveTypes": self.objective_types,
            "initialInput": self.initial_input,
            "initialOutput": self.initial_output,
            "minimumBounds": self.uncertain_min,
            "maximumBounds": self.uncertain_max
        }