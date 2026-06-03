# Research Agent Framework - Project Guidelines

## Core Principles

### Free Tools Only
This project uses **ONLY FREE TOOLS** throughout the entire development lifecycle. No paid APIs or services are permitted.

### Approved Tools & Services
- **LLM Model**: Ollama with Qwen2.5:7b (free local model)
- **Framework**: LangChain + LangGraph (open source)
- **Dependencies**: Open source Python packages only
- **Development**: Local development environment

### Prohibited Tools
- OpenAI API (paid service)
- Anthropic Claude API (paid service)
- Google Gemini API (paid service)
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
- **Model**: ollama:qwen2.5:7b
- **Temperature**: 0.2
- **API**: LangGraph init_chat_model

## Project Structure
- `main.py` - CLI wrapper and agent implementation
- `requirements.txt` - Free dependencies only
- `CLAUDE.md` - This guidelines file
- `prompt-log.md` - Session documentation