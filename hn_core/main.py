import datetime
import json
import logging
import os

import fire
from dotenv import load_dotenv
from hn_core.core.agent import Agent
from hn_core.core.environment import Environment
from hn_core.core.post import Post
from hn_core.utils import save_simulation_results, load_personas

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)



def run(model: str, num_agents: int = None, total_time_steps: int = 24, batch_size: int = 10):
    load_dotenv()

    simulation_start = datetime.datetime.now()

    # create post
    post = Post(
        title="Show HN: I Created ErisForge, a Python Library for Abliteration of LLMs",
        url="https://github.com/Tsadoq/ErisForge",
        text="""
        ErisForge is a Python library designed to modify Large Language Models (LLMs) by applying transformations to their internal layers. Named after Eris, the goddess of strife and discord, ErisForge allows you to alter model behavior in a controlled manner, creating both ablated and augmented versions of LLMs that respond differently to specific types of input.
        It is also quite useful to perform studies on propaganda and bias in LLMs (planning to experiment with deepseek).
        Features - Modify internal layers of LLMs to produce altered behaviors. - Ablate or enhance model responses with the AblationDecoderLayer and AdditionDecoderLayer classes. - Measure refusal expressions in model responses using the ExpressionRefusalScorer. - Supports custom behavior directions for applying specific types of transformations.""",
    )

    logging.info(f"Loading personas...")
    personas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "personas_data/500_v1.jsonl")

    personas = load_personas(personas_path)

    # limit number of personas
    if num_agents is not None:
        logging.info(f"using {num_agents} personas for simulation")
        personas = personas[:num_agents]
    else:
        logging.info(f"using all available personas for simulation")

    # create agents
    logging.info("generating agents with personas...")
    agents = []

    # TODO: implement activation probability based on time
    for persona in personas:
        agent = Agent(
            model=model,
            bio=persona["bio"],
            activation_probability=0.8,
            model_params={"temperature": 1.0},
        )
        agents.append(agent)

    # Run the environment
    logging.info(f"starting simulation with {len(agents)} agents...")
    environment = Environment(
        total_time_steps=total_time_steps,
        agents=agents,
        post=post,
    )

    k = 0.1
    threshold = 5
    environment.run(batch_size, k, threshold)

    # Save results
    save_simulation_results(environment, simulation_start)


if __name__ == "__main__":
    fire.Fire(run)
