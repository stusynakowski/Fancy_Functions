# Specification: Workflows

## 1. Definition
A **Workflow** is a **strictly ordered sequence** of **Workflow Steps**. 

While the flow of *data* between steps effectively forms a Directed Acyclic Graph (DAG) (since Step 4 can use data from Step 1), the **Execution Interface** is purely linear.

*   **Design Goal:** To present the user with a simple, intelligible list of actions ("Do A, then B, then C") rather than a complex node graph.
*   **Encapsulation:** Any "branching" logic (like parallel processing, splitting, or merging) is either managed by the Engine via data availability or encapsulated within the logic of a complex Step.

## 2. Execution Logic
1.  The Workflow starts with a set of **Initial Cells** (Inputs) provided by the user or trigger.
2.  The Engine iterates through the `steps` list.
3.  For each Step:
    *   It resolves the `inputs` (Cell IDs) from the Context.
    *   It retrieves the `FancyFunction` matching the `function_slug`.
    *   It executes the function with the resolved inputs and `config`.
    *   It wraps the result in a new `FancyCell` (or multiple cells).
    *   It registers the new Cell(s) into the Context.
4.  The result is a traceable chain of Cells.

## 3. Schema (Level 3)

```python
from typing import List
from uuid import UUID
from pydantic import BaseModel
# Note: In actual implementation, recursive imports need handling
# from .workflow_step import WorkflowStep 

class Workflow(BaseModel):
    id: UUID
    name: str
    
    # The Blueprint
    # A linear sequence of steps to be executed
    steps: List['WorkflowStep'] 
```
