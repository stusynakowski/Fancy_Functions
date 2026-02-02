# Cell Definition & Granularity

## The Core Concept
A **Cell** is the fundamental unit of state and computation in the reactive graph. However, "atomicity" is contextual. To handle the requirement where a cell can be a scalar, a row, or an entire table, we must define a Cell by its **Behavioral Interface** rather than just its data type.

## 1. The Dimensionality of a Cell

A Cell is a container for `Value`. The nature of `Value` determines how we interact with it. We do not need different classes (`ScalarCell`, `RowCell`) if we design the Cell to be polymorphic.

| Mode | Dim | Example Payload | Usage Context |
| :--- | :--- | :--- | :--- |
| **Scalar** | 0D | `42`, `"Hello"`, `True` | Configuration, constants, single metrics. |
| **Vector** | 1D | `[1, 2, 3]`, `pd.Series` | A row of data, a list of filenames, a time series. |
| **Matrix** | 2D | `pd.DataFrame`, `List[List]` | A full dataset, an image, a lookup table. |

## 2. Solving the "Part vs Whole" Problem

The user's challenge: *"Sometimes I have a table where the cells might be rows, or the cells in the table."*

This is a **Granularity** decision. The definition of a "Cell" depends on the **Unit of Invalidation**.

### Strategy: The Invalidation Rule
> **"A Cell is the smallest unit of data that, when changed, triggers a recalculation event."**

#### Scenario A: The Table is the Cell (Coarse-Grained)
*   **Use Case:** ETL pipelines, Bulk processing.
*   **Structure:** One Cell holds the entire `DataFrame`.
*   **Behavior:** If *any* value in the table changes, the entire Cell is marked `dirty`. Downstream functions receive the whole table.
*   **Pros:** Efficient for Python/Pandas (vectorized operations).
*   **Cons:** Re-runs everything even for small changes.

#### Scenario B: The Row is the Cell (Medium-Grained)
*   **Use Case:** Processing a list of independent URLs, Files, or Customers.
*   **Structure:** The Table is a *List of Cells* (one Cell per row).
*   **Behavior:** If Row 5 changes, only the pipeline for Row 5 re-runs. Row 6 is unaffected.
*   **Pros:** Parallelism, isolate failures.

#### Scenario C: The Value is the Cell (Fine-Grained - Excel Style)
*   **Use Case:** Financial models, complex inter-dependent logic.
*   **Structure:** A 10x10 grid acts as 100 individual Cells.
*   **Behavior:** Changing A1 only updates B1 (if B1 depends on A1).
*   **Pros:** Precision dependency tracking.
*   **Cons:** Massive overhead for large datasets in Python (1M cells = 1M objects).

## 3. Structural Definition

To support all three, the Cell class should remain generic, but we need **Operators** to switch between granularities.

```python
@dataclass
class Cell:
    id: str
    value: Any
    version: int = 0
```

We need **Transition Primitives** to move between definitions:

### 1. `Explode` (Coarse -> Fine)
Takes a `List-Cell` or `Table-Cell` and converts it into a list of `Scalar-Cells`.
*   *Input:* `Cell(value=[A, B, C])`
*   *Output:* `[Cell(A), Cell(B), Cell(C)]`
*   *Purpose:* Allows you to branch logic per-item.

### 2. `Implode` / `Collect` (Fine -> Coarse)
Takes a list of `Scalar-Cells` and bundles them into one `List-Cell`.
*   *Input:* `[Cell(A), Cell(B), Cell(C)]`
*   *Output:* `Cell(value=[A, B, C])`
*   *Purpose:* Aggregation, reducing results.

### 3. `View` (Virtual Addressing)
Allows treating a Coarse Cell as if it were Fine cells without actually creating objects.
*   `my_table_cell.at[0, 'col_name']` returns a specific value, but dependency tracking remains on the parent table.

## 4. The Universal Cell Wrapper: Crucial Components

To wrap *any* python object—from a simple integer to a complex Machine Learning model—the Cell wrapper must enforce a strict contract. Here are the 5 absolutely crucial components required to make it work in a reactive system.

### 1. The Container (Payload)
*   **What:** A variable to hold the actual object (the "Value").
*   **Requirement:** Must be able to hold `Any` type.
*   **Why:** The wrapper doesn't care what the data is, only that it *has* data.

### 2. The Identity (Address)
*   **What:** A unique ID, key, or Coordinate.
*   **Requirement:** Must be Hashable and Immutable (String, Tuple, UUID).
*   **Why:** The dependency graph needs to know *who* changed. You can't track dependencies without names.

### 3. The Version (State)
*   **What:** An integer counter or timestamp.
*   **Requirement:** Increments on every write.
*   **Why:** To determine if a cache is stale. If `inputs.version > result.version`, re-run.

### 4. The Edges (Graph Links)
*   **What:** A list of `observers` (who is watching me) and `dependencies` (who I am watching).
*   **Requirement:** A Set of IDs.
*   **Why:** Efficient propagation. When this cell changes, we iterate the `observers` list to notify them.

### 5. The Accessors (The Gatekeepers)
*   **What:** `.get()` and `.set()` methods (not direct property access).
*   **Requirement:**
    *   `get()` MUST record the caller as a dependent.
    *   `set()` MUST increment the version and notify observers.
    *   **Crucial:** Direct access (e.g., `cell.value = 5`) bypasses the system and breaks reactivity.

---

### Minimal Implementation Class

```python
class Cell:
    def __init__(self, key, value):
        self.key = key              # 2. Identity
        self._value = value         # 1. Container
        self.version = 0            # 3. Version
        self.observers = set()      # 4. Edges (Downstream)

    def get(self):
        # ... (Log "Current Process depends on self.key") ...
        return self._value

    def set(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self.version += 1       # 3. Update State
            self.notify()           # 5. Trigger Reactivity

    def notify(self):
        # ... (Tell all self.observers to mark themselves dirty) ...
        pass
```

## 5. Object Decomposition Patterns

To "easily define a set of cells" from a given object, we can use a **Decomposition Strategy**. This maps the structure of a raw Python object into a collection of managed `Cell` instances.

### The `decompose` Helper

We can imagine a helper that recursively breaks an object down based on desired granularity.

```python
def decompose(obj, scheme='auto', prefix=''):
    """
    Break an object into a list or dict of Cells.
    """
    # 1. Dictionary / Object -> Named Cells
    if isinstance(obj, dict):
        return {
            f"{prefix}{k}": Cell(id=f"{prefix}{k}", value=v) 
            for k, v in obj.items()
        }
    
    # 2. List -> Indexed Cells
    if isinstance(obj, list):
        return [
            Cell(id=f"{prefix}{i}", value=v) 
            for i, v in enumerate(obj)
        ]
        
    # 3. Pandas DataFrame (The "Choice" Point)
    if isinstance(obj, pd.DataFrame):
        if scheme == 'by_pro':
            # Row-as-Cell (Best for parallel processing)
            return [
                Cell(id=f"{prefix}row_{i}", value=row) 
                for i, row in obj.iterrows()
            ]
        elif scheme == 'by_col':
            # Column-as-Cell (Best for analytics)
            return {
                col: Cell(id=f"{prefix}{col}", value=obj[col]) 
                for col in obj.columns
            }
        elif scheme == 'grid':
            # Value-as-Cell (Excel emulation - expensive!)
            cells = []
            for r in range(len(obj)):
                for c in obj.columns:
                     cells.append(Cell(id=f"{r}_{c}", value=obj.at[r, c]))
            return cells

    # 4. Scalar -> Single Cell
    return Cell(id=prefix or 'root', value=obj)
```

### Usage Examples

1.  **Config Object -> Dictionary of Cells**
    ```python
    config = {"rate": 1.5, "limit": 100}
    # Becomes: {'rate': Cell(1.5), 'limit': Cell(100)}
    ```

2.  **Dataset -> List of Row Cells**
    ```python
    df = pd.read_csv("urls.csv")
    # Becomes: [Cell(row1), Cell(row2), Cell(row3)...]
    # Each cell contains a Row Series or Dictionary.
    # Changing one URL only invalidates that one Cell.
    ```

## 6. Intuitive Mental Model: The "Cellification" Spectrum

To intuitively decide how to break down an object, use the **Container Analogy**. Imagine your data is a Table. How do you want to pick it up?

| Metaphor | Granularity | Meaning | Best For... |
| :--- | :--- | :--- | :--- |
| **The Briefcase** | **Monolith** (1 Cell) | The entire table is one sealed unit. You pass it around whole. If you edit one typo inside, you replace the whole briefcase. | **Bulk Transformations** (Cleaning, Saving to SQL, Exporting). |
| **The Rolodex** | **Row-Based** (N Cells) | You have a stack of index cards. You can pull out *one* card (row) to write on it without disturbing the others. | **Item Processing** (Scraping URLs, API calls per user). |
| **The Cabinet** | **Column-Based** (M Cells) | You separate data by type (folder for Names, folder for Dates). You process entire columns at once. | **Analytics** (Calculating averages, plotting charts). |
| **The Mosaic** | **Atom-Based** (NxM Cells) | Every single tile is separate. Moving one tile might shift its neighbor, but keeps the rest still. | **Financial Modeling** (Complex inter-cell formulas). |

### Convenience Methods (Syntactic Sugar)

Instead of a generic `decompose` function, we can expose these metaphors directly on the Cell API:

```python
# The Briefcase
cell = Cell(df)

# The Rolodex
cells = Cell.from_rows(df) 

# The Cabinet
cells = Cell.from_columns(df)

# The Mosaic
cells = Cell.from_grid(df)
```

## 7. Collection Factories (Lists & Dictionaries)

To handle lists or dictionaries of arbitrary objects, we can provide explicit factory methods.

### A. From List (`Cell.from_list`)

Creates a list where each item is wrapped in a Cell.

```python
@classmethod
def from_list(cls, items: list, id_prefix: str = "item") -> list['Cell']:
    """
    Converts [A, B, C] -> [Cell(A), Cell(B), Cell(C)]
    """
    return [
        cls(id=f"{id_prefix}_{i}", value=item)
        for i, item in enumerate(items)
    ]
```

**Usage:**
```python
users = [User("Alice"), User("Bob")]
user_cells = Cell.from_list(users, id_prefix="user")
# Result: [Cell(id="user_0", value=Alice), Cell(id="user_1", value=Bob)]
```

### B. From Dictionary (`Cell.from_dict`)

Creates a dictionary where each value is wrapped in a Cell, preserving keys.

```python
@classmethod
def from_dict(cls, data: dict, id_prefix: str = "") -> dict[str, 'Cell']:
    """
    Converts {'k': V} -> {'k': Cell(V)}
    """
    return {
        key: cls(id=f"{id_prefix}{key}", value=val)
        for key, val in data.items()
    }
```

**Usage:**
```python
config = {"theme": "dark", "retries": 3}
config_cells = Cell.from_dict(config)
# Result: {'theme': Cell("dark"), 'retries': Cell(3)}
```

### C. Deep/Recursive Creation (`Cell.from_structure`)

For nested structures (List of Dicts, Dict of Lists), simple iteration isn't enough.

```python
@classmethod
def from_structure(cls, data, path="root"):
    """
    Recursively turns leaves of a structure into Cells.
    """
    if isinstance(data, dict):
        return {k: cls.from_structure(v, path=f"{path}.{k}") for k, v in data.items()}
    
    if isinstance(data, list):
        return [cls.from_structure(v, path=f"{path}[{i}]") for i, v in enumerate(data)]
    
    # Base case: It's a semantic leaf
    return cls(id=path, value=data)
```

## 8. Introspection Capabilities

Once a Cell wraps an object, the system needs to "understand" the content without necessarily processing it. Here are the key capabilities for introspection.

### A. Type Inference (`.kind`)
**"What is this?"**
The Cell should expose high-level classifications, not just the raw Python type.
*   **Scalar:** `int`, `float`, `str`, `bool`
*   **Container:** `list`, `dict`, `set`
*   **Tabular:** `pd.DataFrame`, `polars.DataFrame`
*   **Tensor:** `np.array`, `torch.Tensor`
*   **Binary:** `bytes`, `Image`

```python
@property
def kind(self):
    if isinstance(self.value, (int, float)): return "Numeric"
    if hasattr(self.value, "columns"): return "Tabular"
    return "Object"
```

### B. Shape & Dimensions (`.shape`)
**"How big is this?"**
Standardizes size reporting across detailed types.
*   Scalar: `()`
*   List: `(N,)`
*   DataeFrame: `(Rows, Cols)`
*   Image: `(H, W, Channels)`

### C. The Preview Interface (`.peek()`)
**"Show me a glimpse."**
Cells holding large data (1GB CSVs) must provide a lightweight preview for UIs/Logs.
*   **Text:** First 50 chars...
*   **List:** First 3 items...
*   **Table:** `df.head(5)`
*   **Image:** A generic integer tuple `(1024x1024 Image)`

### D. Validation (`.valid()`)
**"Is this garbage?"**
Capabilities to check internal consistency.
*   `cell.is_empty` (Null/None check)
*   `cell.has_nan` (For numerical consistency)
*   `cell.schema` (Returns column names for tables, keys for dicts)

### E. Metadata Tags
**"What else do we know?"**
A dedicated dictionary `cell.meta` for arbitrary annotations.
*   `source`: "user_upload", "api_response"
*   `timestamp`: Creation time
*   `description`: Human readable docstring

## 9. The Compute Link: Motivating Fancy Functions

Cells are often not just static data holders; they are the **Outputs of Computation**. This introduces a critical requirement: The system must handle the *process* that fills the cell, not just the result.

This variance in computation motivates the need for **Fancy Functions**.

### The Computation Spectrum

Functions producing Cell values fall into two distinct categories that require different handling:

| Type | Characteristics | Examples | System Needs |
| :--- | :--- | :--- | :--- |
| **Lightweight** | CPU-bound, instant, synchronous. | `A + B`, `str.upper()`, `lookup` | **Zero Overhead.** Direct execution. No progress bars. |
| **Heavyweight** | IO-bound, slow, complex. | `query_db`, `run_ml_inference`, `scrape_url` | **Async implementation**, caching, retry logic, timeout handling, progress reporting. |

### Why "Plain" Functions Fail Here

If we just use raw Python functions to populate Cells, we hit the **Black Box Problem**:
1.  **Blocking:** A slow function freezes the entire Cell graph update.
2.  **Opacity:** We don't know *why* a Cell effectively "timed out."
3.  **Redundancy:** If `func(x)` takes 5 minutes, we must not run it twice for the same `x`.

### The Role of Fancy Functions
A "Fancy Function" is a wrapper around logic (similar to how a Cell wraps data) that bridges this gap:
*   It tells the Cell: "I am slow, put me in a background thread." (Async)
*   It tells the Cell: "I am deterministic, cache my result." (Memoization)
*   It tells the Cell: "I operate on Rows, not Tables." (Granularity Mapping)

This relationship—**Fancy Functions populate Generic Cells**—is the core architectural loop.

## 10. Defining Derived Cells (Functional Output)

To define a Cell that represents the *output* of a function, you have three primary patterns depending on whether you want a static snapshot or a live reactive link.

### Pattern A: The Snapshot (Static)
*Compute once, store forever.*
The function runs immediately, and the `Cell` just holds the dead result.

```python
# 1. Run the function
raw_result = process_data(input_cell.value)

# 2. Wrap the result
output_cell = Cell(raw_result)
```

### Pattern B: The Computed Cell (Reactive)
*Define the recipe, not the result.*
The Cell holds a reference to the function and its input cells. It automatically re-runs when inputs change.

```python
# Usage: Cell.computed(function, inputs...)
output_cell = Cell.computed(
    func=calculate_tax, 
    inputs=[price_cell, rate_cell]
)
```

### Pattern C: The Granular Application (Map/Apply)
*Apply a function across a collection cell to generate a collection of output cells.*

This effectively handles the **1-to-N** or **N-to-N** cases automatically.

#### 1. The Map (Broadcasting)
Running a scalar function over a list of cells.
```python
# Input: List of Cells [Cell(1), Cell(2)]
# Logic: def double(x): return x * 2

output_cells = Cell.map(double, input_cells) 
# Result: [Cell(2), Cell(4)]
# Each output cell depends only on its corresponding input cell.
```

#### 2. The Explode (Generator)
Running a generator function that takes 1 Cell and makes N Cells.
```python
# Input: Cell("A,B,C")
# Logic: def split_csv(txt): return txt.split(',')

output_cells = Cell.explode(split_csv, source_cell)
# Result: [Cell("A"), Cell("B"), Cell("C")]
# If source_cell changes, the LIST of output cells is rebuilt.
```

### Handling Function Arguments (Binding & Partials)

Often, functions require a mix of **Reactive Inputs** (Cells) and **Static Arguments** (Configuration).

#### 1. Mixed Arguments in `Cell.computed`
The system should distinguish between arguments that trigger updates (Cells) and arguments that are constant parameters.

```python
def fetch_data(url, timeout, retries):
    # url is dynamic, timeout/retries are static config
    pass

url_cell = Cell("http://api.com")

# Option A: Helper Wrapper
result_cell = Cell.computed(
    func=fetch_data,
    inputs=[url_cell],          # Watch these for changes
    kwargs={'timeout': 10, 'retries': 3} # Pass these as constants
)
```

#### 2. The `partial` Pattern (`functools`)
Pre-bind the static arguments before creating the cell. This is cleaner and more "Pythonic".

```python
from functools import partial

# Create a specialized version of the function
fetch_fast = partial(fetch_data, timeout=1, retries=0)

# The cell only sees the dynamic input
result_cell = Cell.computed(fetch_fast, inputs=[url_cell])
```

#### 3. The Lambda Pattern (Closure)
Useful for ad-hoc mappings or quick calculations involving constants.

```python
offset = 100
# Capture 'offset' in the closure
result_cell = Cell.computed(
    func=lambda x: x + offset, 
    inputs=[input_cell]
)
```

## 11. The "Fancy" Syntax: Decorator-Based Auto-Wiring

The `Cell.computed(...)` syntax is verbose. The user preference is for a cleaner, function-call style syntax where logic and graph construction look the same.

**Target Syntax:**
```python
result_cell = my_fancy_func(cell_a, arg_b, kwarg_c=10)
```

To achieve this, we introduce the `@fancy` (or `@reactive`) decorator.

### How it Works
The decorator intercepts the function call at runtime and performs **Argument Resolution**:

1.  **Inspection:** It looks at `*args` and `**kwargs`.
2.  **Segregation:** It separates inputs into:
    *   **Dependencies:** Arguments that are `Cell` instances.
    *   **Constants:** Arguments that are raw values (`int`, `str`, `df`).
3.  **Construction:** usage of the decorated function *returns a new Cell* (derived), not the raw value.
4.  **Auto-Unwrapping:** Inside the graph logic, it automatically unwraps `cell.value` before passing it to the underlying function, so the inner Python logic stays pure.

### Example Implementation Design

```python
@fancy
def calculate_total(price, tax_rate, discount=0.0):
    return price * (1 + tax_rate) - discount

# Setup
c_price = Cell(100)
c_tax   = Cell(0.05)

# Usage 1: All Cells
cell_1 = calculate_total(c_price, c_tax) 
# -> Returns Cell (Computed).
# -> Logic: Depends on [c_price, c_tax]. Uses default discount=0.0.

# Usage 2: Mixed Cells and Constants
cell_2 = calculate_total(c_price, tax_rate=0.08, discount=5.0)
# -> Returns Cell (Computed).
# -> Logic: Depends on [c_price]. keys 'tax_rate' and 'discount' are bound as constants.

# Usage 3: Overriding Defaults with Cells
c_disc = Cell(10)
cell_3 = calculate_total(c_price, 0.05, discount=c_disc)
# -> Returns Cell (Computed).
# -> Logic: Depends on [c_price, c_disc].
```

### Handling Default Arguments
The decorator must use `inspect.signature` to bind provided arguments to the function signature. This allows it to:
1.  Know that `discount` exists even if not passed.
2.  Use the default value (`0.0`) as a constant if the user doesn't provide a Cell.

This pattern makes the Reactive Graph definition code look almost identical to standard imperative Python code.

## 12. Functional Composition (Externalizing Map)

The user requirement is to keep the `Cell` class simple and not pollute it with methods like `.map()`. Instead, we use higher-order functions (decorators) to transform *how a function applies to its inputs*.

### The Goal
Transform a function that operates on a **Single Cell** into a function that operates on a **Collection of Cells**, producing a **Collection of Output Cells**.

**Syntax:**
```python
# Create the mapped function
vectorized_func = map_decorator(fancy_function)

# Use it
cells_b = vectorized_func(cells_a)
```

### 1. The `map_decorator` (aka `vectorize`)

This decorator redefines the function's input/output signature.
*   **Input:** An Iterable of Cells (or Values).
*   **Logic:** Applies the underlying `fancy_function` to each item.
*   **Output:** A List of Cells.

```python
def map_decorator(func):
    """
    Lifts a function (Cell -> Cell) to operate on (List[Cell] -> List[Cell]).
    """
    def wrapper(inputs, *args, **kwargs):
        # 1. Inputs is expected to be an iterable (List, Tuple, Generator)
        if not hasattr(inputs, '__iter__'):
            # Fallback for single item (strictness optional)
            inputs = [inputs]
            
        # 2. Apply the function to each element
        # 'func' here is likely already a @fancy function that handles
        # creating the output ComputedCell for a single input.
        return [func(item, *args, **kwargs) for item in inputs]
        
    return wrapper
```

### 2. Usage Example

```python
# 1. Define the atomic unit logic
@fancy
def process_item(cell_x, scale=1):
    # This logic assumes 'cell_x' is a single unit (e.g., one number)
    return cell_x * scale

# 2. Lift it
process_all = map_decorator(process_item)

# 3. Apply to data
# Assume inputs is [Cell(1), Cell(2), Cell(3)]
outputs = process_all(inputs, scale=10)

# Result:
# [
#   ComputedCell(fn=process_item, input=Cell(1), scale=10),
#   ComputedCell(fn=process_item, input=Cell(2), scale=10),
#   ComputedCell(fn=process_item, input=Cell(3), scale=10)
# ]
```

### 3. Why this approach?
1.  **Separation of Concerns:** The `Cell` class doesn't need to know about lists or iteration.
2.  **Reusable Logic:** The `process_item` function logic is written for the simplest case (1 item).
3.  **Flexibility:** You can choose to apply `process_item` to a single cell `process_item(c)` or a list `process_all(list_c)` without rewriting the math.




