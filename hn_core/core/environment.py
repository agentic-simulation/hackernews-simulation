import random
from typing import List

from core.agent import Agent
from core.post import Post


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
        self.current_agent_idx = 0

    def run(self):
        """Run the simulation with sequential agent interactions."""
        for time_step in range(self.total_time_steps):
            # Each hour, go through agents in sequence
            for agent_idx in range(len(self.agents)):
                agent = self.agents[agent_idx]

                # Check if agent should be activated
                if agent.is_active and agent.activation_probability >= random.random():
                    # Agent sees current post state and acts
                    action = agent.run(self.post)

                    # Update post with agent's actions
                    self.post.update(action)

                    # Deactivate agent after interaction
                    agent.is_active = False

                    # Log the interaction (optional)
                    print(
                        f"Hour {time_step}: Agent {agent_idx} ({agent.bio}) performed action: {action.action}"
                    )

            # At the end of each hour, recalculate post rank
            self.post.rank = self.post.calculate_rank()
