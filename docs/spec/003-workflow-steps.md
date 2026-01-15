# Specification: Workflow Steps

## 1. Definition
A **Workflow Step** (or simply "Step") is a configured instance of a `FancyFunction` placed within a specific execution context. It bridges the static "Tool" (Function) with specific "Cells" (Data).

**Key Concept:** A Step does not just run a function; it maps *existing* Cell IDs to the function's arguments.

## 2. Configuration vs. Wiring
A Step performs two types of parameterization:
1.  **Configuration (Static):** Parameters that are known at design time and typically set by the user (e.g., `threshold=0.5`, `method="inner"`). These are stored in the `config` dictionary.
2.  **Wiring (Dynamic):** Parameter values that come from the output of previous steps (Cells). These are mapped in the `inputs` dictionary.

## 3. Schema (Level 2)

```python
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel

class WorkflowStep(BaseModel):
    step_id: UUID
    function_slug: str          # Reference to the FancyFunction to use
    
    # Configuration (Static Parameters)
    # Passed directly to the function's non-data arguments
    config: Dict[str, Any]      
    
    # Data Mapping (Wiring)
    # Maps Function Argument Names -> Cell IDs available in context
    inputs: Dict[str, UUID]     
```
