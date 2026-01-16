from typing import Dict, Optional
from .functions import FancyFunction

class FunctionRegistry:
    """
    Singleton registry to hold all discovered FancyFunctions.
    """
    _instance = None
    _registry: Dict[str, FancyFunction] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FunctionRegistry, cls).__new__(cls)
            cls._instance._registry = {}
        return cls._instance

    def register(self, func_def: FancyFunction):
        self._registry[func_def.slug] = func_def

    def get(self, slug: str) -> Optional[FancyFunction]:
        return self._registry.get(slug)

    def list_all(self) -> Dict[str, FancyFunction]:
        return self._registry

    def clear(self):
        self._registry.clear()

# Global Instance
registry = FunctionRegistry()
