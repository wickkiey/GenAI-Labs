# Phase 1: LLM Basics

- `01_simple_completion.py`: sends one user message and prints one response.
- `02_system_prompt.py`: keeps the same user question but changes the system role to show steering.
- `03_conversation.py`: preserves a growing `messages` history for multi-turn context.
- `04_streaming.py`: enables `stream=True` and prints partial tokens as they arrive.
- `05_structured_output.py`: requests JSON using a schema and validates it with Pydantic.
- `06_parameters.py`: compares generation settings like temperature, max tokens, and seed.

These scripts all use shared setup from `/home/runner/work/GenAI-Labs/GenAI-Labs/common/config.py` and `/home/runner/work/GenAI-Labs/GenAI-Labs/common/llm.py`.
