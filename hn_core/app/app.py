import os
import sys

import streamlit as st

from hn_core.simulation.run import run


def main():
    st.title("HackerNews Simulation")

    st.header("Post Details")
    title = st.text_input("Post Title", "")
    url = st.text_input("Post URL", "")
    text = st.text_area("Post Text", "")

    # Model selection
    model = st.text_input("Model Name", "gpt-4o-mini")

    # Optional parameters with default values in sidebar
    st.sidebar.header("Simulation Parameters")
    num_agents = st.sidebar.number_input(
        "Number of Agents",
        min_value=1,
        value=500,
        help="The number of agents that will participate in the simulation. Each agent represents a unique user with their own behavior patterns.",
    )
    total_time_steps = st.sidebar.number_input(
        "Total Time Steps",
        min_value=1,
        value=10,
        help="The total number of time steps to simulate. Each time step represents a discrete moment where agents can take actions.",
    )
    batch_size = st.sidebar.number_input(
        "Batch Size",
        min_value=1,
        value=10,
        help="The number of agents to process in each batch. A larger batch size may speed up simulation but consume more memory.",
    )
    k = st.sidebar.number_input(
        "Steepness Parameter (k)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        help="Controls how quickly the probability of agent actions changes with respect to post scores. Higher values make agents more sensitive to score differences.",
    )

    # Run simulation button
    if st.button("Run Simulation"):
        if not title:
            st.error("Please fill in all required fields (Title)")
            return

        try:
            with st.spinner("Running simulation..."):
                agent_profile, post_history = run(
                    title=title,
                    url=url,
                    text=text,
                    model=model,
                    num_agents=num_agents if num_agents else None,
                    total_time_steps=total_time_steps,
                    batch_size=batch_size,
                    k=k,
                )

                # Display results
                st.header("Simulation Results")

                # Display post history
                st.subheader("Final Post State")
                st.json(post_history)

                # Display agent profiles
                st.subheader("Agent Profiles")
                st.json(agent_profile)

        except Exception as e:
            st.error(f"An error occurred during simulation: {str(e)}")


if __name__ == "__main__":
    main()
