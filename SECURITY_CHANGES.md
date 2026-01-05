# Security Changes to Flat File

## Summary

All security violations have been removed from `globalmoo_flat.py` to make it safe for restricted/sandboxed environments.

## Security Violations Removed

### 1. ❌ Removed `os` module
- **Before**: `import os` at line 33
- **After**: Completely removed
- **Impact**: No filesystem access

### 2. ❌ Removed `urllib.parse` module
- **Before**: `from urllib.parse import urlparse` at line 42
- **After**: Completely removed, replaced with simple string validation
- **Impact**: No URL parsing dependencies

### 3. ❌ Removed `python-dotenv` module
- **Before**: `from dotenv import load_dotenv` at line 48
- **After**: Completely removed
- **Impact**: No .env file loading

### 4. ❌ Removed `sys` module usage
- **Before**: `import sys` at lines 1148, 1151 and `sys.tracebacklimit` manipulation
- **After**: Completely removed
- **Impact**: No system manipulation

### 5. ❌ Removed environment variable access
- **Before**: `os.getenv('GMOO_API_KEY')` at line 1068
- **Before**: `os.getenv('GMOO_API_URI')` at line 1075
- **After**: Credentials must be passed explicitly
- **Impact**: No environment variable dependencies

## Changes to API

### Credentials Class

**Before:**
```python
# Optional parameters with environment variable fallback
creds = Credentials()  # Would load from environment
creds = Credentials(api_key="key")  # Would load base_uri from environment
```

**After:**
```python
# Both parameters are now REQUIRED
creds = Credentials(
    api_key="your-api-key",          # REQUIRED
    base_uri="https://api.globalmoo.ai"  # REQUIRED
)
```

### Client Class

**Before:**
```python
# Credentials were optional
client = Client()  # Would create Credentials() internally
```

**After:**
```python
# Credentials are now REQUIRED
client = Client(
    credentials=Credentials(
        api_key="your-api-key",
        base_uri="https://api.globalmoo.ai"
    )
)
```

## Reduced Dependencies

**Before:**
- httpx>=0.26.0
- pydantic>=2.5.0
- python-dotenv>=1.0.0 ❌ REMOVED
- tenacity>=8.2.3 ❌ REMOVED
- numpy==1.26.4 ❌ REMOVED
- rich==13.9.4

**After:**
- httpx>=0.26.0
- pydantic>=2.5.0
- rich==13.9.4

## File Size Changes

- **Before security fixes**: 1352 lines, 45 KB
- **After security fixes**: 1323 lines, 43 KB
- **Final with example**: 1523 lines, 52 KB
- **Net change**: +171 lines, +7 KB (includes complete working example in `__main__` block)

## Validation Status

✅ All tests pass
✅ No `os` imports
✅ No `sys` imports
✅ No `urllib` imports
✅ No `dotenv` imports
✅ No `os.getenv()` calls
✅ No `sys.tracebacklimit` manipulation
✅ No URL parsing with `urlparse()`

Run `grep -n "import os\|import sys\|from urllib\|from dotenv\|os.getenv\|load_dotenv\|urlparse\|sys.tracebacklimit" globalmoo_flat.py` to verify - returns no results.

## Usage Example

```python
from globalmoo_flat import Client, Credentials

# Create credentials (both parameters are required)
credentials = Credentials(
    api_key="your-api-key-here",
    base_uri="https://api.globalmoo.ai"
)

# Create client (credentials parameter is required)
client = Client(credentials=credentials)

# Use the SDK normally
from globalmoo_flat import CreateProject, LoadOutputCases, LoadObjectives

# Your optimization code here...
```

## Benefits for Restricted Environments

1. **No filesystem access** - Won't trigger security scanners
2. **No environment variables** - Works in sandboxed environments
3. **Explicit configuration** - All settings passed as parameters
4. **Reduced dependencies** - Fewer packages to approve/install
5. **Smaller size** - Easier to paste into restricted code editors

## Testing

Run the test suite to verify everything works:

```bash
python3 test_flat_file.py
```

Expected output:
```
Testing globalMOO SDK flat file...

✓ Successfully imported Client
✓ Successfully imported Credentials
✓ Successfully imported exceptions
✓ Successfully imported enums
✓ Successfully imported request classes

✓ InputType enum works correctly
✓ ObjectiveType enum works correctly
✓ StopReason enum works correctly

✓ InvalidArgumentException works correctly

✓ API key validation works correctly
✓ Base URI validation works correctly
✓ Credentials creation works correctly

✓ CreateProject validation works correctly
✓ Array length validation works correctly

==================================================
All tests passed! ✓
==================================================
```

## Built-in Example

The flat file now includes a complete working example in the `__main__` block at the bottom. This example demonstrates:

### Features Demonstrated

1. **Credentials Setup** - Shows how to create credentials explicitly
2. **Model Creation** - Creates a namespace for the optimization
3. **Project Setup** - Defines input specifications (2 inputs, range 0-10)
4. **Function Definition** - Simple linear function: `f(x,y) = [x+y, 2x+y, x+2y]`
5. **Output Cases** - Computes outputs for API-provided input cases
6. **Optimization Goal** - Finds inputs that produce outputs `[2.0, 3.0, 3.0]`
7. **Iterative Optimization** - Loops through suggestions until convergence
8. **Result Display** - Shows formatted results with satisfaction status

### Running the Example

The example is designed to work as a header in your code. When you paste the flat file at the top of your script, the example won't run automatically (it's protected by `if __name__ == "__main__"`).

**To test the SDK:**
1. Edit the flat file
2. Replace `YOUR_API_KEY_HERE` with your actual API key (line 1358)
3. Update `YOUR_BASE_URI` if needed (line 1359)
4. Run: `python globalmoo_flat.py`

**When using as a header:**
Your own code will run instead of the example, since `__name__` will not be `"__main__"` when imported.

### Example Output

```
globalMOO SDK - Linear Function Example
This example finds inputs that produce target outputs for a linear function
Make sure to replace YOUR_API_KEY_HERE with your actual API credentials!

Successfully initialized globalMOO client
Created model with ID: 123
Created project with ID: 456
Received 50 input cases from the API
Computed 50 output cases
Created trial with ID: 789

Optimization Goal
Finding inputs that produce outputs: [2.0, 3.0, 3.0]
...
```

The example provides a complete, annotated walkthrough of the SDK's core functionality.
