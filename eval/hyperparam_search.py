import json
import os
import datetime

import fire
import optuna
from dotenv import load_dotenv

from hn_core.core.agent import Agent
from hn_core.core.environment import Environment 
from hn_core.core.post import Post
from hn_core.utils import load_personas

load_dotenv()


def run_eval_simulation(
        post: dict, 
        personas: list, 
        num_agents: int, 
        activation_probability: float, 
        model: str, 
        temperature: float, 
        total_time_steps: int, 
        batch_size: int,
        k: float,
        threshold: float
    ):
    """ Run the evaluation simulation """
    
    personas = personas[:num_agents]

    # Create a Post object from the dictionary
    post_obj = Post(
        title=post['title'],
        url=post['url'],
        text=post['text']
    )

    # Create agents
    agents = []
    for persona in personas:
        agent = Agent(
            bio=persona["bio"],
            activation_probability=activation_probability,
            model=model,
            model_params={"temperature": temperature},
        )
        agents.append(agent)

    # Run the environment
    environment = Environment(
        total_time_steps=total_time_steps,
        agents=agents,
        post=post_obj,
        k=k,
        threshold=threshold
    )
    environment.run(batch_size)
    
    # Return final state from history
    final_state = {
        'upvotes': environment.post.upvotes,
        'comments': len(environment.post.comments)
    }

    return final_state

def objective(trial: optuna.Trial, post: dict, personas: list, model: str, total_time_steps: int, post_metrics: dict):
    """Optuna objective function for hyperparameter optimization"""

    # Define hyperparameter search space
    num_agents = len(personas) # trial.suggest_int('num_agents', 50, len(personas))
    temperature = 0.2 # trial.suggest_float('temperature', 0.1, 1.0)
    batch_size = trial.suggest_int('batch_size', 5, num_agents)
    k = trial.suggest_float('k', 0.01, 0.5)
    threshold = trial.suggest_float('threshold', 2.0, 15.0)
    activation_probability = trial.suggest_float('activation_probability', 0.0, 1.0)

    final_state = run_eval_simulation(
        post=post,
        personas=personas,
        num_agents=num_agents,
        activation_probability=activation_probability,
        model=model,
        temperature=temperature,
        total_time_steps=total_time_steps,
        batch_size=batch_size,
        k=k,
        threshold=threshold
    )
    
    # Calculate MSE using length of comments list
    mse = (
        (final_state['upvotes'] - post_metrics['upvotes'])**2 +
        (final_state['comments'] - post_metrics['comments'])**2
    ) / 2.0
    
    return mse

def run_hyperparam_search(model: str = "groq/gemma2-9b-it", n_trials: int = 10, personas_path: str | None = None):
    """Run hyperparameter optimization for the simulation.
    
    Args:
        model (str): The name/identifier of the LLM model to use.
        n_trials (int): Number of optimization trials to run.
        personas_path (str, optional): Path to personas data. If None, uses default path.
    """
    # Load personas
    if personas_path is None:
        personas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "personas_data/500_v1.jsonl")
    personas = load_personas(personas_path)

    # Post to run the search with
    post = {
        "title": "Show HN: I Created ErisForge, a Python Library for Abliteration of LLMs",
        "url": "https://github.com/Tsadoq/ErisForge",
        "text": "ErisForge is a Python library designed to modify Large Language Models (LLMs) by applying transformations to their internal layers. Named after Eris, the goddess of strife and discord, ErisForge allows you to alter model behavior in a controlled manner, creating both ablated and augmented versions of LLMs that respond differently to specific types of input.\nIt is also quite useful to perform studies on propaganda and bias in LLMs (planning to experiment with deepseek).\nFeatures - Modify internal layers of LLMs to produce altered behaviors. - Ablate or enhance model responses with the AblationDecoderLayer and AdditionDecoderLayer classes. - Measure refusal expressions in model responses using the ExpressionRefusalScorer. - Supports custom behavior directions for applying specific types of transformations.",
        "upvotes": 98,
        "comments": 42,
        "time_delta": 11,
    }

    post_metrics = {
        'upvotes': post['upvotes'],
        'comments': post['comments'],
    }
    
    # Run the optimization
    study = optuna.create_study(
        direction='minimize',
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    study.optimize(
        lambda trial: objective(
            trial, 
            post=post,
            personas=personas,
            model=model,
            total_time_steps=post['time_delta'],
            post_metrics=post_metrics
        ),
        n_trials=n_trials
    )

    # Return the best hyperparameters and the results
    best_params = study.best_params
    best_value = study.best_value
    
    # Create results dictionary
    results = {
        "best_parameters": best_params,
        "best_mse": best_value,
        "n_trials": n_trials
    }
    
    # Save results to JSON file
    output_dir = "hyperparam_search_results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"hyperparam_search_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    fire.Fire(run_hyperparam_search)
