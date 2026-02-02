"""
Strategies for Serializing Workflows in Fancy Functions
=====================================================

Since `Workflow` and `WorkflowStep` are built on Pydantic (BaseModel), 
we get robust serialization to JSON for free.

Here is a demonstration of how to serialize and deserialize a workflow.
"""

from uuid import uuid4
import json
from src.fancy_core.workflow import Workflow
from src.fancy_core.workflow_step import WorkflowStep

def demo_serialization_strategy():
    # 1. Create a dummy workflow
    workflow = Workflow(name="My Serializable Workflow")
    
    # 2. Add some steps
    # Step 1: Ingest data
    step1_id = uuid4()
    step1 = WorkflowStep(
        step_id=step1_id,
        function_slug="web_scraper",
        config={"url": "https://example.com", "depth": 2}, # Simple types are JSON safe
        inputs={},
        outputs={"html_content": uuid4()}
    )
    workflow.add_step(step1)

    # Step 2: Process data
    step2 = WorkflowStep(
        function_slug="text_extractor",
        config={"format": "markdown"},
        inputs={"raw_html": step1.outputs["html_content"]}, # Wiring step 1 output to step 2 input
        outputs={"text": uuid4()}
    )
    workflow.add_step(step2)

    print("--- Original Workflow Object ---")
    print(workflow)

    # 3. Strategy A: JSON Serialization (Pydantic Native)
    # The simplest method. Perfect for storage, API transmission, etc.
    json_str = workflow.model_dump_json(indent=2)
    
    print("\n--- Serialized JSON ---")
    print(json_str)
    
    # 4. Saving to file (Simulation)
    file_path = "my_workflow.json"
    with open(file_path, "w") as f:
        f.write(json_str)
        
    # 5. Loading from file / Deserialization
    with open(file_path, "r") as f:
        loaded_json_str = f.read()
        
    restored_workflow = Workflow.model_validate_json(loaded_json_str)

    print("\n--- Restored Workflow Object ---")
    print(f"Name: {restored_workflow.name}")
    print(f"Steps: {len(restored_workflow.steps)}")
    print(f"ID Matches: {workflow.id == restored_workflow.id}")
    
    # Verify deep structure matches
    assert workflow.steps[0].config == restored_workflow.steps[0].config
    
    # 6. Strategy B: YAML Serialization (Optional)
    # Better for human-writable configs.
    # Requires: pip install pyyaml
    try:
        import yaml
        yaml_str = yaml.dump(workflow.model_dump(), sort_keys=False)
        print("\n--- Serialized YAML ---")
        print(yaml_str)
        
        # Restore from YAML
        data_dict = yaml.safe_load(yaml_str)
        yaml_workflow = Workflow.model_validate(data_dict)
        print(f"Restored from YAML: {yaml_workflow.name}")
        
    except ImportError:
        print("\n(PyYAML not installed, skipping YAML demo)")

if __name__ == "__main__":
    demo_serialization_strategy()
