# globalmoo/request/register_account.py
from typing import Type

from ..models.account import Account
from .base import BaseRequest

class RegisterAccount(BaseRequest):
    """Request to register a new account."""

    def __init__(self, company: str, first_name: str, last_name: str, email: str, password: str, time_zone: str, agreement: bool = True) -> None:
        self.company = company
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.time_zone = time_zone
        self.agreement = agreement

    def _get_path(self) -> str:
        return "accounts/register"

    def get_response_type(self) -> Type[Account]:
        return Account

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "password": self.password,
            "timeZone": self.time_zone,
            "agreement": self.agreement
        }