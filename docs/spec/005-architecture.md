# Architecture & Design

## Purpose
To provide a lightweight, extensible, and robust foundation for building data workflows that can be visually represented in the frontend and executed in a backend Python environment.

## Logic Flow

1.  **Definition Phase:**
    *   Developer defines Python functions (e.g., `clean_data(df, threshold)`).
    *   Functions are decorated with `@step` to register metadata and constraints (Contracts).

2.  **Composition Phase:**
    *   **Instantiation:** A user "calls" the decorated function, passing in `FancyCell` references as arguments.
    *   **Orchestration:** This call returns a `WorkflowStep` object (not a result), which captures the wiring (Input Cells -> Logic).
    *   **Sequencing:** Steps are added to a `Workflow` list, effectively squashing the DAG into a linear story.

3.  **Serialization Phase (Optional):**
    *   Workflow state (Logic + Wiring) is serialized to JSON.
    *   This JSON can be sent to a UI, stored, or passed to a distributed scheduler.

4.  **Execution Phase (The Engine):**
    *   The Engine accepts the Workflow and a Context (the Cell Store).
    *   It iterates through the steps strictly.
    *   It resolves Cell IDs to actual objects (loading from memory or reference).
    *   It executes the function logic.
    *   It wraps results in new `FancyCells` and registers them in the Context.

## Core Components

### 1. The Registry (`FunctionRegistry`)
A mechanism to map `slugs` (e.g., `"clean_nulls"`) back to the specific Python executable.

### 2. The Fancy Function (`FancyFunction`)
The metadata wrapper around the user's code.
*   `slug`: Unique identifier.
*   `contracts`: Input/Output type definitions.
*   `traits`: Execution hints (e.g., `batch`, `row_wise`).

### 3. The Step (`WorkflowStep`)
The configured unit of work.
*   `function_slug`: "Which tool?"
*   `wiring`: "Which cells go into which arguments?"
*   `config`: "What are the static parameters?"

### 4. The Store (`DatumStore`)
The component responsible for the physics of data.
*   Abstracts *where* data lives (Memory, Local Disk, S3).
*   `resolve(cell_id) -> Object`
*   `persist(object) -> URI`

### 5. The Engine (`Orchestrator`)
The runtime driver.
*   Manages the sequence.
*   Handles error boundaries.
*   Updates execution status.

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
