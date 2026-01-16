import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from fancy_core.cells import FancyCell, StorageKind
from fancy_core.store import InMemoryStore

def main():
    print("=== Fancy Functions: Milestone 1 Demo ===\n")

    # 1. Initialize the Store
    print("1. Initializing InMemoryStore...")
    store = InMemoryStore()
    print("   [OK] Store ready.\n")

    # 2. Create a 'Value' Cell (Small data, held in memory)
    print("2. Creating a VALUE Cell (Direct data)...")
    val_cell = FancyCell.create_value(42, alias="The Answer", type_hint="int")
    print(f"   Created Cell: {val_cell.id} | Alias: {val_cell.alias} | Kind: {val_cell.storage_kind}")
    
    # Store/Register it (though value cells hold their own data, we might track them)
    # The 'put' method on store usually takes raw data, let's try that flow too.
    
    # 3. Use Store.put() to handle data storage automatically
    print("\n3. Using store.put() to store a dictionary...")
    my_data = {"user": "Stuart", "role": "Admin"}
    ref_cell = store.put(my_data, alias="User Config")
    print(f"   Created Cell: {ref_cell.id} | Alias: {ref_cell.alias}")
    print(f"   Storage Kind: {ref_cell.storage_kind}")
    print(f"   Reference URI: {ref_cell.reference_uri}")

    # 4. Resolve data back from the cell
    print("\n4. Resolving data back from the Store...")
    resolved_data = store.resolve(ref_cell)
    print(f"   Resolved Data: {resolved_data}")
    
    # 5. Verify it matches
    is_match = (resolved_data == my_data)
    print(f"   Match Original? {is_match}")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
