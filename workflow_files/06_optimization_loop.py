"""
STEP 6: Optimization Loop
==========================

This step runs the iterative optimization loop to find inputs that produce
the target outputs.

INPUT VARIABLES (define in interface):
- objective_id: int              (from Step 5)
- target_outputs: List[float]    (from Step 5, for display)
- max_iterations: int            (e.g., 20 - maximum iterations to run)
- api_key: str                   (from Step 1)
- base_uri: str                  (from Step 1)

Also need to define the same function from Step 3!

OUTPUT VARIABLES (available after running):
- final_input: List[float]       (the optimal input found)
- final_output: List[float]      (the output produced by final_input)
- iterations_run: int            (number of iterations executed)
- converged: bool                (whether optimization converged)
- stop_reason: str               (why optimization stopped)
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


# =============================================================================
# YOUR FUNCTION DEFINITION (same as Step 3)
# =============================================================================

def linear_function(inputs):
    """
    This is your actual function to optimize.
    MUST BE THE SAME AS STEP 3!

    Args:
        inputs: List of input values [x, y, ...]

    Returns:
        List of output values
    """
    x, y = inputs
    return [
        x + y,          # Output 1
        2 * x + y,      # Output 2
        x + 2 * y       # Output 3
    ]

# =============================================================================
# OPTIMIZATION LOOP CODE
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
print("=" * 60)
print("Starting Optimization Loop")
print("=" * 60)

# Initialize output variables
final_input = None
final_output = None
iterations_run = 0
converged = False
stop_reason = "Not started"

try:
    # Step 3: Run optimization loop
    for iteration in range(max_iterations):
        iterations_run = iteration + 1

        # Get suggestion from optimizer
        suggest_req = suggest_inverse_request(objective_id)  # INPUT: from Step 5
        inverse = execute_request(client, suggest_req)

        if is_error(inverse):
            print_error_message(inverse)
            stop_reason = f"Error getting suggestion: {inverse['message']}"
            break

        # Compute output for suggested input
        suggested_input = inverse['input']
        computed_output = linear_function(suggested_input)

        # Load the computed output back to the optimizer
        load_req = load_inversed_output_request(inverse['id'], computed_output)

        if is_error(load_req):
            print_error_message(load_req)
            stop_reason = f"Error creating load request: {load_req['message']}"
            break

        inverse = execute_request(client, load_req)

        if is_error(inverse):
            print_error_message(inverse)
            stop_reason = f"Error loading output: {inverse['message']}"
            break

        # Update final values
        final_input = suggested_input
        final_output = computed_output

        # Display progress
        print(f"\nIteration {iterations_run}:")
        print(f"  Input:  {[f'{x:.4f}' for x in final_input]}")
        print(f"  Output: {[f'{x:.4f}' for x in final_output]}")
        print(f"  Target: {[f'{x:.4f}' for x in target_outputs]}")

        # Check if should stop
        if should_stop(inverse):
            reason_code = get_stop_reason(inverse)
            stop_reason = get_stop_reason_description(reason_code)
            converged = (reason_code == STOP_REASON_SATISFIED)
            print(f"\n✓ Optimization complete: {stop_reason}")
            break

    # If loop completed without stopping
    if iterations_run == max_iterations and not should_stop(inverse):
        stop_reason = "Reached maximum iterations"

finally:
    # Always close the client
    close_client(client)

# Step 4: Display final results
print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)
print(f"Iterations run: {iterations_run}")
print(f"Converged: {converged}")
print(f"Stop reason: {stop_reason}")

if final_input and final_output:
    print(f"\nFinal input:  {final_input}")
    print(f"Final output: {final_output}")
    print(f"Target:       {target_outputs}")

    # Calculate errors
    errors = [abs(out - target) for out, target in zip(final_output, target_outputs)]
    print(f"Errors:       {[f'{e:.6f}' for e in errors]}")

    if converged:
        print("\n✓ Solution satisfied all objectives!")
    else:
        print("\n⚠ Solution did not fully satisfy objectives")
else:
    print("\n⚠ No solution found")

print("=" * 60)

# OUTPUT VARIABLES (available after running):
# - final_input
# - final_output
# - iterations_run
# - converged
# - stop_reason
