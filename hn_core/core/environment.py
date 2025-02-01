import math
import random
from concurrent.futures import ThreadPoolExecutor
from typing import List

from hn_core.core.agent import Agent
from hn_core.core.post import Post
from hn_core.provider.litellm import LLM
from hn_core.utils.logger import get_logger

from .model import ClassifyModel

logger = get_logger("hn_environment")


class Environment:
    def __init__(
        self,
        total_time_steps: int,
        agents: List[Agent],
        post: Post,
        k: float,
    ):
        """Initialize the environment.

        Args:
            total_time_steps (int): The total number of time steps to simulate (in hours)
            agents (list): List of Agent objects that can interact with the post
            post (Post): A Post object representing the content being interacted with
            k (float): The steepness parameter for the sigmoid function that modifies agent
                       activation probability based on post score.
        """
        self.total_time_steps = total_time_steps
        self.agents = agents
        self.post = post
        self.k = k
        self.agent_actions = []
        self.activated = 0

    def run(self, max_workers: int = 10, batch_size: int | None = None):
        """Run the simulation with sequential or parallel agent interactions."""

        if batch_size is None:
            batch_size = len(self.agents)

        for time_step in range(self.total_time_steps):
            logger.info(f"Processing time step {time_step}")
            random.shuffle(self.agents)

            # Process agents in batches
            for i in range(0, len(self.agents), batch_size):
                batch = self.agents[i : i + batch_size]

                # Process each agent in parallel
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # force immediate execution and proper error propagation
                    list(
                        executor.map(
                            lambda agent: self._process_agent(agent, time_step), batch
                        )
                    )
                self.post.update_step_state(time_step)

                logger.info(
                    f"Activated agents: {self.activated} at time_step: {time_step}"
                )

    def _process_agent(self, agent: Agent, time_step: int):
        """Process a single agent's interaction with the post.

        The activation probability is determined by the base_probabilty * modifier
        where modifier is a sigmoid function with parameter k.

        final_prob = base_prob * (1 / (1 + e^(-score / k)))

        - base_prob is the agent's initial activation probability
        - score is the post's score
        - k controls how much score affects the final activation probabilty.

        This ensures:
        - Low score gets penalized with low activation probability.
        - High scores gets rewarded with high activation probability
        - The effect is smooth and bounded between 0 and the original probabilit
        """
        # sigmoid function to reward/penalize probabilty based on the score
        score_modifier = 1 / (1 + math.exp(-self.post.score / self.k))
        final_probability = agent.activation_probability * score_modifier

        if agent.is_active and final_probability >= random.random():
            self.activated += 1
            action = agent.run(self.post)

            self.agent_actions.append(
                {"sim_step": time_step, "agent_bio": agent.bio, "actions": action}
            )

            self.post.update(action=action, current_time=time_step)
            agent.is_active = False
