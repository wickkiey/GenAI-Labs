# Phase 7A: PydanticAI

PydanticAI is a Python framework that makes Pydantic's type validation core to agent design.
It's one of the newest frameworks and has excellent type safety and validation.

## Setup

```powershell
pip install pydantic-ai
# Verify torch still works
python -c "import torch; print(torch.__version__)"
```

## Files

- `01_basic_agent.py` - Simple question answering with Ollama
- `02_tools.py` - Add calculator and database tools
- `03_structured_output.py` - Return Pydantic model output
- `04_dependencies.py` - Use dependencies for context injection
- `05_mcp.py` - Pattern for MCP tool integration
- `06_the_spec_task.py` - Complete task with both tools and structured output

## Key Concepts

- **Agent**: Core class that wraps a model and manages tool use
- **Tools**: Decorated methods that the agent can call
- **Result Type**: Define output schema, automatically validated
- **Dependencies**: Inject context into tools via `deps` parameter
- **ModelProvider**: Supports any OpenAI-compatible endpoint

## Run Tests

```powershell
python 06_frameworks/pydantic_ai/06_the_spec_task.py "What is 1234 * 5678?"
pytest tests/test_framework_pydantic_ai.py -v
```

## What Surprised Me

- PydanticAI's type system is very strict, which is both a feature and requires careful schema design
- The dependency injection pattern is elegant for stateful operations
- Performance is good; tool calling happens in one round trip

## What Broke

- Initial attempts to use `ModelProvider` directly without `via_url` - needed to specify the full endpoint
- The `result_type` requires matching the LLM output format exactly
