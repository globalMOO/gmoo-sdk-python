import pytest
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from globalmoo.client import Client
from globalmoo.models.inverse import Inverse
from globalmoo.request.create_model import CreateModel
from globalmoo.request.create_project import CreateProject
from globalmoo.request.load_output_cases import LoadOutputCases
from globalmoo.request.load_objectives import LoadObjectives
from globalmoo.request.suggest_inverse import SuggestInverse
from globalmoo.request.load_inversed_output import LoadInversedOutput
from globalmoo.enums.input_type import InputType
from globalmoo.enums.objective_type import ObjectiveType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True  # This will override any existing logging configuration
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def verify_inverse_timing(inverse: Inverse) -> None:
    """Verify that inverse timing information is present and valid."""
    assert inverse.suggest_time >= 0, "Suggest time should be non-negative"
    assert inverse.compute_time >= 0, "Compute time should be non-negative"



def generate_coefficients(n: int, m: int, seed: Optional[int] = None) -> List[List[float]]:
    """Generate coefficient matrix C[i,j] for the equations."""
    if seed is not None:
        np.random.seed(seed)
    return [np.random.uniform(-1, 1, n).tolist() for _ in range(m)]

def linear_model(x: np.ndarray, m: int = 3, n: int = None, C: Optional[List[List[float]]] = None, seed: Optional[int] = None) -> np.ndarray:
    """Linear model implementation."""
    x = np.array(x, ndmin=1)
    if n is None:
        n = len(x)
    
    if C is None:
        C = generate_coefficients(n, m, seed)
    
    y = np.zeros(m)
    for j in range(m):
        y[j] = sum((1 + C[j][i] * x[i]) for i in range(n))
    return y.tolist()

def quadratic_model(x: np.ndarray, m: int = 3, n: int = 3, C: Optional[List[List[float]]] = None, seed: Optional[int] = None) -> np.ndarray:
    """Quadratic model implementation."""
    x = np.array(x, ndmin=1)
    if C is None:
        C = generate_coefficients(n, m, seed)
    
    y = np.zeros(m)
    for j in range(m):
        y[j] = sum((1 + C[j][i] * x[i])**2 for i in range(n))
    return y.tolist()

def cubic_model(x: np.ndarray, m: int = 3, n: int = 3, C: Optional[List[List[float]]] = None, seed: Optional[int] = None) -> np.ndarray:
    """Cubic model implementation."""
    x = np.array(x, ndmin=1)
    if C is None:
        C = generate_coefficients(n, m, seed)
    
    y = np.zeros(m)
    for j in range(m):
        y[j] = sum((1 + C[j][i] * x[i])**3 for i in range(n))
    return y.tolist()

def nonlinear_model1(x: np.ndarray, m: int = 3, n: int = 3, C: Optional[List[List[float]]] = None, seed: Optional[int] = None) -> np.ndarray:
    """First nonlinear model implementation."""
    x = np.array(x, ndmin=1)
    if C is None:
        C = generate_coefficients(n, m, seed)
    
    y = np.zeros(m)
    for j in range(m):
        base_term = (1 + C[j][0] * x[0])**2
        sum_term = sum((1 + C[j][i-1] * x[i-1]) * (1 + C[j][i] * x[i]) for i in range(1, n))
        y[j] = base_term + sum_term
    return y.tolist()

def nonlinear_model2(x: np.ndarray, m: int = 3, n: int = 3, C: Optional[List[List[float]]] = None, seed: Optional[int] = None) -> np.ndarray:
    """Second nonlinear model implementation."""
    x = np.array(x, ndmin=1)
    if C is None:
        C = generate_coefficients(n, m, seed)
    
    y = np.zeros(m)
    for j in range(m):
        first_term = (1 + C[j][n-1] * x[n-1]) * (1 + C[j][0] * x[0])**2
        sum_term = sum((1 + C[j][i-1] * x[i-1]) * (1 + C[j][i] * x[i])**2 for i in range(1, n))
        y[j] = first_term + sum_term
    return y.tolist()

def JavaTestFunction(inputArr):
    """Nonlinear test function with nine outputs."""
    #inputArr = np.array(inputArr, ndmin=1)
    v1, v2, v3 = inputArr[0], inputArr[1], inputArr[2]
    
    output1 = v1 * v2 + 6.54321
    output2 = v2 * v3
    output3 = v1 + v2 + v3
    output4 = 2.0 * v1 + v2 + 5.0
    output5 = 3.0 * v1 + v2
    output6 = 4.0 * v1 + v2 + 70.0
    output7 = 2.0 * v1 + v3
    output8 = 3.0 * v1 + v3 - 5.0
    output9 = 4.0 * v1 + v3
    
    return [output1, output2, output3, output4, output5, output6, output7, output8, output9]

# Test Function Definitions
def SimpleTestFunction(inputArr):
    """Nonlinear test function with continuous variables only."""
    #inputArr = np.array(inputArr, ndmin=1)
    v01, v02, v03 = inputArr[0], inputArr[1], inputArr[2]
    
    o01 = v01 * v01 * v03 * v03
    o02 = (v01 - 2.0) * (v01 - 2.0) * v03
    o03 = (v02 - 2.0) * (v02 - 2.0) * v03
    o04 = v01 * v02 * v03 * v03
    
    return [float(o01), float(o02), float(o03), float(o04)]

def NonlinearTestFunction(inputArr):
    """Nonlinear test function with continuous variables only."""
    #inputArr = np.array(inputArr, ndmin=1)
    v01, v02, v03 = inputArr[0], inputArr[1], inputArr[2]
    
    o01 = v01 * v01 * v03 * v03 / v02
    o02 = (v01 - 2.0) * (v01 - 2.0) * v03 + v01 * v02
    o03 = (v02 - 2.0) * (v02 - 2.0) * v03 + v02 * v03
    o04 = v01 * v02 * v03 * v03 + v01 * v01
    
    return [float(o01), float(o02), float(o03), float(o04)]

def IntegerTestFunction(inputArr):
    """Test function with mixed integer and continuous variables."""
    #inputArr = np.array(inputArr, ndmin=1)
    v01, v02 = inputArr[0], inputArr[1]  # Real, Integer
    
    o01 = 1.0 * v01 + v02
    o02 = 2.0 * v01 + v02
    o03 = 3.0 * v01 + v02
    o04 = v02 + 7.0 * v01
    o05 = 1.5 * v01 + v02
    o06 = 2.5 * v01 + v02
    o07 = 3.5 * v01 + v02
    o08 = v01 * v02
    o09 = 1.5 * v01 * v02
    
    return [o01, o02, o03, o04, o05, o06, o07, o08, o09]

def LogicalTestFunction(inputArr):
    """Test function with logical/boolean variables."""
    #inputArr = np.array(inputArr, ndmin=1)
    v01, v02 = inputArr[0], inputArr[1]  # Real, Logical
    
    logical_term = 100.0 if (v02 == 0 or v02 == 0.0) else -5.4321
    
    o01 = 1.0 * v01 * logical_term
    o02 = 2.0 * v01 * logical_term
    o03 = 3.0 * v01 + logical_term
    o04 = v01 / logical_term
    o05 = 1.5 * v01 * logical_term
    o06 = 2.5 * v01 * logical_term
    o07 = 3.5 * v01 + logical_term
    o08 = v01 * logical_term
    o09 = 1.5 * v01 + logical_term / 1000.0
    
    return [o01, o02, o03, o04, o05, o06, o07, o08, o09]

def MixedInputTypeFunction(inputArr):
    """Test function with mixed variable types: real, integer, and logical/boolean."""
    #inputArr = np.array(inputArr, ndmin=1)
    
    v01 = inputArr[0]  # Real type variable
    v02 = inputArr[1]  # Integer type variable
    v03 = inputArr[2]  # Real type variable
    v04 = inputArr[3]  # Integer type variable
    v05 = inputArr[4]  # Boolean type variable

    boolean_coeff = v05

    o01 = 0.5 * v01 + v02 * boolean_coeff
    o02 = 0.5 * v02 + v03 * boolean_coeff
    o03 = 0.5 * v03 + v04 * boolean_coeff
    o04 = 0.5 * v04 + v05
    o05 = 0.5 * v05 + v01
    o06 = 0.5 * v01 + v03
    o07 = 0.5 * v02 + v04 * boolean_coeff
    o08 = 0.5 * v03 + v05 * boolean_coeff
    o09 = 1.5 * v05 + v04 * boolean_coeff
    o10 = 1.5 * v01 + 2.5 * v03 + 1.0 * v04
    o11 = 1.5 * v01 + 2.5 * v03 + 2.0 * v04
    o12 = v01 * v02 + 1.0 * v04
    o13 = v01 * v02 + 2.0 * v04 * boolean_coeff
    o14 = v02 * v05 * boolean_coeff
    o15 = v02 * v05 * boolean_coeff

    outcomes = [o01, o02, o03, o04, o05, o06, o07, o08, o09, o10, o11, o12, o13, o14, o15]

    return outcomes

def CategoricalTestFunction(inputArr):
   #inputArr = np.array(inputArr, ndmin=1)
   v01, v02, v03 = inputArr[0:3]
   additive_terms = {
       1: 5.0, #1.0,
       2: 1.0, #5.0,
       3: 10.0,
       4: 100.0,
       5: 1000.0,  
       6: -5.0027
   }
   
   a = additive_terms.get(int(v03))
   if a is None:
       raise ValueError(f"Invalid categorical value: {v03}")
   
   # Linear combinations: c1*v01 + c2*v02 + c3*a
   outputs = [
       1.0*v01 + 0*v02 + 1.0*a,  # o01
       2.0*v01 + 0*v02 + 1.0*a,  # o02
       3.0*v01 + 0*v02 + 1.0*a,  # o03
       1.0*v01 + 0*v02 + 1.0*a,  # o04
       1.5*v01 + 0*v02 + 1.0*a,  # o05 
       3.0*v01 + 0*v02 + 1.0*a,  # o06
       4.5*v01 + 0*v02 + 1.0*a,  # o07
       1.0*v01 + 0*v02 + 1.0*a,  # o08
       1.5*v01 + 0*v02 + 1.0*a,  # o09
       0*v01 + 1.0*v02 + 1.0*a,  # o10
       0*v01 + 2.0*v02 + 1.0*a,  # o11
       0*v01 + 3.0*v02 + 1.0*a,  # o12
       0*v01 + 1.0*v02 + 1.0*a,  # o13
       0*v01 + 1.5*v02 + 1.0*a,  # o14
       0*v01 + 3.0*v02 + 1.0*a,  # o15
       0*v01 + 4.5*v02 + 1.0*a,  # o16
       0*v01 + 1.0*v02 + 1.0*a,  # o17
       0*v01 + 1.5*v02 + 1.0*a,  # o18
       1.0*v01 + 1.0*v02 + 1.0*a,  # o19
       1.0*v01 + 1.0*v02 + 2.0*a,   # o20
   ]
   
   return outputs

def ComplexFunction(inputArr):
    """Test function combining exponential, polynomial, and logarithmic components."""
    #inputArr = np.array(inputArr, ndmin=1)
    v1, v2, v3, v4, v5 = inputArr[0], inputArr[1], inputArr[2], inputArr[3], inputArr[4]
    
    # Exponential components
    o1 = np.exp(0.5 * v1) + v2**2
    o2 = np.exp(-0.3 * v3) + v4 * v5
    
    # Polynomial components
    o3 = v1**3 + v2**2 + v1
    o4 = (v1 - 2)**2 * v2
    
    # Logarithmic components
    o5 = np.log(v1 + 2) * v2 + v3
    o6 = np.log10(v4 + 3) * v5**2
    
    # Mixed components
    o7 = np.exp(0.1 * v1) * np.log(v2 + 2) + v3**2
    o8 = v4**3 * np.log10(v5 + 1.5)
    
    # Complex combinations
    o9 = np.exp(0.2 * v1) * v2**2 * np.log(v3 + 1.5) + v4 * v5
    o10 = np.log10(v1 + 2) * v2**2 + np.exp(0.15 * v3) + v4**2 * v5
    
    outcomes = [o1, o2, o3, o4, o5, o6, o7, o8, o9, o10]
    
    return outcomes

TEST_CONFIGS = {
    'linear_small': {
        'function': linear_model,
        'num_inputs': 3,
        'num_outputs': 5,
        'var_mins': [-1.0]*3,
        'var_maxs': [1.0]*3,
        'var_types': [InputType.FLOAT]*3,
        'categories_list': [],
        'truth_case': [0.5]*3,
        'initial_guess': [0.0]*3,
        'objective_types': [ObjectiveType.PERCENT]*5,
        'minimum_bounds': [-0.1]*5,
        'maximum_bounds': [0.1]*5,
        'maximum_l1_norm': 0.0,
    },
    'quadratic_medium': {
        'function': quadratic_model,
        'num_inputs': 3,
        'num_outputs': 3,
        'var_mins': [-1.0]*3,
        'var_maxs': [1.0]*3,
        'var_types': [InputType.FLOAT]*3,
        'categories_list': [],
        'truth_case': [0.25]*3,
        'initial_guess': [0.0]*3,
        'objective_types': [ObjectiveType.PERCENT]*3,
        'minimum_bounds': [-5.0]*3,
        'maximum_bounds': [5.0]*3,
        'maximum_l1_norm': 0.0,
    },
    'cubic_large': {
        'function': cubic_model,
        'num_inputs': 4,
        'num_outputs': 4,
        'var_mins': [-1.0]*4,
        'var_maxs': [1.0]*4,
        'var_types': [InputType.FLOAT]*4,
        'categories_list': [],
        'truth_case': [0.2]*4,
        'initial_guess': [0.0]*4,
        'objective_types': [ObjectiveType.PERCENT]*4,
        'minimum_bounds': [-5.0]*4,
        'maximum_bounds': [5.0]*4,
        'maximum_l1_norm': 0.0,
    },
    'nonlinear1_medium': {
        'function': nonlinear_model1,
        'num_inputs': 4,
        'num_outputs': 3,
        'var_mins': [-1.0]*4,
        'var_maxs': [1.0]*4,
        'var_types': [InputType.FLOAT]*4,
        'categories_list': [],
        'truth_case': [0.25]*4,
        'initial_guess': [0.0]*4,
        'objective_types': [ObjectiveType.PERCENT]*3,
        'minimum_bounds': [-0.1]*3,
        'maximum_bounds': [0.1]*3,
        'maximum_l1_norm': 0.0,
    },
    'nonlinear2_large': {
        'function': nonlinear_model2,
        'num_inputs': 5,
        'num_outputs': 4,
        'var_mins': [-1.0]*5,
        'var_maxs': [1.0]*5,
        'var_types': [InputType.FLOAT]*5,
        'categories_list': [],
        'truth_case': [0.15]*5,
        'initial_guess': [0.0]*5,
        'objective_types': [ObjectiveType.PERCENT]*4,
        'minimum_bounds': [-0.1]*4,
        'maximum_bounds': [0.1]*4,
        'maximum_l1_norm': 0.0,
    },
    'java_test': {
        'function': JavaTestFunction,
        'num_inputs': 3,
        'num_outputs': 9,
        'var_mins': [0.3]*3,
        'var_maxs': [0.5]*3,
        'var_types': [InputType.FLOAT]*3,
        'categories_list': [],
        'truth_case': [0.4321, 0.321, 0.415],
        'initial_guess': [0.4]*3,
        'objective_types': [ObjectiveType.PERCENT]*9,
        'minimum_bounds': [-0.1]*9,
        'maximum_bounds': [0.1]*9,
        'maximum_l1_norm': 0.0,
    },
    'simple_test': {
        'function': SimpleTestFunction,
        'num_inputs': 3,
        'num_outputs': 4,
        'var_mins': [0.0]*3,
        'var_maxs': [10.0]*3,
        'var_types': [InputType.FLOAT]*3,
        'categories_list': [],
        'truth_case': [5.4321]*3,
        'initial_guess': [5.0]*3,
        'objective_types': [ObjectiveType.VALUE]*4,
        'minimum_bounds': [-25.0]*4,
        'maximum_bounds': [25.0]*4,
        'maximum_l1_norm': 0.0,
    },
    'nonlinear_test': {
        'function': NonlinearTestFunction,
        'num_inputs': 3,
        'num_outputs': 4,
        'var_mins': [0.1]*3,
        'var_maxs': [10.0]*3,
        'var_types': [InputType.FLOAT]*3,
        'categories_list': [],
        'truth_case': [5.4321]*3,
        'initial_guess': [5.0]*3,
        'objective_types': [ObjectiveType.PERCENT]*4,
        'minimum_bounds': [-5.0]*4,
        'maximum_bounds': [5.0]*4,
        'maximum_l1_norm': 0.0,
    },
    'integer_test': {
        'function': IntegerTestFunction,
        'num_inputs': 2,
        'num_outputs': 9,
        'var_mins': [0.0, 0],
        'var_maxs': [10.0, 7],
        'var_types': [InputType.FLOAT, InputType.INTEGER],
        'categories_list': [],
        'truth_case': [5.4321, 4],
        'initial_guess': [6.21, 2],
        'objective_types': [ObjectiveType.PERCENT]*9,
        'minimum_bounds': [-0.1]*9,
        'maximum_bounds': [0.1]*9,
        'maximum_l1_norm': 0.0,
    },
    'logical_test': {
        'function': LogicalTestFunction,
        'num_inputs': 2,
        'num_outputs': 9,
        'var_mins': [0.0, 0],
        'var_maxs': [10.0, 1],
        'var_types': [InputType.FLOAT, InputType.BOOLEAN],
        'categories_list': [],
        'truth_case': [5.4321, 1],
        'initial_guess': [6.21, 0],
        'objective_types': [ObjectiveType.PERCENT]*9,
        'minimum_bounds': [-0.1]*9,
        'maximum_bounds': [0.1]*9,
        'maximum_l1_norm': 0.0,
    },
    'categorical': {
        'function': CategoricalTestFunction,
        'num_inputs': 3,
        'num_outputs': 20,
        'var_mins': [0.0, 0.0, 1],
        'var_maxs': [10.0, 10.0, 4],
        'var_types': [
            InputType.FLOAT,
            InputType.FLOAT,
            InputType.CATEGORY
        ],
        'categories_list': ['cat','dog','fish','mouse'],
        'truth_case': [5.1, 4.9, 3],
        'initial_guess': [5.0, 5.0, 3],
        'objective_types': [ObjectiveType.PERCENT]*20,
        'minimum_bounds': [-25.0]*20,
        'maximum_bounds': [25.0]*20,
        'maximum_l1_norm': 0.0,
    },
    'complex': {
        'function': ComplexFunction,
        'num_inputs': 5,
        'num_outputs': 10,
        'var_mins': [4.0]*5,
        'var_maxs': [5.0]*5,
        'var_types': [InputType.FLOAT]*5,
        'categories_list': [],
        'truth_case': [4.5, 4.4, 4.3, 4.2, 4.1],
        'initial_guess': [1.0]*5,
        'objective_types': [ObjectiveType.PERCENT]*10,
        'minimum_bounds': [-5.0]*10,
        'maximum_bounds': [5.0]*10,
        'maximum_l1_norm': 0.0,
    },
    'mixed_input_types': {
        'function': MixedInputTypeFunction,
        'num_inputs': 5,
        'num_outputs': 15,
        'var_mins': [-15.0, 0, 30.0, 1, 0],
        'var_maxs': [-0.01, 300, 50.0, 25, 1],
        'var_types': [
            InputType.FLOAT,
            InputType.INTEGER,
            InputType.FLOAT,
            InputType.INTEGER,
            InputType.BOOLEAN
        ],
        'categories_list': [],
        'truth_case': [-1.2345, 250, 32.0, 19, 1],
        'initial_guess': [-5.0, 150, 40.0, 12, 1],
        'objective_types': [ObjectiveType.PERCENT]*15,
        'minimum_bounds': [-5.0]*15,
        'maximum_bounds': [5.0]*15,
        'maximum_l1_norm': 0.0,
    },
}

@pytest.mark.parametrize("test_name,config", TEST_CONFIGS.items())
def test_optimization(test_name: str, config: Dict[str, Any]):
    """
    Parametrized test that runs each test configuration using the web SDK.
    """
    MAX_ITERATIONS = 40
    MODEL_NAME = f"WebSDK_test_{test_name}"
    
    # Convert variable types to web SDK format
    input_types = config['var_types']
    objective_types = config['objective_types']
    
    # Initialize function with proper parameters
    #test_function = config['function']
    #if 'm' in test_function.__code__.co_varnames:
    #    test_function = lambda x, f=test_function: f(x, m=config['num_outputs'], n=config['num_inputs'])
    # Initialize function with proper parameters
    test_function = config['function']
    if 'm' in test_function.__code__.co_varnames:
        test_function = lambda x, f=test_function: f(x, m=config['num_outputs'], n=config['num_inputs'], seed=43)
    
    # Calculate truth case outputs
    truth_outputs = test_function(config['truth_case'])
    initial_outputs = test_function(config['initial_guess'])
    
    try:
        # Initialize client
        client = Client(debug=True)
        logger.info(f"Starting test: {test_name}")
        
        # Create model
        model = client.execute_request(CreateModel(
        name=MODEL_NAME,
        description=f"Test optimization model for algorithm: {test_name}"
        ))
        
        # Create project
        project = client.execute_request(CreateProject(
            model_id=model.id,
            name=f"{MODEL_NAME}_Project",
            input_count=config['num_inputs'],
            minimums=config['var_mins'],
            maximums=config['var_maxs'],
            input_types=input_types,
            categories=config['categories_list']
        ))
        
        # Get and evaluate training cases
        input_cases = project.input_cases
        output_cases = [test_function(case) for case in input_cases]
        
        # Load output cases and verify response
        trial = client.execute_request(LoadOutputCases(
            project_id=project.id,
            output_count=config['num_outputs'],
            output_cases=output_cases
        ))
        
        # Verify trial has required properties
        assert trial.case_count == len(output_cases), "Trial case count mismatch"
        assert trial.number >= 1, "Trial number should be at least 1"
        
        # Initialize inverse optimization
        objective = client.execute_request(LoadObjectives(
            trial_id=trial.id,
            objectives=truth_outputs,
            objective_types=objective_types,
            initial_input=config['initial_guess'],
            initial_output=initial_outputs,
            minimum_bounds=config['minimum_bounds'],
            maximum_bounds=config['maximum_bounds'],
            desired_l1_norm=config['maximum_l1_norm']
        ))
        
        for iteration in range(MAX_ITERATIONS):
            # Get next suggestion
            inverse = client.execute_request(SuggestInverse(
                objective_id=objective.id
            ))
            
            if inverse.satisfied_at or inverse.should_stop():
                satisfied_or_stopped = True
                break
                
            # Evaluate suggestion
            next_output = test_function(inverse.input)

            # In your test function, after evaluating next_output:
            logger.info("Current solution details:")
            logger.info(f"  Input: {[f'{x:.4f}' for x in inverse.input]}")
            logger.info(f"  Output: {[f'{x:.4f}' for x in next_output]}")
            logger.info(f"  Target: {[f'{x:.4f}' for x in truth_outputs]}")
            logger.info(f"  Suggest Time: {inverse.suggest_time}ns")
            logger.info(f"  Compute Time: {inverse.compute_time}ns")

            # Verify timing information
            verify_inverse_timing(inverse)

            # Add detailed result logging
            if inverse.results:
                for i, result in enumerate(inverse.results):
                    logger.info(f"  Objective {i}:")
                    logger.info(f"    Type: {result.get('type')}")
                    logger.info(f"    Error: {result.get('error'):.6f}")
                    logger.info(f"    Satisfied: {result.get('satisfied')}")
                    logger.info(f"    Detail: {result.get('detail')}")
                
            # Load results
            inverse = client.execute_request(LoadInversedOutput(
                inverse_id=inverse.id,
                output=next_output
            ))
            
            if inverse.should_stop():
                break
                
        # Verify results
        #assert satisfied_or_stopped is not None, "No solution found"
        
        # Check if solution satisfies objectives
        if inverse.satisfied_at:
            logger.info(f"Test {test_name} succeeded - All objectives satisfied")
            assert True
        else:
            satisfaction_status = inverse.get_satisfaction_status()
            result_details = inverse.get_result_details()
            
            # Log detailed results for debugging
            logger.error(f"Test {test_name} failed - Not all objectives satisfied")
            for i, (satisfied, detail) in enumerate(zip(satisfaction_status, result_details)):
                logger.error(f"Objective {i}: {'✓' if satisfied else '✗'} - {detail}")
            
            assert False, f"Test {test_name} failed to satisfy all objectives"
            
    finally:
        if 'client' in locals():
            client.http_client.close()