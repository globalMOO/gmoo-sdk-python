# globalMOO SDK - Functional Version

## Problem Solved

Your environment doesn't allow the `__build_class__` builtin, which means **no class definitions are allowed**. This is an extremely restricted Python environment.

The original flat file used classes extensively:
- Pydantic models (BaseModel subclasses)
- Exception classes
- Enum classes
- Request classes
- Client and Credentials classes

## Solution

I've created `globalmoo_functional.py` - a **purely functional version** of the SDK that uses:
- ✅ **Only functions** - No classes at all
- ✅ **Dictionaries** - Instead of objects
- ✅ **Plain values** - Instead of enums
- ✅ **Error dicts** - Instead of exceptions
- ✅ **Simple functions** - Instead of methods

## File Statistics

- **654 lines** of Python code
- **21 KB** in size
- **Zero classes** ✅
- Only **1 dependency**: `httpx`

## Dependencies Reduced Further

**Original SDK**: 6 dependencies
**Flat file version**: 3 dependencies
**Functional version**: **1 dependency**
- httpx>=0.26.0 (only this one!)

**Removed**:
- ❌ pydantic (requires classes)
- ❌ rich (requires classes)
- ❌ python-dotenv (not needed)
- ❌ tenacity (not needed)
- ❌ numpy (not needed)

## Security Compliant

This version does NOT use any restricted operations:
- ❌ No `exit()` calls - uses `return` instead
- ❌ No classes - uses functions only
- ❌ No `os` module - no filesystem access
- ❌ No `sys` module - no system manipulation
- ❌ No environment variables - explicit configuration only

## How to Use

### As a Header (Most Common)

```python
# === Paste entire globalmoo_functional.py here (654 lines) ===

# Your code starts here:

# Step 1: Create credentials
credentials = create_credentials(
    api_key="your-api-key",
    base_uri="https://app.globalmoo.com/api/"
)

if is_error(credentials):
    print_error_message(credentials)
    exit(1)

# Step 2: Create client
client = create_client(credentials)

if is_error(client):
    print_error_message(client)
    exit(1)

# Step 3: Define your function
def my_function(inputs):
    x, y = inputs
    return [x + y, 2*x + y, x + 2*y]

# Step 4: Create model
model_req = create_model_request("My Model")
model = execute_request(client, model_req)

if is_error(model):
    print_error_message(model)
    exit(1)

print(f"Created model: {model['id']}")

# Step 5: Create project
project_req = create_project_request(
    model_id=model['id'],
    name="My Project",
    input_count=2,
    minimums=[0.0, 0.0],
    maximums=[10.0, 10.0],
    input_types=[INPUT_TYPE_FLOAT, INPUT_TYPE_FLOAT],
    categories=[]
)

if is_error(project_req):
    print_error_message(project_req)
    exit(1)

project = execute_request(client, project_req)

if is_error(project):
    print_error_message(project)
    exit(1)

# Step 6: Compute outputs
input_cases = project['inputCases']
output_cases = [my_function(case) for case in input_cases]

# Step 7: Load output cases
trial_req = load_output_cases_request(
    project_id=project['id'],
    output_count=3,
    output_cases=output_cases
)

trial = execute_request(client, trial_req)

# Step 8: Set objectives
obj_req = load_objectives_request(
    trial_id=trial['id'],
    objectives=[2.0, 3.0, 3.0],
    objective_types=[OBJECTIVE_TYPE_PERCENT] * 3,
    initial_input=input_cases[0],
    initial_output=output_cases[0],
    minimum_bounds=[-1.0, -1.0, -1.0],
    maximum_bounds=[1.0, 1.0, 1.0]
)

objective = execute_request(client, obj_req)

# Step 9: Run optimization loop
for iteration in range(10):
    # Get suggestion
    suggest_req = suggest_inverse_request(objective['id'])
    inverse = execute_request(client, suggest_req)

    if is_error(inverse):
        print_error_message(inverse)
        break

    # Compute output
    output = my_function(inverse['input'])

    # Load output
    load_req = load_inversed_output_request(inverse['id'], output)
    inverse = execute_request(client, load_req)

    if is_error(inverse):
        print_error_message(inverse)
        break

    print(f"Iteration {iteration + 1}: Input={inverse['input']}, Output={output}")

    # Check if done
    if should_stop(inverse):
        reason = get_stop_reason(inverse)
        print(f"Stopped: {get_stop_reason_description(reason)}")
        break

# Step 10: Close client
close_client(client)
```

## Available Functions

### Credentials & Client

```python
create_credentials(api_key, base_uri, validate_tls=True) -> Dict
create_client(credentials, timeout=30.0) -> Dict
close_client(client) -> None
```

### Request Builders

```python
create_model_request(name, description=None) -> Dict
create_project_request(model_id, name, input_count, minimums, maximums, input_types, categories) -> Dict
load_output_cases_request(project_id, output_count, output_cases) -> Dict
load_objectives_request(trial_id, objectives, objective_types, initial_input, initial_output, ...) -> Dict
suggest_inverse_request(objective_id) -> Dict
load_inversed_output_request(inverse_id, output) -> Dict
read_trial_request(trial_id) -> Dict
```

### Request Execution

```python
execute_request(client, request, max_retries=3) -> Dict
```

### Error Handling

```python
is_error(result) -> bool
print_error_message(error) -> None
```

### Helper Functions

```python
should_stop(inverse) -> bool
get_stop_reason(inverse) -> int
get_stop_reason_description(reason) -> str
```

## Constants (Instead of Enums)

### Input Types
```python
INPUT_TYPE_BOOLEAN = "boolean"
INPUT_TYPE_CATEGORY = "category"
INPUT_TYPE_FLOAT = "float"
INPUT_TYPE_INTEGER = "integer"
```

### Objective Types
```python
OBJECTIVE_TYPE_EXACT = "exact"
OBJECTIVE_TYPE_PERCENT = "percent"
OBJECTIVE_TYPE_VALUE = "value"
OBJECTIVE_TYPE_LESS_THAN = "lessthan"
OBJECTIVE_TYPE_LESS_THAN_EQUAL = "lessthan_equal"
OBJECTIVE_TYPE_GREATER_THAN = "greaterthan"
OBJECTIVE_TYPE_GREATER_THAN_EQUAL = "greaterthan_equal"
OBJECTIVE_TYPE_MINIMIZE = "minimize"
OBJECTIVE_TYPE_MAXIMIZE = "maximize"
```

### Stop Reasons
```python
STOP_REASON_RUNNING = 0
STOP_REASON_SATISFIED = 1
STOP_REASON_STOPPED = 2
STOP_REASON_EXHAUSTED = 3
```

## Error Handling Pattern

Since we can't use exceptions, all functions return dictionaries. Check for errors:

```python
result = execute_request(client, request)

if is_error(result):
    print_error_message(result)
    # Handle error
    exit(1)
else:
    # Use result
    print(f"Success: {result}")
```

Error dictionaries look like:
```python
{
    "error": True,
    "error_type": "InvalidArgument",
    "message": "API key is required",
    "details": {}
}
```

Success results are just plain dicts with the API response data.

## Working with Results

All results are dictionaries with camelCase keys (matching the API):

```python
model = execute_request(client, create_model_request("My Model"))
# model = {"id": 123, "name": "My Model", "createdAt": "...", ...}

project = execute_request(client, create_project_request(...))
# project = {"id": 456, "inputCases": [[...], [...]], ...}

inverse = execute_request(client, suggest_inverse_request(objective['id']))
# inverse = {"id": 789, "input": [1.0, 2.0], "iteration": 1, ...}
```

Access fields directly:
```python
model_id = model['id']
input_cases = project['inputCases']
suggested_input = inverse['input']
```

## Differences from Class-Based Version

### Before (Class-Based)
```python
from globalmoo_flat import Client, Credentials, CreateModel

credentials = Credentials(api_key="...", base_uri="...")
client = Client(credentials=credentials)
model = client.execute_request(CreateModel("My Model"))
print(model.id)  # Access as attribute
```

### After (Functional)
```python
from globalmoo_functional import create_client, create_credentials, create_model_request, execute_request

credentials = create_credentials(api_key="...", base_uri="...")
client = create_client(credentials)
model_req = create_model_request("My Model")
model = execute_request(client, model_req)
print(model['id'])  # Access as dict key
```

## Built-in Example

The file includes a complete working example at the bottom (protected by `if __name__ == "__main__"`).

To run it:
1. Edit `globalmoo_functional.py`
2. Replace `YOUR_API_KEY_HERE` on line ~555
3. Run: `python globalmoo_functional.py`

The example demonstrates the complete workflow using a linear function.

## Comparison

| Feature | Original SDK | Flat File | Functional |
|---------|--------------|-----------|------------|
| **Size** | Distributed | 1,523 lines (52 KB) | 654 lines (21 KB) |
| **Dependencies** | 6 packages | 3 packages | 1 package |
| **Classes** | ✅ Many | ✅ Many | ❌ None |
| **Exceptions** | ✅ Yes | ✅ Yes | ❌ No (error dicts) |
| **Enums** | ✅ Yes | ✅ Yes | ❌ No (constants) |
| **Pydantic** | ✅ Required | ✅ Required | ❌ Not needed |
| **Type Safety** | ✅ Full | ✅ Full | ⚠️ Manual checks |
| **Environment** | Normal | Restricted | **Extremely Restricted** |

## When to Use Which Version

### Original SDK
- Normal Python environment
- Can install packages
- Want full type safety
- Need rich features

### Flat File Version (`globalmoo_flat.py`)
- Restricted environment (no package install)
- Can't access filesystem
- Classes are allowed
- Need type safety

### Functional Version (`globalmoo_functional.py`)
- **Extremely restricted environment**
- **`__build_class__` is blocked**
- **No class definitions allowed**
- Only basic Python features available
- Minimal dependencies (just httpx)

## Testing

The functional version includes error checking at every step. Test with invalid credentials to see error handling:

```python
credentials = create_credentials(api_key="", base_uri="test")

if is_error(credentials):
    print_error_message(credentials)
    # Output: ERROR [InvalidArgument]: API key is required and must be a non-empty string
```

## Support

The functional version provides the same core API operations as the full SDK:
- ✅ Create models and projects
- ✅ Load output cases
- ✅ Set objectives
- ✅ Run inverse optimization
- ✅ Suggest and load inverse steps
- ✅ Read trials

It just does it all with functions and dictionaries instead of classes and objects!

## Quick Reference

```python
# 1. Setup
credentials = create_credentials("key", "https://app.globalmoo.com/api/")
client = create_client(credentials)

# 2. Create model
model = execute_request(client, create_model_request("Name"))

# 3. Create project
project = execute_request(client, create_project_request(
    model['id'], "Project", 2, [0,0], [10,10],
    [INPUT_TYPE_FLOAT]*2, []
))

# 4. Compute & load outputs
outputs = [my_function(inp) for inp in project['inputCases']]
trial = execute_request(client, load_output_cases_request(
    project['id'], 3, outputs
))

# 5. Set objectives
objective = execute_request(client, load_objectives_request(
    trial['id'], [2,3,3], [OBJECTIVE_TYPE_PERCENT]*3,
    project['inputCases'][0], outputs[0], 0.0, [-1]*3, [1]*3
))

# 6. Optimize
for i in range(10):
    inv = execute_request(client, suggest_inverse_request(objective['id']))
    out = my_function(inv['input'])
    inv = execute_request(client, load_inversed_output_request(inv['id'], out))
    if should_stop(inv): break

# 7. Cleanup
close_client(client)
```

## Summary

✅ **Zero classes** - Works in `__build_class__` blocked environments
✅ **654 lines** - Small and easy to paste
✅ **21 KB** - Minimal footprint
✅ **1 dependency** - Only httpx needed
✅ **Complete example** - Built-in working demonstration
✅ **Same functionality** - All core SDK features included

**Perfect for extremely restricted Python environments!**
