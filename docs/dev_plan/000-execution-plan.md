# Execution Plan

## Purpose
Define the step-by-step plan to implement the Python Core Library (`fancy_core`) based on the specs.

## Milestones

### Milestone 1: Core Scaffolding
**Goal:** A working package where we can register a step and see it in a list.
- [ ] Initialize Python project structure (src/, tests/).
- [ ] Configure `pyproject.toml` dependencies (pydantic).
- [ ] Implement `StepRegistry` singleton.
- [ ] Implement `@step` decorator.

### Milestone 2: Data Models & Serialization
**Goal:** Ability to load/save workflows from JSON compatible with frontend.
- [ ] Implement `StepConfig` model (Pydantic).
- [ ] Implement `Workflow` model (Pydantic).
- [ ] Create unit tests for JSON serialization/deserialization.

### Milestone 3: Execution Engine
**Goal:** Running a workflow end-to-end.
- [ ] Implement `RuntimeContext` for data storage.
- [ ] Implement `Engine` class (run loop).
- [ ] Add error handling and status updates.

### Milestone 4: Integration Verification
**Goal:** Verify against frontend expectations.
- [ ] Create a complex sample workflow matching frontend `000-overview.md` examples.
- [ ] Run it and verify output.

