# Fancy Function Decorators & Iteration Strategies

To enable "Iterative Analysis" on sets of cells of arbitrary size without writing loops in every function, we provide a suite of decorators. These decorators handle the **Shape Transformation** of the data.

## 1. The Operator Taxonomy

This table defines which decorator to use based on the **Dimensions** of your Input and Output.

| Decorator | Input | Output | Name | Excel Equivalent |
| :--- | :--- | :--- | :--- | :--- |
| **`@apply`** (Default) | 1 | 1 | Scalar | `=A1+1` |
| **`@reduce`** | N | 1 | Reduction | `=SUM(A:A)` |
| **`@expand`** | 1 | N | Generator | `=SEQUENCE(10)` |
| **`@vectorize`** | N | N | Map | `=ArrayFormula(A:A*2)` |
| **`@filter`** | N | M | Relational | `=FILTER(...)` |
| **`@grid_apply`** | NxM | NxM | Table Map | `=A1:C10 * 2` |
| **`@summarize`** | NxM | 1 | Aggregate | `=SUM(A1:C10)` |
| **`@reshape`** | NxM | KxL | Pivot | `=TRANSPOSE(...)` |

---

## 2. The Core Decorators

These decorators wrap your pure Python functions to handle the "Fancy" logic (Cells, Graph Connections, and Iteration).

### The Standard: `@apply` (1 -> 1)
*Alias for `@fancy`.*
Use this for simple, atomic logic. It runs **once** per cell.
```python
@apply
def to_upper(text: str) -> str:
    return text.upper()

# Usage:
# c_out = to_upper(c_in)
```

### The iterator: `@vectorize` (N -> N)
*Use this to apply 1->1 logic to a list of arbitrary size.*
The decorator iterates over the input list, creating a new Output Cell for each Input Cell.
```python
@vectorize
def double(x: int) -> int:
    return x * 2

# Usage:
# cells_in = [Cell(1), Cell(2), Cell(3)]
# cells_out = double(cells_in) 
# -> [Cell(2), Cell(4), Cell(6)]
```

### The Sieve: `@filter` (N -> M)
*Use this to select a subset of cells.*
The decorated function must return `True` or `False`.
```python
@filter
def is_positive(x: int) -> bool:
    return x > 0

# Usage:
# cells_in = [Cell(1), Cell(-5), Cell(3)]
# cells_out = is_positive(cells_in)
# -> [Cell(1), Cell(3)]
```

### The Cruncher: `@reduce` (N -> 1)
*Use this to collapse a list into a single value.*
The decorator ensures the function receives the list of **Values**, not Cells (it unwraps them automatically).
```python
@reduce
def calculate_mean(values: list) -> float:
    return sum(values) / len(values)

# Usage:
# c_mean = calculate_mean(cells_in)
# -> Cell(2.0)
```

### The Spawner: `@expand` (1 -> N)
*Use this to generate multiple cells from one input.*
The decorator takes a list of values returned by the function and wraps each one in a new Cell.
```python
@expand
def get_user_posts(user_id: str) -> list:
    # returns ["Post A", "Post B"]
    return fetch_posts(user_id)

# Usage:
# list_of_cells = get_user_posts(cell_user_id)
# -> [Cell("Post A"), Cell("Post B")]
```

### Universal Alias: `@apply_to_all`

*The "Just Do It" decorator.*
This is a smart alias that encompasses both `vectorize` (N->N) and `grid_apply` (NxM->NxM). It inspects the input at runtime to decide how to iterate.

*   If Input is **List (1D)**: Acts like `@vectorize`.
*   If Input is **Matrix (2D)**: Acts like `@grid_apply`.

```python
@apply_to_all
def clean_text(text):
    return text.strip()

# Works on a list of cells
clean_list = clean_text(list_of_cells)

# Works on a table of cells
clean_table = clean_text(matrix_of_cells)
```

---

## 3. Matrix Decorators (2D Analysis)

When dealing with tables (`ListOf[ListOf[Cell]]` or DataFrames), specific iterators help manage the grid.

### `@grid_apply` (NxM -> NxM)
Applies a function to every single cell in a table.
*   **Input:** Matrix of Cells.
*   **Logic:** `x * 2`
*   **Output:** Matrix of Computed Cells.

### `@summarize` (NxM -> 1)
Flattens the entire table and reduces it.
*   **Input:** Matrix of Cells.
*   **Logic:** `sum(all_values)`
*   **Output:** Single Computed Cell.

### `@reshape` (NxM -> KxL)
Allows transforming the structure (e.g., Pivot, Transpose).
*   **Input:** Matrix.
*   **Logic:** `df.pivot(...)`
*   **Output:** New Matrix of Cells.

---

## 4. Why this matters?

By using these decorators, the user **never writes a loop**.

*   **Wrong:**
    ```python
    outputs = []
    for c in inputs:
        outputs.append(my_func(c))
    ```
*   **Right:**
    ```python
    @vectorize
    def my_func(x): ...
    
    outputs = my_func(inputs)
    ```

This ensures the **Dependency Graph** is built correctly by the framework, not hacked together by the user.
