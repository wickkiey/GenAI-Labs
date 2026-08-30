"""
Phase 7A: PydanticAI - 03_structured_output.py

Return structured output using Pydantic models.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic import BaseModel
from pydantic_ai import Agent, ModelProvider

from common.config import settings

# Import the Answer model from spec
spec = import_module("06_frameworks.spec")
Answer = spec.Answer


def main() -> None:
    agent = Agent(
        model=ModelProvider.via_url(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.OLLAMA_MODEL,
            api_key=settings.OLLAMA_API_KEY,
        ),
        result_type=Answer,
        system_prompt="You are a helpful assistant. Return your answer in the specified JSON format.",
    )

    question = "What is 100 + 50?"
    result = agent.run_sync(question)
    print(result.data.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
