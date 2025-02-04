import os
from dataclasses import dataclass
from typing import Optional

import fire
from dotenv import load_dotenv
from hn_core.utils import utils
from hn_core.utils.logger import get_logger

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
    personas_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "data/persona/personas.jsonl"
    )
    personas = utils.load_personas(
        bucket="personas", key="personas_final.jsonl", filepath=personas_path
    )

    if num_agents is not None:
        logger.info(f"Using {num_agents} personas for simulation")
        personas = personas[:num_agents]
    else:
        logger.info(f"Using all available personas for simulation")

    # Create agents
    logger.info("Generating agents with personas...")
    agents = []

    for persona in personas:
        agent = Agent(
            provider="litellm",
            model=model,
            bio=persona["bio"],
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
    _, post_history = utils.build_simulation_results(environment=environment)

    # Save results
    utils.save_simulation_results(environment=environment)

    return post_history[-1]


if __name__ == "__main__":
    fire.Fire(run)
