# Workflow Construction & Serialization Methods

This document outlines how to construct workflows explicitly for the purpose of serialization, decoupling the **Definition** (Blueprint) from the **Execution**.

## Core Concept: The Builder Pattern

We move away from "running" Python functions to "declaring" steps. We use the `FunctionRegistry` to validate that functions exist, but we do not execute them during the construction phase.

### 1. The Registry (The Menu)
The `FunctionRegistry` (already exists in `src/fancy_core/registry.py`) holds the definitions of available tools. It knows the inputs, outputs, and the Python callable.

### 2. The Workflow Definition (The Blueprint)
The `Workflow` object (in `src/fancy_core/workflow.py`) is simply a container for `WorkflowSteps`. Because it is a Pydantic model, it is natively serializable.

### 3. The Builder Interface (The Architect)
This is the new piece. It allows a user to "write python" that actually just builds the graph.

```python
from src.fancy_core.workflow import Workflow
from src.fancy_core.workflow_step import WorkflowStep
from src.fancy_core.registry import registry
from uuid import uuid4

class WorkflowBuilder:
    def __init__(self, name: str):
        self.workflow = Workflow(name=name)
        # Keep track of active cells (virtual outputs)
        # Map: alias/variable_name -> Cell UUID
        self.vars = {} 

    def add_step(self, function_slug: str, inputs: dict, config: dict, output_alias: str = None):
        """
        Adds a step to the blueprint.
        
        :param function_slug: Name of the function in registry (e.g., 'add_numbers')
        :param inputs: Dict mapping arg_name -> input_cell_uuid
        :param config: Static values (literals) to pass to the function
        :param output_alias: Friendly name for the output (optional)
        """
        # 1. Validation: Check if function exists
        func_def = registry.get(function_slug)
        if not func_def:
            raise ValueError(f"Function '{function_slug}' not found in registry.")

        # 2. Generate IDs
        step_id = uuid4()
        output_id = uuid4()

        # 3. Create Step Definition
        step = WorkflowStep(
            step_id=step_id,
            function_slug=function_slug,
            config=config,
            inputs=inputs, 
            outputs={"return": output_id} # Assuming single output for simplicity
        )
        
        self.workflow.add_step(step)
        
        # 4. Return the Output ID (Reference for next steps)
        if output_alias:
            self.vars[output_alias] = output_id
            
        return output_id

    def export(self) -> str:
        """Serializes the constructed workflow"""
        return self.workflow.model_dump_json(indent=2)
```

## Example Usage

This allows you to scripting the creation of a serializable file without running any actual logic.

```python
# 1. Instantiate Builder
builder = WorkflowBuilder("Data Mining Pipeline")

# 2. Define Steps (Note: We pass UUIDs, not values, for inputs)

# Step A: Scrape URL
# config={'url': ...} are static values. inputs={} because it starts the chain.
url_output_id = builder.add_step(
    function_slug="scrape_url", 
    inputs={}, 
    config={"url": "https://example.com"}
)

# Step B: Parse HTML
# inputs={'html': url_output_id} links Step A to Step B
parse_output_id = builder.add_step(
    function_slug="parse_html",
    inputs={"html": url_output_id},
    config={"parser": "lxml"}
)

# Step C: Save to Disk
builder.add_step(
    function_slug="save_file",
    inputs={"data": parse_output_id},
    config={"filename": "output.txt"}
)

# 3. Serialize
json_output = builder.export()

# 4. Save to file
with open("pipeline.json", "w") as f:
    f.write(json_output)
```

## Advantages of this Approach

1.  **Safety:** You can define a workflow on a machine that doesn't even have the libraries installed to *run* the workflow (e.g. define a GPU workflow on a laptop).
2.  **Portability:** The resulting JSON file is language-agnostic.
3.  **Versioning:** The JSON file describes exactly which function slugs are used, making it easier to manage version upgrades.

## How to execute later?

You load the JSON, deserialize it back into a `Workflow` object, and pass it to your `Engine`.

```python
# On the execution server...
from src.fancy_core.workflow import Workflow
from src.fancy_core.engine import Engine

# 1. Load context
with open("pipeline.json", "r") as f:
    workflow = Workflow.model_validate_json(f.read())

# 2. Execute
engine = Engine()
engine.run(workflow)
```
