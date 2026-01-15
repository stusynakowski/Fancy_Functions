# Specification: Fancy Cells# Specification: Fancy Cells# Specification: Fancy Cells



## 1. Definition

The **Fancy Cell** is the fundamental atomic unit of data within the Fancy Functions ecosystem. It acts as the universal container for all information flowing through a workflow.

## 1. Definition## 1. Definition

- **Universal Wrapper:** Whether it is a single integer, a user profile JSON, a 10TB CSV file, or a CAD drawing, it is wrapped in a `FancyCell`.

- **Identity:** Every piece of data has a unique identity and a lifecycle.The **Fancy Cell** is the fundamental atomic unit of data within the Fancy Functions ecosystem. It acts as the universal container for all information flowing through a workflow.The **Fancy Cell** is the fundamental atomic unit of data within the Fancy Functions ecosystem. It acts as the universal container for all information flowing through a workflow.

- **Traceability:** Because every input and output is a Cell, lineage can be tracked precisely.



## 2. Core Attributes

Every Fancy Cell must possess the following properties:- **Universal Wrapper:** Whether it is a single integer, a user profile JSON, a 10TB CSV file, or a CAD drawing, it is wrapped in a `FancyCell`.- **Universal Wrapper:** Whether it is a single integer, a user profile JSON, a 10GB CSV file, or a CAD drawing, it is wrapped in a `FancyCell`.



*   **ID:** A globally unique identifier (UUID) ensuring the specific instance of data is addressable.- **Identity:** Every piece of data has a unique identity and a lifecycle.- **Identity:** Every piece of data has a unique identity and a lifecycle.

*   **Alias:** A human-readable label (e.g., "Cleaned Transaction Data", "User 101 Receipt").

*   **Type Hint:** A descriptor of what kind of data is held (e.g., `pandas.DataFrame`, `dict`, `image/png`).- **Traceability:** Because every input and output is a Cell, lineage can be tracked precisely.- **Traceability:** Because every input and output is a Cell, lineage can be tracked precisely.

*   **Storage Kind:** Indicates if the data is stored by value, by reference, or as a group.



## 3. Storage Strategy

The defining feature of a Fancy Cell is its ability to handle data of any size via a multi-mode representation.## 2. Core Attributes## 2. Core Attributes



### 3.1 Mode A: Value (By Content)Every Fancy Cell must possess the following properties:Every Fancy Cell must possess the following properties:

Used for "Small Data" that natively fits into JSON (strings, numbers, booleans, small dicts/lists).

*   **Use Case:** Configuration parameters, single database records, API responses, status flags.



### 3.2 Mode B: Reference (By Pointer)*   **ID:** A globally unique identifier (UUID) ensuring the specific instance of data is addressable.*   **ID:** A globally unique identifier (UUID) ensuring the specific instance of data is addressable.

Used for "Big Data" or binary objects (DataFrames, Images, Models, Folders). The Cell contains metadata and a pointer.

*   **Use Case:** A 1M row DataFrame, a trained Neural Network, a directory of PDFs.*   **Alias:** A human-readable label (e.g., "Cleaned Transaction Data", "User 101 Receipt").*   **Name:** A human-readable label (e.g., "Cleaned Transaction Data", "User 101 Receipt").

*   **Reference Meta:** Allows the UI/API to inspect the object (e.g., show columns) without loading the heavy payload.

*   **Type Hint:** A descriptor of what kind of data is held (e.g., `pandas.DataFrame`, `dict`, `image/png`).*   **Type Kind:** A descriptor of what kind of data is held (e.g., `pandas.DataFrame`, `dict`, `image/png`).

### 3.3 Mode C: Composite (Cell-of-Cells)

Used to group existing cells into a logical unit. *   **Storage Kind:** Indicates if the data is stored by value or by reference.*   **Content:** The actual payload (or reference to it).

*   **Use Case:** Grouping a "Training Set" (X_train, y_train) or a "Project Bundle".

*   **Structure:** The `value` contains a list or dictionary of `UUID`s pointing to other cells.

*   **Benefit:** Allows operations to pass around complex hierarchies as a single unit without hiding the individual artifacts from the system.

## 3. Storage Strategy## 3. Storage & Serialization Strategy

## 4. Schema (Level 0)

The defining feature of a Fancy Cell is its ability to handle data of any size via a dual-mode representation.The defining feature of a Fancy Cell is its ability to handle data of any size via a dual-mode representation. The cell itself is *always* lightweight and JSON-serializable, but the *content* it points to may not be.

```python

from typing import Any, Dict, Optional, List, Union

from uuid import UUID

from enum import Enum### 3.1 Mode A: Value (By Content)### 3.1 Mode A: Direct Content (Value-by-Content)

from pydantic import BaseModel

Used for "Small Data" that natively fits into JSON (strings, numbers, booleans, small dicts/lists).Used for "Small Data" that natively fits into JSON (strings, numbers, booleans, small dicts/lists).

class StorageKind(str, Enum):

    VALUE = "VALUE"*   **Use Case:** Configuration parameters, single database records, API responses, status flags.*   **Use Case:** Configuration parameters, single database records, API responses, status flags.

    REFERENCE = "REFERENCE"

    COMPOSITE = "COMPOSITE"*   **Structure:**



class FancyCell(BaseModel):### 3.2 Mode B: Reference (By Pointer)    ```json

    id: UUID

    alias: str                  # Human readable name ("User Input", "Cleaned Data")Used for "Big Data" or binary objects (DataFrames, Images, Models, Folders). The Cell contains metadata and a pointer.    {

    type_hint: str              # "pandas.DataFrame", "dict", "str", "List[Cell]"

    storage_kind: StorageKind *   **Use Case:** A 1M row DataFrame, a trained Neural Network, a directory of PDFs.      "id": "cell-001",

    

    # Payload (Exclusive based on storage_kind)*   **Reference Meta:** Allows the UI/API to inspect the object (e.g., show columns) without loading the heavy payload.      "name": "Configuration",

    value: Union[Any, List[UUID], Dict[str, UUID], None] # For VALUE (data) or COMPOSITE (List[UUID] or Dict[str, UUID])

    reference_uri: str | None   # For REFERENCE (s3://..., file://...)      "storage_mode": "direct",

    reference_meta: Dict | None # Cache/Preview (e.g. {"rows": 500, "columns": ["a"]})

```## 4. Schema (Level 0)      "data": { "threshold": 0.5, "unit": "metric" }


    }

```python    ```

from typing import Any, Dict, Optional

from uuid import UUID### 3.2 Mode B: Referenced Content (Value-by-Reference)

from enum import EnumUsed for "Big Data" or binary objects (DataFrames, Images, Models, Folders). The Cell contains metadata and a pointer.

from pydantic import BaseModel*   **Use Case:** A 1M row DataFrame, a trained Neural Network, a directory of PDFs.

*   **Structure:**

class StorageKind(str, Enum):    ```json

    VALUE = "VALUE"    {

    REFERENCE = "REFERENCE"      "id": "cell-002",

      "name": "Sales Data 2024",

class FancyCell(BaseModel):      "storage_mode": "reference",

    id: UUID      "reference_uri": "s3://bucket/data/sales_2024_v1.parquet",

    alias: str                  # Human readable name ("User Input", "Cleaned Data")      "metadata": {

    type_hint: str              # "pandas.DataFrame", "dict", "str"        "columns": ["date", "amount"],

    storage_kind: StorageKind         "row_count": 1000000,

            "format": "parquet"

    # Payload (Exclusive based on storage_kind)      }

    value: Any | None           # For small, JSON-compatible data    }

    reference_uri: str | None   # For pointers (s3://..., file://...)    ```

    reference_meta: Dict | None # Cache/Preview (e.g. {"rows": 500, "columns": ["a"]})    *   *Note:* The `metadata` field allows the UI/API to inspect the object (e.g., show columns) without loading the heavy payload.

### 3.3 Mode C: Composite (Cell-of-Cells)
Used to group existing cells into a logical unit. 
*   **Use Case:** Grouping a "Training Set" (X_train, y_train) or a "Project Bundle".
*   **Structure:** The `value` contains a list or dictionary of `UUID`s pointing to other cells.
*   **Benefit:** Allows operations to pass around complex hierarchies as a single unit without hiding the individual artifacts from the system.



## 4. Interaction with Fancy Functions

The `FancyFunction` contract is redefined in terms of Cells:
*   **Input:** A Fancy Function accepts a list/dict of `FancyCell`s.
*   **Output:** A Fancy Function produces one or more `FancyCell`s.
*   **Execution:** The Function logic (the "Micro-Kernel") is responsible for "opening" the Cell.
    *   If `direct`: usage is immediate `data = cell.data`.
    *   If `reference`: the system resolves `reference_uri` into an object (e.g., loading a Parquet file into memory).

## 5. Python Data Model

```python
from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel

class StorageMode(str, Enum):
    DIRECT = "direct"
    REFERENCE = "reference"

class FancyCell(BaseModel):
    id: str
    name: str
    kind: str  # e.g., "dataframe", "json", "image"
    mode: StorageMode
    
    # Direct Data
    value: Optional[Any] = None
    
    # Reference Data
    uri: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    
    def get_content(self):
        """Resolves value or loads from URI."""
        if self.mode == StorageMode.DIRECT:
            return self.value
        else:
            # Logic to load data from reference
            pass
```
