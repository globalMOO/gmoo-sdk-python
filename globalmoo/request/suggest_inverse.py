# globalmoo/request/suggest_inverse.py
from typing import Type
from .base import BaseRequest
from ..models.inverse import Inverse


class SuggestInverse(BaseRequest):
    """Request to suggest the next inverse optimization step."""

    def __init__(self, objective_id: int):
        """Initialize the request."""
        self.objective_id = objective_id

    def _get_path(self) -> str:
        return f"objectives/{self.objective_id}/suggest-inverse"

    def get_response_type(self) -> Type[Inverse]:
        return Inverse

    def to_dict(self) -> dict:
        return {}
