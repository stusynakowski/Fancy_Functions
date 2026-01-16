from typing import Dict, Any, List, Optional
from uuid import UUID
from .store import DatumStore
from .workflow import Workflow
from .registry import registry
from .cells import FancyCell

class Engine:
    """
    The runtime engine that executes a Workflow.
    """
    def __init__(self, store: DatumStore):
        self.store = store

    def run(self, workflow: Workflow, initial_cells: List[FancyCell] = []) -> Dict[UUID, FancyCell]:
        """
        Executes the workflow steps in order.
        
        Args:
            workflow: The Workflow definition to run.
            initial_cells: Existing data cells available at start (e.g. user inputs).
            
        Returns:
            Dict[UUID, FancyCell]: A map of all cells (inputs + produced) by their ID.
        """
        # Context holds the state of all available cells by ID
        context: Dict[UUID, FancyCell] = {cell.id: cell for cell in initial_cells}

        for step in workflow.steps:
            # 1. Resolve Inputs
            execution_args = {}
            
            # Map wired inputs
            for arg_name, cell_id in step.inputs.items():
                if cell_id not in context:
                    raise ValueError(f"Step '{step.function_slug}' (ID: {step.step_id}) Missing input cell: {cell_id}")
                
                cell = context[cell_id]
                val = self.store.resolve(cell)
                execution_args[arg_name] = val
            
            # 2. Merge Configuration (Static args)
            # Priorities: Config overrides wired inputs? Or inputs override config?
            # Usually explicit inputs override static default config if key collision. 
            # But here config is usually parameters, inputs are data.
            # We'll merge config in.
            
            final_kwargs = {**execution_args, **step.config}
            
            # 3. Locate Function
            func_def = registry.get(step.function_slug)
            if not func_def:
                raise ValueError(f"Function definition not found for slug: {step.function_slug}")
            
            # 4. Execute Logic
            try:
                result = func_def.execute(**final_kwargs)
            except Exception as e:
                # TODO: Better error wrapping
                raise RuntimeError(f"Error executing step {step.function_slug}: {str(e)}") from e
            
            # 5. Handle Outputs
            # We need to map the result back to the expected output cells defined in `step.outputs`.
            # Result could be:
            # - single value
            # - tuple (not supported nicely yet)
            # - dict (named outputs)
            
            # If step.outputs has mapping, we try to fulfill it.
            
            # Case A: Single output expected (or "return" key)
            # Case B: Multiple outputs (Dict returned)
            
            # We'll enforce a convention: If function returns Dict and keys match output names, map them.
            # Otherwise treat whole result as the "return" value.
            
            outputs_map = {}
            
            # If the function metadata says it returns multiple things, or if result is a dict matching keys
            # For now, simplistic approach:
            is_multi_output = isinstance(result, dict) and any(k in step.outputs for k in result.keys())
            
            if is_multi_output:
                outputs_map = result
            else:
                # Default single return. 
                # If the step expects "return", use that.
                # If the step expects exactly one output and it's not named 'return', imply it?
                # Let's stick to "return" as default output key if not specified otherwise.
                outputs_map = {"return": result}

            for output_name, target_cell_id in step.outputs.items():
                if output_name in outputs_map:
                    val = outputs_map[output_name]
                    
                    # Store data
                    # Use function slug + output name as alias hint
                    alias_hint = f"{step.function_slug}::{output_name}"
                    
                    # The store creates a cell with a NEW ID.
                    stored_cell = self.store.put(val, alias=alias_hint)
                    
                    # IMPORTANT: We must override the stored_cell.id to match the target_cell_id
                    # that was pre-wired in the workflow.
                    # We copy the cell but change the ID.
                    
                    # Pydantic's copy or model_copy
                    final_cell = stored_cell.model_copy(update={"id": target_cell_id})
                    
                    # Add to context
                    context[target_cell_id] = final_cell
                else:
                    # Helper: If we expected an output but didn't get it
                    # Just skip? Or error? 
                    # For now, loose contract.
                    pass

        return context
