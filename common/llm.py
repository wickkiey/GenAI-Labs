from __future__ import annotations

from typing import Any

from openai import OpenAI

from common.config import settings


def get_openai_client() -> OpenAI:
    return OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key=settings.OLLAMA_API_KEY)


def chat(messages: list[dict[str, str]], **kwargs: Any) -> Any:
    client = kwargs.pop("client", None) or get_openai_client()
    model = kwargs.pop("model", settings.OLLAMA_MODEL)
    return client.chat.completions.create(model=model, messages=messages, **kwargs)
