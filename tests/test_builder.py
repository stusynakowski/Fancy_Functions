import pytest
from uuid import UUID
from src.fancy_core.builder import WorkflowBuilder
from src.fancy_core.registry import registry
from src.fancy_core.functions import FancyFunction
from src.fancy_core.workflow import Workflow

# Setup some dummy functions for testing
def func_add(a, b):
    return a + b

def func_str_len(text):
    return len(text)

@pytest.fixture(autouse=True)
def setup_registry():
    """Register dummy functions before each test"""
    registry.clear()
    
    f1 = FancyFunction(slug="add", name="Add", input_contract={"a":"int", "b":"int"}, output_contract={"return":"int"})
    f1.set_executable(func_add)
    registry.register(f1)
    
    f2 = FancyFunction(slug="len", name="Length", input_contract={"text":"str"}, output_contract={"return":"int"})
    f2.set_executable(func_str_len)
    registry.register(f2)
    
    yield
    registry.clear()

def test_builder_initialization():
    builder = WorkflowBuilder("Test Workflow")
    assert builder.workflow.name == "Test Workflow"
    assert len(builder.workflow.steps) == 0

def test_builder_add_step_simple():
    builder = WorkflowBuilder("Simple")
    
    # Step 1: Add (using static config only for now? No, inputs map to cells.)
    # We don't have input cells yet. 
    # Usually Step 0 is some Load or strictly Config step.
    # Let's say 'add' takes config for this test or we simulate an input from 'unknown' source?
    # Builder requires inputs to be mapped to *something*.
    # If we want a 'root' step, we usually use config or an empty input step.
    
    # Let's verify we can add a step with just config
    step_id = builder.add_step("add", config={"a": 1, "b": 2}, output_alias="result")
    
    assert isinstance(step_id, UUID)
    assert len(builder.workflow.steps) == 1
    assert "result" in builder.vars
    assert builder.vars["result"] == step_id

def test_builder_chaining():
    builder = WorkflowBuilder("Chain")
    
    # Step 1: 5 + 5 = 10
    step1_id = builder.add_step("add", config={"a": 5, "b": 5}, output_alias="sum1")
    
    # Step 2: len("hello") = 5 (using config)
    # We want to chain. Let's pretend 'add' takes one input from previous.
    # Our 'add' func signature is (a, b). 
    # We can wire 'a' to 'sum1' and 'b' to static 10.
    
    step2_id = builder.add_step("add", 
                                inputs={"a": "sum1"}, 
                                config={"b": 10}, 
                                output_alias="final")
    
    assert len(builder.workflow.steps) == 2
    step2 = builder.workflow.steps[1]
    
    # Check wiring
    assert step2.inputs["a"] == step1_id
    assert step2.config["b"] == 10

def test_builder_invalid_function():
    builder = WorkflowBuilder("Invalid")
    with pytest.raises(ValueError, match="not found in registry"):
        builder.add_step("missing_func")

def test_builder_invalid_alias():
    builder = WorkflowBuilder("Bad Alias")
    with pytest.raises(ValueError, match="not defined"):
        builder.add_step("add", inputs={"a": "non_existent_var"})

def test_builder_serialization():
    builder = WorkflowBuilder("Serialize Me")
    builder.add_step("add", config={"a": 1, "b": 2}, output_alias="res")
    
    json_str = builder.export_json()
    assert "Serialize Me" in json_str
    assert "add" in json_str
    
    # Reconstruct
    wf_loaded = Workflow.from_json(json_str)
    assert wf_loaded.name == "Serialize Me"
    assert len(wf_loaded.steps) == 1
    assert wf_loaded.steps[0].function_slug == "add"

