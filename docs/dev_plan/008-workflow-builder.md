# Development Plan: Workflow Builder & Serialization (Plan 008)

**Reference Spec:** `docs/spec/009-workflow_construction_methods.md` (and `docs/dev_notes/workflow_construction_methods.md`)

## Overview
Currently, constructing a workflow involves manually instantiating `WorkflowStep` objects and wiring them together using UUIDs. This is error-prone and verbose.
This plan introduces the **Builder Pattern** to provide a fluent, Pythonic API for defining workflows, and enables **Serialization** so workflows can be saved to and loaded from disk (JSON/YAML).

## Stage 1: The Workflow Builder

### Objective
Create a high-level `WorkflowBuilder` class that manages the complexity of step creation, ID generation, and wiring.

### Tasks
- [ ] **Create `src/fancy_core/builder.py`**
    - [ ] Define `class WorkflowBuilder`.
    - [ ] Initialize with a named `Workflow` instance.
    - [ ] Maintain an internal registry of "active variables" (alias -> UUID map).
- [ ] **Implement `add_step` Method**
    - [ ] arguments: `function_slug`, `inputs` (dict of alias->alias), `config` (static values), `output_alias`.
    - [ ] **Validation**: Check `function_slug` describes a valid function in `registry`.
    - [ ] **Resolution**: Convert input aliases (e.g. "scraped_html") to Cell UUIDs from the internal map.
    - [ ] **Creation**: Instantiate `WorkflowStep`.
    - [ ] **Registration**: Add step to the workflow.
    - [ ] **Output**: Store the produced Cell UUID under `output_alias` for future steps to reference.
- [ ] **Testing**
    - [ ] Create `tests/test_builder.py`.
    - [ ] Verify a 3-step linear chain can be built with 5 lines of code.

## Stage 2: Serialization (Save/Load)

### Objective
Allow workflows to be persisted. This is crucial for running workflows created by a frontend or saved for later execution.

### Tasks
- [ ] **Update `Workflow` Model for Pydantic V2 (if needed)**
    - [ ] Ensure `Workflow` and `WorkflowStep` cleanly serialize to JSON.
    - [ ] Handle `UUID` serialization (Pydantic does this usually, but check format).
- [ ] **Implement Export/Import**
    - [ ] `WorkflowBuilder.export_json() -> str`
    - [ ] `Workflow.from_json(json_str) -> Workflow`
    - [ ] `Workflow.to_json() -> str`
- [ ] **Testing**
    - [ ] Build a workflow.
    - [ ] Export to JSON.
    - [ ] Re-import from JSON.
    - [ ] Run the re-imported workflow and verify identical results.

## Stage 3: Validation & Guardrails

### Objective
Ensure that "Blueprints" (serialized workflows) are valid before we try to run them.

### Tasks
- [ ] **Static Analysis (Dry Run)**
    - [ ] Check for circular dependencies (DAG validation).
    - [ ] Check for "Dangling References" (inputs that don't come from any known step).
- [ ] **Registry Validation**
    - [ ] When loading, warn if the current runtime doesn't have the functions required by the blueprint.

## Migration
- Existing tests that manually construct workflows should remain valid.
- New tests should prefer the `WorkflowBuilder`.

