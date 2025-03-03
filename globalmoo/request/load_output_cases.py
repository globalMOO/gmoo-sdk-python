# globalmoo/request/load_output_cases.py
from typing import List, Union, Type
from .base import BaseRequest
from ..models.trial import Trial
from ..exceptions.invalid_argument import InvalidArgumentException


class LoadOutputCases(BaseRequest):
    """Request to load output cases into a trial."""
    
    def __init__(
        self,
        project_id: int,
        output_count: int,
        output_cases: List[List[Union[int, float]]]
    ):
        """Initialize the request."""
        if not isinstance(output_cases, list):
            raise InvalidArgumentException("output_cases must be a list")
        
        # Check all are lists
        if not all(isinstance(case, list) for case in output_cases):
            raise InvalidArgumentException(
                "output_cases must be a list of lists containing numeric values"
            )
        
        # Validate lengths and numeric values
        if any(len(case) != output_count for case in output_cases):
            raise InvalidArgumentException(
                "All output cases must have length matching output_count",
                details={
                    "expected_length": output_count,
                    "actual_lengths": [len(case) for case in output_cases]
                }
            )
        
        # Check all values are numeric
        if not all(isinstance(val, (int, float)) 
                  for case in output_cases 
                  for val in case):
            raise InvalidArgumentException(
                "All output case values must be numbers"
            )

        self.project_id = project_id
        self.output_count = output_count
        self.output_cases = output_cases

    def _get_path(self) -> str:
        return f"projects/{self.project_id}/output-cases"

    def get_response_type(self) -> Type[Trial]:
        return Trial

    def to_dict(self) -> dict:
        return {
            "outputCount": self.output_count,
            "outputCases": self.output_cases,
        }
