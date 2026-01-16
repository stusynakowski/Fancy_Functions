from typing import Dict, Any, Callable
from pydantic import BaseModel, PrivateAttr

class FancyFunction(BaseModel):
    """
    Metadata definition for a specific function capability (The 'Tool').
    """
    slug: str
    name: str
    description: str = ""
    
    # Contracts (Type hints as strings)
    input_contract: Dict[str, str] = {}
    output_contract: Dict[str, str] = {}
    
    # The actual code
    _executable: Callable = PrivateAttr()
    
    def set_executable(self, func: Callable):
        self._executable = func
        
    def execute(self, *args, **kwargs) -> Any:
        if not hasattr(self, "_executable") or self._executable is None:
            raise ValueError(f"Function {self.slug} has no executable attached.")
        return self._executable(*args, **kwargs)
