# Research Agent Framework

A LangGraph-based research agent that provides factual, academic, and economic research using free APIs.

## Setup

```bash
# Depending on your python you may need to activate an environment in which case use the two lines commented below:
# python3 -m venv .venv
# source .venv/bin/activate

# Otherwise just install requirements.txt
pip install -r requirements.txt
```

```bash
# Set ENV Vars
FRED_API_KEY=******
GOOGLE_AI_STUDIO_API_KEY=******
```

## Running the Agent

```bash
python agent.py "What is Basel III?"
python agent.py --verbose "What is Basel III?"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

Or run a specific test:

```bash
python -m pytest tests/test_scope_validation.py -v
```
