from fancy_core.cells import FancyCell, StorageKind
from fancy_core.store import InMemoryStore

def test_create_value_cell():
    cell = FancyCell.create_value(100, "My Number")
    assert cell.value == 100
    assert cell.storage_kind == StorageKind.VALUE
    assert cell.alias == "My Number"

def test_store_put_resolve():
    store = InMemoryStore()
    data = {"a": 1, "b": 2}
    
    # Put data into store
    cell = store.put(data, "My Dict")
    
    assert cell.storage_kind == StorageKind.REFERENCE
    assert cell.reference_uri.startswith("memory://")
    
    # Resolve back
    resolved_data = store.resolve(cell)
    assert resolved_data == data 
    assert resolved_data is data # Should be same object in memory store

def test_composite_cell():
    import uuid
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    
    cell = FancyCell.create_composite([id1, id2], "Group")
    assert cell.storage_kind == StorageKind.COMPOSITE
    assert len(cell.value) == 2
