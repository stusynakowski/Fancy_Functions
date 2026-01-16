import pytest
from typing import List

from fancy_core.decorators import step
from fancy_core.workflow import Workflow
from fancy_core.engine import Engine
from fancy_core.store import InMemoryStore
from fancy_core.cells import FancyCell
from fancy_core.registry import registry

# -------------------------------------------------------------------------
# Define our "Fancy Functions"
# -------------------------------------------------------------------------

@step
def filter_evens(nums: List[int]) -> List[int]:
    """Filters a list to keep only even numbers."""
    return [n for n in nums if n % 2 == 0]

@step
def square_numbers(nums: List[int]) -> List[int]:
    """Squares every number in the list."""
    return [n * n for n in nums]

@step
def sum_numbers(nums: List[int]) -> int:
    """Calculates the sum of the list."""
    return sum(nums)

# -------------------------------------------------------------------------
# Test the Pipeline
# -------------------------------------------------------------------------

def test_number_processing_pipeline():
    """
    Goal: Take [1, 2, 3, 4, 5] -> Filter Evens -> Square -> Sum
    Logic: 
      [1, 2, 3, 4, 5] 
      -> [2, 4] 
      -> [4, 16] 
      -> 20
    """
    
    # 1. Setup Data
    user_input = [1, 2, 3, 4, 5]
    input_cell = FancyCell.create_value(user_input, alias="Raw Numbers")
    
    # 2. Build Workflow (The "Happy Path" construction)
    # Notice we chain the calls just like normal python, but we get 'wirings' back.
    wiring_1 = filter_evens(input_cell)
    wiring_2 = square_numbers(wiring_1)
    wiring_3 = sum_numbers(wiring_2)
    
    # 3. Assemble the Workflow definition
    workflow = Workflow(name="Number Cruncher")
    workflow.add_step(wiring_1.step)
    workflow.add_step(wiring_2.step)
    workflow.add_step(wiring_3.step)
    
    # 4. Execute
    store = InMemoryStore()
    
    # We must register the functions (The decorator does this automatically at import time,
    # but in a clean test environment we might need to ensure registry is active. 
    # Here, importing the module runs the decorators.)
    
    engine = Engine(store)
    
    # Run!
    # Note: We pass the actual input_cell so it's resolved by ID.
    context = engine.run(workflow, initial_cells=[input_cell])
    
    # 5. Verify Results
    
    # The final result is in the output cell of the last step
    final_cell_id = wiring_3.outputs.id
    final_cell = context[final_cell_id]
    
    result = store.resolve(final_cell)
    
    assert result == 20
    print(f"\nPipeline Result: {result}")
