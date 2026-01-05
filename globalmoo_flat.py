"""
globalMOO SDK - Flat File Version
==================================

This file contains the entire globalMOO SDK in a single file for easy inline use.
Simply paste this at the top of your code to use the SDK without installing the package.

REQUIRED DEPENDENCIES:
- httpx>=0.26.0
- pydantic>=2.5.0
- rich==13.9.4

Usage:
    from globalmoo_flat import Client, Credentials

    # Create client with credentials (REQUIRED)
    client = Client(
        credentials=Credentials(
            api_key="your-api-key",
            base_uri="https://api.globalmoo.ai"
        )
    )
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    Any, Dict, List, Literal, Optional, Protocol, Type,
    TypeVar, Union, cast, get_type_hints
)

import httpx
from pydantic import (
    BaseModel, ConfigDict, Field, ValidationError, field_validator
)
from rich.console import Console
from rich.theme import Theme
from rich.text import Text


# =============================================================================
# EXCEPTIONS
# =============================================================================

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


# =============================================================================
# ENUMS
# =============================================================================

class InputType(str, Enum):
    """Enumeration of possible input types for globalMOO models."""
    BOOLEAN = "boolean"
    CATEGORY = "category"
    FLOAT = "float"
    INTEGER = "integer"


class ObjectiveType(str, Enum):
    """Enumeration of possible objective types for globalMOO models."""
    EXACT = "exact"
    PERCENT = "percent"
    VALUE = "value"
    LESS_THAN = "lessthan"
    LESS_THAN_EQUAL = "lessthan_equal"
    GREATER_THAN = "greaterthan"
    GREATER_THAN_EQUAL = "greaterthan_equal"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"

    def is_percent(self) -> bool:
        """Check if objective type is percentage-based."""
        return self == ObjectiveType.PERCENT


class StopReason(IntEnum):
    """Enumeration of possible reasons for a trial to stop."""
    RUNNING = 0
    SATISFIED = 1
    STOPPED = 2
    EXHAUSTED = 3

    def description(self) -> str:
        """Get a human-readable description of the stop reason."""
        descriptions = {
            self.RUNNING: "is still running or being evaluated",
            self.SATISFIED: "satisfied to an optimal input and output",
            self.STOPPED: "stopped due to duplicate suggested inputs",
            self.EXHAUSTED: "exhausted all attempts to converge"
        }
        return descriptions[self]

    def is_running(self) -> bool:
        """Check if the optimization is still running."""
        return self == self.RUNNING

    def is_satisfied(self) -> bool:
        """Check if the optimization is satisfied."""
        return self == self.SATISFIED

    def is_stopped(self) -> bool:
        """Check if the optimization was stopped."""
        return self == self.STOPPED

    def is_exhausted(self) -> bool:
        """Check if the optimization was exhausted."""
        return self == self.EXHAUSTED

    def should_stop(self) -> bool:
        """Determine if this stop reason indicates the trial should stop."""
        return self != self.RUNNING


# =============================================================================
# MODELS
# =============================================================================

class GlobalMooModel(BaseModel):
    """Base model for all globalMOO data models."""
    model_config = ConfigDict(
        frozen=True,
        alias_generator=lambda s: ''.join(word.capitalize() if i else word for i, word in enumerate(s.split('_'))),
        populate_by_name=True,
        from_attributes=True
    )


class Error(GlobalMooModel):
    """Error response from the globalMOO API."""
    status: int
    title: str
    message: str
    errors: List[Dict[str, str]] = []


class Account(GlobalMooModel):
    """Account model representing a globalMOO user account."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    company: str
    name: str
    email: str
    api_key: str
    time_zone: str
    customer_id: str


class Result(GlobalMooModel):
    """Model representing a result from an inverse optimization step."""
    model_config = ConfigDict(frozen=True)

    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    number: int = Field(ge=0)
    objective: float = 0.0
    objective_type: ObjectiveType = ObjectiveType.EXACT
    minimum_bound: float = 0.0
    maximum_bound: float = 0.0
    output: float = 0.0
    error: float = 0.0
    detail: Optional[str] = None
    satisfied: bool = True

    def get_objective_formatted(self) -> str:
        """Get formatted objective value."""
        return self._format_value(self.objective)

    def get_minimum_bound_formatted(self) -> str:
        """Get formatted minimum bound."""
        return self._format_value(self.minimum_bound)

    def get_maximum_bound_formatted(self) -> str:
        """Get formatted maximum bound."""
        return self._format_value(self.maximum_bound)

    def get_output_formatted(self) -> str:
        """Get formatted output value."""
        return self._format_value(self.output)

    def get_error_formatted(self) -> str:
        """Get formatted error value."""
        return self._format_value(self.error)

    def _format_value(self, value: float) -> str:
        """Format a value based on objective type."""
        if self.objective_type.is_percent():
            return f"{value:.6f}%"
        return f"{value:.6f}"

    def with_satisfied_detail(self, detail: str) -> 'Result':
        """Create new instance with satisfied status and detail."""
        return self.model_copy(update={"satisfied": True, "detail": detail})

    def with_unsatisfied_detail(self, detail: str) -> 'Result':
        """Create new instance with unsatisfied status and detail."""
        return self.model_copy(update={"satisfied": False, "detail": detail})


class Inverse(GlobalMooModel):
    """Model representing an inverse optimization step."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    loaded_at: Optional[datetime] = None
    satisfied_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    exhausted_at: Optional[datetime] = None
    iteration: int
    l1_norm: float = 0.0
    suggest_time: int = 0
    compute_time: int = 0
    input: List[Union[int, float]]
    output: Optional[List[Union[int, float]]] = None
    errors: Optional[List[Union[int, float]]] = None
    results: Optional[List[Result]] = None

    @field_validator('results', mode='before')
    def validate_results(cls, v: Optional[List[Dict[str, Any]]]) -> Optional[List[Result]]:
        """Convert result dictionaries to Result objects."""
        if v is None:
            return None
        return [Result.model_validate(result) for result in v]

    def get_result_details(self) -> List[str]:
        """Get the satisfaction details for each objective."""
        if not self.results:
            return []
        return [result.detail or '' for result in self.results]

    def get_satisfaction_status(self) -> List[bool]:
        """Get the satisfaction status for each objective."""
        if not self.results:
            return []
        return [result.satisfied for result in self.results]

    def get_objective_errors(self) -> List[float]:
        """Get the error values for each objective."""
        if not self.results:
            return []
        return [result.error for result in self.results]

    def get_stop_reason(self) -> StopReason:
        """Get the reason why the optimization stopped (if it has)."""
        if self.satisfied_at is not None:
            return StopReason.SATISFIED
        elif self.stopped_at is not None:
            return StopReason.STOPPED
        elif self.exhausted_at is not None:
            return StopReason.EXHAUSTED
        return StopReason.RUNNING

    def should_stop(self) -> bool:
        """Determine if the optimization should stop."""
        return self.get_stop_reason() != StopReason.RUNNING


class Objective(GlobalMooModel):
    """Model representing an optimization objective."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    optimal_inverse: Optional[Inverse] = None
    attempt_count: int = 0
    stop_reason: StopReason
    desired_l1_norm: float
    objectives: List[Union[int, float]]
    objective_types: List[ObjectiveType]
    minimum_bounds: List[Union[int, float]]
    maximum_bounds: List[Union[int, float]]
    inverses: List[Inverse] = []

    @property
    def iteration_count(self) -> int:
        """Get the total number of iterations."""
        return len(self.inverses)

    @property
    def last_inverse(self) -> Optional[Inverse]:
        """Get the last inverse if any exist."""
        if not self.inverses:
            return None
        return self.inverses[-1]


class Trial(GlobalMooModel):
    """Trial model representing a single globalMOO optimization trial."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    number: int
    output_count: int
    output_cases: List[List[Union[int, float]]]
    case_count: int
    objectives: List[Objective] = []


class Project(GlobalMooModel):
    """Project model representing a globalMOO optimization project."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    developed_at: Optional[datetime] = None
    name: str
    input_count: int
    minimums: List[Union[int, float]]
    maximums: List[Union[int, float]]
    input_types: List[InputType]
    categories: List[str]
    input_cases: List[List[Union[int, float]]]
    case_count: int
    trials: List[Trial] = []


class Model(GlobalMooModel):
    """Model representing a globalMOO ML model namespace."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    name: str
    description: Optional[str] = None
    projects: List[Project] = []


class EventName(str, Enum):
    """Enumeration of possible event types for globalMOO models."""
    PROJECT_CREATED = "project.created"
    INVERSE_SUGGESTED = "inverse.suggested"

    def data_type(self) -> Type[Union[Project, Inverse]]:
        """Get the expected data type for this event."""
        data_type = {
            self.PROJECT_CREATED: Project,
            self.INVERSE_SUGGESTED: Inverse
        }[self]
        return data_type


class Event(GlobalMooModel):
    """Model representing an event from the globalMOO API."""
    id: int
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None
    name: EventName
    subject: Optional[str] = None
    data: Union[Project, Inverse]


# =============================================================================
# INVALID REQUEST EXCEPTION (depends on Error model)
# =============================================================================

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


# =============================================================================
# UTILITIES
# =============================================================================

# Define symbols - using ASCII for better compatibility
CHECK_MARK = "+"
X_MARK = "x"
IN_SET = "in"

# Create a custom theme for consistent styling
custom_theme = Theme({
    'info': 'cyan',
    'success': 'green',
    'error': 'red',
    'warning': 'yellow',
    'satisfied': 'bold green',
    'unsatisfied': 'bold red',
})

console = Console(
    theme=custom_theme,
    force_terminal=True,
    color_system="auto"
)

def print_satisfaction_status(objective_num: int, satisfied: bool, detail: str):
    """Print the satisfaction status of an objective with checkmark/x and detail."""
    symbol = f"({CHECK_MARK})" if satisfied else f"({X_MARK})"
    style = "satisfied" if satisfied else "unsatisfied"

    text = Text()
    text.append(f"  Objective {objective_num}: ", style="default")
    text.append(symbol, style=style)

    detail_text = detail.replace(' within ', ' in ').replace(' in ', f' {IN_SET} ')
    text.append(f" - {detail_text}", style="default")

    console.print(text)

def print_section_header(title: str):
    """Print a section header with consistent styling."""
    console.print(f"\n[bold]{title}[/bold]")

def print_values(label: str, values: list, precision: int = 4):
    """Print a list of values with consistent formatting."""
    formatted_values = [f"{x:.{precision}f}" for x in values]
    console.print(f"  {label}: {formatted_values}")

def print_info(message: str):
    """Print an info message."""
    console.print(f"[info]{message}[/info]")

def print_success(message: str):
    """Print a success message."""
    console.print(f"[success]{message}[/success]")

def print_error(message: str):
    """Print an error message."""
    console.print(f"[error]{message}[/error]")

def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[warning]{message}[/warning]")


# =============================================================================
# REQUESTS
# =============================================================================

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
        return "POST"

    @abstractmethod
    def get_response_type(self) -> Type[T]:
        """Get the expected response type."""
        pass

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert request to dictionary format for the API."""
        return None


class CreateModel(BaseRequest):
    """Request to create a new model."""

    def __init__(self, name: str, description: Optional[str] = None) -> None:
        self.name = name
        self.description = description

    def _get_path(self) -> str:
        return "models"

    def get_response_type(self) -> Type[Model]:
        return Model

    def to_dict(self) -> dict[str, Optional[str]]:
        return {
            "name": self.name,
            "description": self.description
        }


class CreateProject(BaseRequest):
    """Request to create a new project."""

    def __init__(
        self,
        model_id: int,
        name: str,
        input_count: int,
        minimums: List[Union[int, float]],
        maximums: List[Union[int, float]],
        input_types: List[str],
        categories: List[str]
    ):
        """Initialize the request."""
        if not isinstance(name, str) or len(name.strip()) < 4:
            raise InvalidArgumentException("Project name must be a non-empty string of at least 4 characters")

        if len(minimums) != input_count:
            raise InvalidArgumentException(
                "Length of minimums must match input_count",
                details={
                    "input_count": input_count,
                    "minimums_length": len(minimums)
                }
            )

        if len(maximums) != input_count:
            raise InvalidArgumentException(
                "Length of maximums must match input_count",
                details={
                    "input_count": input_count,
                    "maximums_length": len(maximums)
                }
            )

        if len(input_types) != input_count:
            raise InvalidArgumentException(
                "Length of input_types must match input_count",
                details={
                    "input_count": input_count,
                    "input_types_length": len(input_types)
                }
            )

        if not all(isinstance(x, (int, float)) for x in minimums + maximums):
            raise InvalidArgumentException("All minimums and maximums must be numbers")

        for input_type in input_types:
            if isinstance(input_type, str):
                try:
                    InputType(input_type)
                except ValueError:
                    raise InvalidArgumentException(
                        f"Invalid input type: {input_type}",
                        details={"valid_types": [t.value for t in InputType]}
                    )
            elif not isinstance(input_type, InputType):
                raise InvalidArgumentException(
                    "input_types must be InputType enum or strings",
                    details={"type": type(input_type).__name__}
                )

        self.categories = [] if categories is None else categories
        if not isinstance(self.categories, list):
            raise InvalidArgumentException("categories must be a list")
        if not all(isinstance(cat, str) for cat in self.categories):
            raise InvalidArgumentException("each category must be a string")

        self.model_id = model_id
        self.name = name
        self.input_count = input_count
        self.minimums = minimums
        self.maximums = maximums
        self.input_types = input_types

    def _get_path(self) -> str:
        return f"models/{self.model_id}/projects"

    def get_response_type(self) -> Type[Project]:
        return Project

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "inputCount": self.input_count,
            "minimums": self.minimums,
            "maximums": self.maximums,
            "inputTypes": [t.value if isinstance(t, InputType) else t for t in self.input_types],
            "categories": self.categories
        }


class InitializeInverse(BaseRequest):
    """Request to initialize inverse optimization."""

    def __init__(
        self,
        trial_id: int,
        convergence: float,
        objectives: List[Union[int, float]],
        objective_types: List[ObjectiveType],
        initial_input: List[Union[int, float]],
        initial_output: List[Union[int, float]],
        uncertain_min: List[Union[int, float]],
        uncertain_max: List[Union[int, float]]
    ) -> None:
        self.trial_id = trial_id
        self.convergence = convergence
        self.objectives = objectives
        self.objective_types = objective_types
        self.initial_input = initial_input
        self.initial_output = initial_output
        self.uncertain_min = uncertain_min
        self.uncertain_max = uncertain_max

    def get_url(self) -> str:
        return f"trials/{self.trial_id}/initialize-inverse"

    def get_response_type(self) -> Type[Trial]:
        return Trial

    def to_dict(self) -> dict:
        return {
            "convergence": self.convergence,
            "objectives": self.objectives,
            "objectiveTypes": self.objective_types,
            "initialInput": self.initial_input,
            "initialOutput": self.initial_output,
            "minimumBounds": self.uncertain_min,
            "maximumBounds": self.uncertain_max
        }


class LoadDevelopedOutputs(BaseRequest):
    """Request to load developed outputs into a trial."""

    def __init__(
        self,
        trial_id: int,
        count: int,
        outputs: List[List[Union[int, float]]]
    ) -> None:
        self.trial_id = trial_id
        self.count = count
        self.outputs = outputs

    def get_url(self) -> str:
        return f"trials/{self.trial_id}/load-developed-outputs"

    def get_response_type(self) -> Type[Trial]:
        return Trial

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "outputs": self.outputs
        }


class LoadInversedOutput(BaseRequest):
    """Request to load output for an inverse optimization step."""

    def __init__(
        self,
        inverse_id: int,
        output: List[Union[int, float]]
    ):
        """Initialize the request."""
        if not isinstance(output, list):
            raise InvalidArgumentException("output must be a list")

        if not all(isinstance(val, (int, float)) for val in output):
            raise InvalidArgumentException("all output values must be numbers")

        self.inverse_id = inverse_id
        self.output = output

    def _get_path(self) -> str:
        return f"inverses/{self.inverse_id}/load-output"

    def get_response_type(self) -> Type[Inverse]:
        return Inverse

    def to_dict(self) -> dict:
        return {
            "output": self.output
        }


class LoadObjectives(BaseRequest):
    """Request to load objectives for a trial."""

    def __init__(
        self,
        trial_id: int,
        objectives: List[Union[int, float]],
        objective_types: List[ObjectiveType],
        initial_input: List[Union[int, float]],
        initial_output: List[Union[int, float]],
        desired_l1_norm: float = None,
        minimum_bounds: List[Union[int, float]] = None,
        maximum_bounds: List[Union[int, float]] = None,
    ):
        """Initialize the request."""
        self.trial_id = trial_id
        self.objectives = objectives

        self.objective_types = [ot if isinstance(ot, ObjectiveType) else ObjectiveType(ot)
                              for ot in objective_types]

        self.initial_input = initial_input
        self.initial_output = initial_output

        if all(ot == ObjectiveType.EXACT for ot in self.objective_types):
            self.minimum_bounds = [0.0] * len(objectives) if minimum_bounds is None else minimum_bounds
            self.maximum_bounds = [0.0] * len(objectives) if maximum_bounds is None else maximum_bounds
        else:
            self.minimum_bounds = minimum_bounds
            self.maximum_bounds = maximum_bounds

        self.desired_l1_norm = 0.0 if desired_l1_norm is None else desired_l1_norm

    def _get_path(self) -> str:
        return f"trials/{self.trial_id}/objectives"

    def get_response_type(self) -> Type[Objective]:
        return Objective

    def to_dict(self) -> dict:
        return {
            "desiredL1Norm": self.desired_l1_norm,
            "objectives": self.objectives,
            "objectiveTypes": [ot.value for ot in self.objective_types],
            "initialInput": self.initial_input,
            "initialOutput": self.initial_output,
            "minimumBounds": self.minimum_bounds,
            "maximumBounds": self.maximum_bounds,
        }


class LoadOutputCases(BaseRequest):
    """Request to load output cases into a trial."""

    def __init__(
        self,
        project_id: int,
        output_count: int,
        output_cases: List[List[Union[int, float]]]
    ):
        """Initialize the request."""
        if not isinstance(output_cases, list):
            raise InvalidArgumentException("output_cases must be a list")

        if not all(isinstance(case, list) for case in output_cases):
            raise InvalidArgumentException(
                "output_cases must be a list of lists containing numeric values"
            )

        if any(len(case) != output_count for case in output_cases):
            raise InvalidArgumentException(
                "All output cases must have length matching output_count",
                details={
                    "expected_length": output_count,
                    "actual_lengths": [len(case) for case in output_cases]
                }
            )

        if not all(isinstance(val, (int, float))
                  for case in output_cases
                  for val in case):
            raise InvalidArgumentException(
                "All output case values must be numbers"
            )

        self.project_id = project_id
        self.output_count = output_count
        self.output_cases = output_cases

    def _get_path(self) -> str:
        return f"projects/{self.project_id}/output-cases"

    def get_response_type(self) -> Type[Trial]:
        return Trial

    def to_dict(self) -> dict:
        return {
            "outputCount": self.output_count,
            "outputCases": self.output_cases,
        }


class ReadModels(BaseRequest):
    """Request to list all models."""

    def get_method(self) -> str:
        return "GET"

    def _get_path(self) -> str:
        return "models"

    def get_response_type(self) -> Type[List[Model]]:
        return List[Model]


class ReadTrial(BaseRequest):
    """Request to read a specific trial."""

    def __init__(self, trial_id: int) -> None:
        self.trial_id = trial_id

    def get_method(self) -> str:
        return "GET"

    def _get_path(self) -> str:
        return f"trials/{self.trial_id}"

    def get_response_type(self) -> Type[Trial]:
        return Trial


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


class SuggestInverse(BaseRequest):
    """Request to suggest the next inverse optimization step."""

    def __init__(self, objective_id: int):
        """Initialize the request."""
        self.objective_id = objective_id

    def _get_path(self) -> str:
        return f"objectives/{self.objective_id}/suggest-inverse"

    def get_response_type(self) -> Type[Inverse]:
        return Inverse

    def to_dict(self) -> dict:
        return {}


# =============================================================================
# CREDENTIALS
# =============================================================================

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
        api_key: str,
        base_uri: str,
        validate_tls: bool = True
    ) -> None:
        """
        Initialize credentials with required parameters.

        Args:
            api_key: API key for authentication (REQUIRED).
            base_uri: Base URI for the API (REQUIRED, e.g., "https://api.globalmoo.ai").
            validate_tls: Whether to validate TLS certificates, defaults to True.

        Raises:
            InvalidArgumentException: If api_key or base_uri are empty or None.
        """
        if not api_key or not isinstance(api_key, str):
            raise InvalidArgumentException(
                'API key is required and must be a non-empty string.'
            )

        if not base_uri or not isinstance(base_uri, str):
            raise InvalidArgumentException(
                'Base URI is required and must be a non-empty string.'
            )

        # Basic validation that base_uri looks like a URL
        if not base_uri.startswith(('http://', 'https://')):
            raise InvalidArgumentException(
                f'Base URI must start with http:// or https://'
            )

        self._api_key = api_key
        self._base_uri = base_uri
        self._validate_tls = validate_tls

    def get_api_key(self) -> str:
        """Get the API key for authentication."""
        return self._api_key

    def get_base_uri(self) -> str:
        """Get the base URI for the API."""
        return self._base_uri

    def should_validate_tls(self) -> bool:
        """Get whether TLS validation should be performed."""
        return self._validate_tls


# =============================================================================
# CLIENT
# =============================================================================

logger = logging.getLogger(__name__)

TResponse = TypeVar('TResponse', bound=Union[Model, List[Model], Account, Project, Trial, Inverse, Objective])

class Client:
    """
    Main client for interacting with the globalMOO API.

    This client handles all communication with the API, including authentication,
    request sending, and response processing. It provides a high-level interface
    for all API operations.
    """

    def __init__(
        self,
        credentials: CredentialsProtocol,
        http_client: Optional[httpx.Client] = None,
        timeout: float = 30.0,
        debug: bool = False
    ) -> None:
        """
        Initialize a new globalMOO client.

        Args:
            credentials: Credentials for API authentication (REQUIRED).
            http_client: Optional pre-configured HTTP client.
            timeout: Request timeout in seconds.
            debug: Whether to enable debug logging.

        Raises:
            InvalidArgumentException: If credentials are invalid.
        """
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)

        if credentials is None:
            raise InvalidArgumentException('Credentials are required to create a Client.')
        self.credentials = credentials

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
                verify=verify
            )
        else:
            if isinstance(http_client, httpx.Client):
                http_client.headers.update(default_headers)
            self.http_client = http_client

    def _do_execute_request(self, request: BaseRequest) -> TResponse:
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
                return cast(TResponse, [item_type.model_validate(item) for item in data])
            else:
                return cast(TResponse, response_type.model_validate(data))

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error = Error.model_validate(error_data)
                exception = InvalidRequestException(request, error)
                if self.debug:
                    logger.error(exception.get_debug_message())
                else:
                    logger.error(exception.get_message())
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

    def execute_request(self, request: BaseRequest) -> TResponse:
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
                wait_time = min(4 * (2 ** (retry_count - 1)), 10)
                time.sleep(wait_time)
            except (InvalidRequestException, InvalidResponseException) as e:
                raise e

    def _denormalize(self, data: Union[dict, List[dict]], target_type: Type[TResponse]) -> TResponse:
        """Helper method to denormalize data into model objects."""
        try:
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
            event_name = EventName(event_data['name'])
            data_type = event_name.data_type()
            if 'data' in event_data:
                event_data['data'] = self._denormalize(event_data['data'], data_type)
            event = self._denormalize(event_data, Event)
            return event
        except ValueError as e:
            raise InvalidArgumentException(f'The event name "{event_data["name"]}" is invalid.') from e

    def __enter__(self) -> 'Client':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.http_client.close()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Client
    'Client',
    'Credentials',
    'CredentialsProtocol',

    # Models
    'Account',
    'Error',
    'Event',
    'Inverse',
    'Model',
    'Objective',
    'Project',
    'Result',
    'Trial',

    # Enums
    'EventName',
    'InputType',
    'ObjectiveType',
    'StopReason',

    # Exceptions
    'GlobalMooException',
    'InvalidArgumentException',
    'InvalidRequestException',
    'InvalidResponseException',
    'NetworkConnectionException',

    # Requests
    'BaseRequest',
    'CreateModel',
    'CreateProject',
    'InitializeInverse',
    'LoadDevelopedOutputs',
    'LoadInversedOutput',
    'LoadObjectives',
    'LoadOutputCases',
    'ReadModels',
    'ReadTrial',
    'RegisterAccount',
    'SuggestInverse',

    # Utilities
    'console',
    'print_satisfaction_status',
    'print_section_header',
    'print_values',
    'print_info',
    'print_success',
    'print_error',
    'print_warning',
]

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Linear Function Optimization Example
    
    This example demonstrates how to use the globalMOO SDK to find inputs
    that produce desired outputs for a simple linear function.
    
    IMPORTANT: Replace YOUR_API_KEY and YOUR_BASE_URI with your actual credentials!
    """
    
    # Silence httpx logs for cleaner output
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    def linear_function(inputs):
        """Simple 2-input, 3-output linear function for demonstration."""
        x, y = inputs
        return [
            x + y,          # Output 1
            2 * x + y,      # Output 2
            x + 2 * y       # Output 3
        ]
    
    def run_example():
        """Run the linear function optimization example."""
        
        # ====================================================================
        # STEP 1: Initialize Client with Credentials
        # ====================================================================
        # IMPORTANT: Replace these with your actual API credentials!
        API_KEY = "YOUR_API_KEY_HERE"
        BASE_URI = "https://app.globalmoo.com/api/"
        
        if API_KEY == "YOUR_API_KEY_HERE":
            print_error("ERROR: Please replace YOUR_API_KEY_HERE with your actual API key!")
            print_info("Edit the globalmoo_flat.py file and update the API_KEY and BASE_URI variables.")
            return
        
        try:
            credentials = Credentials(
                api_key=API_KEY,
                base_uri=BASE_URI
            )
            client = Client(credentials=credentials)
            print_info("Successfully initialized globalMOO client")
        except InvalidArgumentException as e:
            print_error(f"Failed to create credentials: {e}")
            return
        
        try:
            # ====================================================================
            # STEP 2: Create Model
            # ====================================================================
            model = client.execute_request(CreateModel(
                name="Linear Function Example"
            ))
            print_info(f"Created model with ID: {model.id}")
            
            # ====================================================================
            # STEP 3: Create Project with Input Specifications
            # ====================================================================
            project = client.execute_request(CreateProject(
                model_id=model.id,
                name="Flat File Example Project",
                input_count=2,
                minimums=[0.0, 0.0],
                maximums=[10.0, 10.0],
                input_types=["float", "float"],
                categories=[]
            ))
            print_info(f"Created project with ID: {project.id}")
            
            # ====================================================================
            # STEP 4: Get Input Cases and Compute Outputs
            # ====================================================================
            input_cases = project.input_cases
            print_info(f"Received {len(input_cases)} input cases from the API")
            
            # Compute outputs for all input cases using our function
            output_cases = [linear_function(case) for case in input_cases]
            print_info(f"Computed {len(output_cases)} output cases")
            
            # ====================================================================
            # STEP 5: Create Trial with Computed Outputs
            # ====================================================================
            trial = client.execute_request(LoadOutputCases(
                project_id=project.id,
                output_count=3,  # Our function has 3 outputs
                output_cases=output_cases
            ))
            print_info(f"Created trial with ID: {trial.id}")
            
            # ====================================================================
            # STEP 6: Set Optimization Objectives
            # ====================================================================
            # We want to find inputs that produce these target outputs
            target_values = [2.0, 3.0, 3.0]
            print_section_header("Optimization Goal")
            print_info(f"Finding inputs that produce outputs: {target_values}")
            
            objective = client.execute_request(LoadObjectives(
                trial_id=trial.id,
                desired_l1_norm=0.0,
                objectives=target_values,
                objective_types=[ObjectiveType.PERCENT] * 3,  # Allow ±1% error
                initial_input=input_cases[0],
                initial_output=output_cases[0],
                minimum_bounds=[-1.0, -1.0, -1.0],  # -1% tolerance
                maximum_bounds=[1.0, 1.0, 1.0]      # +1% tolerance
            ))
            print_info(f"Initialized inverse optimization with objective ID: {objective.id}")
            
            # ====================================================================
            # STEP 7: Run Optimization Loop
            # ====================================================================
            max_iterations = 10
            print_section_header(f"Starting Optimization (max {max_iterations} iterations)")
            
            for iteration in range(max_iterations):
                # Get next suggested inputs from the API
                inverse = client.execute_request(SuggestInverse(
                    objective_id=objective.id
                ))
                
                # Run our function with the suggested inputs
                next_output = linear_function(inverse.input)
                
                # Report the results back to the API
                inverse = client.execute_request(LoadInversedOutput(
                    inverse_id=inverse.id,
                    output=next_output
                ))
                
                # Display progress
                print_section_header(f"Iteration {iteration + 1}")
                print_values("Suggested Input", inverse.input)
                print_values("Computed Output", next_output)
                print_values("Target Output", target_values)
                
                if inverse.results:
                    for i, result in enumerate(inverse.results):
                        print_satisfaction_status(i, result.satisfied, result.detail)
                
                # Check if optimization is complete
                if inverse.should_stop():
                    stop_reason = inverse.get_stop_reason()
                    print_info(f"Optimization stopped: {stop_reason.description()}")
                    break
                
                print_info(f"Continuing to iteration {iteration + 2}...")
            
            # ====================================================================
            # STEP 8: Display Final Results
            # ====================================================================
            print_section_header("FINAL RESULTS")
            
            if inverse.satisfied_at:
                print_success("✓ Solution satisfied all objectives!")
            else:
                print_warning("⚠ Solution did not satisfy all objectives")
            
            print_section_header("Solution Details")
            for i, (satisfied, detail) in enumerate(zip(
                inverse.get_satisfaction_status(),
                inverse.get_result_details()
            )):
                print_satisfaction_status(i, satisfied, detail)
            
            print_section_header("Final Values")
            print_values("Input values", inverse.input)
            print_values("Output values", next_output)
            print_values("Target values", target_values)
            print_values("Error values", inverse.get_objective_errors(), precision=6)
            
            print_section_header("Summary")
            print_info(f"Total iterations: {iteration + 1}")
            print_info(f"Stop reason: {inverse.get_stop_reason().description()}")
            
        except InvalidRequestException as e:
            print_error(f"API request failed: {e}")
        except NetworkConnectionException as e:
            print_error(f"Network error: {e}")
        except Exception as e:
            print_error(f"Unexpected error: {e}")
        finally:
            # Always close the HTTP client
            client.http_client.close()
            print_info("Closed client connection")
    
    # Run the example
    print_section_header("globalMOO SDK - Linear Function Example")
    print_info("This example finds inputs that produce target outputs for a linear function")
    print_warning("Make sure to replace YOUR_API_KEY_HERE with your actual API credentials!")
    print()
    
    run_example()
