# Cell to Cell Mapping with Functions

To map one cell to another using a function, you follow a simple pattern:
1. Define a function with the `@step` decorator.
2. Create your input `FancyCell`.
3. Call the decorated function passing the cell as an argument.

This process ("wiring") creates a new `FancyCell` that represents the future output of that function.

## Example

```python
from fancy_core.cells import FancyCell
from fancy_core.decorators import step

# 1. Define your transformation function (The Mapper)
@step
def double_number(value: int) -> int:
    """Doubles the input value."""
    return value * 2

# 2. Create your source cell
# This cell holds the initial data.
input_cell = FancyCell.create_value(21, "My Input")

# 3. Map the cell
# Pass the input_cell to the function. 
# The function will return a 'StepWiring' object containing the output cell.
wiring = double_number(value=input_cell)

# Access the resulting output cell
output_cell = wiring.outputs

print(f"Mapped {input_cell.alias} to {output_cell.alias}")
# Output: Mapped My Input to double_number_out
```

In this example, `output_cell` is a `PENDING` cell. It will be populated with the value `42` once the workflow is executed by the `Engine`.
