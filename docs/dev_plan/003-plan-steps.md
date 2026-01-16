# Implementation Plan: Workflow Steps (Spec 003)

## Overview
This plan covers the `WorkflowStep` definition, which represents a configured instance of a function wired to specific data cells, as defined in `docs/spec/003-workflow-steps.md`.

## 1. Class: `WorkflowStep`
**File:** `src/fancy_core/steps.py`

### 1.1 Data Model
- [ ] Define `WorkflowStep` Pydantic Model:
    - `step_id`: UUID
    - `function_slug`: str
    - `inputs`: `Dict[str, UUID]` (Mapping arg_name -> cell_id)
    - `config`: `Dict[str, Any]` (Static parameters)
    - `outputs`: `Dict[str, UUID]` (Mapping output_name -> new_cell_id)

## 2. Wiring Logic (Integration with @step)
**File:** `src/fancy_core/wiring.py` or within `decorators.py`

### 2.1 The "Invokation" Logic
- [ ] When `@step` is called:
    1.  Separate `FancyCell` arguments (Inputs) from static values (Config).
    2.  Validate inputs against `Function.input_contract`.
    3.  Generate new `UUID`s for expected `Function.output_contract`.
    4.  Create `WorkflowStep` instance.
    5.  Create new `FancyCell` placeholders (`StorageKind.PENDING` or future reference) for outputs.
    6.  Return the Output Cells (so they can be passed to next step).

## 3. Testing
**File:** `tests/test_steps.py`
- [ ] Create 2 dummy cells (Cell A, Cell B).
- [ ] "Call" a decorated function with Cell A.
- [ ] Assert returned object is a Cell (Output C).
- [ ] Inspect generated `WorkflowStep`:
    - `inputs` should point to Cell A ID.
    - `function_slug` should match.
    - `outputs` should point to Cell C ID.
