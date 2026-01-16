from typing import Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class WorkflowStep(BaseModel):
    """
    A configured instance of a FancyFunction in a workflow.
    """
    step_id: UUID = Field(default_factory=uuid4)
    function_slug: str
    
    # Configuration (Static Parameters -> passed as literal args)
    config: Dict[str, Any] = {}
    
    # Data Mapping (Wiring -> passed as Cell IDs)
    # Maps Function Argument Name -> Input Cell ID
    inputs: Dict[str, UUID] = {}

    # Output Mapping (Wiring -> produced Cell IDs)
    # Maps Output Name (e.g. "return") -> Output Cell ID
    outputs: Dict[str, UUID] = {}
