# globalmoo/models/error.py
from typing import List, Dict
from .base import GlobalMooModel


class Error(GlobalMooModel):
    """Error response from the globalMOO API."""
    status: int
    title: str
    message: str
    errors: List[Dict[str, str]] = []
