# globalmoo/request/read_objective.py
from typing import Type

from ..models.objective import Objective
from .base import BaseRequest

class ReadObjective(BaseRequest):
    """Request to read a specific objective."""

    def __init__(self, objective_id: int) -> None:
        self.objective_id = objective_id

    def get_method(self) -> str:
        return "GET"

    def _get_path(self) -> str:
        return f"objectives/{self.objective_id}"

    def get_response_type(self) -> Type[Objective]:
        return Objective
