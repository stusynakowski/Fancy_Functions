# Development Plan: Workflow Builder Syntax Examples (Plan 010)

**Reference Spec:** `docs/spec/009-workflow_construction_methods.md` and `docs/dev_notes/ideal_syntax_of_example_usecase_of_backend.py`

## Overview
This plan focuses entirely on the **User Syntax** for creating workflows. It bridges the gap between the low-level "Builder" API (Plan 008) and the high-level, decorator-driven, "Pythonic" syntax that users actually want (as seen in `ideal_syntax...py`).
This acts as a requirement document for the `WorkflowBuilder` to ensure it supports these usage patterns.

## Target User Experience

The goal is to allow users to define workflows in two ways:
1.  **Explicit Builder**: Using `add_step()` manually (Good for UIs and scripts).
2.  **Context Manager**: Using `with Workflow() as wf:` (Good for Python developers).

### Syntax 1: The Explicit Builder (Low Level)
*Already covered in Plan 008, but refined here.*

```python
from fancy_core import WorkflowBuilder

# 1. Initialize
builder = WorkflowBuilder("YouTube Analysis")

# 2. Add Steps with explicit wiring
url_step_id = builder.add_step(
    "fetch_url", 
    config={"url": "https://youtube.com/my_channel"}
)

titles_step_id = builder.add_step(
    "extract_titles",
    inputs={"html": url_step_id} # Wiring by ID
)

builder.add_step(
    "save_csv",
    inputs={"data": titles_step_id},
    config={"filename": "output.csv"}
)

# 3. Compile
workflow = builder.build()
```

### Syntax 2: The Context Manager (High Level)
This is the "Magic" layer. It intercepts function calls to build the graph instead of running them.

```python
from fancy_core import Workflow, fancy
from fancy_functions.scraping import fetch_url, extract_titles, save_csv

# Note: Functions must be decorated with @fancy or registered
# This mode essentially wraps the Builder.

with Workflow("YouTube Analysis") as wf:
    # 1. Start with a constant or config
    # 'html' is a Cell Pointer (Future/Promise), not the actual data
    html = fetch_url(url="https://youtube.com/my_channel")
    
    # 2. Pass pointers to next function
    titles = extract_titles(html=html)
    
    # 3. Final step
    save_csv(data=titles, filename="output.csv")
    
    # The 'wf' object now contains the fully wired graph.
```

## Implementation Strategy: The Dual-Mode Decorator

To support Syntax 2, the `@step` (or `@fancy`) decorator must be context-aware.

### 1. Context Awareness
The `Workflow` class needs a global/thread-local context stack.
- `Workflow.__enter__`: Pushes self to `_current_workflow`.
- `Workflow.__exit__`: Pops self.

### 2. Decorator Logic (`@step`)
When a decorated function (e.g., `fetch_url`) is called:
1.  **Check Context**: Is there an active `_current_workflow`?
2.  **If NO (Execution Mode)**: Run the function immediately (legacy/direct execution).
3.  **If YES (Definition Mode)**:
    - **Do NOT run** the function.
    - Inspect arguments to find `Cell` (or `StepOutput`) objects.
    - Resolve those `Cell` objects to their upstream `step_id` or `cell_id`.
    - Call `_current_workflow.builder.add_step(...)`.
    - Return a **Proxy Object** (a dummy Cell) representing the *future result* of this step.

## Example Use Cases

### Case A: Simple Linear Chain
```python
with Workflow("Math Ops") as wf:
    res1 = add(a=5, b=10)      # Returns Proxy(Step1)
    res2 = multiply(x=res1, y=2) # Returns Proxy(Step2), inputs wired to Step1
```

### Case B: Branching
```python
with Workflow("Branching") as wf:
    data = load_data()
    
    # Branch 1
    stats = calculate_stats(data)
    save_stats(stats)
    
    # Branch 2
    clean = clean_data(data)
    save_data(clean)
```

### Case C: The "Broadcasting" (Auto-Map) impl
Ideally, the syntax shouldn't change for lists vs items. 
If `load_videos` returns a list-like Proxy, and `get_metadata` takes a scalar, the **Engine** handles the broadcasting (as per Plan 007). The **Builder** just wires A to B.

```python
with Workflow("Video Processing") as wf:
    # returns a Composite Proxy
    videos = get_video_list(channel_id="...") 
    
    # Engine will see "Composite Input" -> "Scalar Function" = Broadcast
    # Builder just wires them.
    meta = get_metadata(video=videos) 
    
    # Engine sees "list of dicts" -> "Aggregate Function" = Reduce
    summary = create_summary(meta) 
```

## Tasks required (Update to Plan 008)

To support this syntax, **Plan 008 (Builder)** needs to include:
- [ ] **Context Manager Implementation** in `Workflow`.
- [ ] **Decorator Update**: Update `@step` in `src/fancy_core/decorators.py` to handle "Definition Mode" (return Proxies instead of running).
- [ ] **Proxy Class**: `class StepProxy` (or reuse `FancyCell` as a promise) to track the UUID of the step that *will* produce the value.
