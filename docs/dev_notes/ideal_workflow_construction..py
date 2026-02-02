from enum import Enum
from uuid import UUID
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

# 1. State Enums for better control
class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class Workflow:
    """
    A unified manager for Definition, Data, and Execution.
    """
    def __init__(self, name: str, store: Optional['DatumStore'] = None):
        self.name = name
        
        # 1. Owns the Data Context
        # (Pass a persistent store if you want to save to disk/db)
        self.store = store or InMemoryStore()
        
        # 2. Owns the Definition (The Steps)
        self._steps: List['WorkflowStep'] = []
        
        # 3. Owns the Runtime State
        # Map step_id -> Status
        self._status: Dict[UUID, StepStatus] = {}
        # Map step_id -> Output Cell IDs (The artifacts produced)
        self._artifacts: Dict[UUID, Dict[str, UUID]] = {}

    # --- Definition API ---
    
    def add(self, func_slug: str, inputs: Dict[str, Any], **config) -> UUID:
        """
        Adds a step to the workflow.
        Returns the step_id so it can be used as input for future steps.
        """
        # Logic to create WorkflowStep...
        pass

    # --- Execution API (The "VCR" Controls) ---

    def start(self):
        """Runs from the beginning or resumes where left off."""
        for step in self._steps:
            if self._status.get(step.step_id) == StepStatus.COMPLETED:
                continue # Skip done steps
            
            self.execute_step(step.step_id)

    def execute_step(self, step_id: UUID):
        """
        Executes a specific step immediately.
        1. Resolves inputs from self.store
        2. Runs the function
        3. Saves results back to self.store
        4. Updates self._status and self._artifacts
        """
        self._status[step_id] = StepStatus.RUNNING
        try:
            # ... execution logic moved here from Engine ...
            self._status[step_id] = StepStatus.COMPLETED
        except Exception as e:
            self._status[step_id] = StepStatus.FAILED
            raise e

    def retry(self, step_id: UUID):
        """Marks a step as PENDING so it can be run again."""
        self._status[step_id] = StepStatus.PENDING
        # Optionally verify if downstream steps need to be invalidated
        self.run()

    # --- Data API ---

    def get_result(self, step_id: UUID, output_name: str = "return") -> Any:
        """
        Retrieves the actual value produced by a step.
        """
        if self._status[step_id] != StepStatus.COMPLETED:
            raise ValueError("Step not completed yet.")
            
        cell_id = self._artifacts[step_id][output_name]
        cell = self.store.get_cell(cell_id) # Need to implement get_cell on store
        return self.store.resolve(cell)