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
        output_contract=output_contract
    )
    ff.set_executable(func)
    registry.register(ff)
    
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
