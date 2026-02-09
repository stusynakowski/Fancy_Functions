# Development Plan: Decorators & Function Types (Plan 011)

**Reference Spec:** `docs/dev_notes/fancy_function_decorators.md`

## Overview
This plan focuses on implementing the specific decorators (or operation modes) that allow users to define *how* a function behaves with respect to lists of data.
Currently, our Engine is responsible for "Broadcasting" (Plan 007). These decorators serve as **Metadata Markers** that tell the Engine what the function *expects* and what it *produces* (Contract Definition).

## Stage 1: Extended Metadata

### Objective
Update `FancyFunction` to store "Operation Traits".

### Tasks
- [ ] **Update `FancyFunction` Model**
    - [ ] Add `kind` field: `FunctionKind.SCALAR`, `FunctionKind.AGGREGATE`, `FunctionKind.GENERATOR`.
    - [ ] Add `is_map` boolean (for vectorize).
- [ ] **Update Registry**
    - [ ] Ensure `registry.register()` accepts these new fields.

## Stage 2: The Decorators (Markers)

### Objective
Implement the decorators from `fancy_function_decorators.md`. Note: In our current architecture, these decorators primarily set metadata on the registered function so the **Engine** knows what to do. They don't necessarily contain the runtime loop logic themselves (the Engine handles that to ensure valid graph state).

### Step 1: `@apply` (Scalar 1->1)
The default behavior.
- [ ] Mark function as `SCALAR`.
- [ ] Engine Logic: Broadcasts if input is List.

### Step 2: `@expand` (Generator 1->N)
- [ ] Mark function as `GENERATOR`.
- [ ] Wrapper Logic: Wraps result items into individual Cells (if running locally).
- [ ] Engine Logic: Expects list return; wraps items into Composite Cell.

### Step 3: `@reduce` / `@summarize` (Aggregate N->1)
- [ ] Mark function as `AGGREGATE`.
- [ ] Engine Logic: Passes full list to function. Returns single Cell.

### Step 4: `@vectorize` (Map N->N)
- [ ] Mark function as `SCALAR` (effectively).
- [ ] *Note*: Explicit `@vectorize` is often just `@apply` being forced to run on a list. We can treat it as a hint.

## Stage 3: Implementation Strategy

Instead of implementing 5 different complex decorators, we will implement a parameter on the base `@step` decorator or specialized aliases that call it.

```python
# In decorators.py

def expand(func):
    return step(func, kind="generator")

def reduce(func):
    return step(func, kind="aggregate")

def apply(func):
    return step(func, kind="scalar")
```

## Stage 4: Engine Support (Refinement of Plan 007)

The Engine's dispatch logic (Plan 007) needs to respect these markers.
- If `kind == GENERATOR`: Handle unpacking of result list into multiple cells.
- If `kind == AGGREGATE`: Disable broadcasting; pass the Composite Cell's value (list) directly.

## Tasks
- [ ] **Refactor `decorators.py`**: Add the alias functions (`expand`, `reduce`, etc).
- [ ] **Update `WorkflowStep`**: Ensure it carries the `FunctionKind` so the Engine sees it.
- [ ] **Test**: Create a test file `tests/test_decorators_integration.py` verifying that metadata is correctly set.
