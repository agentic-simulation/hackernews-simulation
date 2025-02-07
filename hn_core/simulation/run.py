import json
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from hn_core.prompts.prompt import agent_prompt
<<<<<<< HEAD
from hn_core.simulation.persona import Persona
=======
from hn_core.simulation.hn_persona import HNPersona
>>>>>>> 2b49455 (feat: build and deploy to DO)
from hn_core.utils import utils
from hn_core.utils.logger import get_logger
from hn_core.utils.storage import R2Storage

from .agent import Agent
from .environment import Environment
from .post import Post

logger = get_logger("hn_main")

load_dotenv()


def run(
    title: str,
    url: str,
    text: str,
    model: str,
    num_agents: Optional[int] = None,
    total_time_steps: Optional[int] = 10,
    batch_size: Optional[int] = 10,
    k: Optional[float] = 1.0,
):
    """Runs a simulation of agent interactions on a Hacker News-style post.

    This function simulates how multiple AI agents with different personas interact with and
    respond to a post, modeling social dynamics and discussion patterns similar to those on
    Hacker News.

    Args:
        model (str): The name/identifier of the LLM model to use for agents (e.g., "openai/gpt-4o-mini").
        num_agents (int, optional): Number of agents to use in simulation. If None, uses all
            available personas. Defaults to None.
        total_time_steps (int, optional): Duration of simulation in time steps. Each time
            step represents a unit of simulated time (e.g., 1 hour). Defaults to 24.
        batch_size (int, optional): Number of agents to process in parallel during each
            simulation step. Higher values increase throughput but use more resources.
            Defaults to 10.
        k (float, optional): Steepness parameter for the sigmoid function that modifies agent
            activation probability based on post score. Higher values make the probability
            change more sharply around the threshold. Defaults to 0.1.
    """

    # Create post
    post = Post(
        title=title,
        url=url,
        text=text,
    )

    # Load personas
    logger.info(f"Loading personas...")
    # if hn_archive does not exist locally then download it from R2
    hn_archive_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "data/hn_archive"
    )
    if not os.path.exists(hn_archive_path):
        os.makedirs(hn_archive_path)
        storage = R2Storage()
        storage.download_file(
            "hn-archive", "users.json", hn_archive_path + "/users.json"
        )
        storage.download_file(
            "hn-archive", "items.json", hn_archive_path + "/items.json"
        )

    users = json.load(open(hn_archive_path + "/users.json"))
    items = json.load(open(hn_archive_path + "/items.json"))

    user_ids = list(users.keys())
    if num_agents is not None:
        logger.info(f"Using {num_agents} users for simulation")
        user_ids = user_ids[:num_agents]
    else:
        logger.info(f"Using all available {len(users)} users for simulation")

    # Create agents
    logger.info("Generating agents with personas...")
    agents = []

    persona = Persona(users, items, agent_prompt)
    for user_id in user_ids:
        prompt = persona.get_prompt(user_id)
        agent = Agent(
            id=user_id,
            provider="litellm",
            model=model,
            agent_prompt=prompt,
            activation_probability=0.7,
            model_params={"temperature": 1.0},
        )
        agents.append(agent)

    # Run the environment
    logger.info(f"Starting simulation with {len(agents)} agents...")
    environment = Environment(
        total_time_steps=total_time_steps,
        agents=agents,
        post=post,
        k=k,
    )
    environment.run(batch_size=batch_size)

    # build simulation result
    actions, post_history = utils.build_simulation_results(environment=environment)
    # Save results
    utils.save_simulation_results(environment=environment)
    # build agent role
    agent_profile = utils.build_agent_profile(actions=actions)

    return agent_profile, post_history[-1]