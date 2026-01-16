# Implementation Plan: Workflows & Engine (Spec 004 & 005)

## Overview
This plan covers the container `Workflow`, the execution `Engine`, and the orchestrator logic as defined in `docs/spec/004-workflows.md` and `docs/spec/005-architecture.md`.

## 1. Class: `Workflow`
**File:** `src/fancy_core/workflow.py`

### 1.1 Data Model
- [ ] Define `Workflow` Pydantic Model:
    - `id`: UUID
    - `name`: str
    - `steps`: `List[WorkflowStep]`
- [ ] Method `add_step(step: WorkflowStep)`
- [ ] Method `to_json() / from_json()` (Inherited from Pydantic but verify format).

## 2. Class: `Engine`
**File:** `src/fancy_core/engine.py`

### 2.1 Initialization
- [ ] `__init__(store: DatumStore)`

### 2.2 Execution Loop (`run`)
- [ ] Accept `workflow` and `context` (or just use Store as context).
- [ ] Loop through `workflow.steps`:
    1.  **Resolve Inputs:** Use `store.resolve(cell_id)` for everything in `step.inputs`.
    2.  **Fetch Function:** Look up `step.function_slug` in Registry.
    3.  **Execute:** Call `func(**inputs, **config)`.
    4.  **Handle Output:**
        - If N-to-M dict returned, map keys to `step.outputs`.
        - Use `store.put(result, alias)` to persist/cache result.
        - Update the `FancyCell` associated with `step.outputs` with the new URI/Value.
    5.  **Status:** Update step status (if tracking run state).

## 3. Testing
**File:** `tests/test_engine.py` (Integration)
- [ ] **Linear Chain Test:**
    - Step 1: `create_data` -> Cell A
    - Step 2: `process_data(Cell A)` -> Cell B
    - Workflow holds [Step 1, Step 2].
    - Run Engine.
    - Assert Cell B contains expected result.
- [ ] **State Persistence:**
    - Verify intermediate results are found in Store.
