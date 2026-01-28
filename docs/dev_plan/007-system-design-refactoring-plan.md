# Development Plan: System Refactoring (Spec 007)

**Reference Spec:** `docs/spec/007-system-design-refactoring.md`

## Overview
This plan outlines the implementation of the "Broadcasting" engine and "Composite" data structures. This refactoring enables the system to operate on collections of data (rows, lists) as easily as single values, creating a "Spreadsheet-like" execution model.

## Stage 1: Data Structure Fundamentals

### Objective
Enable the system to store, retrieve, and traverse collections of data cells.

### Tasks
- [ ] **Update `FancyCell` Model**
    - [ ] Enforce strict typing for `StorageKind.COMPOSITE`.
    - [ ] Validate that `value` is `List[UUID]` or `Dict[str, UUID]` when kind is COMPOSITE.
- [ ] **Upgrade `DatumStore` Resolution**
    - [ ] Implement `store.resolve(cell_id, recursive=False)` (Default): Returns the raw structure (List/Dict of UUIDs).
    - [ ] Implement `store.resolve(cell_id, recursive=True)`:
        - Detects if cell is COMPOSITE.
        - Iterates over children and resolves them recursively.
        - Returns a pure Python `List[Any]` or `Dict[str, Any]` (the actual data values).
- [ ] **Testing**
    - [ ] Create `tests/test_core_data_composite.py`.
    - [ ] Verify: Storing a list of UUIDs, retrieving it raw, retrieving it deeply resolved.

## Stage 2: Engine Runtime & Broadcasting

### Objective
Upgrade the Engine to automatically detect when to "Broadcast" (iterate) a function over a list of inputs.

### Tasks
- [ ] **Refactor `Engine.run_step` Execution Flow**
    - [ ] Inspect the definition of the function being called (Scalar vs Collection input).
    - [ ] Inspect the `storage_kind` of the input cell (Scalar vs Composite).
- [ ] **Implement The Dispatch Logic**
    1.  **Scalar Input + Scalar Func** -> `Execute Standard` (Keep existing logic).
    2.  **Composite Input + Collection Func** -> `Execute Standard` (Pass the resolved List/Dict directly).
    3.  **Composite Input + Scalar Func** -> `Execute Broadcast` (New Logic).
- [ ] **Implement `Execute Broadcast`**
    - [ ] Resolve the Composite Input to get list of Child Cells.
    - [ ] **Loop**: For each Child Cell:
        - [ ] Resolve Child Value.
        - [ ] Run Function.
        - [ ] Store Result as new Atomic Cell.
    - [ ] **Bundle**: Create a new `COMPOSITE` cell containing all Result UUIDs.
    - [ ] Register this new Composite as the output of the Step.

## Stage 3: Generator Support (Fan-Out)

### Objective
Allow Steps to produce multiple outputs that become a collection, feeding into the broadcasting mechanism.

### Tasks
- [ ] **Update Execution Wrapper**
    - [ ] Detect if a user function returns a Python `Generator` or `List`.
    - [ ] **If Generator/List**:
        - [ ] Iterate through all items.
        - [ ] Save each item as an individual `FancyCell(VALUE)`.
        - [ ] Collect all new UUIDs.
        - [ ] Create and save a `FancyCell(COMPOSITE)` containing these UUIDs.
        - [ ] Return the Composite UUID as the Step result.
- [ ] **Testing**
    - [ ] Create a test with a function `def generate_range(n): return range(n)`.
    - [ ] Ensure it produces 1 Composite Cell and N Value Cells.

## Stage 4: Integration & Validation

### Objective
Verify the end-to-end flow: Generate -> Broadcast -> Aggregate.

### Tasks
- [ ] **Create Integration Test: `tests/test_workflow_broadcast.py`**
    - [ ] **Step 1 (Generate)**: Return `[1, 2, 3]`.
    - [ ] **Step 2 (Broadcast)**: `multiply_by_two(x)`. Should run 3 times.
    - [ ] **Step 3 (Aggregate)**: `sum_values(list)`. Should run 1 time.
    - [ ] **Validation**: Assert final result is `12` ((1*2) + (2*2) + (3*2)).

## Migration Notes
- Existing tests using Scalar-to-Scalar logic must continue to pass.
- The `Engine` changes should be backward compatible for all Scalar operations.
