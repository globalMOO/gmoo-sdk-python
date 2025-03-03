# globalmoo/request/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, get_type_hints

from ..models.base import GlobalMooModel

T = TypeVar('T', bound=GlobalMooModel)

class BaseRequest(ABC):
    """Base class for all API requests."""
    
    def get_url(self) -> str:
        """Get the endpoint URL for this request."""
        path = self._get_path()
        if not path.startswith('/'):
            path = '/' + path
        return path

    @abstractmethod
    def _get_path(self) -> str:
        """Get the endpoint path for this request."""
        pass
    
    def get_method(self) -> str:
        """Get the HTTP method for this request."""
        return "POST"  # Default method is POST unless overridden
    
    @abstractmethod
    def get_response_type(self) -> Type[T]:
        """Get the expected response type."""
        pass
    
    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert request to dictionary format for the API."""
        return None