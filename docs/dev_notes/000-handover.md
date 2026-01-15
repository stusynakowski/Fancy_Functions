# Developer Handover Guide

## Purpose
This document provides a quickstart for developers picking up the implementation of the `fancy_core` library based on the specs in `docs_new/spec/`.

## Immediate Next Steps (Implementation Plan)

### Phase 1: Skeleton Setup
1.  Initialize the Python package structure in `src/`.
2.  Install `pydantic`.
3.  Create the `Registry` singleton to hold step definitions.

### Phase 2: Core Logic
1.  Implement the `@step` decorator.
    *   It should wrap the function and register it in the `Registry`.
    *   It should extract input arguments to build a schema.
2.  Implement `Workflow` and `Step` classes using Pydantic models.
    *   Ensure fields match the Frontend specs (see `docs_from_front_end/spec/002-data-model.md`).

### Phase 3: Execution Engine
1.  Create `RuntimeContext` class (simple dict wrapper initially).
2.  Create `Engine` class with a loop to iterate steps.
3.  Implement Reference passing.
    *   *Decision:* For V1, passing data via a generic `data` key in context is sufficient.

## Testing Strategy
- **Unit Tests:** Test the `@step` decorator effectively registers functions.
- **Integration Tests:** Define a workflow with 3 mock steps and ensure data is passed through.
- **Serialization Tests:** Load the JSON examples from `docs_from_front_end` and ensure they parse into valid Python objects. 
