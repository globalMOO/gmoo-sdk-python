# globalmoo/request/create_model.py
from typing import Optional, Type

from ..models.model import Model
from .base import BaseRequest

class CreateModel(BaseRequest):
    """Request to create a new model."""
    
    def __init__(self, name: str, description: Optional[str] = None) -> None:
        self.name = name
        self.description = description
    
    def _get_path(self) -> str:
        return "models"
    
    def get_response_type(self) -> Type[Model]:
        return Model
    
    def to_dict(self) -> dict[str, Optional[str]]:
        return {
            "name": self.name,
            "description": self.description
        }