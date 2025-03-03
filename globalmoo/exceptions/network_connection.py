from typing import Union
# globalmoo/exceptions/network_connection.py
from .base import GlobalMooException


class NetworkConnectionException(GlobalMooException):
    """Raised when network connection issues occur."""
    def __init__(self, message_or_error: Union[str, Exception]):
        if isinstance(message_or_error, str):
            self.message = message_or_error
            self.original_error = None
        else:
            self.original_error = message_or_error
            self.message = "A network error occurred when attempting to connect to the globalMOO API server."
        super().__init__(self.message)
        self.__cause__ = None
        self.__context__ = None

    def get_message(self) -> str:
        """Get a user-friendly error message."""
        return self.message

    def get_debug_message(self) -> str:
        """Get detailed debug information."""
        msg = [f"Network Connection Error: {self.message}"]
        if self.original_error:
            msg.extend([
                "Original Error:",
                f"  Type: {type(self.original_error).__name__}",
                f"  Message: {str(self.original_error)}"
            ])
            if hasattr(self.original_error, 'request'):
                msg.extend([
                    "Request Details:",
                    f"  Method: {self.original_error.request.method}",
                    f"  URL: {self.original_error.request.url}"
                ])
        return "\n".join(msg)