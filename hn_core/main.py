import json
from dotenv import load_dotenv

from hn_core.agent import Agent
from hn_core.environment import Environment
from hn_core.post import Post


load_dotenv()

if __name__ == "__main__":
    # Create a sample post
    post = Post(
        title="How to build a startup",
        url="https://www.example.com",
        text="This is a post about how to build a startup",
    )

    # Create some agents based on personas (from personas.jsonl)
    with open("hn_core/personas.jsonl", "r") as f:
        personas = [json.loads(line) for line in f]
    
    agents = []
    for persona in personas:
        agent = Agent(
            model="gpt-4o-mini",
            temperature=0.5,
            bio=persona["bio"],
            activation_probability=persona["activation_probability"],
        )
        agents.append(agent)

    # TODO: we migth want to run the environment multiple times and average the results
    # Run the environment
    environment = Environment(
        total_time_steps=10,
        agents=agents,
        post=post,
    )
    environment.run()

    # Print the results
    print(f"Post rank: {post.rank}\n")
    print(f"Post upvotes: {post.upvotes}\n")
    print(f"Post comments: {post.comments}\n")
