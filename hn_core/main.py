import logging
import os

import fire
from dotenv import load_dotenv
from hn_core.core.agent import Agent
from hn_core.core.environment import Environment
from hn_core.core.post import Post
from hn_core.utils.utils import load_personas, save_simulation_results

# Load environment variables
load_dotenv()

# Set up custom logger
logger = logging.getLogger('hn_main')
logger.setLevel(logging.INFO)
# Create handlers and formatter only if no handlers exist
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def run(
        model: str,
        num_agents: int | None = None,
        total_time_steps: int = 24,
        batch_size: int = 10,
        k: float = 0.1,
        threshold: float = 5,
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
        threshold (float, optional): Score threshold in the sigmoid function where agent
            activation probability starts increasing significantly. Posts with scores below
            this value decrease agent participation, while scores above increase it.
            Defaults to 5.
    """

    # Create post
    post = Post(
        title="Show HN: I Created ErisForge, a Python Library for Abliteration of LLMs",
        url="https://github.com/Tsadoq/ErisForge",
        text="""
        ErisForge is a Python library designed to modify Large Language Models (LLMs) by applying transformations to their internal layers. Named after Eris, the goddess of strife and discord, ErisForge allows you to alter model behavior in a controlled manner, creating both ablated and augmented versions of LLMs that respond differently to specific types of input.
        It is also quite useful to perform studies on propaganda and bias in LLMs (planning to experiment with deepseek).
        Features - Modify internal layers of LLMs to produce altered behaviors. - Ablate or enhance model responses with the AblationDecoderLayer and AdditionDecoderLayer classes. - Measure refusal expressions in model responses using the ExpressionRefusalScorer. - Supports custom behavior directions for applying specific types of transformations.""",
    )

    # Load personas
    logger.info(f"Loading personas...")
    personas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "personas_data/personas.jsonl")
    personas = load_personas(bucket="personas", key="hn_personas_final.jsonl", filepath=personas_path)

    if num_agents is not None:
        logger.info(f"Using {num_agents} personas for simulation")
        personas = personas[:num_agents]
    else:
        logger.info(f"Using all available personas for simulation")

    # Create agents
    logger.info("Generating agents with personas...")
    agents = []

    # TODO: implement activation probability based on time
    for persona in personas:
        agent = Agent(
            bio=persona["bio"],
            activation_probability=0.8,
            model=model,
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
        threshold=threshold,
    )
    environment.run(batch_size)

    # Save results
    save_simulation_results(environment)


if __name__ == "__main__":
    fire.Fire(run)
