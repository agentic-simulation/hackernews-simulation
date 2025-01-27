import datetime
import json
import logging
import os

import fire
from dotenv import load_dotenv
from hn_core.core.agent import Agent
from hn_core.core.environment import Environment
from hn_core.core.post import Post

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def handler(obj):
    """convert objects compatible with json"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_simulation_results(post: Post, timestamp: datetime.datetime):
    """Save simulation results to a JSON file in the Results directory."""
    # Create Results directory if it doesn't exist
    results_dir = "./results"
    os.makedirs(results_dir, exist_ok=True)

    # Create filename with timestamp
    filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_results.json"
    filepath = os.path.join(results_dir, filename)

    # Prepare results data
    results = {
        "timestamp": timestamp.isoformat(),
        "post": {
            "title": post.title,
            "url": post.url,
            "text": post.text,
            "final_score": post.score,
            "final_upvotes": post.upvotes,
            "comments_count": len(post.comments),
            "comments": post.comments,
        },
    }

    # Save to file with custom serialization
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=handler)

    return filepath


def run(model: str, num_agents: int = None):
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
    personas_path = os.path.join(os.path.dirname(__file__), "personas.jsonl")

    # load personas
    try:
        with open(personas_path, "r") as f:
            personas = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        persona = json.loads(line)
                        personas.append(persona)
                    except json.JSONDecodeError as e:
                        logging.error(
                            f"Error parsing persona line: {line}, error: {str(e)}"
                        )

            if not personas:
                raise ValueError("No valid personas found in file")
    except Exception as e:
        raise Exception(f"error loading personas: {str(e)}")

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
            activation_probability=0.3,
            model_params={"temperature": 1.0},
        )
        agents.append(agent)

    # Run the environment
    logging.info(f"starting simulation with {len(agents)} agents...")
    environment = Environment(
        total_time_steps=24,  # 24 hours
        agents=agents,
        post=post,
    )
    environment.run()

    # Save results
    results_file = save_simulation_results(environment.post, simulation_start)
    logging.info(f"\nresults saved to: {results_file}")


if __name__ == "__main__":
    fire.Fire(run)
