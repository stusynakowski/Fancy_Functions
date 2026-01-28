# Refactor Specification: Collection Broadcasting & Composite Cells

## 1. Introduction
This specification defines the architectural changes required to support collections of data ("Composite Cells") and the automatic iteration of logic over these collections ("Broadcasting"). This moves the system from a linear 1-to-1 execution model to a dynamic 1-to-N or N-to-N model, enabling "spreadhseet-like" operations on rows of data.

## 2. Data Structure Updates

### 2.1 StorageKind.COMPOSITE
A new or formalized storage kind used to represent a collection of other cells.

- **Type Definition**:
  - `kind`: `StorageKind.COMPOSITE`
  - `value`: `List[UUID]` (standard ordered list) or `Dict[str, UUID]` (structured record).
- **Constraints**:
  - A Composite Cell DOES NOT store data values directly. It only stores references (UUIDs) to other cells.
  - Immutability: Once created, the list of UUIDs usually shouldn't change, though the workflow may append if defining an accumulator (implementation detail).

### 2.2 DatumStore Resolution
The `DatumStore` must be improved to handle retrieval of these complex structures.

- **`resolve(cell_id, recursive=False)`**:
  - **Input**: UUID of a cell.
  - **Behavior**:
    - If `recursive=False` (default for internal logic): Returns the raw value (e.g., the `List[UUID]`).
    - If `recursive=True` (for user output or specific function needs): Recursively resolves the values of children.
      - *Example*: Resolving a Composite of Integers returns `[1, 2, 3]` instead of `[uuid1, uuid2, uuid3]`.


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

For details on **Representation & Inspection**, **Workflow Accessors**, **Step Introspection**, **Simplified Construction Syntax**, and **Data Flow Visualization**, please refer to [010-data-printing-representation.md](./010-data-printing-representation.md). This content has been moved to keep specifications focused.

