import pytest
from uuid import UUID
from src.fancy_core.cells import FancyCell, StorageKind
from src.fancy_core.decorators import step, StepWiring
from src.fancy_core.workflow_step import WorkflowStep

def test_workflow_step_creation():
    # Define a simple function
    @step
    def add(a: int, b: int) -> int:
        return a + b

    # Create dummy input cells
    cell_a = FancyCell(alias="A", value=10, type_hint='int', storage_kind=StorageKind.VALUE)
    cell_b = FancyCell(alias="B", value=20, type_hint='int', storage_kind=StorageKind.VALUE)

    # "Call" the function to get the wiring
    # Case 1: All inputs are cells
    wiring = add(a=cell_a, b=cell_b)

    # Assertions
    assert isinstance(wiring, StepWiring)
    assert isinstance(wiring.step, WorkflowStep)
    assert isinstance(wiring.outputs, FancyCell)
    
    # Check outputs are PENDING
    assert wiring.outputs.storage_kind == StorageKind.PENDING
    
    # Check wiring connections
    assert wiring.step.function_slug == "add"
    assert wiring.step.inputs["a"] == cell_a.id
    assert wiring.step.inputs["b"] == cell_b.id
    
    # Check output mapping
    assert "return" in wiring.step.outputs
    assert wiring.step.outputs["return"] == wiring.outputs.id

def test_workflow_step_chaining():
    @step
    def increment(x: int) -> int:
        return x + 1
        
    cell_start = FancyCell(alias="Start", value=1, type_hint='int', storage_kind=StorageKind.VALUE)
    
    # Step 1
    wiring1 = increment(x=cell_start)
    assert wiring1.outputs.storage_kind == StorageKind.PENDING
    
    # Step 2 (using output of Step 1)
    # The factory logic in decorators.py accepts StepWiring OR FancyCell or raw value.
    # If we pass wiring1 (StepWiring), the decorator logic handles it:
    # elif isinstance(value, StepWiring):
    #     if isinstance(value.outputs, FancyCell): ...
    wiring2 = increment(x=wiring1)
    
    # Check inputs of Step 2 point to output of Step 1
    assert wiring2.step.inputs["x"] == wiring1.outputs.id

def test_workflow_step_mixed_args():
    @step
    def scale(data: int, factor: int) -> int:
        return data * factor
        
    cell_data = FancyCell(alias="Data", value=100, type_hint='int', storage_kind=StorageKind.VALUE)
    
    # Call with one cell and one static config
    wiring = scale(data=cell_data, factor=5)
    
    assert wiring.step.inputs["data"] == cell_data.id
    assert wiring.step.config["factor"] == 5
    assert "factor" not in wiring.step.inputs
