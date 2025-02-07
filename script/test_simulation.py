from hn_core.simulation import run as simulation

post = {
    "title": "How to Scale Your Model: A Systems View of LLMs on TPUs",
    "url": "jax-ml.github.io",
    "text": "",
}


if __name__ == "__main__":
    roles, result = simulation.run(
        **post,
        model="gpt-4o-mini",
        num_agents=30,
        total_time_steps=5,
        batch_size=5,
    )

    print(result)
