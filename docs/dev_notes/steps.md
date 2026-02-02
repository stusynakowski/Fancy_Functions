# Workflow Steps

Steps are defined to manage and abstract the workflow defined by the user.

## Purpose
- **Consolidate Functions**: They help the user consolidate functions into a coherent sequence or graph.
- **Workflow Abstraction**: They serve as the building blocks that define the user's workflow.

## Execution Management
Steps enable users to manage the execution of each operation. Key capabilities include:
- **Control Flow**: Pause, start, and stop execution.
- **Iteration/Recovery**: Rerun operations.
- **Placeholders**: Create placeholders for future implementation or conditional execution.

## Implementation Details (Current)
Currently implemented in `src/fancy_core/workflow_step.py`:
- `WorkflowStep` is a Pydantic model.
- Handles `step_id`, `function_slug`, `config` (static params), `inputs` (wiring), and `outputs` (wiring).
