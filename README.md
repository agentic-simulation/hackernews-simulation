# Overview
Core infrastructure for agentic simulation.

- Set up dependencies: `poetry install`

## How to run
Run: `python hn_core/main.py --model <provider/model> --num-agents 5 --total-time-steps 12 --batch-size 5`

### Command Line Arguments
Required:
- `--model`: The LLM model to use (follows LiteLLM naming convention, e.g. 'anthropic/claude-3-sonnet')

Optional:
- `--total-time-steps`: Total number of time steps to simulate (default: 24)
- `--num-agents`: Number of agents to simulate in the environment (default: all agents)
- `--batch-size`: Maximum number of concurrent API calls to process (default: None)


## How to run hyperparameter search
Run: `python eval/hyperparam_search.py --model <provider/model> --n-trials 10 --personas-path <path/to/personas.json>`

### Command Line Arguments
Required:
- `--model`: The LLM model to use (follows LiteLLM naming convention, e.g. 'anthropic/claude-3-sonnet')

Optional:
- `--n-trials`: Number of trials to run (default: 10)
- `--personas-path`: Path to the personas file (default: `personas_data/500_v1.jsonl`)

## Note
- Model name follows `LiteLLM` convention.
