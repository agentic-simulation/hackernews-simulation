# HackerNews Simulation: An Agent-Based Approach to Digital Community Modeling

This project presents a framework for using AI agents in simulating social media - HackerNews.

## Architectural Framework

### Environment

The environmentfunctions as the orchestrator, coordinating all components within the simulation system. To accurately represent temporal dynamics inherent in real-world systems, we have implemented discrete timestep progression.

For each temporal iteration:
- Agent activation is determined by a probabilistic activation function
- Activated agents execute behavioral protocols
- All agent-environment interactions are recorded and system state is updated accordingly

<img src="./assets/environment.png" width="600" height="500">

### Agent

The agent is designed to emulate authentic user interaction patterns based on activity data. The activation function incorporates multiple parameters including post score and temporal variables to determine agent participation probability.

<img src="./assets/agent.png" width="600" height="500">

## Implementation Protocol

Install requisite dependencies utilizing Poetry package management: `poetry install`

## Execution Procedure

Execute `sh run.sh` from the root directory and access the visualization interface at `http://localhost:8501/`

## Bibliographic References

- [OASIS: Open Agent Social Interaction Simulations with One Million Agents](https://arxiv.org/abs/2411.11581)
- [Scaling Synthetic Data Creation with 1,000,000,000 Personas](https://arxiv.org/abs/2406.20094)
