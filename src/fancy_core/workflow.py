from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from .workflow_step import WorkflowStep

class Workflow(BaseModel):
    """
    A linear sequence of steps to be executed.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    steps: List[WorkflowStep] = []

    _context_stack: List["Workflow"] = []

    def __enter__(self):
        Workflow._context_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if Workflow._context_stack:
            Workflow._context_stack.pop()

    @classmethod
    def get_current(cls) -> Optional["Workflow"]:
        if cls._context_stack:
            return cls._context_stack[-1]
        return None

    def add_step(self, step: WorkflowStep):
        self.steps.append(step)

    def get_step_by_id(self, step_id: UUID) -> Optional[WorkflowStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    @classmethod
    def from_json(cls, json_str: str) -> "Workflow":
        """Reconstruct a Workflow from its JSON representation."""
        return cls.model_validate_json(json_str)

    def to_json(self) -> str:
        """Serialize the workflow to a JSON string."""
        return self.model_dump_json(indent=2)
