# Phase 2: First Agent

These framework-free examples use `OLLAMA_MODEL` from `.env` through the shared
OpenAI-compatible Ollama client. They intentionally do not depend on an agent framework.

- `01_basic_agent.py` keeps conversation history for a single model call per turn.
- `02_agent_with_tool.py` handles one calculator tool round-trip.
- `03_agent_loop.py` supports sequential calculator calls and stops after five rounds.
- `04_structured_agent.py` returns the final response as an `AgentAnswer` Pydantic model.

Run the bounded tool loop against the local model:

```powershell
python 02_agents/03_agent_loop.py "What is 1234 * 5678, then subtract 1000?"
```
