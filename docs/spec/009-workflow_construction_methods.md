# Specification: Workflow Construction & Execution Strategies

## 1. Introduction
This document outlines how workflows are built, ranging from simple 1-to-1 atomic operations to complex 1-to-N broadcasting over collections.

## 2. The Base Case: Simple 1-to-1 Execution
Before handling complex collections, the system must handle the "Atomic" case seamlessly. This is the entry point for developers starting small.

### 2.1 The "Hello World" Workflow
A workflow with a single step that transforms one scalar value into another.

```python
# 1. Define a pure Python function
def add_five(x: int) -> int:
    return x + 5

# 2. Create Workflow
wf = Workflow("Simple Math")

# 3. Add Step with Direct Value
# The system automatically wraps the integer '10' into an Input Cell.
# It registers 'add_five' as a FancyFunction.


step = wf.add_step(add_five, 10)




# 4. Result
# The function executes immediately (or lazily), producing an Output Cell.
print(step.output.value) 
# >> 15
```

**Internal Flow:**
1.  **Input wrappping:** `10` -> `FancyCell(kind=VALUE, val=10)`
2.  **Execution:** `add_five(10)` -> `15`
3.  **Output wrapping:** `15` -> `FancyCell(kind=VALUE, val=15)`

## 3. Advanced Strategy: Collection Broadcasting
As workflows scale, we move from linear 1-to-1 execution to dynamic 1-to-N models ("Broadcasting") enabling spreadsheet-like operations.

### 3.1 StorageKind.COMPOSITE
A new or formalized storage kind used to represent a collection of other cells.

- **Type Definition**:
  - `kind`: `StorageKind.COMPOSITE`
  - `value`: `List[UUID]` (standard ordered list) or `Dict[str, UUID]` (structured record).
- **Constraints**:
  - A Composite Cell DOES NOT store data values directly. It only stores references (UUIDs) to other cells.
  - Immutability: Once created, the list of UUIDs usually shouldn't change, though the workflow may append if defining an accumulator (implementation detail).

### 2.2 DatumStore Resolution
The `DatumStore` must be improved to handle retrieval of these complex structures.

## 4. Functional Construction (The "Wiring" Approach)

The primary method for building workflows is **Functional Composition**. This approach mitigates "leaky abstractions" by allowing users to write code that looks like standard Python, while the system transparently constructs the execution graph in the background.

### 4.1 Motivation: Why "Wire" instead of Run?
A standard Python script executes linearly and is forgotten. By "Wiring" steps together, we create a persistent **Graph Object** (The Workflow) that exists independently of execution.

This separation provides three key benefits:
1.  **Inspection**: We can visualize the `Workflow` (Data Flow, Dependencies) *before* spending resources running it.
2.  **Robustness**: The Engine can handle retries, caching, and resumption because it understands the boundaries between steps.
3.  **Optimization**: The Engine can detect independent branches and execute them in parallel.

### 4.2 Syntax Example
Users define logic using the `@step` decorator, then call these functions to "wire" them together. The return value is not the *result*, but a `StepWiring` object (a promise of a future result) that can be passed to subsequent steps.

```python
from fancy_core import Workflow
from steps import load_urls, extract_title, prepend_text, count_items

# 1. Define the Graph (Wiring Phase)
# --------------------------------------------------------
# Calling the functions creates specific Step instances and links them.
# 'urls' is a FancyCell (Future), not the data itself.

urls = load_urls(sitemap="sitemap.xml") 
titles = extract_title(url=urls)        # Auto-detects 1-to-N broadcast
formatted = prepend_text(text=titles, prefix="Title: ")
summary = count_items(data=formatted)

# 2. Capture into Workflow
# --------------------------------------------------------
# We create a workflow from the terminal node(s). 
# The system walks backwards to find all dependencies.
wf = Workflow.from_terminal_step(summary, name="Youtube Analysis")

# 5. Access and Review
print(wf)  # Prints the summary table
print(formatted_step.output.value) # Preview the data
```

**Alternative "Fluent" Syntax (Syntactic Sugar)**:
For users who prefer method chaining (like jQuery or Pandas):
```python
# Assuming Cell objects have an .apply() method that calls wf.add_step()
summary = (
    wf.start(load_urls, "sitemap.xml")
      .apply(extract_title)
      .apply(prepend_text, "Title: ")
      .apply(count_items)
)
```
*Note: The primary `wf.add_step` syntax is the implementation priority due to its clarity and flexibility.*

## 3. Execution Engine: Broadcasting Logic

The Engine is responsible for matching the **Input Shape** (Scalar vs. Composite) to the **Function Signature** (Scalar vs. Collection).

### 3.1 Type Definitions
- **Scalar Input**: A single `ATOMIC` cell.
- **Composite Input**: A `COMPOSITE` cell (List of UUIDs).
- **Scalar Function**: A function expecting a single item (e.g., `process(url: str)`).
- **Collection Function**: A function expecting a list (e.g., `summarize(urls: List[str])`).

### 3.2 Dispatch Rules
The `Engine.run_step` method must apply the following logic:

| Input Type | Function Type | Operation | Description |
| :--- | :--- | :--- | :--- |
| **Scalar** | **Scalar** | `Execute Once` | Standard 1:1 execution. Current behavior. |
| **Composite** | **Collection** | `Execute Once` | Pass the resolved list of values to the function. (Many-to-One / Aggregation). |
| **Composite** | **Scalar** | **`Broadcast`** | **New Behavior**. Iterate over children, execute function for each. (One-to-Many / Map). |

### 3.3 The "Broadcast" Operation
When a broadcast is triggered:
1.  **Iterate**: The Engine retrieves the children of the Composite Input.
2.  **Execute**: The Scalar Function is called $N$ times, once for each child value.
3.  **Collect**: The $N$ resulting values are stored as new independent Cells.
4.  **Bundle**: A new `COMPOSITE` cell is created containing the list of result UUIDs.
5.  **Return**: The Step returns the UUID of this new Composite Cell.

## 4. Workflows & Generators

### 4.1 Generators
Functions can now produce multiple values.
- If a user function returns a Python `list` or `generator`, the system captures this.
- **Storage**:
  - Each item in the yielded list is saved as a new `ATOMIC` cell.
  - A parent `COMPOSITE` cell is created to hold them.
- This allows a Step to "explode" a single input into multiple outputs (1-to-N), which subsequent steps can then Broadcast over.

### 4.2 Step Chaining
- `step2 = process(step1)`
- If `step1` outputs a Composite and `process` is a Scalar function, the system automatically infers a Broadcast operation.

## 5. Workflow Construction & Review (DX)

For details on **Representation & Inspection**, **Workflow Accessors**, **Step Introspection**, and **Data Flow Visualization**, please refer to [010-data-printing-representation.md](./010-data-printing-representation.md). This content has been moved to keep specifications focused.

# Workflow Construction Patterns

There are three primary mental models for constructing a Workflow. We need to decide which level of abstraction best serves the user.

## Option 1: The "Pipeline" Builder (Explicit)
**Intuition**: You are manually assembling an instruction list.

In this model, the `Workflow` object is the active builder. You don't call functions directly; you tell the workflow to add them.

```python
# 1. Create the container
wf = Workflow("My Analysis")

# 2. Add steps explicitly
# Returns a reference (StepID or Cell) that allows chaining
step1_out = wf.add(fetch_channel_videos, url="http://...")
step2_out = wf.add(extract_metadata, videos=step1_out)
step3_out = wf.add(generate_report, data=step2_out)

# 3. Execution
wf.run()
```
*   **Pros**: 
    *   No ambiguity. It is obvious step1 belongs to `wf`. 
    *   No global state or context managers.
*   **Cons**: 
    *   Verbose. 
    *   Cannot just copy-paste standard Python code; must rewrite it into `wf.add()` syntax.


## Option 2: The "Functional" Graph (Implicit/Lazy)
**Intuition**: You are drawing a schematic diagram. Wiring nodes together.

In this model, calling a function doesn't run it *or* add it to a specific workflow immediately. It returns a "Node" or "Lazy Promise". The Workflow is created by looking at the final result and tracing back the history.

```python
# 1. Define the graph connections purely as objects
# fetch_channel_videos is decorated to return a "Node" not a value
start_node = Cell("http://...")
video_node = fetch_channel_videos(start_node) 
meta_node  = extract_metadata(video_node)
report_node = generate_report(meta_node)

# 2. Instantiate the workflow from the output
# The workflow crawls backwards: report -> meta -> video -> start
wf = Workflow("My Analysis", outputs=[report_node])

# 3. Execution
wf.run()
```
*   **Pros**: 
    *   Familiar to users of TensorFlow, PyTorch, or Airflow.
    *   Logic is declarative.
*   **Cons**: 
    *   Users must manually manage the "Graph" object (the variables `video_node`, `meta_node`).
    *   Debugging can be hard if the graph is disconnected.


## Option 3: The "Recorder" (Context Aware)
**Intuition**: A "Macro Recorder". You function as normal, but a silent observer records your actions.

This is the "Ideal Syntax" proposal. The `Workflow` acts as a context manager (`with wf:`) or global state that intercepts calls.

```python
# 1. Instantiate the recorder
wf = Workflow("My Analysis")

# 2. Start recording context
with wf:
    # 3. Write standard Python (The @fancy decorator notices the active workflow)
    videos = fetch_channel_videos(url="http://...")
    meta = extract_metadata(videos)
    # The 'videos' variable is actually a Proxy/Cell, allowing it to be passed to 'meta'

# 4. Execution
# The recording is finished. 'wf.steps' is populated.
wf.run()
```
*   **Pros**: 
    *   "It just looks like Python." 
    *   Zero boilerplate inside the logical block.
*   **Cons**: 
    *   "Magic." Users might not understand *why* `fetch_channel_videos` didn't actually fetch videos yet.
    *   Requires strict use of decorators on everything.

