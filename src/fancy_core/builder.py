from typing import Dict, Any, Optional, Union
from uuid import UUID, uuid4
from .workflow import Workflow
from .workflow_step import WorkflowStep
from .registry import registry

class WorkflowBuilder:
    """
    Helper class to construct Workflows programmatically.
    Manages ID generation and wiring resolution.
    """
    def __init__(self, name: str):
        self.workflow = Workflow(name=name)
        # Aliases for Cell UUIDs (e.g., "cleaned_data" -> uuid-1234)
        self.vars: Dict[str, UUID] = {}
    
    def add_step(self, 
                 function_slug: str, 
                 inputs: Dict[str, Union[str, UUID]] = {}, 
                 config: Dict[str, Any] = {},
                 output_alias: Optional[str] = None) -> UUID:
        """
        Adds a step to the workflow.
        
        Args:
            function_slug: The name of the registered function to call.
            inputs: Mapping of argument names to input sources. 
                    Values can be valid UUIDs (direct cell ref) or strings (aliases).
            config: Static configuration values passed as literals to the function.
            output_alias: If provided, stores the output cell's UUID under this name 
                          for easy reference in future steps.
                          
        Returns:
            UUID: The ID of the primary output cell ("return").
        """
        
        # 1. Validation
        if not registry.get(function_slug):
             # For builder, we might want to be strict, but maybe allow relaxed for 'stub' testing? 
             # Plan says: "Check function_slug describes a valid function"
             raise ValueError(f"Function '{function_slug}' not found in registry.")

        # 2. Resolve Inputs (Alias -> UUID)
        resolved_inputs: Dict[str, UUID] = {}
        for arg_name, arg_val in inputs.items():
            if isinstance(arg_val, UUID):
                resolved_inputs[arg_name] = arg_val
            elif isinstance(arg_val, str):
                if arg_val in self.vars:
                    resolved_inputs[arg_name] = self.vars[arg_val]
                else:
                    raise ValueError(f"Input '{arg_name}' uses alias '{arg_val}' which is not defined in this builder.")
            else:
                 raise TypeError(f"Input '{arg_name}' must be a UUID or a registered Alias string. Got {type(arg_val)}")

        # 3. Generate Output ID
        # TODO: Support multi-output functions explicitly in future.
        output_id = uuid4()
        
        # 4. Create Step
        step = WorkflowStep(
            function_slug=function_slug,
            config=config,
            inputs=resolved_inputs,
            outputs={"return": output_id} # Single output assumption for now
        )
        
        self.workflow.add_step(step)
        
        # 5. Register Output Alias
        if output_alias:
            self.vars[output_alias] = output_id
            
        return output_id

    def build(self) -> Workflow:
        """Returns the constructed Workflow object."""
        return self.workflow

    def get_variable(self, alias: str) -> UUID:
        """Retrieve the UUID associated with an alias."""
        if alias not in self.vars:
            raise KeyError(f"Variable '{alias}' not found.")
        return self.vars[alias]
    
    def export_json(self) -> str:
        """Serializes the constructed workflow to a JSON string."""
        return self.workflow.to_json()
