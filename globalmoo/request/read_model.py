# globalmoo/request/read_model.py
from typing import Type

from ..models.model import Model
from .base import BaseRequest

class ReadModel(BaseRequest):
    """Request to read a specific model."""

    def __init__(self, model_id: int) -> None:
        self.model_id = model_id

    def get_method(self) -> str:
        return "GET"

    def _get_path(self) -> str:
        return f"models/{self.model_id}"

    def get_response_type(self) -> Type[Model]:
        return Model
