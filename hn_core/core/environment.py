import random
import math
from typing import List
from concurrent.futures import ThreadPoolExecutor

from hn_core.core.agent import Agent
from hn_core.core.post import Post


class Environment:
    def __init__(self, total_time_steps: int, agents: List[Agent], post: Post):
        """Initialize the environment.

        Args:
            total_time_steps (int): The total number of time steps to simulate (in hours)
            agents (list): List of Agent objects that can interact with the post in sequence
            post (Post): A Post object representing the content being interacted with
        """
        self.total_time_steps = total_time_steps
        self.agents = agents
        self.post = post
        self.agent_actions = []

    def run(self, batch_size: int = 20, k: float = 0.1, threshold: float = 5):
        """Run the simulation with sequential or parallel agent interactions.
        
        Args:
            batch_size (int | None): If provided, runs simulation in batches
                                   of specified size. If None, runs sequentially.
            delay (int | None): If provided, adds a delay between each batch of agents or agent (in seconds).
        """

        for time_step in range(self.total_time_steps):
            random.shuffle(self.agents)
            
            # Process agents in batches
            for i in range(0, len(self.agents), batch_size):
                batch = self.agents[i:i + batch_size]
                
                # Process each agent in parallel
                with ThreadPoolExecutor(max_workers=batch_size) as executor:
                    executor.map(
                        lambda agent: self._process_agent(agent, time_step, k, threshold),
                        batch
                    )
            self.post.record_history()

    def _process_agent(self, agent: Agent, time_step: int, k: float, threshold: float):
        """Process a single agent's interaction with the post.
        
        The activation probability is modified by the post's score using a sigmoid function:
        final_prob = base_prob * (1 / (1 + e^(-k * (score - threshold))))

        where:
        - base_prob is the agent's initial activation probability
        - score is the post's score
        - threshold is the score threshold where probability starts increasing significantly
        - k is the sigmoid's steepness and controls how quickly the probability changes
        
        This ensures:
        - Very low scores (<threshold) result in lower activation probability
        - Very high scores (>threshold) result in higher activation probability
        - The effect is smooth and bounded between 0 and the original probability
        """
        # Calculate score modifier using sigmoid function
        score_modifier = 1 / (1 + math.exp(-k * (self.post.score - threshold)))
        
        # Combine base probability with score modifier
        final_probability = agent.activation_probability * score_modifier

        if agent.is_active and final_probability >= random.random():
            # agent sees current post state and acts
            action = agent.run(self.post)
            # update post with agent's actions
            # TODO update time_step to reflect agent behavior in current time step
            self.agent_actions.append({
                "sim_step": time_step,
                "agent_bio": agent.bio,
                "actions": action
            })
            self.post.update(action=action, current_time=time_step)
            agent.is_active = False
            print(f"Hour {time_step}: Agent ({agent.bio}) performed action: {action}")
