# globalmoo/request/read_trial.py
from typing import Type

from ..models.trial import Trial
from .base import BaseRequest

class ReadTrial(BaseRequest):
    """Request to read a specific trial."""
    
    def __init__(self, trial_id: int) -> None:
        self.trial_id = trial_id
    
    def get_method(self) -> str:
        return "GET"
    
    def _get_path(self) -> str:
        return f"trials/{self.trial_id}"
    
    def get_response_type(self) -> Type[Trial]:
        return Trial