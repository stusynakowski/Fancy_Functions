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

    def add_step(self, step: WorkflowStep):
        self.steps.append(step)

    def get_step_by_id(self, step_id: UUID) -> Optional[WorkflowStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
