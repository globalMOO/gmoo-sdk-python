# globalmoo/models/trial.py
from datetime import datetime
from typing import List, Optional, Union
from .base import GlobalMooModel
from .objective import Objective


class Trial(GlobalMooModel):
    """Trial model representing a single globalMOO optimization trial."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    number: int
    output_count: int
    output_cases: List[List[Union[int, float]]]
    case_count: int
    objectives: List[Objective] = []