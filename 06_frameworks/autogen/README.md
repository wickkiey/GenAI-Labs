# Phase 7F: AutoGen

AutoGen is a framework for creating multi-agent systems with conversational patterns.

⚠️ **MAINTENANCE MODE WARNING**: AutoGen has transitioned to a new API.
The old pyautogen is in maintenance mode. New projects should consider LangGraph.

## Setup

```powershell
# New API (recommended)
pip install autogen-agentchat autogen-ext

# If dependencies conflict, use Docker:
docker-compose up
```

## Implementation Notes

- `01_agent.py` - Spec task with AutoGen agent pattern
- AutoGen excels at:
  - Multi-agent conversations
  - Group chat patterns
  - Human-in-the-loop workflows
  - Code execution and review

## Key Concepts

- **AssistantAgent**: AI-powered agent
- **UserProxyAgent**: Human representative in conversation
- **GroupChat**: Multiple agents discussing
- **Tool**: Functions agents can call

## Run

```powershell
python 06_frameworks/autogen/01_agent.py
# Or with Docker:
docker-compose -f 06_frameworks/autogen/docker-compose.yml up
```

## ⚠️ Maintenance Status

AutoGen v0.2 is in maintenance mode. The new `autogen-agentchat` API is 
recommended for new projects, but the ecosystem is still stabilizing.

For production systems, consider LangGraph or PydanticAI instead.
