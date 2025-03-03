# globalmoo/exceptions/base.py
class GlobalMooException(Exception):
    """Base exception class for all globalMOO SDK exceptions."""

    def __str__(self) -> str:
        """Return a string representation of the error.
        In non-debug mode, returns just the essential error message.
        """
        return self.get_message()
    
    def get_message(self) -> str:
        """Get the basic error message."""
        raise NotImplementedError
    
    def get_debug_message(self) -> str:
        """Get the detailed debug message."""
        raise NotImplementedError