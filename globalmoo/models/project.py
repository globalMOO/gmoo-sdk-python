# globalmoo/models/project.py
from datetime import datetime
from typing import List, Optional, Union
from .base import GlobalMooModel
from .trial import Trial
from ..enums.input_type import InputType


class Project(GlobalMooModel):
    """Project model representing a globalMOO optimization project."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    developed_at: Optional[datetime] = None
    name: str
    input_count: int
    minimums: List[Union[int, float]]
    maximums: List[Union[int, float]]
    input_types: List[InputType]
    categories: List[str]
    input_cases: List[List[Union[int, float]]]
    case_count: int
    trials: List[Trial] = []