# globalmoo/request/load_inversed_output.py
from typing import List, Union, Type
from .base import BaseRequest
from ..models.inverse import Inverse
from ..exceptions.invalid_argument import InvalidArgumentException


class LoadInversedOutput(BaseRequest):
    """Request to load output for an inverse optimization step."""

    def __init__(
        self,
        inverse_id: int,
        output: List[Union[int, float]]
    ):
        """Initialize the request."""
        # Validate output is a list
        if not isinstance(output, list):
            raise InvalidArgumentException("output must be a list")
            
        # Validate all values are numeric
        if not all(isinstance(val, (int, float)) for val in output):
            raise InvalidArgumentException("all output values must be numbers")

        self.inverse_id = inverse_id
        self.output = output

    def _get_path(self) -> str:
        return f"inverses/{self.inverse_id}/load-output"

    def get_response_type(self) -> Type[Inverse]:
        return Inverse

    def to_dict(self) -> dict:
        return {
            "output": self.output
        }