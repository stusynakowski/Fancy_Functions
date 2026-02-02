# Fancy Function Usage Guide

This document outlines the usage patterns for **Fancy Functions**, the core mechanism for creating reactive computations in the Fancy Functions framework.

## 1. The Core Philosophy

The library is designed to make reactive programming look like imperative programming.
*   You write standard Python functions.
*   You decorate them with `@fancy`.
*   When called with `Cells`, they return `Cells`.

## 2. Defining a Fancy Function

A "Fancy Function" is just a pure Python function wrapped with the `@fancy` decorator.

```python
from fancy_core import fancy, Cell

@fancy
def calculate_price(cost: float, margin: float = 0.2, tax: float = 0.05) -> float:
    """
    Pure logic. Knows nothing about Cells, Graphs, or Reactivity.
    """
    return cost * (1 + margin) * (1 + tax)
```

## 3. Using Fancy Functions (The "Auto-Wiring" Syntax)

When you call a decorated function, the behavior adapts based on the inputs.

### A. Reactive Mode (Creating the Graph)
Passing **Cells** as arguments creates a live dependency link. The result is a new `Cell` that updates whenever inputs change.

```python
# Setup Inputs
cost_cell = Cell(100)
margin_cell = Cell(0.25)

# 1. Fully Reactive
price_cell = calculate_price(cost_cell, margin_cell, tax=0.1)
# Result: price_cell is a ComputedCell.
# Logic: Updates if cost_cell OR margin_cell changes. Tax is fixed at 0.1.

# 2. Mixed Inputs (Cells + Constants)
price_cell_2 = calculate_price(cost_cell, margin=0.5)
# Result: price_cell_2 depends ONLY on cost_cell. 
# Margin is fixed at 0.5. Tax uses default (0.05).
```

### B. Direct Mode (Bypass)
Passing raw values (no Cells) works just like a normal function call. This is useful for debugging or simple scripts.

```python
final_price = calculate_price(100, margin=0.2)
# Result: 126.0 (float)
# No overhead. No graph creation.
```

## 4. Vectorization (Mapping Lists of Cells)

To apply a function that works on a single item to a list of items, use the `vectorize` (or `map_decorator`) helper. **Do not modify the original function.**

```python
from fancy_core import vectorize

# 1. Existing atomic logic
@fancy
def double(x):
    return x * 2

# 2. Create a version that accepts Lists of Cells
double_all = vectorize(double)

# 3. Usage
input_cells = [Cell(1), Cell(2), Cell(3)]
output_cells = double_all(input_cells)

# Result: [Cell(2), Cell(4), Cell(6)]
# Each output cell is independently linked to its corresponding input.
```

## 5. Summary of Decorators

| Decorator | Role | Input Signature | Output Signature |
| :--- | :--- | :--- | :--- |
| `@fancy` | **The Builder.** Connects logic to the graph. | `func(val, ...)` | `func(Cell, ...) -> Cell` |
| `vectorize(func)` | **The Broadcaster.** Applies 1-to-1 logic over N items. | `func(Cell)` | `func(List[Cell]) -> List[Cell]` |

## 6. Best Practices

1.  **Keep Functions Pure:** Your decorated functions should not have side effects (printing, saving files). Side effects belong in `Observers`, not `Fancy Functions`.
2.  **Granularity Matches Logic:** If your function adds two numbers, write it for two numbers. Use `vectorize` if you have lists of numbers. Don't write the function to accept lists unless the logic *requires* the whole list (e.g., `sum` or `sort`).
3.  **Explicit Kwargs:** When mixing Cells and Constants, naming your arguments (validating against the signature) is safer than relying on position.

## 7. Handling Expensive Operations (Lazy & Defers)

When functions are "Too Expensive to be Reactive" (e.g., API calls, heavy ML models), we must decouple the *definition* of the Cell from the *execution* of the logic.

### A. The Definition: Placeholder Cells
A Cell created from a lazy function acts as a **Recipe/Placeholder**. It contains the definition (Function + Arguments) but holds no value (or a `Pending` state).

```python
@fancy(lazy=True)
def run_heavy_model(data, params):
    # Imagine this takes 30 seconds
    return model.predict(data, params)

# 1. Definition (Instant)
# Returns a ComputedCell marked as 'dirty' or 'pending'.
result_cell = run_heavy_model(input_cell, params={'iter': 1000})

# At this point:
# result_cell.value is None (or Deferred)
# result_cell.has_value is False
# result_cell.recipe is (run_heavy_model, input_cell, {'iter': 1000})
```

### B. The Execution Strategies

Once we have these placeholder cells, we need a strategy to compute them.

#### 1. Manual Trigger (`.compute()`)
The user explicitly requests the value. This ensures control over when resources are spent.
```python
# Blocks until finished
val = result_cell.compute() 
```

#### 2. Async / Background Execution
Ideally, heavy functions offload to a thread or worker.
```python
# Returns a Future/Task object immediately
future = result_cell.compute_async()

# Later...
if future.done():
    print(result_cell.value)
```

#### 3. The "Loading" State
Ideally, a Lazy Cell should expose a way to check its status so usage in UIs is graceful.
```python
if result_cell.is_pending:
    return "Loading..."
else:
    return result_cell.value
```

### C. Design Pattern: The "Plan then Run"
This is effectively a DAG (Directed Acyclic Graph) execution engine.
1.  **Phase 1 (Planning):** Run your python script. It instantiates thousands of Cells. No computation happens. All cells are "Placeholders" connected by edges.
2.  **Phase 2 (Optimization):** (Optional) The engine looks at the graph. It sees 50 calls to `run_heavy_model`.
3.  **Phase 3 (Execution):** You call `graph.execute()`. The engine runs the functions in parallel/batch based on the dependency tree.

## 8. The "Idiot-Proof" Syntax (Excel Mode)

You asked for the syntax to be "Idiot Proof in the same way Excel is."

**What makes Excel idiot proof?**
1.  **Reference transparency:** cell "A1" is just "A1", you don't care if it's computed or static.
2.  **No explicit graph building:** You don't "add edges," you just use values.
3.  **Automatic resolution:** If you ask for a value, Excel figures out how to get it. You never have to manually call `.compute()`.

### Implementation: The `value` Property Magic

To achieve this in Python, the `Complex(Graph)` complexity MUST be hidden behind the simple `cell.value` property (or `__getitem__` / `__repr__`).

#### 1. Just ask for the value
The user should never need to know if a cell is Lazy, Eager, Async, or Cached.

```python
# The User View
c_a = Cell(10)
c_b = expensive_func(c_a) # Takes 5 seconds, is Lazy

print("Doing other stuff...")
# ...

# The "Idiot Proof" moment:
print(c_b.value) 
# -> The system detects the value is missing.
# -> The system triggers the computation automatically (blocking if needed).
# -> The system returns the result.
```

#### 2. Chaining just works
Because every operation returns a Cell, you can chain them without thinking about the graph.

```python
# Excel: =UPPER(TRIM(A1))
# Python:
c_result = func_upper(func_trim(c_a1))

# The user didn't build a graph consciously. 
# They just nested functions function calls.
```

#### 3. Operator Overloading (The Ultimate Excel Feel)
Ideally, basic math should work without `@fancy` functions visible to the user.

```python
c_a = Cell(10)
c_b = Cell(20)

# "A1 + B1"
c_total = c_a + c_b 

# Behind the scenes:
# This creates a ComputedCell(lambda x,y: x+y, inputs=[c_a, c_b])
```

### Summary of the "Idiot Proof" Contract

1.  **Defining:** Just call functions. `y = f(x)`.
2.  **Reading:** Just access `.value`. `print(y.value)`.
3.  **Updating:** Just set `.value`. `x.value = 5`. `y` updates automatically.

No `.compute()`, no `.build_graph()`, no `dag.execute()`. Just Cells and Values.