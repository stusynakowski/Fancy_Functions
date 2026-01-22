# Phase 2 Development Plan: Refactoring for Iteration & Scale

## Overview
This plan outlines the staged development process to support the "Spreadsheet Model" of execution.
**Reference Spec:** `docs/spec/007-refactor.md`

## Stage 1: Data Structure Foundation

### Objective
Formalize `StorageKind.COMPOSITE` to handle collections of cells robustly. This is the prerequisite for any collection-based logic.

### Tasks
- [ ] **Update `FancyCell` Model:**
    - Ensure `FancyCell.value` is properly typed to support `List[UUID]` or `Dict[str, UUID]` when `kind=COMPOSITE`.
    - Validate that creating a composite cell requires providing child UUIDs.
- [ ] **Update `DatumStore`:**
    - Add `store.get_children(composite_id) -> List[FancyCell]` convenience method.
    - Implement "Recursive Resolution": `store.resolve(composite_cell, recursive=True)` should return `[store.resolve(child) for child in composite_cell.value]`.
    - Keep `store.resolve(composite_cell, recursive=False)` returning just the list of UUIDs.
- [ ] **Stage 1 Verification:**
    - Create `tests/test_composite_cells.py`.
    - Verify creating a Composite cell, resolving it shallowly, and resolving it recursively.

## Stage 2: Engine Broadcasting Logic

### Objective
Enable the `Engine` to automatically iterate a function over a `Composite` input if the function expects a single item ("Mapping").

### Tasks
- [ ] **Update `Engine.run()` Loop:**
    - Inside the step execution loop, inspect resolved inputs.
    - **Detection Logic:**
        - Check if input is `COMPOSITE`.
        - Check `FancyFunction` input contract (List vs Scalar).
    - **Branching Logic:**
        1.  **Scalar Input / Scalar Func** -> `Execute Once` (Existing).
        2.  **Composite Input / Collection Func** -> `Execute Once` (Pass full list).
        3.  **Composite Input / Scalar Func** -> **`Execute Iteratively`** (Broadcast).
- [ ] **Implement `Execute Iteratively`:**
    - Iterate through children of Composite input.
    - Call function for each child.
    - Collect resulting output UUIDs.
    - Create new `COMPOSITE` cell containing results.
    - Register this new Composite as Step output.
- [ ] **Stage 2 Verification:**
    - Create `tests/test_iterative_execution.py`.
    - Test mapping a simple math function (e.g., `x * 2`) over a pre-made Composite list of numbers.

## Stage 3: Decorators & Generator Support

### Objective
Allow Python functions to easily produce collections of cells, feeding the broadcasting engine.

### Tasks
- [ ] **Generator Support:**
    - Modify the `@step` execution wrapper.
    - If user function returns `List` or `Generator`:
        - Create `FancyCell(VALUE)` for each item.
        - Create parent `FancyCell(COMPOSITE)` holding them.
        - Return Parent UUID.
- [ ] **Stage 3 Verification:**
    - Test a "Generator" step (e.g., `range(5)`) feeding into a "Broadcast" step.

## Stage 4: Wiring & DSL (Future)

### Objective
Ensure `my_step(input_cell)` returns a `WorkflowStep` configuration object properly in this new paradigm.

### Tasks
- [ ] Review `Workflow` definition to ensure it handles Step dependencies that are effectively dynamic (though the dependency graph itself remains static, the data volume is dynamic).

## Dependencies
- Stage 1 MUST be completed before Stage 2.
- Stage 2 MUST be completed before Stage 3.
