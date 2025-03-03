# globalmoo/models/model.py
from datetime import datetime
from typing import List, Optional
from .base import GlobalMooModel
from .project import Project

class Model(GlobalMooModel):
    """Model representing a globalMOO ML model namespace."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    name: str
    description: Optional[str] = None
    projects: List[Project] = []
    