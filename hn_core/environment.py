import random

class Environment:
    def __init__(self, total_time_steps, agents, post):
        """Initialize the environment.

        Args:
            total_time_steps (int): The total number of time steps to simulate (in hours)
            agents (list): List of Agent objects that can interact with the post
            post (Post): A Post object representing the content being interacted with
        """
        self.total_time_steps = total_time_steps
        self.agents = agents
        self.post = post


    def run(self):
        for time_step in range(self.total_time_steps):
            random.shuffle(self.agents)
            for agent in self.agents:
                if agent.activation_probability >= random.random(): # TODO: Agents could also be activated based on the post rank and some randomness (i.e. agent.p >= weight * self.post.rank)
                    actions = agent.run(self.post)
                    self.post.update(actions)