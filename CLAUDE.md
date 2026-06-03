# Research Agent Framework - Project Guidelines

## Core Principles

### Free Tools Only
This project uses **ONLY FREE TOOLS** throughout the entire development lifecycle. No paid APIs or services are permitted.

### DO NOT USE STRONG TYPING IN PYTHON IN THIS PROJECT. WE DO NOT NEED TO TYPE CHECK RIGHT NOW

### Approved Tools & Services
- **LLM Model**: Google AI Studio with Gemini Pro (free tier)
- **Framework**: LangChain + LangGraph (open source)
- **Dependencies**: Open source Python packages only
- **Development**: Local development environment

### Prohibited Tools
- OpenAI API (paid service)
- Anthropic Claude API (paid service)
- Any other paid LLM services

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running the Agent
```bash
python main.py "your research query"
python main.py --verbose "your research query"
```

### Testing
```bash
python main.py --help
```

## Model Configuration
- **Model**: Google AI Studio Gemini Pro
- **Temperature**: 0.2
- **API Key**: GOOGLE_AI_STUDIO_API_KEY environment variable

## Project Structure
- `main.py` - CLI wrapper and agent implementation
- `requirements.txt` - Free dependencies only
- `CLAUDE.md` - This guidelines file
- `prompt-log.md` - Session documentation
- `/agents` - Langgraph Agents
- `/tools` - Tools for API calls