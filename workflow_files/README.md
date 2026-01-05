# globalMOO SDK - Workflow Files

This directory contains 6 separate files that implement the complete globalMOO optimization workflow. Each file is designed to be run independently in a system where you define input variables in an interface.

## 📋 Overview

The workflow is broken into 6 sequential steps:

1. **01_create_model.py** - Creates a model (optimization namespace)
2. **02_create_project.py** - Creates a project with input specifications
3. **03_evaluate_function.py** - Evaluates your function on input cases
4. **04_load_outputs.py** - Loads computed outputs to create a trial
5. **05_load_objectives.py** - Sets target objectives for optimization
6. **06_optimization_loop.py** - Runs iterative optimization to find optimal inputs

## 🔗 Data Flow

```
Step 1: Create Model
  IN:  api_key, base_uri
  OUT: model_id → Step 2

Step 2: Create Project
  IN:  model_id, api_key, base_uri, input_count, input_min, input_max
  OUT: project_id → Step 4
       input_cases → Step 3

Step 3: Evaluate Function
  IN:  input_cases
  OUT: output_cases → Step 4, Step 5
       output_count → Step 4

Step 4: Load Outputs
  IN:  project_id, output_cases, output_count, api_key, base_uri
  OUT: trial_id → Step 5

Step 5: Load Objectives
  IN:  trial_id, target_outputs, input_cases, output_cases, api_key, base_uri
  OUT: objective_id → Step 6

Step 6: Optimization Loop
  IN:  objective_id, target_outputs, max_iterations, api_key, base_uri
  OUT: final_input, final_output, iterations_run, converged, stop_reason
```

## 🚀 Quick Start

### Prerequisites

Each file needs the `globalmoo_functional.py` SDK pasted at the top (except Step 3 which is pure Python).

**For each file (except 03_evaluate_function.py):**
1. Open the file
2. Find the comment: `# === PASTE globalmoo_functional.py SDK HERE (660 lines) ===`
3. Replace the placeholder section with the complete contents of `globalmoo_functional.py`

### Configuration

Here's an example of running all 6 steps with a 2-input, 3-output linear function:

#### Step 1: Create Model

```python
# Define these variables in your interface:
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"

# Run: 01_create_model.py

# Outputs:
# model_id = 123
```

#### Step 2: Create Project

```python
# Define these variables in your interface:
model_id = 123  # from Step 1
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]

# Run: 02_create_project.py

# Outputs:
# project_id = 456
# input_cases = [[5.0, 5.0], [2.5, 7.5], [7.5, 2.5], ...]
```

#### Step 3: Evaluate Function

```python
# Define these variables in your interface:
input_cases = [[5.0, 5.0], [2.5, 7.5], [7.5, 2.5], ...]  # from Step 2

# Modify the linear_function() in the file to match your actual function!

# Run: 03_evaluate_function.py

# Outputs:
# output_cases = [[10.0, 15.0, 15.0], [10.0, 12.5, 17.5], ...]
# output_count = 3
```

#### Step 4: Load Outputs

```python
# Define these variables in your interface:
project_id = 456  # from Step 2
output_cases = [[10.0, 15.0, 15.0], [10.0, 12.5, 17.5], ...]  # from Step 3
output_count = 3  # from Step 3
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"

# Run: 04_load_outputs.py

# Outputs:
# trial_id = 789
```

#### Step 5: Load Objectives

```python
# Define these variables in your interface:
trial_id = 789  # from Step 4
target_outputs = [2.0, 3.0, 3.0]  # YOUR desired outputs
input_cases = [[5.0, 5.0], [2.5, 7.5], ...]  # from Step 2
output_cases = [[10.0, 15.0, 15.0], ...]  # from Step 3
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"

# Run: 05_load_objectives.py

# Outputs:
# objective_id = 101112
```

#### Step 6: Optimization Loop

```python
# Define these variables in your interface:
objective_id = 101112  # from Step 5
target_outputs = [2.0, 3.0, 3.0]  # same as Step 5
max_iterations = 20
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"

# IMPORTANT: Also paste the same function from Step 3!

# Run: 06_optimization_loop.py

# Outputs:
# final_input = [1.0, 1.0]
# final_output = [2.0, 3.0, 3.0]
# iterations_run = 8
# converged = True
# stop_reason = "satisfied to an optimal input and output"
```

## 📝 Customizing Your Function

In **Step 3** and **Step 6**, you need to define your actual function. Currently, it's a simple linear function:

```python
def linear_function(inputs):
    x, y = inputs
    return [
        x + y,          # Output 1
        2 * x + y,      # Output 2
        x + 2 * y       # Output 3
    ]
```

**Replace this with your actual computation!**

For example, if you have a complex simulation:
```python
def my_simulation(inputs):
    # Unpack inputs
    temperature, pressure, flow_rate = inputs

    # Your complex calculation
    efficiency = (temperature * 0.3 + pressure * 0.5) / flow_rate
    cost = temperature * 2 + pressure * 3
    quality = flow_rate / (temperature + pressure)

    # Return outputs
    return [efficiency, cost, quality]
```

## 🔑 Important Notes

### 1. SDK Installation

All files (except Step 3) need the SDK pasted at the top. The SDK is 660 lines from `globalmoo_functional.py`.

**Why?** Your system doesn't allow package imports or filesystem access, so we paste the SDK code directly.

### 2. Function Consistency

**CRITICAL:** The function in Step 3 and Step 6 MUST BE IDENTICAL!

- Step 3: Initial evaluation of input cases
- Step 6: Iterative evaluation during optimization

If they differ, optimization will fail or give wrong results.

### 3. Variable Passing

Your system works by defining variables in an interface. After each step completes:
1. The output variables become available
2. You pass them as inputs to the next step
3. Some variables (api_key, base_uri) pass through multiple steps

### 4. API Key Security

The example uses a real API key. In production:
- Store the API key securely in your interface
- Don't hardcode it in the files
- Pass it as an input variable to each step

### 5. Error Handling

Each file includes error handling that will:
- Print descriptive error messages
- Raise exceptions to stop execution
- This helps you debug issues quickly

## 🎯 Example Use Case

**Problem:** Find inputs (x, y) that produce outputs close to [2.0, 3.0, 3.0] for the function:
- f₁(x, y) = x + y
- f₂(x, y) = 2x + y
- f₃(x, y) = x + 2y

**Solution:**
1. Run Steps 1-2 to set up model and project
2. In Step 3, define the function (already done in the example)
3. Run Steps 4-5 to load data and objectives
4. Run Step 6 to find optimal inputs

**Result:** Finds x ≈ 1.0, y ≈ 1.0 which gives outputs [2.0, 3.0, 3.0]

## 🛠️ Troubleshooting

### "API key is required"
- Make sure you defined `api_key` variable in your interface
- Check the variable name matches exactly: `api_key`

### "Variable not found: model_id"
- Make sure you passed the output from the previous step
- Check variable names match exactly

### "Function returned wrong number of outputs"
- Check your function in Step 3 returns the correct number of values
- The `output_count` should match the number of values your function returns

### "httpx not found"
- The SDK requires `httpx` to be installed
- Request that httpx>=0.26.0 be installed in the environment

### "Optimization not converging"
- Increase `max_iterations` (try 50-100)
- Check your function is continuous and smooth
- Verify target_outputs are achievable by your function

## 📧 Support

For questions or issues:
- **SDK Issues:** https://github.com/globalMOO/gmoo-sdk-python/issues
- **API Questions:** support@globalmoo.com

## ✅ Checklist

Before running the workflow:

- [ ] Pasted SDK into files 01, 02, 04, 05, 06
- [ ] Defined your function in files 03 and 06
- [ ] Verified function is IDENTICAL in both files
- [ ] Set your API key and base URI
- [ ] Defined target outputs for Step 5
- [ ] Set reasonable max_iterations for Step 6

## 🎉 Summary

You now have a complete, modular workflow that:
- ✅ Works in restricted environments (no package installs)
- ✅ Uses simple variable passing (no complex data structures)
- ✅ Has clear input/output for each step
- ✅ Includes error handling and progress display
- ✅ Can be customized for any function

**Just paste the SDK, define your function, and run each step in sequence!**
