import datetime
import json
import logging
import os
import numpy as np
import optuna

from dotenv import load_dotenv
from hn_core.core.agent import Agent
from hn_core.core.environment import Environment
from hn_core.core.post import Post
from hn_core.utils import load_personas


load_dotenv()


def run_eval_simulation(
        post, 
        personas, 
        num_agents, 
        activation_probability, 
        model, 
        temperature, 
        total_time_steps, 
        batch_size,
        k,
        threshold
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
            model=model,
            bio=persona["bio"],
            activation_probability=activation_probability,
            model_params={"temperature": temperature},
        )
        agents.append(agent)

    # Run the environment with Post object instead of dict
    print(f"starting simulation with {len(agents)} agents...")
    environment = Environment(
        total_time_steps=total_time_steps,
        agents=agents,
        post=post_obj,
    )
    environment.run(batch_size, k, threshold)
    
    # Return final state from history
    return environment.post.history[-1]

def objective(trial, post, personas, model, total_time_steps, snapshot_metrics):
    """Optuna objective function for hyperparameter optimization"""
    # Define hyperparameter search space
    num_agents = trial.suggest_int('num_agents', 50, len(personas))
    temperature = trial.suggest_float('temperature', 0.1, 1.0)
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
        (final_state['upvotes'] - snapshot_metrics['upvotes'])**2 +
        (len(final_state['comments']) - snapshot_metrics['comments'])**2
    ) / 2.0
    
    return mse

if __name__ == "__main__":
    
    # Get personas and post to evaluate
    personas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "personas_data/500_v1.jsonl")
    personas = load_personas(personas_path) # Load personas

    # Fixed parameters
    model = "groq/gemma2-9b-it" # Model to use

    # 1. Get a post (preferably from the snapshot)
    post_snapshot = {
        "title": "Show HN: I Created ErisForge, a Python Library for Abliteration of LLMs",
        "url": "https://github.com/Tsadoq/ErisForge",
        "text": "ErisForge is a Python library designed to modify Large Language Models (LLMs) by applying transformations to their internal layers. Named after Eris, the goddess of strife and discord, ErisForge allows you to alter model behavior in a controlled manner, creating both ablated and augmented versions of LLMs that respond differently to specific types of input.\nIt is also quite useful to perform studies on propaganda and bias in LLMs (planning to experiment with deepseek).\nFeatures - Modify internal layers of LLMs to produce altered behaviors. - Ablate or enhance model responses with the AblationDecoderLayer and AdditionDecoderLayer classes. - Measure refusal expressions in model responses using the ExpressionRefusalScorer. - Supports custom behavior directions for applying specific types of transformations.",
        "upvotes": 98,
        "comments": 42,
        "time_delta": 11,
    }
   
    # 2. Do the search of best hyperparameters for the post
    snapshot_metrics = {
        'upvotes': post_snapshot['upvotes'],
        'comments': post_snapshot['comments'],
    }
    
    study = optuna.create_study(
        direction='minimize',
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    study.optimize(
        lambda trial: objective(
            trial, 
            post=post_snapshot,
            personas=personas,
            model=model,
            total_time_steps=post_snapshot['time_delta'],
            snapshot_metrics=snapshot_metrics
        ),
        n_trials=2  # Adjust based on your computational budget
    )

    # 3. Return the best hyperparameters and the results
    best_params = study.best_params
    best_value = study.best_value
    
    print("Best hyperparameters found:")
    print(json.dumps(best_params, indent=2))
    print(f"Best MSE: {best_value}")
