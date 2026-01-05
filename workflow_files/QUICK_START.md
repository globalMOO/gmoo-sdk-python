# Quick Start - Workflow Files

All files are **ready to copy** with the full SDK embedded!

## Files Ready to Use

| File | Size | Has SDK? | Purpose |
|------|------|----------|---------|
| `01_create_model.py` | 13 KB | ✅ Yes | Creates optimization model |
| `02_create_project.py` | 14 KB | ✅ Yes | Defines input variables |
| `03_evaluate_function.py` | 2 KB | ❌ No (Pure Python) | **YOUR FUNCTION** |
| `04_load_outputs.py` | 13 KB | ✅ Yes | Loads computed outputs |
| `05_load_objectives.py` | 14 KB | ✅ Yes | Sets target outputs |
| `06_optimization_loop.py` | 17 KB | ✅ Yes | Runs optimization |

## Usage in Your Interface

### Step 1: Create Model

Define these variables:
```python
api_key = "your-api-key"
base_uri = "https://app.globalmoo.com/api/"
```

Copy and run `01_create_model.py`

**Output:** `model_id`

---

### Step 2: Create Project

Define these variables:
```python
# model_id already available from Step 1
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]
```

Copy and run `02_create_project.py`

**Outputs:** `project_id`, `input_cases`

---

### Step 3: Evaluate Function

Define this variable:
```python
# input_cases already available from Step 2
```

**IMPORTANT:** Edit `03_evaluate_function.py` to define YOUR function!

Copy and run `03_evaluate_function.py`

**Outputs:** `output_cases`, `output_count`

---

### Step 4: Load Outputs

Define these variables:
```python
# project_id, output_cases, output_count already available
```

Copy and run `04_load_outputs.py`

**Output:** `trial_id`

---

### Step 5: Load Objectives

Define this variable:
```python
target_outputs = [2.0, 3.0, 3.0]  # YOUR DESIRED OUTPUTS
# trial_id, input_cases, output_cases already available
```

Copy and run `05_load_objectives.py`

**Output:** `objective_id`

---

### Step 6: Optimization Loop

Define this variable:
```python
max_iterations = 20
# objective_id, target_outputs already available
```

**IMPORTANT:** Edit `06_optimization_loop.py` - the function MUST match Step 3!

Copy and run `06_optimization_loop.py`

**Outputs:** `final_input`, `final_output`, `converged`

---

## What to Customize

### File 03: Your Function

```python
def linear_function(inputs):
    """Replace this with YOUR actual function!"""
    x, y = inputs
    return [
        x + y,          # Output 1
        2 * x + y,      # Output 2
        x + 2 * y       # Output 3
    ]
```

### File 06: Same Function

```python
def linear_function(inputs):
    """MUST BE IDENTICAL to Step 3!"""
    x, y = inputs
    return [
        x + y,
        2 * x + y,
        x + 2 * y
    ]
```

## Complete Data Flow

```
api_key, base_uri
    ↓
[Step 1] → model_id
    ↓
[Step 2] → project_id, input_cases
    ↓         ↓
[Step 4] ← [Step 3] → output_cases, output_count
    ↓
[Step 5] → objective_id
    ↓
[Step 6] → final_input, final_output, converged
```

## Variable Pass-Through

These variables need to be passed through multiple steps:

- `api_key`, `base_uri`: Steps 1, 2, 4, 5, 6
- `input_cases`: Steps 2 → 3, 5
- `output_cases`: Steps 3 → 4, 5

## Tips

1. **Copy entire files** - Each file is self-contained with full SDK
2. **No modifications needed** - Except for defining your function in files 03 and 06
3. **Run sequentially** - Must run in order (Step 1 → 2 → 3 → 4 → 5 → 6)
4. **Function consistency** - Step 3 and Step 6 functions MUST be identical
5. **Error handling** - All files have error handling built-in

## Example Values

```python
# Step 1
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"

# Step 2
model_id = 123  # from Step 1
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]

# Step 2 Outputs
project_id = 456
input_cases = [[5.0, 5.0], [2.5, 7.5], ...]

# Step 3 Outputs
output_cases = [[10.0, 15.0, 15.0], ...]
output_count = 3

# Step 4 Output
trial_id = 789

# Step 5
target_outputs = [2.0, 3.0, 3.0]

# Step 5 Output
objective_id = 101112

# Step 6
max_iterations = 20

# Step 6 Outputs
final_input = [1.0, 1.0]
final_output = [2.0, 3.0, 3.0]
converged = True
```

## Ready to Go!

All files have the full SDK embedded and are ready to copy and paste into your system. Just:

1. ✅ Copy each file when needed
2. ✅ Define the required input variables in your interface
3. ✅ Customize your function in files 03 and 06
4. ✅ Run them in sequence

**No SDK installation needed - everything is self-contained!**
