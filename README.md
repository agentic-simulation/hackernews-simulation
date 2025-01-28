# Overview
Core infrastructure for agentic simulation.

## How to run
1. Set up dependencies: `poetry install`
2. Run: `python main.py --model <provider/model> --num-agents 5 --total-time-steps 12 --batch-size 5`

### Command Line Arguments
Required:
- `--model`: The LLM model to use (follows LiteLLM naming convention, e.g. 'anthropic/claude-3-sonnet')

Optional:
- `--total-time-steps`: Total number of time steps to simulate (default: 24)
- `--num-agents`: Number of agents to simulate in the environment (default: all agents)
- `--batch-size`: Maximum number of concurrent API calls to process (default: None)

## Note
- Model name follows `LiteLLM` convention.