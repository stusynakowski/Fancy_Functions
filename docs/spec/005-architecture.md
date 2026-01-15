# Architecture & Design

## Purpose
To provide a lightweight, extensible, and robust foundation for building data workflows that can be visually represented in the frontend and executed in a backend Python environment.

## Logic Flow

1.  **Definition Phase:**
    *   Developer defines Python functions (e.g., `clean_data(df, threshold)`).
    *   Functions are decorated with `@step_type` to register metadata (parameters, docs).

2.  **Composition Phase:**
    *   A `Workflow` object is instantiated.
    *   Specific `StepInstance`s are created from `StepType`s with concrete configuration values (e.g., `threshold=0.5`).
    *   Steps are added to the Workflow.

3.  **Serialization Phase (Optional):**
    *   Workflow state is serialized to JSON to be sent to the Frontend.
    *   Frontend edits the JSON and sends it back.
    *   Library deserializes JSON back into a `Workflow` object.

4.  **Execution Phase:**
    *   `WorkflowRunner` takes a `Workflow` and a `RuntimeContext`.
    *   It iterates through steps sequentially.
    *   It resolves input references from the Context.
    *   Executes the step logic.
    *   Stores output references back to the Context.

## Core Components

### 1. The Registry (`StepRegistry`)
A singleton or module-level dictionary that maps string identifiers (e.g., `"clean_nulls"`) to actual Python callables or Step classes.

### 2. The Step Definition (`StepType`)
Metadata about a registered operation.
*   `name`: Human readable name.
*   `slug`: Unique string ID.
*   `parameters`: Schema of expected configuration (using `pydantic` or `inspect`).
*   `input_type`: Expected data type for the primary input (e.g., `DataFrame`, `JSON`, `FileReference`).
*   `output_type`: Expected data type for the result.
*   `execution_mode`: How this logic is applied (e.g., `batch`, `streaming`, `row_iterative`).
*   `metadata`: Arbitrary dictionary for extra context (e.g., `{"requires_gpu": true, "category": "ml_inference"}`).


### 3. The Step Instance (`Step`)
A concrete unit in a workflow, conceptually similar to a configured Jupyter Notebook cell.
*   `step_type_id`: Reference to the definition.
*   `config`: Dictionary of argument values.
*   `execution_strategy`: Overrides or specifics on how to run (e.g., "distribute across 4 workers").
*   `state`: Pending/Running/Completed.

### 4. The Context (`RuntimeContext`)
A storage abstraction for the actual data.
*   Since the goal is to pass "References" (REQ-Data-001), this component acts as a Key-Value store.
*   `get(ref_id)` -> returns actual object (e.g., DataFrame).
*   `put(object)` -> stores object and returns new `ref_id`.

### 5. The Runner (`Engine`)
The engine that drives execution.
*   Handles exception catching.
*   Updates step status.
*   Manages logging.

## Data Models (Internal)

```python
class StepState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Step:
    id: str
    type_slug: str
    config: dict
    status: StepState = StepState.PENDING

@dataclass
class Workflow:
    id: str
    steps: List[Step]
```

## Key Technical Decisions
*   **Pydantic for Validation:** We will use Pydantic for serialization and schema validation to ensure JSON compatibility.
*   **Decorator Pattern:** Use decorators for easiest developer experience when adding new step types.
*   **Separation of Config and Data:** Config is JSON-serializable (parameters); Data is memory-bound (DataFrames in Context).
