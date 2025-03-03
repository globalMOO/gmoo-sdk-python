# globalmoo/client.py
import json
from typing import List, Optional, TypeVar, Type, Union, cast
import httpx
import logging
from pydantic import ValidationError
import time

from .enums.event_name import EventName
from .models.event import Event
from .credentials import Credentials, CredentialsProtocol
from .models.account import Account
from .models.error import Error
from .models.inverse import Inverse
from .models.model import Model
from .models.project import Project
from .models.trial import Trial
from .models.objective import Objective
from .exceptions.invalid_argument import InvalidArgumentException
from .exceptions.invalid_request import InvalidRequestException
from .exceptions.invalid_response import InvalidResponseException
from .exceptions.network_connection import NetworkConnectionException
from .request.base import BaseRequest
from .request.create_model import CreateModel
from .request.create_project import CreateProject
from .request.load_objectives import LoadObjectives
from .request.load_output_cases import LoadOutputCases
from .request.load_inversed_output import LoadInversedOutput
from .request.read_models import ReadModels
from .request.read_trial import ReadTrial
from .request.register_account import RegisterAccount
from .request.suggest_inverse import SuggestInverse

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Union[Model, List[Model], Account, Project, Trial, Inverse, Objective])

class Client:
    """
    Main client for interacting with the globalMOO API.
    
    This client handles all communication with the API, including authentication,
    request sending, and response processing. It provides a high-level interface
    for all API operations.
    """
    
    def __init__(
        self,
        credentials: Optional[CredentialsProtocol] = None,
        http_client: Optional[httpx.Client] = None,
        timeout: float = 30.0,
        debug: bool = False
    ) -> None:
        """
        Initialize a new globalMOO client.
        
        Args:
            credentials: Optional credentials for API authentication.
                        If not provided, will attempt to load from environment.
            http_client: Optional pre-configured HTTP client.
            timeout: Request timeout in seconds.
            debug: Whether to enable debug logging.
        
        Raises:
            InvalidArgumentException: If credentials cannot be loaded.
        """
        self.debug = debug
        # Configure logging and traceback
        if debug:
            logger.setLevel(logging.DEBUG)
            import sys
            sys.tracebacklimit = None
        else:
            # Prevent traceback printing in non-debug mode
            import sys
            sys.tracebacklimit = 0
        
        # Create new credentials if none provided
        if credentials is None:
            credentials = Credentials()
        self.credentials = credentials

        # Create HTTP client if none provided
        # Set default headers
        default_headers = {
            "Authorization": f"Bearer {self.credentials.get_api_key()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if http_client is None:
            verify = self.credentials.should_validate_tls()
            self.http_client = httpx.Client(
                base_url=self.credentials.get_base_uri(),
                timeout=timeout,
                headers=default_headers,
                verify=verify  # Control TLS certificate validation
            )
        else:
            # For a custom client, ensure it has our required headers
            if isinstance(http_client, httpx.Client):
                http_client.headers.update(default_headers)
            self.http_client = http_client

    def _do_execute_request(self, request: BaseRequest) -> T:
        """Internal method to execute the request without retries."""
        try:
            request_data = request.to_dict()
            response = self.http_client.request(
                method=request.get_method(),
                url=request.get_url(),
                json=request_data
            )
            
            response.raise_for_status()
            data = response.json()
            response_type = request.get_response_type()
            
            if hasattr(response_type, '__origin__') and response_type.__origin__ is list:
                item_type = response_type.__args__[0]
                return cast(T, [item_type.model_validate(item) for item in data])
            else:
                return cast(T, response_type.model_validate(data))
                
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error = Error.model_validate(error_data)
                exception = InvalidRequestException(request, error)
                if self.debug:
                    logger.error(exception.get_debug_message())
                else:
                    logger.error(exception.get_message())
                # Re-raise the original exception to preserve error details
                raise exception
            except ValidationError as ve:
                if self.debug:
                    logger.error(f"Error validating API error response: {str(ve)}")
                raise InvalidResponseException(str(ve)) from None
                
        except httpx.NetworkError as e:
            if self.debug:
                logger.error(f"Network error: {str(e)}")
            raise NetworkConnectionException(str(e)) from None
            
        except (ValidationError, ValueError, KeyError) as e:
            if self.debug:
                logger.error(f"Error processing response: {str(e)}")
            raise InvalidResponseException(str(e)) from None
            
        except Exception as e:
            if self.debug:
                logger.error(f"Unexpected error: {str(e)}")
            raise InvalidResponseException(str(e)) from None

    def execute_request(self, request: BaseRequest) -> T:
        """Execute a request with retries for network errors."""
        retry_count = 0
        max_retries = 3
        last_error = None
        
        while True:
            try:
                return self._do_execute_request(request)
            except NetworkConnectionException as e:
                last_error = e
                retry_count += 1
                if retry_count >= max_retries:
                    raise last_error
                wait_time = min(4 * (2 ** (retry_count - 1)), 10)  # Exponential backoff
                time.sleep(wait_time)
            except (InvalidRequestException, InvalidResponseException) as e:
                raise e

    def _denormalize(self, data: Union[dict, List[dict]], target_type: Type[T]) -> T:
        """Helper method to denormalize data into model objects."""
        try:
            # Mirror PHP's denormalize functionality using pydantic
            if isinstance(data, list):
                return [target_type.model_validate(item) for item in data]  # type: ignore
            return target_type.model_validate(data)  # type: ignore
        except ValidationError as e:
            raise InvalidResponseException(e)

    def handle_event(self, payload: str) -> Event:
        """Handle a webhook event from the API.

        Args:
            payload: The raw JSON payload string from the webhook

        Returns:
            The parsed Event object

        Raises:
            InvalidArgumentException: If the payload is not a valid event
        """
        try:
            event_data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise InvalidArgumentException("The payload provided is not valid JSON.") from e

        if not isinstance(event_data, dict) or 'id' not in event_data or 'name' not in event_data:
            raise InvalidArgumentException('The payload provided does not appear to be a valid event.')

        if not isinstance(event_data['name'], str):
            raise InvalidArgumentException('The "name" property is expected to be a string.')

        try:
            # Create EventName enum from the name string
            event_name = EventName(event_data['name'])

            # Denormalize the data object to its proper type
            data_type = event_name.data_type()
            if 'data' in event_data:
                event_data['data'] = self._denormalize(event_data['data'], data_type)

            # Finally, denormalize the entire event
            event = self._denormalize(event_data, Event)
            return event
        except ValueError as e:
            raise InvalidArgumentException(f'The event name "{event_data["name"]}" is invalid.') from e

    def __enter__(self) -> 'Client':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.http_client.close()