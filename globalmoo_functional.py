"""
globalMOO SDK - Functional Version (No Classes)
================================================

This version works in extremely restricted environments that don't allow class definitions.

REQUIRED DEPENDENCIES:
- httpx>=0.26.0

NOTE: This version does NOT use:
- Classes (no __build_class__)
- Pydantic (requires classes)
- Enums (requires classes)
- Rich (requires classes)

All data is represented as dictionaries and all operations are functions.

Usage:
    import httpx
    from globalmoo_functional import create_client, create_credentials, execute_request

    credentials = create_credentials(
        api_key="your-api-key",
        base_uri="https://app.globalmoo.com/api/"
    )

    client = create_client(credentials)

    # Create a model
    model = execute_request(client, create_model_request("My Model"))
"""

import json
import time
from typing import Any, Dict, List, Optional, Union

try:
    import httpx
except ImportError:
    raise ImportError("httpx is required. Install with: pip install httpx>=0.26.0")


# =============================================================================
# CONSTANTS (instead of Enums)
# =============================================================================

# InputType constants
INPUT_TYPE_BOOLEAN = "boolean"
INPUT_TYPE_CATEGORY = "category"
INPUT_TYPE_FLOAT = "float"
INPUT_TYPE_INTEGER = "integer"

# ObjectiveType constants
OBJECTIVE_TYPE_EXACT = "exact"
OBJECTIVE_TYPE_PERCENT = "percent"
OBJECTIVE_TYPE_VALUE = "value"
OBJECTIVE_TYPE_LESS_THAN = "lessthan"
OBJECTIVE_TYPE_LESS_THAN_EQUAL = "lessthan_equal"
OBJECTIVE_TYPE_GREATER_THAN = "greaterthan"
OBJECTIVE_TYPE_GREATER_THAN_EQUAL = "greaterthan_equal"
OBJECTIVE_TYPE_MINIMIZE = "minimize"
OBJECTIVE_TYPE_MAXIMIZE = "maximize"

# StopReason constants
STOP_REASON_RUNNING = 0
STOP_REASON_SATISFIED = 1
STOP_REASON_STOPPED = 2
STOP_REASON_EXHAUSTED = 3


# =============================================================================
# ERROR HANDLING (using dicts instead of exceptions)
# =============================================================================

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


# =============================================================================
# CREDENTIALS
# =============================================================================

def create_credentials(api_key: str, base_uri: str, validate_tls: bool = True) -> Dict:
    """
    Create credentials dictionary.

    Args:
        api_key: API key for authentication (REQUIRED)
        base_uri: Base URI for the API (REQUIRED)
        validate_tls: Whether to validate TLS certificates

    Returns:
        Credentials dict or error dict
    """
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


# =============================================================================
# CLIENT
# =============================================================================

def create_client(credentials: Dict, timeout: float = 30.0) -> Dict:
    """
    Create a client dictionary.

    Args:
        credentials: Credentials dict from create_credentials()
        timeout: Request timeout in seconds

    Returns:
        Client dict or error dict
    """
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


# =============================================================================
# REQUEST BUILDERS
# =============================================================================

def create_model_request(name: str, description: Optional[str] = None) -> Dict:
    """Create a request to create a new model."""
    data = {"name": name}
    # Only include description if it's provided (API requires 8+ chars if present)
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
    # Validation
    if not isinstance(name, str) or len(name.strip()) < 4:
        return create_error("InvalidArgument", "Project name must be at least 4 characters")

    if len(minimums) != input_count:
        return create_error("InvalidArgument", f"minimums length ({len(minimums)}) must match input_count ({input_count})")

    if len(maximums) != input_count:
        return create_error("InvalidArgument", f"maximums length ({len(maximums)}) must match input_count ({input_count})")

    if len(input_types) != input_count:
        return create_error("InvalidArgument", f"input_types length ({len(input_types)}) must match input_count ({input_count})")

    # Validate input types
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
    # Validation
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
    # Set defaults for bounds if all EXACT types
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


# =============================================================================
# REQUEST EXECUTION
# =============================================================================

def execute_request(client: Dict, request: Dict, max_retries: int = 3) -> Union[Dict, Dict]:
    """
    Execute a request with retries.

    Args:
        client: Client dict from create_client()
        request: Request dict from a request builder function
        max_retries: Maximum number of retries for network errors

    Returns:
        Response dict or error dict
    """
    if is_error(client):
        return client

    if is_error(request):
        return request

    http_client = client["http_client"]
    retry_count = 0

    while True:
        try:
            # Make the request
            method = request["method"]
            path = request["path"]
            data = request.get("data")

            # Add leading slash if needed
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


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

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


def print_result(label: str, value: Any) -> None:
    """Simple print helper."""
    print(f"{label}: {value}")


def print_error_message(error: Dict) -> None:
    """Print an error dictionary."""
    if is_error(error):
        print(f"ERROR [{error['error_type']}]: {error['message']}")
        if error.get('details'):
            print(f"Details: {error['details']}")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def run_example():
    """
    Linear Function Optimization Example (Functional Version)

    This demonstrates the SDK without using any classes.
    """

    print("=" * 60)
    print("globalMOO SDK - Functional Version Example")
    print("=" * 60)
    print()

    # Define the function to optimize
    def linear_function(inputs):
        """Simple 2-input, 3-output linear function."""
        x, y = inputs
        return [
            x + y,          # Output 1
            2 * x + y,      # Output 2
            x + 2 * y       # Output 3
        ]

    # Step 1: Create credentials
    API_KEY = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
    BASE_URI = "https://app.globalmoo.com/api/"

    if API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Please replace YOUR_API_KEY_HERE with your actual API key!")
        print("Edit line ~555 in this file.")
        return

    credentials = create_credentials(
        api_key=API_KEY,
        base_uri=BASE_URI
    )

    if is_error(credentials):
        print_error_message(credentials)
        return

    print("✓ Created credentials")

    # Step 2: Create client
    client = create_client(credentials)

    if is_error(client):
        print_error_message(client)
        return

    print("✓ Created client")

    try:
        # Step 3: Create model
        print("\nCreating model...")
        model_req = create_model_request(
            "Functional Example Model",
            "Example model for testing the functional SDK"
        )
        model = execute_request(client, model_req)

        if is_error(model):
            print_error_message(model)
            return

        print(f"✓ Created model with ID: {model['id']}")

        # Step 4: Create project
        print("\nCreating project...")
        project_req = create_project_request(
            model_id=model['id'],
            name="Functional Example Project",
            input_count=2,
            minimums=[0.0, 0.0],
            maximums=[10.0, 10.0],
            input_types=[INPUT_TYPE_FLOAT, INPUT_TYPE_FLOAT],
            categories=[]
        )

        if is_error(project_req):
            print_error_message(project_req)
            return

        project = execute_request(client, project_req)

        if is_error(project):
            print_error_message(project)
            return

        print(f"✓ Created project with ID: {project['id']}")

        # Step 5: Compute outputs
        print("\nComputing outputs...")
        input_cases = project['inputCases']
        output_cases = [linear_function(case) for case in input_cases]
        print(f"✓ Computed {len(output_cases)} output cases")

        # Step 6: Load output cases
        print("\nLoading output cases...")
        trial_req = load_output_cases_request(
            project_id=project['id'],
            output_count=3,
            output_cases=output_cases
        )

        if is_error(trial_req):
            print_error_message(trial_req)
            return

        trial = execute_request(client, trial_req)

        if is_error(trial):
            print_error_message(trial)
            return

        print(f"✓ Created trial with ID: {trial['id']}")

        # Step 7: Set objectives
        print("\nSetting objectives...")
        target_values = [2.0, 3.0, 3.0]
        print(f"Target outputs: {target_values}")

        obj_req = load_objectives_request(
            trial_id=trial['id'],
            objectives=target_values,
            objective_types=[OBJECTIVE_TYPE_PERCENT] * 3,
            initial_input=input_cases[0],
            initial_output=output_cases[0],
            minimum_bounds=[-1.0, -1.0, -1.0],
            maximum_bounds=[1.0, 1.0, 1.0]
        )

        if is_error(obj_req):
            print_error_message(obj_req)
            return

        objective = execute_request(client, obj_req)

        if is_error(objective):
            print_error_message(objective)
            return

        print(f"✓ Created objective with ID: {objective['id']}")

        # Step 8: Run optimization loop
        print("\n" + "=" * 60)
        print("Starting Optimization Loop")
        print("=" * 60)

        max_iterations = 10
        for iteration in range(max_iterations):
            # Get suggestion
            suggest_req = suggest_inverse_request(objective['id'])
            inverse = execute_request(client, suggest_req)

            if is_error(inverse):
                print_error_message(inverse)
                break

            # Compute output
            suggested_input = inverse['input']
            computed_output = linear_function(suggested_input)

            # Load output
            load_req = load_inversed_output_request(inverse['id'], computed_output)
            if is_error(load_req):
                print_error_message(load_req)
                break

            inverse = execute_request(client, load_req)

            if is_error(inverse):
                print_error_message(inverse)
                break

            # Display results
            print(f"\nIteration {iteration + 1}:")
            print(f"  Input:  {[f'{x:.4f}' for x in suggested_input]}")
            print(f"  Output: {[f'{x:.4f}' for x in computed_output]}")
            print(f"  Target: {[f'{x:.4f}' for x in target_values]}")

            # Check if should stop
            if should_stop(inverse):
                reason = get_stop_reason(inverse)
                print(f"\n✓ Optimization complete: {get_stop_reason_description(reason)}")
                break

        # Step 9: Display final results
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Total iterations: {iteration + 1}")
        print(f"Final input:  {inverse['input']}")
        print(f"Final output: {computed_output}")
        print(f"Target:       {target_values}")

        if inverse.get('satisfiedAt'):
            print("\n✓ Solution satisfied all objectives!")
        else:
            print("\n⚠ Solution did not fully satisfy objectives")

    finally:
        # Always close the client
        close_client(client)
        print("\n✓ Closed client connection")

    print("\n" + "=" * 60)

run_example()
