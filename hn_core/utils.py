import datetime
import json
import os

from hn_core.core.environment import Environment

def load_personas(personas_path):
    """
    Load personas from a JSON Lines file where each line contains a persona definition.
    
    Args:
        personas_path (str): Path to the personas file
        
    Returns:
        list: List of parsed persona dictionaries
        
    Raises:
        FileNotFoundError: If the personas file doesn't exist
        ValueError: If no valid personas are found in the file
        Exception: For other errors during file processing
    """
    personas = []
    
    try:
        if not os.path.exists(personas_path):
            raise FileNotFoundError(f"Personas file not found: {personas_path}")
            
        with open(personas_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    persona = json.loads(line)
                    personas.append(persona)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON on line {line_num}: {line!r}\n"
                          f"Error: {str(e)}")

        if not personas:
            raise ValueError(f"No valid personas found in file: {personas_path}")
            
        return personas
        
    except Exception as e:
        print(f"Failed to load personas from {personas_path}: {str(e)}")
        raise

def handler(obj):
    """convert objects compatible with json"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def save_simulation_results(environment: Environment, timestamp: datetime.datetime):
    """Save simulation results to two JSON files in the Results directory."""
    results_dir = "./results"
    os.makedirs(results_dir, exist_ok=True)

    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    
    # Save agent actions
    actions_filepath = os.path.join(results_dir, f"{timestamp_str}_agent_actions.json")
    with open(actions_filepath, "w") as f:
        json.dump(environment.agent_actions, f, indent=2, default=handler)

    # Save post history
    post_filepath = os.path.join(results_dir, f"{timestamp_str}_post_history.json")
    
    # Post metadata
    metadata = {
        "post_title": environment.post.title,
        "post_url": environment.post.url,
        "post_text": environment.post.text
    }
    
    # Create post history records
    post_history = []
    for step, state in enumerate(environment.post.history):
        record = {
            "sim_step": step,
            **metadata,
            "upvotes": state["upvotes"],
            "comments": state["comments"],
            "score": state["score"]
        }
        post_history.append(record)
    
    with open(post_filepath, "w") as f:
        json.dump(post_history, f, indent=2, default=handler)
