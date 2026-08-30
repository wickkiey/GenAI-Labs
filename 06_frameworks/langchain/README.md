# Phase 7B: LangChain

LangChain is a comprehensive framework for building agents with flexible abstractions
for models, tools, memory, and retrieval.

## Setup

```powershell
pip install langchain langchain-community langchain-ollama
# Verify torch still works
python -c "import torch; print(torch.__version__)"
```

## Files

- `01_chat.py` - Basic chat with Ollama LLM
- `02_tools.py` - Decorate functions as tools
- `03_agent.py` - Create agent with AgentExecutor and tool-calling
- `04_structured_output.py` - Return Pydantic model output
- `05_mcp.py` - Pattern for MCP integration
- `06_the_spec_task.py` - Complete task implementation

## Key Concepts

- **LLM**: Wraps any OpenAI-compatible model (Ollama, Claude, etc.)
- **Tool**: Decorated function that an agent can call
- **AgentExecutor**: Runs agent loop: LLM → Tool call → LLM → ...
- **Prompt**: Templates for system, user, and placeholder messages
- **with_structured_output**: Forces LLM to return valid Pydantic model

## Run Tests

```powershell
python 06_frameworks/langchain/06_the_spec_task.py "What is 1234 * 5678?"
pytest tests/test_framework_langchain.py -v
```

## What Surprised Me

- LangChain's abstraction layer is very flexible but sometimes opaque
- Tool calling works smoothly with Ollama through the OpenAI compatibility layer
- The AgentExecutor's verbose mode is very helpful for debugging agent loops

## What Broke

- Initial attempts to use `from langchain_ollama` (the actual import is `langchain_community.llms.ollama`)
- Structured output parsing required careful JSON extraction from agent output
