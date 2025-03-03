# globalmoo/models/base.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GlobalMooModel(BaseModel):
    """Base model for all globalMOO data models."""
    model_config = ConfigDict(
        frozen=True,  # Makes models immutable like PHP readonly classes
        alias_generator=lambda s: ''.join(word.capitalize() if i else word for i, word in enumerate(s.split('_'))),
        populate_by_name=True,
        from_attributes=True
    )