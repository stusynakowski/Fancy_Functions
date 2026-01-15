# Specification: Core Library Overview

## Scope
The Core Library is a pure Python package designed to define, serialize, and execute linear data processing workflows. It serves as the execution engine that mimics the behavior described in the frontend specifications of Simple Steps.

**In Scope:**
- **Step Abstraction:** Wrapping Python functions into serializable logical units ("Steps").
- **Workflow Management:** Composing Steps into linear sequences ("Workflows").
- **Serialization:** Converting Workflows and Steps to/from JSON, compatible with the frontend data model.
- **Local Execution:** Running worklows synchronously or asynchronously in a local Python environment.
- **State Management:** managing data references (inputs/outputs) passed between steps logic.

**Out of Scope:**
- **Distributed Execution Orchestration:** The core library executes workflows within a single process (local execution). However, it **provides all necessary metadata** (execution requirements, resource hints, cell references) to allow external systems (like Ray, Celery, or Kubernetes) to distribute the workload across multiple nodes.
- REST API / Network Transport (handled by a separate integration layer).
- Database persistence (this library handles in-memory or file-based usage).
- UI Rendering.

## Requirements

### Core Functional Requirements
- **REQ-CORE-001:** Users must be able to decorate generic Python functions to register them as available "Step Types".
- **REQ-CORE-002:** The library must allow instantiating a Step Type with specific configuration parameters (arguments) AND input/output data contract validation.
- **REQ-CORE-003:** Workflows must be strictly linear sequences (List[Step]).
- **REQ-CORE-004:** The library must execute a Workflow, passing the output of Step N as the input to Step N+1 (or via a shared context).
- **REQ-CORE-005:** execution must produce a serializable result object containing status and output references.
- **REQ-CORE-006:** The library must handle serialization of the Workflow state to JSON for frontend consumption.

### Data & State Requirements
- **REQ-DATA-001:** Data objects (e.g., pandas DataFrames) must be stored in a `RuntimeContext` and passed by reference ID, not by value, to the steps.
- **REQ-DATA-002:** The library must support saving intermediate artifacts (optional check-pointing).
- **REQ-DATA-003:** Input/Output validation: Step definitions must specify expected input types and output types (e.g., `pd.DataFrame`, `str`, `List[int]`) to ensure compatibility between linked steps.

### Extensibility
- **REQ-EXT-001:** New step types can be added via a plugin system or simple registration.
- **REQ-EXT-002:** The step registration mechanism must support attaching arbitrary metadata. Examples include:
    - **Execution Mode**: `single_container`, `distributed` (e.g., Spark/Dask), `iterative` (row-by-row application).
    - **Resource Requirements**: `gpu_required`, `memory_high`.
    - **Step Classification**: `transform`, `analysis`, `extraction`, `load`.
- **REQ-EXT-003:** Steps must support a "Jupyter Cell" abstraction, where a step is an isolated unit of logic with defined inputs/outputs, capable of being chained.

## Interfaces
- **Python API**: The primary interface for developers using this library.
- **JSON Schema**: The interface for data exchange with the frontend.

## Edge Cases
- **EDGE-001:** Circular dependencies (prevented by linear design).
- **EDGE-002:** Serialization of non-standard Python objects (requires pickle or custom encoders).
- **EDGE-003:** Step execution failure (must capture traceback and stop workflow safely).

## Acceptance Criteria
- **AC-001:** A developer can import the library, define a function `@step`, create a workflow, and run it.
- **AC-002:** The `workflow.to_json()` output matches the frontend's expected format.
- **AC-003:** Running a workflow with a failing step reports "error" status and does not crash the process.
