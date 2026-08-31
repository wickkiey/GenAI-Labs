"""Shared OpenAIChatCompletionClient factory pointed at local Ollama.

qwen3 isn't in autogen's known-model registry, so model_info must be given
explicitly (see /memories agent-frameworks.md).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from autogen_ext.models.openai import OpenAIChatCompletionClient

from common.config import settings


def make_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        api_key=settings.OLLAMA_API_KEY,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
        },
    )
