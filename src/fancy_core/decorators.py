import inspect
from functools import wraps
from typing import Callable, Any, Dict, Union, Optional
from uuid import UUID

from .functions import FancyFunction
from .registry import registry
from .workflow_step import WorkflowStep
from .cells import FancyCell, StorageKind

class StepWiring:
    """
    Interim object returned by calling a @step decorated function.
    Holds the Step definition and the Output Cell(s) it produces.
    """
    def __init__(self, step: WorkflowStep, outputs: Any):
        self.step = step
        self.outputs = outputs

def step(func: Callable):
    """
    Decorator to convert a raw function into a FancyFunction and register it.
    When called, it returns a StepWiring object (Definition of logic), NOT the result.
    """
    # 1. Introspection
    sig = inspect.signature(func)
    slug = func.__name__
    
    input_contract: Dict[str, str] = {}
    for name, param in sig.parameters.items():
        if name == "context": continue 
        annotation = param.annotation
        type_name = str(annotation) if annotation != inspect.Parameter.empty else "Any"
        input_contract[name] = type_name
            
    output_contract: Dict[str, str] = {}
    ret = sig.return_annotation
    if ret != inspect.Signature.empty:
        output_contract["return"] = str(ret)
    
    # 2. Register Metadata
    ff = FancyFunction(
        slug=slug,
        name=slug,
        description=func.__doc__ or "",
        input_contract=input_contract,
        output_contract=output_contract,
        operation_type="Scalar" # Default
    )
    ff.set_executable(func)
    registry.register(ff)
    
    # Tag the function so outer decorators can find the metadata
    func.fancy_function_slug = slug
    
    @wraps(func)
    def factory(*args, **kwargs) -> StepWiring:
        # 3. Wrapping Logic (The Factory)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        step_inputs: Dict[str, UUID] = {}
        step_config: Dict[str, Any] = {}
        
        for name, value in bound.arguments.items():
            # Scenario A: Passed a FancyCell directly
            if isinstance(value, FancyCell):
                step_inputs[name] = value.id
                
            # Scenario B: Passed a StepWiring (Output of previous step)
            elif isinstance(value, StepWiring):
                if isinstance(value.outputs, FancyCell):
                    step_inputs[name] = value.outputs.id
                else:
                    # Generic handling for multi-output: pick default or fail
                    raise ValueError(f"Ambiguous wiring: Step {slug} received multi-output result for arg '{name}'.")
                    
            # Scenario C: Just a static value (Config)
            else:
                step_config[name] = value
                
        # Create Output Placeholder(s)
        output_cell = FancyCell(
            alias=f"{slug}_out",
            type_hint=output_contract.get("return", "Any"),
            storage_kind=StorageKind.PENDING,
            value=None
        )

        # Create the Step definition
        new_step = WorkflowStep(
            function_slug=slug,
            config=step_config,
            inputs=step_inputs,
            outputs={"return": output_cell.id}
        )
        
        return StepWiring(step=new_step, outputs=output_cell)

    return factory

# ==========================================
# Functional Decorators (Data Geometry)
# ==========================================

def apply(func: Callable) -> Callable:
    """
    Scalar (1 -> 1)
    Identity decorator for scalar functions.
    Example: =A1+1
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def vector_reduce(func: Callable) -> Callable:
    """
    Reduction (N -> 1)
    Ensures input is strictly iterable for reduction logic.
    (Aliased as @reduce for friendly usage, but named vector_reduce to avoid conflicts)
    Example: =SUM(A:A)
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "Reduction"

    @wraps(func)
    def wrapper(data, *args, **kwargs):
        if not isinstance(data, (list, tuple)):
            data = [data]
        return func(data, *args, **kwargs)
    return wrapper
# Alias
reduce = vector_reduce

def expand(func: Callable) -> Callable:
    """
    Generator (1 -> N)
    Wraps logic to ensure the output is always a materialized list.
    Example: =SEQUENCE(10)
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "Generator"

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return list(result)
    return wrapper

def vectorize(func: Callable) -> Callable:
    """
    Map (N -> N)
    Transforms a 1->1 scalar function into an N->N map.
    Example: =A:A*2
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "Map"

    @wraps(func)
    def wrapper(data, *args, **kwargs):
        if isinstance(data, list):
            return [func(x, *args, **kwargs) for x in data]
        # Fallback for scalar input
        return func(data, *args, **kwargs)
    return wrapper

def vector_filter(func: Callable) -> Callable:
    """
    Relational (N -> M)
    Acts as a filter. The decorated function should return a Boolean.
    Input: List of N items.
    Result: List of M items (where M <= N) for which func(item) is True.
    Example: =FILTER(A:A,A:A>0)
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "Relational"

    @wraps(func)
    def wrapper(inputs, *args, **kwargs):
        # Assumes inputs is iterable
        return [x for x in inputs if func(x, *args, **kwargs)]
    return wrapper
# Alias
filter = vector_filter

def grid_apply(func: Callable) -> Callable:
    """
    Table Map (NxM -> NxM)
    Applies a scalar function to every cell in a 2D matrix (list of lists).
    Example: =A:C*2
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "TableMap"

    @wraps(func)
    def wrapper(matrix, *args, **kwargs):
        # Assumes matrix is List[List[Any]]
        return [
            [func(cell, *args, **kwargs) for cell in row]
            for row in matrix
        ]
    return wrapper

def summarize(func: Callable) -> Callable:
    """
    Aggregate (NxM -> 1)
    Flattens a matrix to a single list before applying a reduction logic.
    Example: =SUM(A:C)
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "Aggregate"

    @wraps(func)
    def wrapper(matrix, *args, **kwargs):
        # Flatten: [[1,2], [3,4]] -> [1,2,3,4]
        flat_list = [cell for row in matrix for cell in row]
        return func(flat_list, *args, **kwargs)
    return wrapper

def reshape(func: Callable) -> Callable:
    """
    Pivot (NxM -> KxL)
    Takes a 2D matrix, applies logic, expects a 2D matrix back.
    Example: =PIVOT(...)
    """
    if hasattr(func, "fancy_function_slug"):
        registry.get(func.fancy_function_slug).operation_type = "Pivot"

    @wraps(func)
    def wrapper(matrix, *args, **kwargs):
        result = func(matrix, *args, **kwargs)
        # Optional validation: Ensure result is List[List]
        return result
    return wrapper
