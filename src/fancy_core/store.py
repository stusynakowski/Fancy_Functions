from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID
from .cells import FancyCell, StorageKind

class DatumStore(ABC):
    """
    Abstract interface for the 'Physics' of data storage.
    Responsible for resolving Cell IDs to actual Python objects
    and persisting Python objects to generate URIs.
    """
    
    @abstractmethod
    def resolve(self, cell: FancyCell) -> Any:
        """
        Given a Cell, return its actual content.
        - If VALUE: return cell.value
        - If REFERENCE: load from cell.reference_uri
        - If COMPOSITE: return structure of UUIDs (or resolve children?) 
          (Usually composite resolves to the structure of IDs, and logic steps unpack it)
        """
        pass

    @abstractmethod
    def put(self, value: Any, alias: str) -> FancyCell:
        # Use simple object id or uuid for URI
        from uuid import uuid4
        obj_uuid = uuid4()
        uri = f"memory://{obj_uuid}"
        
        # Store it
        self._data[uri] = value
        
        # Return reference cell
        return FancyCell.create_reference(
            uri=uri,
            alias=alias,
            type_hint=type(value).__name__
        )

class InMemoryStore(DatumStore):
    """
    Simple implementation that keeps everything in a dict.
    Useful for local development and testing.
    """
    def __init__(self):
        self._data: Dict[str, Any] = {} # Map URI -> Object

    def resolve(self, cell: FancyCell) -> Any:
        if cell.storage_kind == StorageKind.VALUE:
            return cell.value
        elif cell.storage_kind == StorageKind.COMPOSITE:
            return cell.value
        elif cell.storage_kind == StorageKind.REFERENCE:
            # For in-memory, the URI is just a key in our dict
            uri = cell.reference_uri
            if not uri or uri not in self._data:
                 raise ValueError(f"Data not found for URI: {uri}")
            return self._data[uri]
        return None

    def put(self, value: Any, alias: str) -> FancyCell:
        # For simplicity, we'll store everything by reference in this Store implementation
        # except very small primitives if we wanted to enforce logic, but let's stick to reference for 'put'
        
        # Check if basic type to decide if we want to store as Value?
        # For now, let's treat explicit 'put' as "I want to offload this" -> Reference
        
        import uuid
        obj_uuid = str(uuid.uuid4())
        uri = f"memory://{obj_uuid}"
        
        self._data[uri] = value
        
        # Simple type inference
        type_hint = type(value).__name__
        if hasattr(value, "shape"): # rough check for df/array
             meta = {"shape": value.shape}
        else:
             meta = {}

        return FancyCell.create_reference(
            uri=uri,
            alias=alias,
            type_hint=type_hint,
            meta=meta
        )
