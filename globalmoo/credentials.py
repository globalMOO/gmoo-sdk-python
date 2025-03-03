# globalmoo/credentials.py
from typing import Protocol
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

from .exceptions.invalid_argument import InvalidArgumentException

class CredentialsProtocol(Protocol):
    """Protocol defining the interface for credentials providers."""
    
    def get_api_key(self) -> str:
        """Get the API key for authentication."""
        ...

    def get_base_uri(self) -> str:
        """Get the base URI for the API."""
        ...
        
    def should_validate_tls(self) -> bool:
        """Get whether TLS validation should be performed."""
        ...

class Credentials:
    """Default implementation of credentials provider."""
    
    def __init__(
        self,
        api_key: str | None = None,
        base_uri: str | None = None,
        validate_tls: bool = True,
        skip_dotenv: bool = False
    ) -> None:
        """
        Initialize credentials from parameters or environment.
        
        Args:
            api_key: Optional API key. If not provided, will look for GMOO_API_KEY env var.
            base_uri: Optional base URI. If not provided, will look for GMOO_API_URI env var.
            validate_tls: Whether to validate TLS certificates, defaults to True.
            skip_dotenv: Whether to skip loading from .env file.
            
        Raises:
            InvalidArgumentException: If required credentials cannot be found or validation fails.
        """
        if not skip_dotenv:
            load_dotenv()
        
        self._validate_tls = validate_tls
        
        # Get API key
        self._api_key = api_key or os.getenv('GMOO_API_KEY')
        if not self._api_key:
            raise InvalidArgumentException(
                'The globalMOO SDK could not be created because the "GMOO_API_KEY" '
                'environment variable is not set and no API key was provided.'
            )
            
        # Get and validate base URI
        self._base_uri = base_uri or os.getenv('GMOO_API_URI')
        if not self._base_uri:
            raise InvalidArgumentException(
                'The globalMOO SDK could not be created because the "GMOO_API_URI" '
                'environment variable is not set and no base URI was provided.'
            )
            
        # Parse and validate the URI
        parsed_uri = urlparse(self._base_uri)
        if not parsed_uri.scheme or not parsed_uri.netloc:
            raise InvalidArgumentException(
                f'The API URI "{self._base_uri}" is not a valid URI and cannot be used.'
            )
            
        # Check if using official globalMOO domain
        if (not self.should_validate_tls() and 
            'globalmoo.ai' in parsed_uri.netloc.lower()):
            raise InvalidArgumentException(
                'The "validate_tls" argument must be true when using an official '
                'globalMOO base URI.'
            )

    def get_api_key(self) -> str:
        """Get the API key for authentication."""
        return self._api_key

    def get_base_uri(self) -> str:
        """Get the base URI for the API."""
        return self._base_uri
        
    def should_validate_tls(self) -> bool:
        """Get whether TLS validation should be performed."""
        return self._validate_tls