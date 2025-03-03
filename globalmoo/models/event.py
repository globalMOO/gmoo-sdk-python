from datetime import datetime
from typing import Optional, Union

from .base import GlobalMooModel
from .project import Project
from .inverse import Inverse
from ..enums.event_name import EventName


class Event(GlobalMooModel):
    """Model representing an event from the globalMOO API."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    name: EventName
    subject: Optional[str] = None
    data: Union[Project, Inverse]