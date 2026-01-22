# Fancy Functions (`fancy_core`)

**Logic over Logistics.**

`fancy_core` is a Python library for defining, serializing, and executing self-describing data workflows. It abstracts the "how" (data storage, serialization, pipeline orchestration) so developers can focus on the "what" (pure business logic).

## Core Concepts

The library is built on four atomic concepts:

1.  **Fancy Cells** (`src/fancy_core/cells.py`): The universal container for data. Whether it's a small integer or a 10TB dataset reference, it's wrapped in a Cell with a UUID and a Type ID.
2.  **Fancy Functions** (`src/fancy_core/functions.py`): Standard Python functions decorated with `@step`. They are self-describing, strictly typed, and serializable.
3.  **Workflows** (`src/fancy_core/workflow.py`): A linear sequence of steps. To the user, it is a simple list of actions; to the system, it is a graph of data dependencies.
4.  **The Engine** (`src/fancy_core/engine.py`): The runtime execution driver that handles input resolution, function execution, and output persistence.

## Installation

This project is managed with standard Python tooling.

```bash
pip install -e .
```

## Quick Start

Here is a complete example showing how to define logic, wire it into a pipeline, and execute it.

```python
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
```

## Architecture

*   **Logic Definition**: Found in `src/fancy_core/decorators.py`. The decorator factory pattern separates distinct phases: *Definition Time* (Building the graph) vs *Run Time* (Executing the code).
*   **Data Physics**: Found in `src/fancy_core/store.py`. The `DatumStore` abstract base class allows swapping the storage backend (Memory, S3, SQL) without changing the business logic steps.

## Development

This repository uses a phase-based development workflow. See `docs/context.md` for details on the current phase and development rules.

**Running Tests:**
```bash
pytest
```
