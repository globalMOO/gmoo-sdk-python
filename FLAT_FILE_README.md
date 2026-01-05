# globalMOO SDK - Flat File Version

This directory contains a **flat file version** of the globalMOO SDK that can be pasted directly into your code without requiring package installation.

## Purpose

This flat file is designed for environments where:
- You cannot install packages via pip
- You don't have access to the filesystem to add SDK directories
- You need to paste SDK functionality directly into your code

## Files

- `globalmoo_flat.py` - The complete SDK in a single file (~1000 lines)
- `test_flat_file.py` - Test script to verify the flat file works correctly

## Required Dependencies

The flat file requires these dependencies to be available in your environment:

```
httpx>=0.26.0
pydantic>=2.5.0
rich==13.9.4
```

These are standard Python packages and are commonly available in most Python environments.

## Security Features

This flat file version is designed for **restricted environments** and does NOT use:
- ❌ Filesystem access (`os` module)
- ❌ Environment variables (`os.getenv()`)
- ❌ `.env` file loading (`python-dotenv`)
- ❌ URL parsing (`urllib.parse`)
- ❌ System manipulation (`sys.tracebacklimit`)

All credentials must be passed explicitly as parameters, making it safe for sandboxed environments.

## Usage

### Option 1: Paste at the Top of Your Code

Simply copy the entire contents of `globalmoo_flat.py` and paste it at the top of your script:

```python
# [Paste entire globalmoo_flat.py contents here]

# Your code starts here
from globalmoo_flat import Client

client = Client()
# ... your code
```

### Option 2: Use as a Local Module

If you can add a single file to your project directory, you can import from it:

```python
# Your script.py
from globalmoo_flat import Client, Credentials, CreateProject, LoadObjectives

# Create client with explicit credentials (REQUIRED)
client = Client(
    credentials=Credentials(
        api_key="your-api-key",
        base_uri="https://api.globalmoo.ai"
    )
)

# Note: Environment variable loading is NOT supported in this flat file version
# All credentials must be passed explicitly
```

## What's Included

The flat file includes all SDK functionality:

### Core Classes
- `Client` - Main API client
- `Credentials` - Credentials management

### Models
- `Account` - User account information
- `Model` - ML model namespace
- `Project` - Optimization project
- `Trial` - Optimization trial
- `Objective` - Optimization objective
- `Inverse` - Inverse optimization step
- `Result` - Objective result
- `Event` - Webhook event
- `Error` - API error response

### Enums
- `InputType` - Input variable types (FLOAT, INTEGER, BOOLEAN, CATEGORY)
- `ObjectiveType` - Objective types (EXACT, MINIMIZE, MAXIMIZE, etc.)
- `StopReason` - Trial stop reasons (RUNNING, SATISFIED, STOPPED, EXHAUSTED)
- `EventName` - Event types for webhooks

### Exceptions
- `GlobalMooException` - Base exception
- `InvalidArgumentException` - Invalid argument errors
- `InvalidRequestException` - API request errors
- `InvalidResponseException` - API response errors
- `NetworkConnectionException` - Network errors

### Request Classes
- `CreateModel` - Create a new model
- `CreateProject` - Create a new project
- `LoadObjectives` - Load objectives for optimization
- `LoadOutputCases` - Load output data
- `LoadInversedOutput` - Load inverse optimization output
- `SuggestInverse` - Request next optimization suggestion
- `ReadModels` - List all models
- `ReadTrial` - Read trial details
- `RegisterAccount` - Register new account
- And more...

### Utilities
- Console output functions for formatted display
- Satisfaction status printing
- Rich text formatting

## Example Usage

```python
from globalmoo_flat import (
    Client,
    Credentials,
    CreateProject,
    LoadOutputCases,
    LoadObjectives,
    ObjectiveType,
    InputType,
)

# Initialize client
client = Client(
    credentials=Credentials(
        api_key="your-api-key",
        base_uri="https://api.globalmoo.ai"
    )
)

# Create a project
project_request = CreateProject(
    model_id=1,
    name="My Optimization Project",
    input_count=2,
    minimums=[0.0, 0.0],
    maximums=[10.0, 10.0],
    input_types=["float", "float"],
    categories=[]
)
project = client.execute_request(project_request)

# Load output cases
output_request = LoadOutputCases(
    project_id=project.id,
    output_count=1,
    output_cases=[[5.0], [7.0], [9.0]]
)
trial = client.execute_request(output_request)

# Set optimization objectives
objective_request = LoadObjectives(
    trial_id=trial.id,
    objectives=[8.0],
    objective_types=[ObjectiveType.EXACT],
    initial_input=[5.0, 5.0],
    initial_output=[7.0],
)
objective = client.execute_request(objective_request)

print(f"Objective created with ID: {objective.id}")
```

## Testing

Run the test script to verify the flat file works correctly:

```bash
python test_flat_file.py
```

Expected output:
```
Testing globalMOO SDK flat file...

✓ Successfully imported Client
✓ Successfully imported Credentials
✓ Successfully imported exceptions
✓ Successfully imported enums
✓ Successfully imported request classes

...

All tests passed! ✓
```

## Comparison with Regular SDK

### Regular SDK Usage
```python
# Install package
pip install globalmoo-sdk

# Import from package
from globalmoo import Client

# Can load credentials from environment variables
client = Client()  # Loads from GMOO_API_KEY and GMOO_API_URI env vars
```

### Flat File Usage
```python
# No installation needed
# Just paste globalmoo_flat.py into your project

# Import from flat file
from globalmoo_flat import Client, Credentials

# Must pass credentials explicitly
client = Client(
    credentials=Credentials(
        api_key="your-key",
        base_uri="https://api.globalmoo.ai"
    )
)
```

The flat file provides the same API functionality as the regular SDK, but with important differences:
- ✅ **No filesystem access** - safe for sandboxed environments
- ✅ **Explicit credentials** - no environment variable dependencies
- ✅ **Smaller footprint** - only 3 dependencies instead of 6
- ⚠️ **Must pass credentials** - cannot load from environment variables

## Maintenance

The flat file is generated from the SDK source code and should be regenerated whenever the SDK is updated to ensure it stays in sync with the latest features and bug fixes.

## Size

The flat file is approximately:
- **1523 lines** of Python code (including a complete working example)
- **50 KB** in size

This is small enough to paste into most restricted code environments without issues.

## Built-in Example

The flat file includes a complete working example in a `__main__` block that demonstrates:
- Creating a client with credentials
- Setting up a model and project
- Computing outputs for a linear function
- Running inverse optimization to find inputs that produce target outputs
- Displaying results with formatted console output

To run the example:
1. Edit `globalmoo_flat.py` and replace `YOUR_API_KEY_HERE` with your actual API key
2. Replace `YOUR_BASE_URI` if needed (default: `https://app.globalmoo.com/api/`)
3. Run: `python globalmoo_flat.py`

The example will guide you through a complete optimization workflow.

## Support

For questions or issues with the SDK, please visit:
https://github.com/globalMOO/gmoo-sdk-python/issues
