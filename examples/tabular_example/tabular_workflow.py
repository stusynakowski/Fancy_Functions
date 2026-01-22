import sys
import os

# Put src in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from typing import List, Dict, Any
from uuid import UUID, uuid4
from fancy_core.cells import FancyCell
from fancy_core.workflow import Workflow
from fancy_core.workflow_step import WorkflowStep
from fancy_core.engine import Engine
from fancy_core.store import InMemoryStore
from fancy_core.decorators import step
from fancy_core.registry import registry

# --- 1. Define Fancy Functions (The logic) ---
# Same simple logic, but notice we never call these directly in the Builder.

@step
def add_five(val: int) -> int:
    return val + 5

@step
def double_value(val: int) -> int:
    return val * 2

@step
def format_currency(val: int) -> str:
    return f"${val:.2f}"

# --- 2. The Abstraction: TabularWorkflowBuilder ---

class TabularWorkflowBuilder:
    """
    This class is an 'Abstraction Layer'.
    It DOES NOT execute code.
    It builds a dependency graph (Workflow) representing the operations.
    """
    def __init__(self, name: str):
        self.workflow = Workflow(name=name)
        self.initial_cells: List[FancyCell] = []
        
        # The 'Table' State: A list of rows, where each row is a Dict[ColumnName, Cell_ID]
        # These IDs might be existing data (Inputs) or future data (Step Outputs).
        self.rows: List[Dict[str, UUID]] = []
        self.columns: List[str] = []

    def load_data(self, column_name: str, data: List[Any]):
        """
        Loads raw data as the initial 'seed' columns.
        """
        self.columns.append(column_name)
        
        for i, value in enumerate(data):
            # Create a concrete Input Cell for this data point
            cell = FancyCell.create_value(
                alias=f"Input row {i}",
                value=value,
                type_hint=type(value).__name__
            )
            self.initial_cells.append(cell)
            
            # Update our tracked state
            if i >= len(self.rows):
                self.rows.append({})
            self.rows[i][column_name] = cell.id

    def add_operation(self, func_slug: str, input_col: str, output_col: str, **static_config):
        """
        Compiles a "Column Operation" into many individual "Workflow Steps".
        Does NOT run the function. Just wires up the graph.
        """
        print(f"Compiling operation '{func_slug}' on column '{input_col}' -> '{output_col}'...")
        
        if output_col not in self.columns:
            self.columns.append(output_col)

        # For every row in our virtual table...
        for i, row in enumerate(self.rows):
            if input_col not in row:
                raise ValueError(f"Row {i} missing input column {input_col}")

            input_cell_id = row[input_col]
            
            # 1. Create a "Future" Cell ID for the result of this step
            output_cell_id = uuid4()
            
            # 2. Record this future ID in our virtual table so subsequent steps can use it
            row[output_col] = output_cell_id

            # 3. Create the Step Definition
            step = WorkflowStep(
                function_slug=func_slug,
                config=static_config,
                inputs={"val": input_cell_id},   # Wire input to previous cell
                outputs={"return": output_cell_id} # Wire output to future cell
            )

            # 4. Add to the workflow graph
            self.workflow.add_step(step)

    def print_plan(self):
        print(f"\n--- Workflow Compile Plan: {self.workflow.name} ---")
        print(f"Total Rows: {len(self.rows)}")
        print(f"Total Steps Generated: {len(self.workflow.steps)}")
        print("Dependency Graph (First Row Trace):")
        
        if not self.rows: 
            return

        # Trace the flow of IDs for the first row to prove connectivity
        first_row = self.rows[0]
        for col in self.columns:
            cell_id = first_row.get(col)
            print(f"  Col '{col}' -> Cell ID: {str(cell_id)[:8]}...")

# --- 3. The Execution Layer ---

def run_compiled_workflow():
    # A. Build the Graph (Compile Time)
    # --------------------------------
    builder = TabularWorkflowBuilder("Financial Processing Pipeline")
    
    # Load 3 rows of data
    builder.load_data("seed", [10, 20, 30])
    
    # Define the pipeline
    # Note: These loop over the meta-data, creating a web of steps
    builder.add_operation("add_five", input_col="seed", output_col="boosted")
    builder.add_operation("double_value", input_col="boosted", output_col="doubled")
    builder.add_operation("format_currency", input_col="doubled", output_col="final_str")

    builder.print_plan()
    
    # B. Execute the Graph (Runtime)
    # ------------------------------
    print("\n--- Starting Engine Execution ---")
    store = InMemoryStore()
    engine = Engine(store)
    
    # The engine takes the purely declarative workflow and the initial data
    results = engine.run(builder.workflow, builder.initial_cells)
    
    print("\n--- Execution Complete. Inspecting Results ---")
    
    # We use our builder"s "map" to look up the results we care about
    # This proves the abstraction maintained the link between "Columns" and "Cell IDs"
    print(f"{'SEED':<10} | {'BOOSTED':<10} | {'DOUBLED':<10} | {'FINAL':<10}")
    print("-" * 50)
    
    for row in builder.rows:
        val_seed = results[row["seed"]].value
        val_boost = results[row["boosted"]].value
        val_double = results[row["doubled"]].value
        val_final = results[row["final_str"]].value
        
        print(f"{str(val_seed):<10} | {str(val_boost):<10} | {str(val_double):<10} | {str(val_final):<10}")


if __name__ == "__main__":
    run_compiled_workflow()
