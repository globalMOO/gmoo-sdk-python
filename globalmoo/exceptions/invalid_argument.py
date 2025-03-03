# globalmoo/exceptions/invalid_argument.py
from .base import GlobalMooException


class InvalidArgumentException(GlobalMooException, ValueError):
    """Raised when invalid arguments are provided to the SDK."""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def get_message(self) -> str:
        """Get a user-friendly error message."""
        return self.message

    def get_debug_message(self) -> str:
        """Get detailed debug information."""
        msg = [f"Invalid Argument Error: {self.message}"]
        if self.details:
            msg.append("Details:")
            msg.extend([f"  {k}: {v}" for k, v in self.details.items()])
        return "\n".join(msg)