# Variable Reference Guide

Quick reference for all input/output variables across the 6 workflow files.

## Step 1: Create Model

**File:** `01_create_model.py`

| Variable | Type | Direction | Description |
|----------|------|-----------|-------------|
| `api_key` | `str` | INPUT | Your API key |
| `base_uri` | `str` | INPUT | API base URI (e.g., "https://app.globalmoo.com/api/") |
| `model_id` | `int` | OUTPUT | Created model ID → Pass to Step 2 |
| `model_name` | `str` | OUTPUT | Model name (for reference) |

**Pass to next step:** `model_id`, `api_key`, `base_uri`

---

## Step 2: Create Project

**File:** `02_create_project.py`

| Variable | Type | Direction | Description |
|----------|------|-----------|-------------|
| `model_id` | `int` | INPUT | From Step 1 |
| `api_key` | `str` | INPUT | From Step 1 |
| `base_uri` | `str` | INPUT | From Step 1 |
| `input_count` | `int` | INPUT | Number of inputs (e.g., 2) |
| `input_min` | `List[float]` | INPUT | Minimum values for each input (e.g., [0.0, 0.0]) |
| `input_max` | `List[float]` | INPUT | Maximum values for each input (e.g., [10.0, 10.0]) |
| `project_id` | `int` | OUTPUT | Created project ID → Pass to Step 4 |
| `input_cases` | `List[List[float]]` | OUTPUT | Input cases to evaluate → Pass to Step 3 |

**Pass to next step:** `project_id`, `input_cases`, `api_key`, `base_uri`

---

## Step 3: Evaluate Function

**File:** `03_evaluate_function.py`

| Variable | Type | Direction | Description |
|----------|------|-----------|-------------|
| `input_cases` | `List[List[float]]` | INPUT | From Step 2 |
| `output_cases` | `List[List[float]]` | OUTPUT | Computed outputs → Pass to Step 4 and Step 5 |
| `output_count` | `int` | OUTPUT | Number of outputs per case → Pass to Step 4 |

**Pass to next step:** `output_cases`, `output_count`

**Note:** This file does NOT need the SDK. It's pure Python.

---

## Step 4: Load Outputs

**File:** `04_load_outputs.py`

| Variable | Type | Direction | Description |
|----------|------|-----------|-------------|
| `project_id` | `int` | INPUT | From Step 2 |
| `output_cases` | `List[List[float]]` | INPUT | From Step 3 |
| `output_count` | `int` | INPUT | From Step 3 |
| `api_key` | `str` | INPUT | From Step 1 |
| `base_uri` | `str` | INPUT | From Step 1 |
| `trial_id` | `int` | OUTPUT | Created trial ID → Pass to Step 5 |

**Pass to next step:** `trial_id`, `api_key`, `base_uri`

---

## Step 5: Load Objectives

**File:** `05_load_objectives.py`

| Variable | Type | Direction | Description |
|----------|------|-----------|-------------|
| `trial_id` | `int` | INPUT | From Step 4 |
| `target_outputs` | `List[float]` | INPUT | **YOU DEFINE** - Desired output values (e.g., [2.0, 3.0, 3.0]) |
| `input_cases` | `List[List[float]]` | INPUT | From Step 2 (needed for initial point) |
| `output_cases` | `List[List[float]]` | INPUT | From Step 3 (needed for initial point) |
| `api_key` | `str` | INPUT | From Step 1 |
| `base_uri` | `str` | INPUT | From Step 1 |
| `objective_id` | `int` | OUTPUT | Created objective ID → Pass to Step 6 |

**Pass to next step:** `objective_id`, `target_outputs`, `api_key`, `base_uri`

---

## Step 6: Optimization Loop

**File:** `06_optimization_loop.py`

| Variable | Type | Direction | Description |
|----------|------|-----------|-------------|
| `objective_id` | `int` | INPUT | From Step 5 |
| `target_outputs` | `List[float]` | INPUT | From Step 5 (for display) |
| `max_iterations` | `int` | INPUT | **YOU DEFINE** - Max iterations (e.g., 20) |
| `api_key` | `str` | INPUT | From Step 1 |
| `base_uri` | `str` | INPUT | From Step 1 |
| `final_input` | `List[float]` | OUTPUT | Optimal input found |
| `final_output` | `List[float]` | OUTPUT | Output for final_input |
| `iterations_run` | `int` | OUTPUT | Number of iterations executed |
| `converged` | `bool` | OUTPUT | Whether optimization converged |
| `stop_reason` | `str` | OUTPUT | Human-readable stop reason |

**Note:** Must define the same function as Step 3!

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Create Model                                            │
│                                                                 │
│ INPUT:  api_key, base_uri                                       │
│ OUTPUT: model_id                                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Create Project                                          │
│                                                                 │
│ INPUT:  model_id, api_key, base_uri,                            │
│         input_count, input_min, input_max                       │
│ OUTPUT: project_id, input_cases                                 │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
                 │ project_id                 │ input_cases
                 │                            │
                 ▼                            ▼
┌────────────────────────┐   ┌────────────────────────────────────┐
│ Step 4: Load Outputs   │   │ Step 3: Evaluate Function          │
│                        │   │                                    │
│ INPUT:  project_id,    │◄──│ INPUT:  input_cases                │
│         output_cases,  │   │ OUTPUT: output_cases, output_count │
│         output_count,  │   │                                    │
│         api_key,       │   │ (Pure Python - No SDK needed)      │
│         base_uri       │   └────────────────────────────────────┘
│ OUTPUT: trial_id       │
└────────┬───────────────┘
         │
         │ trial_id
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Load Objectives                                         │
│                                                                 │
│ INPUT:  trial_id, target_outputs, input_cases, output_cases,   │
│         api_key, base_uri                                       │
│ OUTPUT: objective_id                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ objective_id
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Optimization Loop                                       │
│                                                                 │
│ INPUT:  objective_id, target_outputs, max_iterations,          │
│         api_key, base_uri                                       │
│ OUTPUT: final_input, final_output, iterations_run,             │
│         converged, stop_reason                                  │
│                                                                 │
│ (Must define same function as Step 3)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Variable Type Details

### Lists

All lists use Python's standard list type:
- `List[float]` - List of floating-point numbers: `[1.0, 2.5, 3.7]`
- `List[List[float]]` - List of lists: `[[1.0, 2.0], [3.0, 4.0]]`

### Example Values

```python
# Step 1
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"

# Step 2
model_id = 123
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]

# Step 2 Output
project_id = 456
input_cases = [[5.0, 5.0], [2.5, 7.5], [7.5, 2.5]]

# Step 3 Output
output_cases = [[10.0, 15.0, 15.0], [10.0, 12.5, 17.5], [10.0, 17.5, 12.5]]
output_count = 3

# Step 4 Output
trial_id = 789

# Step 5
target_outputs = [2.0, 3.0, 3.0]

# Step 5 Output
objective_id = 101112

# Step 6
max_iterations = 20

# Step 6 Output
final_input = [1.0, 1.0]
final_output = [2.0, 3.0, 3.0]
iterations_run = 8
converged = True
stop_reason = "satisfied to an optimal input and output"
```

---

## Variables That Need to Be Passed Through

Some variables need to be carried through multiple steps:

| Variable | Used In Steps |
|----------|---------------|
| `api_key` | 1, 2, 4, 5, 6 |
| `base_uri` | 1, 2, 4, 5, 6 |
| `input_cases` | 2 (OUT) → 3 (IN), 5 (IN) |
| `output_cases` | 3 (OUT) → 4 (IN), 5 (IN) |
| `target_outputs` | 5 (IN) → 6 (IN) |

---

## Quick Copy-Paste Template

```python
# === STEP 1: Create Model ===
api_key = "YOUR_API_KEY"
base_uri = "https://app.globalmoo.com/api/"
# → Run 01_create_model.py
# → Get: model_id

# === STEP 2: Create Project ===
# model_id = [from Step 1]
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]
# → Run 02_create_project.py
# → Get: project_id, input_cases

# === STEP 3: Evaluate Function ===
# input_cases = [from Step 2]
# → Run 03_evaluate_function.py
# → Get: output_cases, output_count

# === STEP 4: Load Outputs ===
# project_id = [from Step 2]
# output_cases = [from Step 3]
# output_count = [from Step 3]
# → Run 04_load_outputs.py
# → Get: trial_id

# === STEP 5: Load Objectives ===
# trial_id = [from Step 4]
target_outputs = [2.0, 3.0, 3.0]  # YOUR TARGET
# input_cases = [from Step 2]
# output_cases = [from Step 3]
# → Run 05_load_objectives.py
# → Get: objective_id

# === STEP 6: Optimization Loop ===
# objective_id = [from Step 5]
# target_outputs = [from Step 5]
max_iterations = 20
# → Run 06_optimization_loop.py
# → Get: final_input, final_output, iterations_run, converged, stop_reason
```
