# Specification: Data Printing & Representation

## 1. Overview
The `Fancy_Functions` library prioritizes "Development by Inspection." When a user prints a core component (`Workflow`, `Step`, or `Cell`), the output must be informative, structured, and visually clear. This allows users to understand their data pipeline's structure and state without needing external visualization tools.

This specification defines the string representations for:
1.  **Workflows**: The high-level execution plan and status.
2.  **Steps**: Detailed Input -> Operation -> Output mapping.
3.  **Data Flow**: Visualizing the transformation of data across the pipeline.

## 2. Representation & Inspection

To support both **Architectural Design** (Process) and **Data Analysis** (Data), the Workflow object provides two distinct viewing modes.

### 2.1 The Process View (Default)
**Usage:** `print(workflow)`
**Focus:** The Logic Sequence.
Shows distinct processing steps, what functions are called, and their wiring status. Ideal for understanding *what the machine is doing*.

```text
Workflow: Youtube Channel Analysis (Process View)
-------------------------------------------------------------------------------
IDX  STEP NAME        FUNCTION        INPUTS           OPERATION    STATUS
-------------------------------------------------------------------------------
0    Fetch URLs       load_urls       (sitemap.xml)    Standard     [Done]
1    Extract Titles   extract_title   (Step 0)         Broadcast    [Done]
2    Format           prepend_text    (Step 1, '...')  Broadcast    [Done]
3    Count            count_items     (Step 2)         Aggregate    [Pending]
-------------------------------------------------------------------------------
```

### 2.2 The Data View (Pipeline Matrix)
**Usage:** `print(workflow.data_view())` or `workflow.show_data()`
**Focus:** The Data Transformation.
Rotates the perspective to show Steps as Columns and Data Items as Rows (where applicable). Ideal for verifying *what the data looks like* at each stage.

```text
Workflow Data Matrix: Youtube Channel Analysis
-------------------------------------------------------------------------------
ROW # | 0: Fetch URLs      | 1: Extract Titles    | 2: Format Data       
-------------------------------------------------------------------------------
0     | "http://yt.../a"   | "Python Tutorial"    | "Title: Python Tu..."
1     | "http://yt.../b"   | "Cats Video"         | "Title: Cats Vide..."
2     | "http://yt.../c"   | "Music Video"        | "Title: Music Vid..."
...   | ...                | ...                  | ...                  
49    | "http://yt.../z"   | "Gaming"             | "Title: Gaming"      
-------------------------------------------------------------------------------
* Note: Step 3 (Count) is an Aggregation (50 -> 1) and starts a new matrix block or summary.
```

### 2.3 The Step Inspection (The Intersection)
**Usage:** `print(workflow[1])`
**Focus:** The Micro-Process.
The Step view bridges the two worlds. It reveals exactly how the **Process** (Function) transforms the **Input Data** into **Output Data** for that specific node.

**Example: Broadcast (Row-wise Operation)**
```text
Step: Extract Titles (Index 1)
Operation: Broadcast (1-to-N) | Function: extract_title
-------------------------------------------------------------------------------
IDX   INPUT (Composite)                -> MAPPED FUNC    -> OUTPUT (Composite)
-------------------------------------------------------------------------------
0     [Cell A] "https://yt.com/v1"     -> extract_title() -> [Cell X] "Title 1"
1     [Cell B] "https://yt.com/v2"     -> extract_title() -> [Cell Y] "Title 2"
2     [Cell C] "https://yt.com/v3"     -> extract_title() -> [Cell Z] "Title 3"
...   ...                              -> ...            -> ...
49    [Cell N] "https://yt.com/v50"    -> extract_title() -> [Cell Ω] "Title 50"
-------------------------------------------------------------------------------
```

**Example: Aggregation (Many-to-One)**
```text
Step: Count (Index 3)
Operation: Aggregation | Function: count_items
-------------------------------------------------------------------------------
IDX   INPUT (Composite)                  -> MAPPED FUNC      -> OUTPUT (Atomic)
-------------------------------------------------------------------------------
0     [Cell X] "Title 1"                 \
1     [Cell Y] "Title 2"                  |
2     [Cell Z] "Title 3"                  } -> count_items() -> [Cell 99] 50
...   ...                                 |
49    [Cell Ω] "Title 50"                /
-------------------------------------------------------------------------------
```

**Example: Unpack / Generator (One-to-Many)**
This visualizes steps that produce multiple outputs per input (e.g., getting multiple comments for a single video, or splitting a transcript).

```text
Step: Get Comments (Index 2)
Operation: Broadcast + Unpack | Function: fetch_comments
-------------------------------------------------------------------------------
IDX   INPUT (Composite)                -> MAPPED FUNC      -> OUTPUT (Nested Composite)
-------------------------------------------------------------------------------
0     [Cell A] "Video 1"               -> fetch_comments() -> [Composite] (3 items)
                                                              ├── [Cell 101] "Nice!"
                                                              ├── [Cell 102] "First"
                                                              └── [Cell 103] "Cool"
                                                              
1     [Cell B] "Video 2"               -> fetch_comments() -> [Composite] (2 items)
                                                              ├── [Cell 104] "Bad"
                                                              └── [Cell 105] "Why?"
...
-------------------------------------------------------------------------------
```

## 3. Workflow Accessors
The `Workflow` class implements `__getitem__` to support intuitive random access to Steps.

- **Index Access**: `workflow[0]` returns the first Step object.
- **Name Access**: `workflow['Process Rows']` returns the Step object by its alias/name.
- **Iteration**: `for step in workflow:` iterates through steps in execution order.

## 4. Step Introspection
Step objects provide direct access to their components for review.

```python
step = workflow['Process Rows']

# Accessing Inputs
# Returns the actual Cell object (or list of Cells) fed into this step
input_cell = step.inputs[0] 
print(input_cell.value)  # e.g., List of URLs

# Accessing Function
# Returns the FancyFunction wrapper
func = step.function
print(func.name)         # 'extract_meta'
print(func.docstring)    # Function documentation

# Accessing Output
// ...existing code...
# Returns the Cell object produced by this step
output_cell = step.output
print(output_cell.kind)  # StorageKind.COMPOSITE
# If composite, iterate the children
for child_id in output_cell.value:
    child_cell = store.get(child_id)
    print(child_cell.value)
```

## 5. Data Flow Visualization (`wf.show_data`)
// ...existing code...
To visualize the data lineage, the `show_data()` method renders a **Left-to-Right "Spreadsheet" View**. This displays steps as columns and maps individual cells (rows) across the transformation.

**Example Output**:
```text
FLOW MAP: Youtube Channel Analysis
-----------------------------------------------------------------------------------------------
STEP 0: Fetch URLs       STEP 1: Extract Titles   STEP 2: Format           STEP 3: Count
---------------------    ----------------------   ----------------------   --------------------
[Cell A] "yt.com/1"  --> [Cell X] "Title 1"   --> [Cell M] "Title 1" \
[Cell B] "yt.com/2"  --> [Cell Y] "Title 2"   --> [Cell N] "Title 2"  +--> [Cell 99] 50
[Cell C] "yt.com/3"  --> [Cell Z] "Title 3"   --> [Cell O] "Title 3" /
...                      ...                      ...
-----------------------------------------------------------------------------------------------
```

**Features**:
1.  **Columns as Steps**: Each step is a vertical column.
2.  **Rows as Data**: Individual cells are aligned to show their lineage.
3.  **Connectors**: Arrows (`-->`, `+-->`) visualize the operation type (1-to-1 Broadcast vs Many-to-1 Aggregation).

## 6. Cell Representation (`print(cell)`)
When a user inspects a `Cell` object directly, the output should be structured to clearly distinguish its identity, metadata, and content. This ensures clarity when debugging specific data points.

**Format Structure**:
1.  **Header**: `Cell: <Name/ID>`
2.  **Metadata**: A key-value block showing type, storage kind, and other meta fields.
3.  **Value**: The actual data contained, formatted for readability (e.g., truncated if too long).

**Example Output**:
```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  Cell: Title 1 (ID: X)                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  METADATA                                                                    │
│    - Type:        <class 'str'>                                              │
│    - Kind:        StorageKind.ATOMIC                                         │
│    - Created By:  Step 1 (Extract Titles)                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  VALUE                                                                       │
│  "Title 1"                                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Example Output (Composite)**:
```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  Cell: Processed Batch (ID: Y)                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│  METADATA                                                                    │
│    - Type:        Composite (List)                                           │
│    - Kind:        StorageKind.COMPOSITE                                      │
│    - Size:        3 items                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  CONTENTS                                                                    │
│  [0] -> Cell(ID: A..., Alias: "Title A")                                     │
│  [1] -> Cell(ID: B..., Alias: "Title B")                                     │
│  [2] -> Cell(ID: C..., Alias: "Title C")                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 7. Function Representation (`print(func)`)
When a user prints a `FancyFunction` object, the output should clearly define its purpose and the data transformation it performs (what it maps inputs to).

**Format Structure**:
1.  **Header**: `Function: <Name> (<Slug>)`
2.  **Description**: A brief summary of what the function does.
3.  **Mapping Contract**: A clear visualization of the expected input types and the resulting output type.

**Example Output**:
```text
Function: Extract Title (extract_title)
-------------------------------------------------------------------------------
DESCRIPTION
Extracts the <title> tag content from an HTML string.
-------------------------------------------------------------------------------
MAPPING
Input (url: str)  -->  [ extract_title ]  -->  Output (title: str)
-------------------------------------------------------------------------------
```
