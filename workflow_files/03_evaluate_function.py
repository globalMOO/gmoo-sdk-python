"""
STEP 3: Evaluate Function
==========================

This is your actual function that takes inputs and produces outputs.
Modify the linear_function() to match your actual computation.

INPUT VARIABLES (define in interface):
- input_cases: List[List[float]]   (from Step 2)

OUTPUT VARIABLES (available after running):
- output_cases: List[List[float]]  (computed outputs - pass to Step 4)
- output_count: int                (number of outputs - pass to Step 4)
"""

# =============================================================================
# YOUR FUNCTION DEFINITION
# =============================================================================

def linear_function(inputs):
    """
    This is your actual function to optimize.

    Modify this to match your real computation!

    Args:
        inputs: List of input values [x, y, ...]

    Returns:
        List of output values

    Example:
        For 2 inputs (x, y), this returns 3 outputs:
        - Output 1: x + y
        - Output 2: 2x + y
        - Output 3: x + 2y
    """
    x, y = inputs
    return [
        x + y,          # Output 1
        2 * x + y,      # Output 2
        x + 2 * y       # Output 3
    ]

# =============================================================================
# EVALUATION CODE (don't modify this part)
# =============================================================================

# Evaluate the function for all input cases
output_cases = []
for case in input_cases:
    output = linear_function(case)
    output_cases.append(output)

# Determine output count from first output
output_count = len(output_cases[0]) if output_cases else 0

print(f"✓ Evaluated {len(input_cases)} input cases")
print(f"✓ Each output has {output_count} values")
print(f"✓ Sample input:  {input_cases[0]}")
print(f"✓ Sample output: {output_cases[0]}")

# OUTPUTS for next step:
# - output_cases (pass to Step 4)
# - output_count (pass to Step 4)
