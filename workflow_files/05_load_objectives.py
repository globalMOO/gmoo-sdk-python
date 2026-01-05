"""
STEP 5: Load Objectives
========================

INPUT VARIABLES (define in interface):
- trial_id: int                     (from Step 4)
- target_outputs: List[float]       (desired output values, e.g., [2.0, 3.0, 3.0])
- input_cases: List[List[float]]    (from Step 2 - needed for initial point)
- output_cases: List[List[float]]   (from Step 3 - needed for initial point)
- api_key: str                      (from Step 1)
- base_uri: str                     (from Step 1)

OUTPUT VARIABLES (available after running):
- objective_id: int                 (the created objective's ID - pass to Step 6)
"""


# =============================================================================
# globalMOO SDK - Functional Version (Embedded)
# =============================================================================

import json
import time
from typing import Any, Dict, List, Optional, Union

try:
    import httpx
except ImportError:
    raise ImportError("httpx is required. Install with: pip install httpx>=0.26.0")


# CONSTANTS (instead of Enums)
INPUT_TYPE_BOOLEAN = "boolean"
INPUT_TYPE_CATEGORY = "category"
INPUT_TYPE_FLOAT = "float"
INPUT_TYPE_INTEGER = "integer"

OBJECTIVE_TYPE_EXACT = "exact"
OBJECTIVE_TYPE_PERCENT = "percent"
OBJECTIVE_TYPE_VALUE = "value"
OBJECTIVE_TYPE_LESS_THAN = "lessthan"
OBJECTIVE_TYPE_LESS_THAN_EQUAL = "lessthan_equal"
OBJECTIVE_TYPE_GREATER_THAN = "greaterthan"
OBJECTIVE_TYPE_GREATER_THAN_EQUAL = "greaterthan_equal"
OBJECTIVE_TYPE_MINIMIZE = "minimize"
OBJECTIVE_TYPE_MAXIMIZE = "maximize"

STOP_REASON_RUNNING = 0
STOP_REASON_SATISFIED = 1
STOP_REASON_STOPPED = 2
STOP_REASON_EXHAUSTED = 3


# ERROR HANDLING
def create_error(error_type: str, message: str, details: Optional[Dict] = None) -> Dict:
    """Create an error dictionary."""
    return {
        "error": True,
        "error_type": error_type,
        "message": message,
        "details": details or {}
    }


def is_error(result: Any) -> bool:
    """Check if a result is an error."""
    return isinstance(result, dict) and result.get("error") == True


# CREDENTIALS
def create_credentials(api_key: str, base_uri: str, validate_tls: bool = True) -> Dict:
    """Create credentials dictionary."""
    if not api_key or not isinstance(api_key, str):
        return create_error("InvalidArgument", "API key is required and must be a non-empty string")

    if not base_uri or not isinstance(base_uri, str):
        return create_error("InvalidArgument", "Base URI is required and must be a non-empty string")

    if not base_uri.startswith(('http://', 'https://')):
        return create_error("InvalidArgument", "Base URI must start with http:// or https://")

    return {
        "api_key": api_key,
        "base_uri": base_uri,
        "validate_tls": validate_tls
    }


# CLIENT
def create_client(credentials: Dict, timeout: float = 30.0) -> Dict:
    """Create a client dictionary."""
    if is_error(credentials):
        return credentials

    if "api_key" not in credentials or "base_uri" not in credentials:
        return create_error("InvalidArgument", "Invalid credentials dictionary")

    headers = {
        "Authorization": f"Bearer {credentials['api_key']}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    http_client = httpx.Client(
        base_url=credentials['base_uri'],
        timeout=timeout,
        headers=headers,
        verify=credentials.get('validate_tls', True)
    )

    return {
        "http_client": http_client,
        "credentials": credentials
    }


def close_client(client: Dict) -> None:
    """Close the HTTP client."""
    if "http_client" in client:
        client["http_client"].close()


# REQUEST BUILDERS
def create_model_request(name: str, description: Optional[str] = None) -> Dict:
    """Create a request to create a new model."""
    data = {"name": name}
    if description is not None:
        data["description"] = description

    return {
        "method": "POST",
        "path": "models",
        "data": data
    }


def create_project_request(
    model_id: int,
    name: str,
    input_count: int,
    minimums: List[Union[int, float]],
    maximums: List[Union[int, float]],
    input_types: List[str],
    categories: List[str]
) -> Union[Dict, Dict]:
    """Create a request to create a new project."""
    if not isinstance(name, str) or len(name.strip()) < 4:
        return create_error("InvalidArgument", "Project name must be at least 4 characters")

    if len(minimums) != input_count:
        return create_error("InvalidArgument", f"minimums length ({len(minimums)}) must match input_count ({input_count})")

    if len(maximums) != input_count:
        return create_error("InvalidArgument", f"maximums length ({len(maximums)}) must match input_count ({input_count})")

    if len(input_types) != input_count:
        return create_error("InvalidArgument", f"input_types length ({len(input_types)}) must match input_count ({input_count})")

    valid_types = [INPUT_TYPE_BOOLEAN, INPUT_TYPE_CATEGORY, INPUT_TYPE_FLOAT, INPUT_TYPE_INTEGER]
    for input_type in input_types:
        if input_type not in valid_types:
            return create_error("InvalidArgument", f"Invalid input type: {input_type}")

    return {
        "method": "POST",
        "path": f"models/{model_id}/projects",
        "data": {
            "name": name,
            "inputCount": input_count,
            "minimums": minimums,
            "maximums": maximums,
            "inputTypes": input_types,
            "categories": categories
        }
    }


def load_output_cases_request(
    project_id: int,
    output_count: int,
    output_cases: List[List[Union[int, float]]]
) -> Union[Dict, Dict]:
    """Create a request to load output cases."""
    if not isinstance(output_cases, list):
        return create_error("InvalidArgument", "output_cases must be a list")

    for case in output_cases:
        if not isinstance(case, list):
            return create_error("InvalidArgument", "Each output case must be a list")
        if len(case) != output_count:
            return create_error("InvalidArgument", f"All output cases must have length {output_count}")

    return {
        "method": "POST",
        "path": f"projects/{project_id}/output-cases",
        "data": {
            "outputCount": output_count,
            "outputCases": output_cases
        }
    }


def load_objectives_request(
    trial_id: int,
    objectives: List[Union[int, float]],
    objective_types: List[str],
    initial_input: List[Union[int, float]],
    initial_output: List[Union[int, float]],
    desired_l1_norm: float = 0.0,
    minimum_bounds: Optional[List[Union[int, float]]] = None,
    maximum_bounds: Optional[List[Union[int, float]]] = None
) -> Dict:
    """Create a request to load objectives."""
    if all(ot == OBJECTIVE_TYPE_EXACT for ot in objective_types):
        if minimum_bounds is None:
            minimum_bounds = [0.0] * len(objectives)
        if maximum_bounds is None:
            maximum_bounds = [0.0] * len(objectives)

    return {
        "method": "POST",
        "path": f"trials/{trial_id}/objectives",
        "data": {
            "desiredL1Norm": desired_l1_norm,
            "objectives": objectives,
            "objectiveTypes": objective_types,
            "initialInput": initial_input,
            "initialOutput": initial_output,
            "minimumBounds": minimum_bounds,
            "maximumBounds": maximum_bounds
        }
    }


def suggest_inverse_request(objective_id: int) -> Dict:
    """Create a request to suggest next inverse step."""
    return {
        "method": "POST",
        "path": f"objectives/{objective_id}/suggest-inverse",
        "data": {}
    }


def load_inversed_output_request(
    inverse_id: int,
    output: List[Union[int, float]]
) -> Union[Dict, Dict]:
    """Create a request to load output for an inverse step."""
    if not isinstance(output, list):
        return create_error("InvalidArgument", "output must be a list")

    return {
        "method": "POST",
        "path": f"inverses/{inverse_id}/load-output",
        "data": {
            "output": output
        }
    }


def read_trial_request(trial_id: int) -> Dict:
    """Create a request to read a trial."""
    return {
        "method": "GET",
        "path": f"trials/{trial_id}",
        "data": None
    }


# REQUEST EXECUTION
def execute_request(client: Dict, request: Dict, max_retries: int = 3) -> Union[Dict, Dict]:
    """Execute a request with retries."""
    if is_error(client):
        return client

    if is_error(request):
        return request

    http_client = client["http_client"]
    retry_count = 0

    while True:
        try:
            method = request["method"]
            path = request["path"]
            data = request.get("data")

            if not path.startswith('/'):
                path = '/' + path

            response = http_client.request(
                method=method,
                url=path,
                json=data
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                return create_error(
                    "InvalidRequest",
                    error_data.get("message", "API request failed"),
                    {"status": e.response.status_code, "details": error_data}
                )
            except:
                return create_error(
                    "InvalidRequest",
                    f"HTTP {e.response.status_code}: {str(e)}",
                    {"status": e.response.status_code}
                )

        except httpx.NetworkError as e:
            retry_count += 1
            if retry_count >= max_retries:
                return create_error("NetworkError", f"Network error after {max_retries} retries: {str(e)}")

            wait_time = min(4 * (2 ** (retry_count - 1)), 10)
            time.sleep(wait_time)

        except Exception as e:
            return create_error("UnexpectedError", f"Unexpected error: {str(e)}")


# HELPER FUNCTIONS
def should_stop(inverse: Dict) -> bool:
    """Check if inverse optimization should stop."""
    if not isinstance(inverse, dict):
        return False

    return (
        inverse.get("satisfiedAt") is not None or
        inverse.get("stoppedAt") is not None or
        inverse.get("exhaustedAt") is not None
    )


def get_stop_reason(inverse: Dict) -> int:
    """Get the stop reason for an inverse."""
    if not isinstance(inverse, dict):
        return STOP_REASON_RUNNING

    if inverse.get("satisfiedAt"):
        return STOP_REASON_SATISFIED
    elif inverse.get("stoppedAt"):
        return STOP_REASON_STOPPED
    elif inverse.get("exhaustedAt"):
        return STOP_REASON_EXHAUSTED
    else:
        return STOP_REASON_RUNNING


def get_stop_reason_description(reason: int) -> str:
    """Get human-readable description of stop reason."""
    descriptions = {
        STOP_REASON_RUNNING: "is still running or being evaluated",
        STOP_REASON_SATISFIED: "satisfied to an optimal input and output",
        STOP_REASON_STOPPED: "stopped due to duplicate suggested inputs",
        STOP_REASON_EXHAUSTED: "exhausted all attempts to converge"
    }
    return descriptions.get(reason, "unknown")


def print_error_message(error: Dict) -> None:
    """Print an error dictionary."""
    if is_error(error):
        print(f"ERROR [{error['error_type']}]: {error['message']}")
        if error.get('details'):
            print(f"Details: {error['details']}")


# =============================================================================
# YOUR CODE STARTS HERE
# =============================================================================


# Step 1: Create credentials
credentials = create_credentials(
    api_key=api_key,      # INPUT: from interface
    base_uri=base_uri     # INPUT: from interface
)

if is_error(credentials):
    print_error_message(credentials)
    raise Exception(f"Credential error: {credentials['message']}")

# Step 2: Create client
client = create_client(credentials)

if is_error(client):
    print_error_message(client)
    raise Exception(f"Client error: {client['message']}")

print("✓ Created client")

# Step 3: Prepare objective configuration
# Use the first input/output case as the initial point
initial_input = input_cases[0]
initial_output = output_cases[0]

# Create objective types (all PERCENT for percent-based optimization)
# You can change this to EXACT, MINIMIZE, MAXIMIZE, etc.
objective_types = [OBJECTIVE_TYPE_PERCENT] * len(target_outputs)

# Set bounds for percent-based objectives
# These represent the acceptable deviation range
minimum_bounds = [-1.0] * len(target_outputs)  # -100% deviation
maximum_bounds = [1.0] * len(target_outputs)   # +100% deviation

# Step 4: Load objectives
obj_req = load_objectives_request(
    trial_id=trial_id,                  # INPUT: from Step 4
    objectives=target_outputs,          # INPUT: from interface
    objective_types=objective_types,
    initial_input=initial_input,
    initial_output=initial_output,
    minimum_bounds=minimum_bounds,
    maximum_bounds=maximum_bounds
)

if is_error(obj_req):
    print_error_message(obj_req)
    close_client(client)
    raise Exception(f"Objective request error: {obj_req['message']}")

objective = execute_request(client, obj_req)

if is_error(objective):
    print_error_message(objective)
    close_client(client)
    raise Exception(f"Objective creation error: {objective['message']}")

# OUTPUT: This variable will be available for the next step
objective_id = objective['id']

print(f"✓ Created objective with ID: {objective_id}")
print(f"✓ Target outputs: {target_outputs}")
print(f"✓ Initial input:  {initial_input}")
print(f"✓ Initial output: {initial_output}")

# Close client
close_client(client)

# OUTPUTS for next step:
# - objective_id (pass to Step 6)
# - target_outputs (pass to Step 6 for display)
# - api_key (pass through)
# - base_uri (pass through)
