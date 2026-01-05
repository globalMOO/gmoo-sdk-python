# Workflow Files - Complete Summary

## What You Have

I've created **6 workflow files** + **2 documentation files** that break down the globalMOO optimization process into discrete, chainable steps.

### 📁 Files Created

```
workflow_files/
├── 01_create_model.py          (2.3 KB) - Creates optimization model
├── 02_create_project.py        (3.1 KB) - Sets up input specifications
├── 03_evaluate_function.py     (2.0 KB) - Your function evaluation
├── 04_load_outputs.py          (2.6 KB) - Loads computed outputs
├── 05_load_objectives.py       (3.6 KB) - Sets optimization targets
├── 06_optimization_loop.py     (5.8 KB) - Iterative optimization
├── README.md                   (8.7 KB) - Complete usage guide
└── VARIABLE_REFERENCE.md       (12 KB)  - Variable I/O reference
```

**Total: 8 files, ~40 KB**

---

## 🎯 What Each File Does

### 1. `01_create_model.py`
- **Purpose:** Creates a model (namespace for your optimization work)
- **Needs SDK:** ✅ Yes
- **You define:** `api_key`, `base_uri`
- **You get:** `model_id`
- **Run:** Once per optimization project

### 2. `02_create_project.py`
- **Purpose:** Defines input variables and their ranges
- **Needs SDK:** ✅ Yes
- **You define:** `model_id`, `input_count`, `input_min`, `input_max`
- **You get:** `project_id`, `input_cases` (to evaluate)
- **Run:** Once per optimization project

### 3. `03_evaluate_function.py`
- **Purpose:** Evaluates YOUR function on input cases
- **Needs SDK:** ❌ No - Pure Python!
- **You define:** Your function + `input_cases`
- **You get:** `output_cases`, `output_count`
- **Run:** Once for initial evaluation

### 4. `04_load_outputs.py`
- **Purpose:** Loads computed outputs to create a trial
- **Needs SDK:** ✅ Yes
- **You define:** `project_id`, `output_cases`, `output_count`
- **You get:** `trial_id`
- **Run:** Once per optimization run

### 5. `05_load_objectives.py`
- **Purpose:** Sets target outputs you want to achieve
- **Needs SDK:** ✅ Yes
- **You define:** `trial_id`, `target_outputs` (YOUR GOALS!)
- **You get:** `objective_id`
- **Run:** Once per optimization run

### 6. `06_optimization_loop.py`
- **Purpose:** Iteratively finds inputs that produce target outputs
- **Needs SDK:** ✅ Yes
- **You define:** `objective_id`, `max_iterations`, your function
- **You get:** `final_input`, `final_output`, `converged`
- **Run:** Once per optimization run (runs multiple iterations internally)

---

## 🔧 Setup Required

### Before You Run

#### For Files 1, 2, 4, 5, 6:
1. Open each file
2. Find: `# === PASTE globalmoo_functional.py SDK HERE (660 lines) ===`
3. Replace with: Complete contents of `globalmoo_functional.py`

#### For Files 3, 6:
1. Modify the `linear_function()` to match YOUR actual function
2. **CRITICAL:** Function must be IDENTICAL in both files!

### Example Function

Current (linear example):
```python
def linear_function(inputs):
    x, y = inputs
    return [x + y, 2*x + y, x + 2*y]
```

Replace with your actual function:
```python
def my_actual_function(inputs):
    # Your real computation here
    temp, pressure, flow = inputs
    efficiency = calculate_efficiency(temp, pressure, flow)
    cost = calculate_cost(temp, pressure)
    quality = calculate_quality(flow)
    return [efficiency, cost, quality]
```

---

## 🚀 How to Run

### Step-by-Step Execution

#### 1. Define Initial Variables

In your interface, define:
```python
api_key = "yvYbJf8Dzh2E2UvxepQhVABrodFvQwEU6XubNgz1XNgyN5LU"
base_uri = "https://app.globalmoo.com/api/"
```

#### 2. Run Step 1

Execute: `01_create_model.py`

Output variable: `model_id`

#### 3. Define Project Variables

In your interface, define:
```python
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]
```

#### 4. Run Step 2

Execute: `02_create_project.py`

Output variables: `project_id`, `input_cases`

#### 5. Run Step 3

Execute: `03_evaluate_function.py`

Output variables: `output_cases`, `output_count`

#### 6. Run Step 4

Execute: `04_load_outputs.py`

Output variable: `trial_id`

#### 7. Define Target Outputs

In your interface, define:
```python
target_outputs = [2.0, 3.0, 3.0]  # Your desired outputs!
```

#### 8. Run Step 5

Execute: `05_load_objectives.py`

Output variable: `objective_id`

#### 9. Define Max Iterations

In your interface, define:
```python
max_iterations = 20
```

#### 10. Run Step 6

Execute: `06_optimization_loop.py`

Output variables: `final_input`, `final_output`, `converged`

---

## 📊 Data Flow

```
Step 1 → model_id
         ↓
Step 2 → project_id, input_cases
         ↓             ↓
Step 4 ←──────────── Step 3 → output_cases, output_count
  ↓
Step 5 → objective_id
  ↓
Step 6 → final_input, final_output, converged
```

---

## 🎓 Example Scenario

**Goal:** Find inputs (x, y) that produce outputs [2.0, 3.0, 3.0]

**Function:**
- f₁(x,y) = x + y
- f₂(x,y) = 2x + y
- f₃(x,y) = x + 2y

**Steps:**

1. **Step 1:** Create model → `model_id = 123`
2. **Step 2:** Create project with 2 inputs, range [0, 10] → `project_id = 456`, `input_cases = [[5,5], [2.5,7.5], ...]`
3. **Step 3:** Evaluate function → `output_cases = [[10,15,15], [10,12.5,17.5], ...]`
4. **Step 4:** Load outputs → `trial_id = 789`
5. **Step 5:** Set target [2.0, 3.0, 3.0] → `objective_id = 101112`
6. **Step 6:** Optimize → `final_input = [1.0, 1.0]`, `final_output = [2.0, 3.0, 3.0]`, `converged = True`

**Result:** Found optimal inputs x=1, y=1 that produce target outputs!

---

## 📝 Key Variables to Track

### Variables You Define (User Inputs)

| Variable | Step | Description |
|----------|------|-------------|
| `api_key` | 1 | Your API authentication key |
| `base_uri` | 1 | API endpoint URL |
| `input_count` | 2 | Number of input variables |
| `input_min` | 2 | Minimum values for inputs |
| `input_max` | 2 | Maximum values for inputs |
| `target_outputs` | 5 | Desired output values |
| `max_iterations` | 6 | Maximum optimization iterations |

### Variables Passed Between Steps

| Variable | From Step | To Step | Description |
|----------|-----------|---------|-------------|
| `model_id` | 1 | 2 | Model identifier |
| `project_id` | 2 | 4 | Project identifier |
| `input_cases` | 2 | 3 | Inputs to evaluate |
| `output_cases` | 3 | 4, 5 | Computed outputs |
| `output_count` | 3 | 4 | Number of outputs |
| `trial_id` | 4 | 5 | Trial identifier |
| `objective_id` | 5 | 6 | Objective identifier |

### Variables You Get (Final Results)

| Variable | Step | Description |
|----------|------|-------------|
| `final_input` | 6 | Optimal input found |
| `final_output` | 6 | Output for final input |
| `iterations_run` | 6 | Number of iterations executed |
| `converged` | 6 | Whether solution was found |
| `stop_reason` | 6 | Why optimization stopped |

---

## ⚙️ System Integration

Your system works by defining variables in an interface. Here's how to integrate:

### Variable Definition Pattern

```python
# In your interface, before running each step:

# Step 1 variables:
api_key = "your-key"
base_uri = "your-uri"

# Run Step 1
# [execute 01_create_model.py]

# After Step 1, these variables are available:
# - model_id

# Step 2 variables:
# (model_id already available from Step 1)
input_count = 2
input_min = [0.0, 0.0]
input_max = [10.0, 10.0]

# Run Step 2
# [execute 02_create_project.py]

# After Step 2, these variables are available:
# - project_id
# - input_cases

# ... and so on
```

---

## 🛡️ Error Handling

Each file includes error handling that will:

1. **Print** clear error messages
2. **Raise** exceptions to stop execution
3. **Close** network connections properly

Example error output:
```
ERROR [InvalidArgument]: API key is required and must be a non-empty string
```

---

## 🔍 Troubleshooting

### "Variable not found"
- Check you ran the previous step
- Check variable names match exactly (case-sensitive)

### "Function returns wrong number of outputs"
- Verify your function in Step 3 matches the `output_count`
- Check function in Step 6 is identical to Step 3

### "Optimization not converging"
- Increase `max_iterations` (try 50+)
- Check `target_outputs` are achievable by your function
- Verify function is continuous (no sudden jumps)

### "HTTP 401 Unauthorized"
- Check your `api_key` is correct
- Verify key has not expired

---

## ✅ Pre-Flight Checklist

Before running the workflow:

- [ ] Pasted SDK into files 01, 02, 04, 05, 06
- [ ] Defined your function in files 03 and 06
- [ ] Verified function is IDENTICAL in both files
- [ ] Set your actual API key
- [ ] Set appropriate input ranges (min/max)
- [ ] Defined realistic target outputs
- [ ] Set reasonable max_iterations (20-50 for most cases)
- [ ] Verified httpx is installed in environment

---

## 📚 Documentation Files

### `README.md`
- Complete usage guide
- Detailed examples
- Troubleshooting tips
- Configuration options

### `VARIABLE_REFERENCE.md`
- Quick variable lookup
- Type specifications
- Data flow diagrams
- Copy-paste templates

### This File (`WORKFLOW_SUMMARY.md`)
- High-level overview
- File descriptions
- Setup instructions
- Quick reference

---

## 🎉 Summary

You now have a **complete, modular optimization workflow** that:

✅ **Works in restricted environments** - No package installs needed
✅ **Clear I/O boundaries** - Simple variable passing between steps
✅ **Fully documented** - Every variable explained
✅ **Error-handled** - Clear error messages at every step
✅ **Customizable** - Easy to adapt to your function
✅ **Tested** - Based on working globalmoo_functional.py

**Just paste the SDK, define your function, and run each step in sequence!**

---

## 📞 Need Help?

- **README.md** - Full usage guide
- **VARIABLE_REFERENCE.md** - Variable quick reference
- **GitHub Issues:** https://github.com/globalMOO/gmoo-sdk-python/issues
- **Email Support:** support@globalmoo.com

---

## 🚦 Next Steps

1. ✅ Read this summary (you're doing it!)
2. ⬜ Read `README.md` for detailed instructions
3. ⬜ Paste SDK into files 01, 02, 04, 05, 06
4. ⬜ Define your function in files 03 and 06
5. ⬜ Run Step 1 with your API credentials
6. ⬜ Continue through Steps 2-6 sequentially
7. ⬜ Celebrate when you get optimal results! 🎊

**You're all set!** 🚀
