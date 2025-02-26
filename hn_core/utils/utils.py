import datetime
import json
import os
from collections import defaultdict
from typing import Dict, List

from hn_core.simulation.environment import Environment


def handler(obj):
    """convert objects compatible with json"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def build_simulation_results(environment: Environment) -> tuple[List, List]:
    metadata = {
        "post_title": environment.post.title,
        "post_url": environment.post.url,
        "post_text": environment.post.text,
    }

    # Create post history records
    post_history = []
    for state in environment.post.history:
        record = {
            "sim_step": state["sim_step"],
            **metadata,
            "upvotes": state["upvotes"],
            "comments_count": state["comments_count"],
            "comments": state["comments"],
            "score": state["score"],
        }
        post_history.append(record)

    return environment.agent_actions, post_history


def save_simulation_results(environment: Environment):
    """Save simulation results to JSON files in a timestamped Results directory.

    This function preserves the state and outcomes of a Hacker News post simulation by saving:
    1. Agent Actions: A chronological record of all agent interactions and behaviors
    2. Post History: The complete evolution of the post's performance metrics over time

    The results are saved in a directory structure:
        ./results/
            └── YYYYMMDD_HHMMSS/
                ├── agent_actions.json
                └── post_history.json

    Args:
        environment (Environment): The simulation environment containing:
            - agent_actions: List of all agent interactions during simulation
            - post: The simulated HN post object with its complete history
        timestamp (datetime.datetime): Timestamp used to create a unique directory name

    The saved files contain:
        agent_actions.json: Chronological record of agent behaviors and interactions
        post_history.json: Time series data for the post, including:
            - Metadata (title, URL, text)
            - Performance metrics per simulation step (upvotes, comments, score)
    """
    results_dir = "hn_core/results"
    os.makedirs(results_dir, exist_ok=True)

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a subfolder for this simulation run
    simulation_dir = os.path.join(results_dir, timestamp_str)
    os.makedirs(simulation_dir, exist_ok=True)

    agent_actions, post_history = build_simulation_results(environment=environment)

    # Save agent actions
    actions_filepath = os.path.join(simulation_dir, "agent_actions.json")
    with open(actions_filepath, "w") as f:
        json.dump(agent_actions, f, indent=2, default=handler)

    # Save post history
    post_filepath = os.path.join(simulation_dir, "post_history.json")
    with open(post_filepath, "w") as f:
        json.dump(post_history, f, indent=2, default=handler)


def build_agent_profile(actions: Dict):
    agg = defaultdict(lambda: {"upvotes": 0, "comments_count": 0, "comments": []})
    for action in actions:
        role = action["actions"]["role"]
        if action["actions"]["upvote"]:
            agg[role]["upvotes"] += 1
        if action["actions"]["comment"]:
            agg[role]["comments_count"] += 1
            agg[role]["comments"].append(action["actions"]["comment"])

    return dict(agg)
