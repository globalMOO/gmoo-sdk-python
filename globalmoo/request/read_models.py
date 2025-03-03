# globalmoo/request/read_models.py
from typing import List, Type

from ..models.model import Model
from .base import BaseRequest

class ReadModels(BaseRequest):
    """Request to list all models."""
    
    def get_method(self) -> str:
        return "GET"
    
    def _get_path(self) -> str:
        return "models"
    
    def get_response_type(self) -> Type[List[Model]]:
        return List[Model]