# globalmoo/enums/input_type.py
from enum import Enum, auto


class InputType(str, Enum):
    """Enumeration of possible input types for globalMOO models."""
    BOOLEAN = "boolean"
    CATEGORY = "category"
    FLOAT = "float"
    INTEGER = "integer"