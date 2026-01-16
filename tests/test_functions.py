import pytest
from fancy_core.functions import FancyFunction
from fancy_core.registry import registry
from fancy_core.decorators import step, StepWiring
from fancy_core.cells import FancyCell, StorageKind
from fancy_core.workflow_step import WorkflowStep

def test_registry_basics():
    registry.clear()
    
    @step
    def my_func(a: int, b: int) -> int:
        """Adds two numbers."""
        return a + b
        
    # Check registration
    ff = registry.get("my_func")
    assert ff is not None
    assert ff.slug == "my_func"
    assert "a" in ff.input_contract
    # Handle both <class 'int'> and int string representations
    assert "int" in str(ff.input_contract["a"])
    
def test_step_factory_wiring():
    registry.clear()
    
    @step
    def source(val: int) -> int:
        return val
        
    @step
    def process(data: int, factor: int) -> int:
        return data * factor
    
    # 1. Call source with Config
    step1_wiring = source(val=10)
    assert isinstance(step1_wiring, StepWiring)
    assert step1_wiring.step.function_slug == "source"
    assert step1_wiring.step.config["val"] == 10
    
    # 2. Call process with Wiring from step1
    step2_wiring = process(data=step1_wiring, factor=2)
    
    assert step2_wiring.step.function_slug == "process"
    # 'data' should be wired to step1's output
    assert step2_wiring.step.inputs["data"] == step1_wiring.outputs.id
    # 'factor' should be config
    assert step2_wiring.step.config["factor"] == 2
    
def test_direct_cell_wiring():
    registry.clear()
    
    @step
    def consumer(item: str):
        pass
        
    cell = FancyCell.create_value("Hello", "Greeting")
    wiring = consumer(item=cell)
    
    assert wiring.step.inputs["item"] == cell.id
