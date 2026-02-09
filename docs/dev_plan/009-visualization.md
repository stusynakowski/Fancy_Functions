# Development Plan: CLI Visualization & Data Inspection (Plan 009)

**Reference Spec:** `docs/spec/010-data-printing-representation.md`

## Overview
The "Fancy" in Fancy Functions implies a superior developer experience. This plan focuses on "Development by Inspection".
We will implement rich string representations for the core objects so that `print(workflow)` gives a dashboard, not just `<Workflow object at 0x...>`.

## Stage 1: Core Object Representation

### Objective
Make `FancyCell`, `WorkflowStep`, and `Workflow` pretty-printable.

### Tasks
- [ ] **Update `FancyCell.__str__`**
    - [ ] Format: `[Kind:VALUE] "Alias" <Type:int> = 42`
    - [ ] Truncate long values (e.g. for long strings or lists).
- [ ] **Update `WorkflowStep.__str__`**
    - [ ] Format: `Step(name='Extract', func='extract_title', inputs=['url'])`
- [ ] **Update `Workflow.__str__`**
    - [ ] Should print the "Process View" summary table (see below).

## Stage 2: The Process View (Workflow Dashboard)

### Objective
Implement the tabular view of the workflow logic chain.

### Tasks
- [ ] **Implement `Workflow.render_process_view() -> str`**
    - [ ] Columns: Index, Step Name, Function, Input Aliases, Op Type, Status.
    - [ ] Iterate through steps.
    - [ ] Resolve input UUIDs to their aliases for readability.
- [ ] **CLI Integration**
    - [ ] Hook this into `__str__` of the Workflow.

## Stage 3: The Data Matrix View

### Objective
Implement the "Spreadsheet" view that shows data flow across steps.

### Tasks
- [ ] **Implement `Workflow.render_data_view() -> str`**
    - [ ] This requires access to the `Engine` results or the `Store`.
    - [ ] *Design Decision*: Should `Workflow` have access to results? 
        - *Correction*: The `Engine` produces results. Maybe this method belongs on a `WorkflowRun` object or similar, OR the Workflow holds its latest state.
        - *Plan*: Assume `Workflow` holds state (as per `007` plan/`workflow.py` refactor).
    - [ ] **Logic**:
        - Iterate Steps as Columns.
        - Iterate "Rows" (if broadcasting).
        - Print a table of values.
- [ ] **Handle Composite Data**
    - [ ] If a cell is Composite (List), print it as a column of values.
    - [ ] If a cell is Scalar, repeat it or show it once? (Align with spreadsheet view).

## Stage 4: Step Inspection

### Objective
Detailed view of a single step's transaction.

### Tasks
- [ ] **Implement `WorkflowStep.render_detailed_view(store) -> str`**
    - [ ] Show table of: Input Value | Function Name | Output Value.
    - [ ] Extremely useful for debugging "Why did this specific row fail?".

## Verification
- Create a demo script `scripts/demo_visualization.py` that builds a workflow, runs it, and prints these views.
