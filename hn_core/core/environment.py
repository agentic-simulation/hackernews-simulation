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

    def run(self):
        """Run the simulation with sequential agent interactions."""
        for time_step in range(self.total_time_steps):
            # TODO: possibly shuffle order at each time step.
            for agent in self.agents:
                # TODO: activation should consider post score since score affects visibility of a post.
                if agent.is_active and agent.activation_probability >= random.random():
                    # agent sees current post state and acts
                    action = agent.run(self.post)
                    # update post with agent's actions
                    # TODO update time_step to reflect agent behavior in current time step
                    self.post.update(action=action, current_time=time_step)
                    agent.is_active = False
                    print(
                        f"Hour {time_step}: Agent ({agent.bio}) performed action: {action.action}"
                    )
