# globalmoo/request/register_account.py
from typing import Type

from ..models.account import Account
from .base import BaseRequest

class RegisterAccount(BaseRequest):
    """Request to register a new account."""
    
    def __init__(self, company: str, name: str, email: str, password: str, time_zone: str) -> None:
        self.company = company
        self.name = name
        self.email = email
        self.password = password
        self.time_zone = time_zone
    
    def _get_path(self) -> str:
        return "accounts/register"
    
    def get_response_type(self) -> Type[Account]:
        return Account
    
    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "timeZone": self.time_zone
        }