# Functional Decorator Taxonomy

We can use Python decorators to "lift" simple functions into higher-dimensional operators. This creates a computational algebra where a single logical definition can be applied to scalars, arrays, or tables depending on the decorator used.

## 5. Full Mapping Matrix

Here is the complete operator taxonomy representing the computational algebra of Excel-like functions:

| Input Dim | Output Dim | Name | Example |
| :--- | :--- | :--- | :--- |
| **1** | **1** | **Scalar** | `=A1+1` |
| **N** | **1** | **Reduction** | `=SUM(A:A)` |
| **1** | **N** | **Generator** | `=SEQUENCE(10)` |
| **N** | **N** | **Map** | `=A:A*2` |
| **N** | **M** | **Relational** | `=FILTER(A:A,A:A>0)` |
| **NxM** | **NxM** | **Table Map** | `=A:C*2` |
| **NxM** | **1** | **Aggregate** | `=SUM(A:C)` |
| **NxM** | **KxL** | **Pivot** | `=PIVOT(...)` |

## Decorator Implementations

Below are example implementations of how to modify a base function to fit specific roles in the taxonomy.

### 1. The Mapper (N → N)
*Takes a Scalar (1→1) function and broadcasts it over a list.*

```python
def as_map(func):
    """
    Transforms a 1->1 scalar function into an N->N map.
    Example: Applies existing logic to every item in a column.
    """
    def wrapper(data, *args, **kwargs):
        if isinstance(data, list):
            return [func(x, *args, **kwargs) for x in data]
        # Fallback for scalar input
        return func(data, *args, **kwargs)
    return wrapper

# Usage
@as_map
def double(x):
    return x * 2

# double([1, 2, 3]) -> [2, 4, 6]
```

### 2. The Reducer (N → 1)
*Takes a function that expects a list and ensures it receives one, even if passed a single value.*

```python
def as_reduction(func):
    """
    Ensures input is strictly iterable for reduction logic.
    """
    def wrapper(data, *args, **kwargs):
        if not isinstance(data, (list, tuple)):
            data = [data]
        return func(data, *args, **kwargs)
    return wrapper
```

### 3. The Table Mapper (NxM → NxM)
*Takes a Scalar (1→1) function and applies it to every cell in a 2D matrix.*

```python
def as_table_map(func):
    """
    Applies a scalar function to every cell in a 2D matrix (list of lists).
    """
    def wrapper(matrix, *args, **kwargs):
        # Assumes matrix is List[List[Any]]
        return [
            [func(cell, *args, **kwargs) for cell in row]
            for row in matrix
        ]
    return wrapper
```

### 4. The Generator (1 → N)
*Standardizes functions that explode a single input into a sequence.*

```python
def as_generator(func):
    """
    Wraps logic to ensure the output is always a materialized list.
    """
    def wrapper(n, *args, **kwargs):
        result = func(n, *args, **kwargs)
        return list(result)
    return wrapper
```

### 5. The Relational Filter (N → M)
*Selects a subset of inputs based on a condition.*

```python
def as_relational(func):
    """
    Acts as a filter. The decorated function should return a Boolean.
    Input: List of N items.
    Result: List of M items (where M <= N) for which func(item) is True.
    """
    def wrapper(inputs, *args, **kwargs):
        return [x for x in inputs if func(x, *args, **kwargs)]
    return wrapper
```

### 6. The Aggregate (NxM → 1)
*Summarizes a 2D Matrix into a single value.*

```python
def as_aggregate(func):
    """
    Flattens a matrix to a single list before applying a reduction logic.
    """
    def wrapper(matrix, *args, **kwargs):
        # Flatten: [[1,2], [3,4]] -> [1,2,3,4]
        flat_list = [cell for row in matrix for cell in row]
        return func(flat_list, *args, **kwargs)
    return wrapper
```

### 7. The Pivot (NxM → KxL)
*Reshapes or Summarizes a table into a new table.*

```python
def as_pivot(func):
    """
    Takes a 2D matrix, applies logic, expects a 2D matrix back.
    Mostly a pass-through identity wrapper for semantic clarity.
    """
    def wrapper(matrix, *args, **kwargs):
        result = func(matrix, *args, **kwargs)
        # Optional validation: Ensure result is List[List]
        return result
    return wrapper
```

## Summary of Intuitive Decorator Names

To make this "Idiot Proof" and readable, we should alias these technical implementations to friendly names:

| Pattern | Technical Name | Friendly Decorator | Logic It Expects |
| :--- | :--- | :--- | :--- |
| **1 → 1** | Scalar | `@apply` | `f(x) -> y` (Simple Math) |
| **N → 1** | Reduction | `@reduce` | `f(list) -> y` (Sum, Avg) |
| **1 → N** | Generator | `@expand` | `f(x) -> list` (Split, Range) |
| **N → N** | Map | `@vectorize` | `f(x) -> y` (applied to all) |
| **N → M** | Relational | `@filter` | `f(x) -> bool` (Keep checks) |
| **NxM → NxM** | Table Map | `@grid_apply` | `f(x) -> y` (applied to all cells) |
| **NxM → 1** | Aggregate | `@summarize` | `f(list) -> y` (Total) |
| **NxM → KxL** | Pivot | `@reshape` | `f(matrix) -> matrix` |