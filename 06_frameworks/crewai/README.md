# Phase 7E: CrewAI

CrewAI is a framework for orchestrating multiple AI agents to work together on tasks.

## Setup

```powershell
pip install crewai crewai-tools
# If dependencies conflict with torch, use Docker:
cd 06_frameworks/crewai
docker-compose up
```

## Implementation Notes

- `01_agent.py` - Spec task with CrewAI agent pattern
- CrewAI excels at:
  - Role-based agent design
  - Task-oriented workflows
  - Multi-agent coordination
  - Memory and context management

## Key Concepts

- **Agent**: Specialized role (e.g., Researcher, Writer)
- **Task**: Work unit with goal and description
- **Tool**: Functions agents can execute
- **Crew**: Collection of agents working together

## Run

```powershell
python 06_frameworks/crewai/01_agent.py
# Or with Docker if conflicts arise:
docker-compose -f 06_frameworks/crewai/docker-compose.yml up
```

## ⚠️ Dependency Warning

CrewAI aggressively pins dependencies. If conflicts arise with torch or other packages:

1. First try: `pip install --upgrade crewai`
2. If that fails, snapshot before install:
   ```powershell
   pip freeze > requirements/snapshot_before_crewai.txt
   pip install crewai crewai-tools
   ```
3. If still broken, use Docker container instead (included)
