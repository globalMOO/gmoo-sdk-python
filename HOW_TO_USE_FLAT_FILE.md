# How to Use the Flat File as a Header

The `globalmoo_flat.py` file is designed to be pasted directly at the top of your code in restricted environments where you can't install packages or access the filesystem.

## Quick Start

### Option 1: Paste as Header (Recommended for Restricted Environments)

1. Open `globalmoo_flat.py`
2. Copy the **entire file contents** (all 1,523 lines)
3. Paste it at the **very top** of your script
4. Write your code below

**Example:**

```python
# === START: Paste globalmoo_flat.py contents here ===
"""
globalMOO SDK - Flat File Version
...
[entire globalmoo_flat.py contents]
...
"""
# === END: globalmoo_flat.py contents ===

# NOW your code starts here:

# Set up credentials
credentials = Credentials(
    api_key="your-actual-api-key",
    base_uri="https://app.globalmoo.com/api/"
)

client = Client(credentials=credentials)

# Define your function
def my_function(inputs):
    x, y = inputs
    return [x * 2, y * 3, x + y]

# Create model and project
model = client.execute_request(CreateModel(name="My Model"))
project = client.execute_request(CreateProject(
    model_id=model.id,
    name="My Project",
    input_count=2,
    minimums=[0.0, 0.0],
    maximums=[10.0, 10.0],
    input_types=["float", "float"],
    categories=[]
))

# Get input cases and compute outputs
input_cases = project.input_cases
output_cases = [my_function(case) for case in input_cases]

# Load outputs and run optimization
trial = client.execute_request(LoadOutputCases(
    project_id=project.id,
    output_count=3,
    output_cases=output_cases
))

# ... rest of your optimization code
```

### Option 2: Use as Module (If You Can Add a File)

If you can add a single file to your project directory:

1. Place `globalmoo_flat.py` in your project folder
2. Import from it:

```python
# your_script.py
from globalmoo_flat import (
    Client,
    Credentials,
    CreateModel,
    CreateProject,
    LoadObjectives,
    LoadOutputCases,
    SuggestInverse,
    LoadInversedOutput,
    ObjectiveType,
    print_info,
    print_success
)

credentials = Credentials(
    api_key="your-api-key",
    base_uri="https://app.globalmoo.com/api/"
)

client = Client(credentials=credentials)
# ... your code
```

## Understanding the __main__ Block

The flat file includes a complete example at the bottom in a `if __name__ == "__main__":` block. This example demonstrates how to use the SDK but **will not run when you paste the file as a header**.

### Why the Example Won't Interfere

Python's `__name__` variable:
- Equals `"__main__"` when the file is run directly: `python globalmoo_flat.py`
- Equals something else (like `"__main__"` or the module name) when pasted/imported
- So the example only runs when you explicitly test the flat file, not when you use it as a header

### Testing the Example

To see how the SDK works:

1. Edit `globalmoo_flat.py`
2. Find lines ~1358-1359:
   ```python
   API_KEY = "YOUR_API_KEY_HERE"
   BASE_URI = "https://app.globalmoo.com/api/"
   ```
3. Replace with your actual credentials
4. Run: `python globalmoo_flat.py`
5. Watch the optimization example run

## What You Need to Replace

When using the flat file, you **must** provide these values in your code:

```python
credentials = Credentials(
    api_key="REPLACE_WITH_YOUR_API_KEY",      # Required
    base_uri="REPLACE_WITH_YOUR_BASE_URI"     # Required
)
```

Common base URIs:
- Production: `https://app.globalmoo.com/api/`
- Custom: `https://your-instance.globalmoo.ai/api/`

## Dependencies Required

The flat file requires these Python packages to be available:
- `httpx>=0.26.0`
- `pydantic>=2.5.0`
- `rich==13.9.4`

These are typically pre-installed in most Python environments. If not, you'll need to request they be installed.

## Security Features

The flat file is designed for restricted environments and does NOT use:
- ❌ Filesystem access (`os` module)
- ❌ Environment variables (`os.getenv()`)
- ❌ `.env` file loading
- ❌ URL parsing (`urllib.parse`)
- ❌ System manipulation (`sys.tracebacklimit`)

All configuration is passed explicitly as parameters.

## File Size

- **1,523 lines** of Python code
- **~52 KB** (52,000 bytes)
- Small enough to paste into most code editors/environments

## Example Workflow

Here's a complete minimal example of using the SDK as a header:

```python
# [Paste entire globalmoo_flat.py here - 1,523 lines]

# Your actual code starts here:
credentials = Credentials(
    api_key="sk-1234567890abcdef",
    base_uri="https://app.globalmoo.com/api/"
)
client = Client(credentials=credentials)

def my_function(inputs):
    x, y, z = inputs
    return [x + y + z, x * y * z]

model = client.execute_request(CreateModel(name="Test"))
project = client.execute_request(CreateProject(
    model_id=model.id,
    name="Test Project",
    input_count=3,
    minimums=[0.0, 0.0, 0.0],
    maximums=[10.0, 10.0, 10.0],
    input_types=["float", "float", "float"],
    categories=[]
))

input_cases = project.input_cases
output_cases = [my_function(case) for case in input_cases]

trial = client.execute_request(LoadOutputCases(
    project_id=project.id,
    output_count=2,
    output_cases=output_cases
))

objective = client.execute_request(LoadObjectives(
    trial_id=trial.id,
    objectives=[15.0, 100.0],
    objective_types=[ObjectiveType.EXACT, ObjectiveType.EXACT],
    initial_input=input_cases[0],
    initial_output=output_cases[0]
))

# Run optimization loop
for i in range(10):
    inverse = client.execute_request(SuggestInverse(objective_id=objective.id))
    output = my_function(inverse.input)
    inverse = client.execute_request(LoadInversedOutput(
        inverse_id=inverse.id,
        output=output
    ))

    if inverse.should_stop():
        print(f"Converged! Input: {inverse.input}, Output: {output}")
        break

client.http_client.close()
```

## Troubleshooting

### "API key is required and must be a non-empty string"
- You forgot to replace `YOUR_API_KEY_HERE` with your actual API key
- Make sure you're setting credentials in YOUR code, not just in the example

### "Base URI is required and must be a non-empty string"
- You forgot to replace `YOUR_BASE_URI`
- Make sure the URI starts with `http://` or `https://`

### "Module not found: httpx/pydantic/rich"
- The required dependencies aren't installed in your environment
- Request that `httpx`, `pydantic`, and `rich` be installed

### Example runs when I paste the file
- This shouldn't happen! The `if __name__ == "__main__":` block prevents this
- If it does run, make sure you're pasting the entire file correctly

## Need Help?

For issues with the SDK itself, visit:
https://github.com/globalMOO/gmoo-sdk-python/issues

For API questions, contact:
support@globalmoo.com
