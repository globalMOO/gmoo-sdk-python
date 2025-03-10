# globalMOO SDK for Python

A Python SDK for interacting with the [globalMOO API](https://app.globalmoo.com/), providing a simple and intuitive interface for optimization tasks.

## Try It Now

Get started now with an [interactive in-browser example](https://colab.research.google.com/drive/1uM7fAx2mMEj_hBAejnGCBenup_KdLIrK#scrollTo=XsLgUduy9kLY).

## Features

- Full support for the globalMOO API
- Type-safe request and response handling using Pydantic models
- Automatic network retry with exponential backoff
- Comprehensive error handling with clear error messages
- Modern Python type hints throughout
- Extensive test coverage

## Requirements

- Python 3.10 or higher
- Valid globalMOO API credentials

## Installation

Install the package using pip:
```bash
pip install globalmoo-sdk
```

## Documentation

For comprehensive documentation and API reference, visit our [globalMOO Documentation](https://globalmoo.gitbook.io/globalmoo-documentation).

## Development

If you're contributing to or modifying the SDK:

1. Clone the repository:
```bash
git clone https://github.com/globalMOO/gmoo-sdk-python.git
cd gmoo-sdk-python
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Install development dependencies:
```bash
pip install pytest
```

5. Run tests:
```bash
pytest
```

## Authentication

There are two ways to provide your API credentials:

### Using Environment Variables

1. Create a `.env` file in your project root:
```
GMOO_API_KEY=your-api-key
GMOO_API_URI=https://app.globalmoo.com/api/
```

2. Initialize the client without explicit credentials:
```python
from globalmoo.client import Client

client = Client()
```

### Passing Credentials Explicitly

```python
from globalmoo.client import Client
from globalmoo.credentials import Credentials

credentials = Credentials(
    api_key="your-api-key",
    base_uri="https://app.globalmoo.com/api/"
)

client = Client(credentials=credentials)
```

## Quick Start Example

Here's a simple example showing how to optimize a mathematical function:

```python
"""
Example from the README demonstrating the basic usage of the globalMOO SDK.
"""
from globalmoo.utils.console import (
    print_satisfaction_status,
    print_section_header,
    print_values,
    print_info,
    print_success
)

from globalmoo.client import Client
from globalmoo.request.create_model import CreateModel
from globalmoo.request.create_project import CreateProject
from globalmoo.request.load_output_cases import LoadOutputCases
from globalmoo.request.load_objectives import LoadObjectives
from globalmoo.request.suggest_inverse import SuggestInverse
from globalmoo.request.load_inversed_output import LoadInversedOutput
from globalmoo.enums.objective_type import ObjectiveType

# Silence httpx logs
import logging
logging.getLogger('httpx').setLevel(logging.WARNING)

def linear_function(inputs):
    """Simple 2-input, 3-output linear function for demonstration."""
    x, y = inputs
    return [
        x + y,          # Output 1
        2 * x + y,      # Output 2
        x + 2 * y       # Output 3
    ]

def main():
    # Load environment variables (if using .env file)
    load_dotenv()

    # Initialize client
    client = Client()
    print_info("Successfully initialized globalMOO client")

    try:
        # Create model
        model = client.execute_request(CreateModel(
            name="Linear Function Example"
        ))
        print_info(f"Created model with ID: {model.id}")

        # Create project with input specifications
        project = client.execute_request(CreateProject(
            model_id=model.id,
            name="README Example Project",
            input_count=2,
            minimums=[0.0, 0.0],
            maximums=[10.0, 10.0],
            input_types=["float", "float"],  # Must be strings
            categories=[]  # Empty list if there are no categorical variables
        ))
        logger.info(f"Created project with ID: {project.id}")

        # Get input cases from the project
        input_cases = project.input_cases
        logger.info(f"Received {len(input_cases)} input cases")
        
        # Compute outputs for all input cases
        output_cases = [linear_function(case) for case in input_cases]
        logger.info(f"Computed {len(output_cases)} output cases")
        
        # Create trial with computed outputs
        trial = client.execute_request(LoadOutputCases(
            project_id=project.id,
            output_count=3,
            output_cases=output_cases
        ))
        logger.info(f"Successfully created trial with ID: {trial.id}")

        # Set optimization objectives - try to find inputs that give these outputs
        target_values = [2.0, 3.0, 3.0]
        objective = client.execute_request(LoadObjectives(
            trial_id=trial.id,
            desired_l1_norm=0.0,  # Default to 0.0 as l1_norm is required
            objectives=target_values,
            objective_types=[ObjectiveType.PERCENT] * 3,  # percent for percentage-based optimization
            initial_input=input_cases[0],     # Use first input case as starting point
            initial_output=output_cases[0],   # And its corresponding output
            minimum_bounds=[-1.0, -1.0, -1.0],  # Allow 1% above target for all outcomes
            maximum_bounds=[ 1.0,  1.0,  1.0]   # Allow 1% below target for all outcomes
        ))
        logger.info("Initialized inverse optimization")

        # Run inverse optimization loop
        max_iterations = 10
        for iteration in range(max_iterations):
            # Get next suggested inputs to try
            inverse = client.execute_request(SuggestInverse(
                objective_id=objective.id
            ))
            logger.info(f"Iteration {iteration + 1}: Received suggestion")
            
            # Run the function with suggested inputs
            next_output = linear_function(inverse.input)
            
            # Report results back to the API
            inverse = client.execute_request(LoadInversedOutput(
                inverse_id=inverse.id,
                output=next_output
            ))
            
            # Log detailed results with nice formatting
            print_section_header("Current solution details:")
            print_values("Input", inverse.input)
            print_values("Output", next_output)
            print_values("Target", target_values)
            
            if inverse.results:
                for i, result in enumerate(inverse.results):
                    print_satisfaction_status(i, result.satisfied, result.detail)
                    print_info(f"    Type: {result.objective_type}")
                    print_info(f"    Error: {result.error}")

            # Check if optimization is complete
            if inverse.should_stop():
                print_info(f"Optimization stopped: {inverse.get_stop_reason().description()}")
                break

            print_info(f"Completed iteration {iteration + 1}")

        # Report final results
        print_section_header("Final Results")
        if inverse.satisfied_at:
            print_success("Solution satisfied all objectives!")
            print_section_header("Satisfaction details:")
            for i, (satisfied, detail) in enumerate(zip(inverse.get_satisfaction_status(), inverse.get_result_details())):
                print_satisfaction_status(i, satisfied, detail)
        else:
            print_info("Solution did not satisfy all objectives")
            print_section_header("Status per objective:")
            for i, (satisfied, detail) in enumerate(zip(inverse.get_satisfaction_status(), inverse.get_result_details())):
                print_satisfaction_status(i, satisfied, detail)

        print_section_header("Final solution:")
        print_values("Input values", inverse.input)
        print_values("Output values", next_output)
        print_values("Target values", target_values)
        print_values("Error values", inverse.get_objective_errors(), precision=6)

    finally:
        client.http_client.close()
        print_info("Closed client connection")

if __name__ == "__main__":
    main()
```

For a suite of examples demonstrating a variety of use cases including inverse solution and constrainted optimization, see the [`gmoo-sdk-suite`](https://github.com/globalMOO/gmoo-sdk-suite/tree/main/python). 

The best starting point for inverse solution is [`linear_example.py`](https://github.com/globalMOO/gmoo-sdk-suite/blob/main/python/linear_example.py).

## Error Handling

The SDK provides detailed error messages while hiding unnecessary complexity:

```python
try:
    model = client.execute_request(CreateModel(name=""))
except InvalidRequestException as e:
    print(f"API error: {e}")  # Will show specific validation errors
except NetworkConnectionException as e:
    print(f"Network error: {e}")
```

For debugging, you can enable more detailed error information:

```python
client = Client(debug=True)  # Will show full stack traces and request details
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact support@globalmoo.com.