# Execution Plan

## Purpose
Define the step-by-step plan to implement the Python Core Library (`fancy_core`) based on the specs.

## Milestones

### Milestone 1: Core Scaffolding & Data Structures (The State)
**Goal:** Establish the project foundation and the atomic unit of data (`FancyCell`).
- [x] **Setup:** Initialize Python project structure (`src/fancy_core`, `tests/`) and configure `pyproject.toml` (dependencies: pydantic, standard libs).
- [x] **Cells:** Implement `FancyCell` and `StorageKind` (Value vs Reference vs Composite).
- [x] **Store:** Implement `DatumStore` interface and a default `InMemoryStore` for local development.
- [x] **Tests:** Unit tests for Cell creation and Store interactions.

### Milestone 2: The Logic Wrapper (The Actions)
**Goal:** Enable developers to define logic (`@step`) that is self-describing and can be "wired" together.
- [ ] **Decorator:** Implement the `@step` decorator to capture metadata (`FancyFunction`).
- [ ] **Contract:** Implement Pydantic models for Input/Output contracts.
- [ ] **Wiring logic:** Implement the functionality where calling a decorated function returns a `WorkflowStep` with properly mapped input cell IDs (The Factory pattern).
- [ ] **Polymorphism:** Support N-to-M outputs in the decorator logic.

### Milestone 3: The Engine & Orchestration (The Runtime)
**Goal:** Run a complete sequence of steps from start to finish.
- [ ] **Workflow Model:** Implement the `Workflow` class as a linear list of Steps.
- [ ] **Context:** Implement `RuntimeContext` to manage the state of Cells during execution.
- [ ] **Execution Loop:** Implement `Engine.run()` to iterate through steps, resolve inputs from the Store, execute logic, and capture outputs.
- [ ] **Serialization:** Ensure the entire Workflow state (from `to_json` to `from_json`) works for UI round-tripping.

### Milestone 4: Integration & Advanced Features
**Goal:** Verify against frontend expectations and support advanced use cases.
- [ ] **Sample Workflow:** Create a complex sample workflow (e.g., ETL + Analysis) to verify end-to-end functionality.
- [ ] **Error Handling:** Robust error catching and status reporting within the Engine.
- [ ] **Composite Cells:** Verify grouping/ungrouping of data using Composite cells.
- [ ] **Distribution Prep:** Validate that the system provides enough metadata for a future separate runner (e.g., Ray/Celery).

