from typing import Union
# globalmoo/exceptions/invalid_response.py
from .base import GlobalMooException


class InvalidResponseException(GlobalMooException):
    """Raised when the API response cannot be properly decoded."""
    def __init__(self, message_or_error: Union[str, Exception]):
        if isinstance(message_or_error, str):
            self.message = message_or_error
            self.original_error = None
        else:
            self.original_error = message_or_error
            self.message = "An error occurred when attempting to decode the response from the globalMOO API."
        super().__init__(self.message)
        self.__cause__ = None
        self.__context__ = None

    def get_message(self) -> str:
        """Get a user-friendly error message."""
        return self.message

    def get_debug_message(self) -> str:
        """Get detailed debug information."""
        msg = [f"Response Error: {self.message}"]
        if self.original_error:
            msg.extend([
                "Original Error:",
                f"  Type: {type(self.original_error).__name__}",
                f"  Message: {str(self.original_error)}"
            ])
        return "\n".join(msg)