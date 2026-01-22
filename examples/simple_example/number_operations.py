from uuid import uuid4
from fancy_core.decorators import step
from fancy_core.workflow import Workflow
from fancy_core.engine import Engine
from fancy_core.store import InMemoryStore
from fancy_core.cells import FancyCell

# 1. Define Logic (The "Fancy Functions")
# The @step decorator handles introspection and registration.

@step
def filter_evens(nums: list[int]) -> list[int]:
    """Keeps only even numbers."""
    return [n for n in nums if n % 2 == 0]

@step
def square_numbers(nums: list[int]) -> list[int]:
    """Squares every number in the list."""
    return [n * n for n in nums]

@step
def sum_numbers(nums: list[int]) -> int:
    """Calculates the sum."""
    return sum(nums)

# 2. Setup Data Store
store = InMemoryStore()
user_input = [1, 2, 3, 4, 5]

# Put raw data into the store to get a FancyCell
input_cell = store.put(user_input, alias="Raw Numbers")

# 3. Define the Workflow wiring
# Calling the decorated function returns a `StepWiring` (definition), 
# NOT the result. We chain these wirings together.

wiring_1 = filter_evens(nums=input_cell)    # Input: Cell(Raw Numbers)
wiring_2 = square_numbers(nums=wiring_1)    # Input: Output of step 1
wiring_3 = sum_numbers(nums=wiring_2)       # Input: Output of step 2

# Assemble the definition
wf = Workflow(name="Number Cruncher")
wf.add_step(wiring_1.step)
wf.add_step(wiring_2.step)
wf.add_step(wiring_3.step)

# 4. Execute (The Engine)
print("Running Workflow...")
engine = Engine(store)

# The run method returns a context dictionary of {Cell_ID: FancyCell}
context = engine.run(wf, initial_cells=[input_cell])

# 5. Resolve Results
final_result_id = wiring_3.outputs.id
final_cell = context[final_result_id]
result_value = store.resolve(final_cell)

print(f"Result: {result_value}") 
# [1, 2, 3, 4, 5] -> [2, 4] -> [4, 16] -> 20