import pytest
from uuid import uuid4
from src.fancy_core.workflow import Workflow
from src.fancy_core.engine import Engine
from src.fancy_core.store import InMemoryStore
from src.fancy_core.cells import FancyCell
from src.fancy_core.functions import FancyFunction
from src.fancy_core.registry import registry
from src.fancy_core.workflow_step import WorkflowStep

# -------------------------------------------------------------------------
# Setup / Helpers
# -------------------------------------------------------------------------

def dummy_add(a: int, b: int) -> int:
    return a + b

def dummy_prefix(text: str, prefix: str = "Hello ") -> str:
    return prefix + text

@pytest.fixture
def clean_registry():
    registry.clear()
    
    # Register dummy functions
    f1 = FancyFunction(
        slug="math.add",
        name="Add Integers",
        input_contract={"a": "int", "b": "int"},
        output_contract={"return": "int"}
    )
    f1.set_executable(dummy_add)
    registry.register(f1)
    
    f2 = FancyFunction(
        slug="str.prefix",
        name="Prefix String",
        input_contract={"text": "str"},
        output_contract={"return": "str"}
    )
    f2.set_executable(dummy_prefix)
    registry.register(f2)
    
    yield registry
    registry.clear()

# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------

def test_engine_simple_flow(clean_registry):
    # 1. Setup Store and Input Data
    store = InMemoryStore()
    
    # Create initial inputs
    cell_a = store.put(10, "input_a")
    cell_b = store.put(20, "input_b")
    
    # 2. Define Workflow
    # Step 1: Add a + b -> c
    # We need to manually wire it since we don't have the decorator wiring logic yet (Part of Milestone 2)
    
    cell_c_id = uuid4()
    
    step1 = WorkflowStep(
        function_slug="math.add",
        inputs={"a": cell_a.id, "b": cell_b.id},
        outputs={"return": cell_c_id}
    )
    
    workflow = Workflow(name="Test Math Flow")
    workflow.add_step(step1)
    
    # 3. Run Engine
    engine = Engine(store)
    context = engine.run(workflow, initial_cells=[cell_a, cell_b])
    
    # 4. Assert
    assert cell_c_id in context
    result_cell = context[cell_c_id]
    result_val = store.resolve(result_cell)
    
    assert result_val == 30
    assert result_cell.alias == "math.add::return"


def test_engine_chained_flow(clean_registry):
    """
    Step 1: 5 + 5 -> 10
    Step 2: "Hello " + str(10) -> "Hello 10" (Simulated by passing int to str func if python allows, or just use strings)
    Wait, dummy_prefix expects str. Python is dynamic, so 10 + "Hello " might fail or work depending on func: `prefix + text`. 
    "Hello " + 10 -> TypeError in Python.
    Let's stick to consistent types for this test or update dummy_prefix.
    """
    
    # Update dummy_prefix for robustness ? No, let's just do math chain
    # Step 1: 5 + 5 -> 10
    # Step 2: 10 + 20 -> 30
    
    store = InMemoryStore()
    cell_in_1 = store.put(5, "in_1")
    cell_in_2 = store.put(5, "in_2")
    cell_in_3 = store.put(20, "in_3") # For step 2
    
    cell_inter_id = uuid4()
    cell_final_id = uuid4()
    
    step1 = WorkflowStep(
        function_slug="math.add",
        inputs={"a": cell_in_1.id, "b": cell_in_2.id},
        outputs={"return": cell_inter_id} 
    )
    
    step2 = WorkflowStep(
        function_slug="math.add",
        inputs={"a": cell_inter_id, "b": cell_in_3.id},
        outputs={"return": cell_final_id}
    )
    
    wf = Workflow(name="Chain")
    wf.add_step(step1)
    wf.add_step(step2)
    
    engine = Engine(store)
    ctx = engine.run(wf, initial_cells=[cell_in_1, cell_in_2, cell_in_3])
    
    assert store.resolve(ctx[cell_final_id]) == 30

def test_engine_config_usage(clean_registry):
    store = InMemoryStore()
    cell_text = store.put("World", "text_in")
    cell_res_id = uuid4()
    
    # wiring: text comes from cell, prefix comes from config
    step = WorkflowStep(
        function_slug="str.prefix",
        inputs={"text": cell_text.id},
        config={"prefix": "So Fancy, "},
        outputs={"return": cell_res_id}
    )
    
    engine = Engine(store)
    ctx = engine.run(Workflow(name="Config Test", steps=[step]), initial_cells=[cell_text])
    
    assert store.resolve(ctx[cell_res_id]) == "So Fancy, World"
