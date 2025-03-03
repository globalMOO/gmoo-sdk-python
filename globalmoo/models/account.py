# globalmoo/models/account.py
from datetime import datetime
from typing import Optional
from .base import GlobalMooModel


class Account(GlobalMooModel):
    """Account model representing a globalMOO user account."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    company: str
    name: str
    email: str
    api_key: str
    time_zone: str
    customer_id: str