import litellm

class Agent:
    def __init__(self, 
                 model: str = "gpt-4o-mini", 
                 temperature: float = 0.5, 
                 bio: str = "", 
                 p: float = 0.5):
        
        self.bio = bio
        self.model = model
        self.temperature = temperature
        self.memory = []
        self.p = p

        # Load agent prompt template
        with open("hn_core/prompts/agent_prompt_template.txt", "r") as f:
            self.prompt_template = f.read()

    def run(self, post):
        actions = self.get_agent_response(self, post)
        self.add_memory(actions)
        return actions

    def add_memory(self, actions):
        self.memory.append(actions)

    def get_agent_response(self, agent, post):
        # TODO: Fill in the agent prompt template with relevant information

        # TODO: Create the messages to send to the LLM

        # TODO: Send the messages to the LLM and return the response 

        # TODO: Parse the response and collect the actions in a structured format 
        # (i.e. list of dictionaries like [{'upvote': True, 'comment': 'This is a great post!'}, {'upvote': False, 'comment': None}, ...])
        # Comments could eventually have nested comments, so we will need to handle that. So the agent can decide to comment on a comment.

        # TODO: Add the actions to the agent's memory

        # TODO: Return the actions

        raise NotImplementedError("get_agent_response not implemented")
