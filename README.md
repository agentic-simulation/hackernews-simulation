# Overview
Core infrastructure for agentic simulation.

- Set up dependencies: `poetry install`

## How to run simulation
From the root directory: `sh script/run.sh`. To change parameters, update `script/test_simulation.py` file.


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
