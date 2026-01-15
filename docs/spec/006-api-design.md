# API Design & Usage

## 1. The @step Decorator (The Factory)
The `@step` decorator is the bridge between pure Python code and the Workflow Engine. It abstracts away all complexity of data loading and saving.

```python
from fancy_core import step

@step(
    slug="apply_sentiment",
    name="Sentiment Analysis",
    description="Calculates sentiment score for text column."
)
def apply_sentiment(df: "pandas.DataFrame", target_col: str) -> "pandas.DataFrame":
    # USER CODE: Pure Logic.
    # The user receives a real DataFrame. They return a real DataFrame.
    # They do NOT know or care if 'df' came from memory, S3, or a SQL DB.
    
    df[target_col + "_score"] = df[target_col].apply(analyze)
    return df
```

## 2. Functional Composition (Building the Graph)
Users build workflows by "calling" these functions. The decorator intercepts the call to wire the cells together.

```python
from fancy_core import Workflow, create_cell

# 1. Initialize Workflow
wf = Workflow(name="Sentiment Pipeline")

# 2. Define Inputs (Initial Cells)
raw_data_cell = create_cell(alias="Raw Data", value=load_csv("data.csv"))

# 3. Chain Steps (Orchestration)
# Calling the decorated function returns a Step + Output Cell(s)
# It does NOT run the code yet.
step1_out = apply_sentiment(df=raw_data_cell, target_col="reviews")

# 4. Add to Workflow
wf.add(step1_out)
```

## 3. Serialization
The resulting workflow object can be serialized to the specific JSON format.

```python
print(wf.to_json())
# {
#   "steps": [
#     { 
#       "function": "apply_sentiment", 
#       "inputs": { "df": "cell-uuid-1" },
#       "config": { "target_col": "reviews" }
#     }
#   ]
# }
```

## 4. Execution (The Engine)
The engine takes the Blueprints (Workflow) and the Materials (Context/Cells) to perform the work.

```python
from fancy_core import Engine

engine = Engine()
result = engine.run(workflow=wf)

print(result.status) # "completed"
```

## 5. Detailed Class Interface

### `RuntimeContext`
Responsible for holding state.
- `store(key: str, value: Any)`
- `retrieve(key: str) -> Any`
- `latest() -> Any`: Helper to get the output of the most recent step.

### `Engine`
- `run_step(step, context)`: Execute single step.
- `run(workflow, context)`: Execute all.

## 6. Error Handling Strategy
- If a step raises an Exception, the `Engine` catches it.
- The Step's status is set to `FAILED`.
- The Exception message and traceback are stored in `step.error_message`.
- The Workflow execution halts (unless `continue_on_error` is set, though linear workflows usually require stop).
