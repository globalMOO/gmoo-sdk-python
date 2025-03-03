# globalmoo/exceptions/invalid_request.py
from typing import Any, Dict, List
from .base import GlobalMooException
from ..models.error import Error


class InvalidRequestException(GlobalMooException):
    """Raised when the API rejects a request as invalid."""
    def __init__(self, request: Any = None, error: Error = None, message: str = None):
        if message is not None:
            self.message = message
            self.request = request
            self.error = None
            self.status = 400
        else:
            self.request = request
            self.error = error
            self.status = error.status
            self.message = error.message

        super().__init__(self.get_message())
        self.__cause__ = None
        self.__context__ = None

    def get_message(self) -> str:
        """Get a user-friendly error message."""
        if self.error is None:
            return self.message
            
        msg = self.error.message
        if self.error.errors:
            errors = [f"- {e.get('property', 'Unknown')}: {e.get('message', '')}" for e in self.error.errors]
            msg = f"{msg}\n{chr(10).join(errors)}"
        return msg

    def get_debug_message(self) -> str:
        """Get detailed debug information."""
        if self.error is None:
            msg = [f"API Error ({self.status}):"]
            if self.request:
                msg.extend([
                    "Request Details:",
                    f"  URL: {self.request.get_url()}",
                    f"  Method: {self.request.get_method()}",
                    f"  Data: {self.request.to_dict()}"
                ])
            return "\n".join(msg)

        msg = [
            f"API Error ({self.status}):",
            f"Title: {self.error.title}",
            f"Message: {self.error.message}"
        ]
        if self.error.errors:
            msg.append("Validation Errors:")
            msg.extend([f"  - {e.get('property', 'Unknown')}: {e.get('message', '')}" for e in self.error.errors])
        msg.extend([
            "Request Details:",
            f"  URL: {self.request.get_url()}",
            f"  Method: {self.request.get_method()}",
            f"  Data: {self.request.to_dict()}"
        ])
        return "\n".join(msg)

    def get_errors(self) -> List[Dict[str, str]]:
        """Get the detailed list of validation errors."""
        return self.error.errors