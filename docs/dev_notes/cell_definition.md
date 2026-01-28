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

## 4. Object Decomposition Patterns

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

## 5. Intuitive Mental Model: The "Cellification" Spectrum

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
