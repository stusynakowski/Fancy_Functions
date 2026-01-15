# Specification: Fancy Functions

## 1. Definition
A **Fancy Function** is a standard Python function that has been enriched (decorated) to become a portable, self-describing, and managed unit of work within a data processing pipeline. 

It upgrades a raw function into a **"Smart Cell"**—conceptually equivalent to a robust, reusable Jupyter Notebook cell that declares its needs, behavior, and interfaces explicitly.

## 2. Core Traits

### 2.1 Self-Describing (Introspection)
A Fancy Function must carry more than just code. It must provide:
*   **Identity:** A unique `slug` and human-readable `name`.
*   **Documentation:** A description usable by UI tooltips or generated docs.
*   **Schema:** A JSON-serializable definition of its accepted arguments (parameters), auto-generated from signature type hints.

### 2.2 Contractual (I/O Validation)
Fancy Functions do not just accept `*args` and `**kwargs`. They enforce specific data contracts:
*   **Input Contract:** What data structure must be present in the context before execution (e.g., `pandas.DataFrame`, `List[str]`).
*   **Output Contract:** What data structure it guarantees to return to the context.

### 2.3 Context-Aware
Fancy Functions accept a `RuntimeContext`. They can pull data references, secrets, or global variables from the context via the defined inputs.

### 2.4 Execution-Agnostic
The function defines **logical execution behavior**, decoupled from physical infrastructure (Local, Dask, Spark).

### 2.5 N-to-M Capability (Polymorphic Outputs)
Steps are not restricted to a single output. The decorator supports defining multiple named outputs.

*   **Logic:** A function can return a `dict` of results or a specialized `Result` object.
*   **Wiring:** Each named output becomes a distinct `FancyCell` in the workflow, allowing downstream steps to wire into specific outputs (e.g., wiring only into the "errors" output of a validation step).

```python
@step
def split_data(df: pd.DataFrame) -> Outputs(train=pd.DataFrame, test=pd.DataFrame):
    # logic
    return {"train": df1, "test": df2}
# Produces 2 distinct cells.
```

### 2.6 The Abstract User Experience (UX) Principle
The core design philosophy is **"Logic over Logistics"**. 

*   **The User Sees:** "I am passing the 'Sales Data' into the 'Cleaning Function' to get 'Cleaned Data'".
*   **The User Ignores:** "I am resolving UUIDs, loading Parquet files from S3, deserializing to Pandas, executing, serializing result to JSON, and upload back to S3."
*   **Implementation:** The `@step` decorator and `Engine` handle *all* strict plumbing (IO, Context switching, Error handling) invisibly. The user's code inside the function should look like standard, synchronous Python.

## 3. Taxonomy of Fancy Functions

| Type | Input | Output | Purpose |
|------|-------|--------|---------|
| **Extractor** | `SourceConfig` | `DataSet` | Loads raw data into the workflow context. |
| **Transformer**| `DataSet` | `DataSet` | Modifies, cleans, or enriches data (Map/Filter). |
| **Analyzer** | `DataSet` | `Artifact` | Produces metrics, plots, or summaries (Reduce). |
| **Loader/Sink**| `DataSet` | `SideEffect` | Exports data to external systems. |

## 4. Schema (Level 1)

```python
from typing import Dict, Type, Callable, Optional
from pydantic import BaseModel

class FancyFunction(BaseModel):
    slug: str                   # Unique ID (e.g. "pandas_join")
    name: str                   # Display Name
    description: str
    
    # The Contract
    input_contract: Dict[str, Type]  # e.g., {"left": DataFrame, "right": DataFrame}
    output_contract: Dict[str, Type] # e.g., {"train": DataFrame, "test": DataFrame}
    
    # Internal: The actual python callable
    # _executable: Callable
```
