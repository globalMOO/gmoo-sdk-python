# globalmoo/request/create_project.py
from typing import List, Union
from typing import Type
from .base import BaseRequest
from ..models.project import Project
from ..enums.input_type import InputType
from ..exceptions.invalid_argument import InvalidArgumentException


class CreateProject(BaseRequest):
    """Request to create a new project."""
    
    def __init__(
        self,
        model_id: int,
        name: str,
        input_count: int,
        minimums: List[Union[int, float]],
        maximums: List[Union[int, float]],
        input_types: List[str],  # String values directly
        categories: List[str]
    ):
        """Initialize the request.
        
        Args:
            name: Project name
            model_id: ID of the model to create project under
            name: Project name - must be at least 4 characters
            input_count: Number of input variables
            minimums: Minimum values for each input
            maximums: Maximum values for each input
            input_types: Types for each input variable
            categories: Categories for categorical inputs, a list of strings, one per category
        """
        # Validate name
        if not isinstance(name, str) or len(name.strip()) < 4:
            raise InvalidArgumentException("Project name must be a non-empty string of at least 4 characters")

        # Validate input arrays length match input_count
        if len(minimums) != input_count:
            raise InvalidArgumentException(
                "Length of minimums must match input_count",
                details={
                    "input_count": input_count,
                    "minimums_length": len(minimums)
                }
            )
            
        if len(maximums) != input_count:
            raise InvalidArgumentException(
                "Length of maximums must match input_count",
                details={
                    "input_count": input_count,
                    "maximums_length": len(maximums)
                }
            )
            
        if len(input_types) != input_count:
            raise InvalidArgumentException(
                "Length of input_types must match input_count",
                details={
                    "input_count": input_count,
                    "input_types_length": len(input_types)
                }
            )
        
        # Validate numeric values
        if not all(isinstance(x, (int, float)) for x in minimums + maximums):
            raise InvalidArgumentException("All minimums and maximums must be numbers")
            
        # Validate input types
        for input_type in input_types:
            if isinstance(input_type, str):
                try:
                    InputType(input_type)
                except ValueError:
                    raise InvalidArgumentException(
                        f"Invalid input type: {input_type}",
                        details={"valid_types": [t.value for t in InputType]}
                    )
            elif not isinstance(input_type, InputType):
                raise InvalidArgumentException(
                    "input_types must be InputType enum or strings",
                    details={"type": type(input_type).__name__}
                )
        
        # Handle categories
        self.categories = [] if categories is None else categories
        if not isinstance(self.categories, list):
            raise InvalidArgumentException("categories must be a list")
        if not all(isinstance(cat, str) for cat in self.categories):
            raise InvalidArgumentException("each category must be a string")

        self.model_id = model_id
        self.name = name
        self.input_count = input_count
        self.minimums = minimums
        self.maximums = maximums
        self.input_types = input_types

    def _get_path(self) -> str:
        return f"models/{self.model_id}/projects"

    def get_response_type(self) -> Type[Project]:
        return Project

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "inputCount": self.input_count,
            "minimums": self.minimums,
            "maximums": self.maximums,
            "inputTypes": [t.value if isinstance(t, InputType) else t for t in self.input_types],
            "categories": self.categories
        }
