# Status Update: Workflow Steps (Plan 003)

**Date:** 2026-01-15
**Status:** Complete

## Overview
We have successfully implemented the internal wiring mechanics for `WorkflowStep` creation and chaining. This closes the gap between the `@step` decorator and the actual Graph definition (DAG) needed for execution.

## Implemented Components

### 1. Enhanced `WorkflowStep` (Source: `src/fancy_core/workflow_step.py`)
- Added `outputs` field to map named outputs (e.g., "return") to their new Cell IDs.
- This completes the graph node definition: inputs + logic + config -> outputs.

### 2. Output Usage in `@step` (Source: `src/fancy_core/decorators.py`)
- Updated the wiring logic to automatically generate storage placeholders for function outputs.
- Introduced `StorageKind.PENDING` for cells that represent future results.
- The `factory` correctly populates `WorkflowStep.outputs`.

### 3. Chaining Logic
- Validated that `StepWiring` objects (results of calling a step) can be passed as inputs to subsequent steps.
- The system correctly resolves `StepWiring` -> `output_cell` -> `cell_id`.

## Verification

### Unit Tests
A new test suite has been added to verify the behaviors:
`tests/test_steps.py`

**To Run:**
```bash
python -m pytest tests/test_steps.py
```

### Key Behaviors Verified
1.  **Output Mapping:** `WorkflowStep` now contains the mapping of output names to their generated Cell IDs.
2.  **Pending Cells:** Output cells are created with `StorageKind.PENDING`.
3.  **Chaining:** One step definition can consume the output of a previous step definition.
