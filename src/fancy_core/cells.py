from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field

class StorageKind(str, Enum):
    VALUE = "VALUE"
    REFERENCE = "REFERENCE"
    COMPOSITE = "COMPOSITE"
    PENDING = "PENDING"

class FancyCell(BaseModel):
    """
    The atomic unit of data in the Fancy Functions ecosystem.
    
    Attributes:
        id (UUID): Globally unique identifier for this specific data instance.
        alias (str): Human-readable name (e.g., "Training Set").
        type_hint (str): Descriptor of data type (e.g., "pandas.DataFrame").
        storage_kind (StorageKind): How the payload is stored.
        value (Any): Actual content for VALUE/COMPOSITE modes.
        reference_uri (str): URI for REFERENCE mode.
        reference_meta (Dict): Lightweight metadata cache for referenced objects.
    """
    id: UUID = Field(default_factory=uuid4)
    alias: str
    type_hint: str = "Any"
    storage_kind: StorageKind
    
    # Payload (Exclusive based on storage_kind)
    value: Union[Any, List[UUID], Dict[str, UUID], None] = None
    reference_uri: Optional[str] = None
    reference_meta: Optional[Dict[str, Any]] = None

    @classmethod
    def create_value(cls, value: Any, alias: str, type_hint: str = "Any") -> "FancyCell":
        """Factory for VALUE mode cells."""
        return cls(
            alias=alias,
            type_hint=type_hint,
            storage_kind=StorageKind.VALUE,
            value=value
        )

    @classmethod
    def create_reference(
        cls, 
        uri: str, 
        alias: str, 
        type_hint: str = "Any", 
        meta: Optional[Dict] = None
    ) -> "FancyCell":
        """Factory for REFERENCE mode cells."""
        return cls(
            alias=alias,
            type_hint=type_hint,
            storage_kind=StorageKind.REFERENCE,
            reference_uri=uri,
            reference_meta=meta or {}
        )

    @classmethod
    def create_composite(
        cls, 
        children: Union[List[UUID], Dict[str, UUID]], 
        alias: str
    ) -> "FancyCell":
        """Factory for COMPOSITE mode cells."""
        return cls(
            alias=alias,
            type_hint="Composite",
            storage_kind=StorageKind.COMPOSITE,
            value=children
        )

    def __str__(self) -> str:
        """
        Rich string representation for inspection.
        Format: [Kind:VALUE] "Alias" <Type:int> = 42
        """
        if self.storage_kind == StorageKind.VALUE:
            val_str = str(self.value)
            if len(val_str) > 50:
                val_str = val_str[:47] + "..."
            content = f"= {val_str}"
        elif self.storage_kind == StorageKind.REFERENCE:
            content = f"@ {self.reference_uri}"
        elif self.storage_kind == StorageKind.COMPOSITE:
            count = len(self.value) if isinstance(self.value, list) else len(self.value)
            content = f"[List of {count} items]"
        else:
            content = "(Pending)"
            
        return f"[{self.storage_kind.value}] \"{self.alias}\" <{self.type_hint}> {content}"
    
    def __repr__(self):
        return self.__str__()

