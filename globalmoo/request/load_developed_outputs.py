# globalmoo/request/load_developed_outputs.py
from typing import List, Union, Type

from ..models.trial import Trial
from .base import BaseRequest

class LoadDevelopedOutputs(BaseRequest):
    """Request to load developed outputs into a trial."""
    
    def __init__(
        self,
        trial_id: int,
        count: int,
        outputs: List[List[Union[int, float]]]
    ) -> None:
        self.trial_id = trial_id
        self.count = count
        self.outputs = outputs
    
    def get_url(self) -> str:
        return f"trials/{self.trial_id}/load-developed-outputs"
    
    def get_response_type(self) -> Type[Trial]:
        return Trial
    
    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "outputs": self.outputs
        }