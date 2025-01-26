"""
HN Core Simulation

This module runs a simulation of agent interactions on a Hacker News-style platform.

To run the simulation:
1. Make sure you have all dependencies installed:
   poetry install

2. Set up your environment variables:
   cp .env.template .env
   # Edit .env with your API keys if needed

3. Run the simulation:
   # From project root:
   # Run with all agents from personas.jsonl:
   poetry run python -m hn_core.main
   
   # Run with specific number of agents:
   poetry run python -m hn_core.main --num-agents 5

   # Or from hn_core directory:
   cd hn_core
   poetry run python main.py --num-agents 5

To run the tests:
1. Run all tests:
   poetry run pytest tests/

2. Run specific test file:
   poetry run pytest tests/test_agent.py
   poetry run pytest tests/test_post.py
   poetry run pytest tests/test_environment.py

3. Run with verbose output:
   poetry run pytest -v tests/

4. Run with coverage report:
   poetry run pytest --cov=hn_core tests/
"""

import json
import os
import sys
from dotenv import load_dotenv
import logging
import datetime
import argparse

from hn_core.agent import Agent
from hn_core.environment import Environment
from hn_core.post import Post

# Adjust imports based on how the script is run
if __name__ == "__main__" and not __package__:
    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, file_path)
    from agent import Agent
    from environment import Environment
    from post import Post

def save_simulation_results(post, timestamp):
    """Save simulation results to a JSON file in the Results directory."""
    # Create Results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Results')
    os.makedirs(results_dir, exist_ok=True)

    # Create filename with timestamp
    filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_results.json"
    filepath = os.path.join(results_dir, filename)

    # Convert datetime objects to ISO format strings
    def datetime_handler(obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    # Create agent ID mapping
    agent_ids = {}
    current_agent_id = 0

    # Map existing agent IDs to sequential ones
    for interaction in post.interaction_stats['interaction_history']:
        original_id = interaction['agent_id']
        if original_id not in agent_ids:
            agent_ids[original_id] = current_agent_id
            current_agent_id += 1

    # Update interaction history with sequential agent IDs
    updated_history = []
    for interaction in post.interaction_stats['interaction_history']:
        updated_interaction = interaction.copy()
        updated_interaction['agent_id'] = agent_ids[interaction['agent_id']]
        updated_history.append(updated_interaction)
    
    # Update interaction_stats with the new history
    updated_stats = post.interaction_stats.copy()
    updated_stats['interaction_history'] = updated_history

    # Prepare results data
    results = {
        'timestamp': timestamp.isoformat(),
        'post': {
            'title': post.title,
            'url': post.url,
            'text': post.text,
            'time_posted': post.time_posted.isoformat(),
            'final_rank': post.rank,
            'final_upvotes': post.upvotes,
            'final_downvotes': post.interaction_stats['downvotes'],
            'final_comments': len(post.comments),
            'final_favorites': post.interaction_stats['favorites'],
            'comments': post.comments
        },
        'interaction_stats': updated_stats
    }

    # Save to file with custom serialization
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=datetime_handler)
    
    return filepath

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run HN Core simulation')
    parser.add_argument('--num-agents', type=int, help='Number of agents to use in simulation. Defaults to all available personas.')
    return parser.parse_args()

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Record simulation start time
    simulation_start = datetime.datetime.now()
    
    # Create a sample post
    post = Post(
        title="Building a Developer-First SaaS: From Zero to Production",
        url="https://www.example.com",
        text="A technical deep-dive into building a SaaS startup, covering architecture decisions, tech stack choices (Rust vs Go for backend, React vs Svelte for frontend), CI/CD pipeline setup, and how we achieved sub-100ms API response times while keeping infrastructure costs under $100/month. Includes code samples and performance benchmarks.",
    )

    # Load personas in order from personas.jsonl
    logging.info("Loading personas in sequence...")
    personas_path = os.path.join(os.path.dirname(__file__), 'personas.jsonl')
    logging.info(f"Loading personas from: {personas_path}")
    
    try:
        with open(personas_path, "r") as f:
            personas = []
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        persona = json.loads(line)
                        personas.append(persona)
                    except json.JSONDecodeError as e:
                        logging.error(f"Error parsing persona line: {line}")
                        logging.error(f"Error details: {str(e)}")
                        continue
        
        if not personas:
            raise ValueError("No valid personas found in file")
            
        logging.info(f"Successfully loaded {len(personas)} personas")
    except Exception as e:
        logging.error(f"Error loading personas: {str(e)}")
        personas = []

    # Limit number of personas if specified
    if args.num_agents is not None:
        if args.num_agents > len(personas):
            logging.warning(f"Requested {args.num_agents} agents but only {len(personas)} personas available. Using all available personas.")
        else:
            logging.info(f"Using first {args.num_agents} personas from {len(personas)} available.")
            personas = personas[:args.num_agents]
    
    # Create agents in the same order as personas
    agents = []
    activation_probability = 0.5  # between 0 and 1
    for idx, persona in enumerate(personas):
        logging.info(f"Creating agent {idx} with bio: {persona['bio']}")
        agent = Agent(
            model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
            temperature=0.5,
            bio=persona["bio"],
            activation_probability=activation_probability,
        )
        agents.append(agent)

    # Run the environment
    logging.info(f"Starting simulation with {len(agents)} agents...")
    environment = Environment(
        total_time_steps=24,  # 24 hours
        agents=agents,
        post=post,
    )
    environment.run()

    # Save results
    results_file = save_simulation_results(post, simulation_start)
    logging.info(f"\nResults saved to: {results_file}")

    # Print the final results
    logging.info("\nSimulation Results:")
    logging.info(f"Post rank: {post.rank}")
    logging.info(f"Post upvotes: {post.upvotes}")
    logging.info("Post comments:")
    for comment in post.comments:
        logging.info(f"- {comment['text']}")
    
    # Print interaction history
    logging.info("\nInteraction History:")
    for interaction in post.interaction_stats['interaction_history']:
        logging.info(f"Time: {interaction['timestamp']}")
        logging.info(f"Action: {interaction['action']}")
        if interaction.get('comment_text'):
            logging.info(f"Comment: {interaction['comment_text']}")
        logging.info("---")
