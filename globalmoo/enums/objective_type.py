# globalmoo/enums/objective_type.py
from enum import Enum


class ObjectiveType(str, Enum):
    """Enumeration of possible objective types for globalMOO models."""
    EXACT = "exact"
    PERCENT = "percent"
    VALUE = "value"
    LESS_THAN = "lessthan"
    LESS_THAN_EQUAL = "lessthan_equal"
    GREATER_THAN = "greaterthan"
    GREATER_THAN_EQUAL = "greaterthan_equal"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"

    def is_percent(self) -> bool:
        """Check if objective type is percentage-based."""
        return self == ObjectiveType.PERCENT