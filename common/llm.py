from __future__ import annotations

from typing import Any

from openai import OpenAI

from common.config import settings


def get_openai_client() -> OpenAI:
    return OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key=settings.OLLAMA_API_KEY)


def chat(messages: list[dict[str, Any]], **kwargs: Any) -> Any:
    client = kwargs.pop("client", None) or get_openai_client()
    model = kwargs.pop("model", settings.OLLAMA_MODEL)
    kwargs.setdefault("extra_body", {"think": False})
    extra_body = kwargs["extra_body"] or {}
    thinking_enabled = bool(
        extra_body.get("think") or extra_body.get("thinking") or extra_body.get("reasoning")
    )
    if not thinking_enabled:
        messages = [
            {
                "role": "system",
                "content": "Do not think. Answer directly.",
            },
            *messages,
        ]
    response = client.chat.completions.create(model=model, messages=messages, **kwargs)
    if kwargs.get("stream"):
        return response

    message = response.choices[0].message
    result = {"response_content": message.content or ""}
    if tool_calls := getattr(message, "tool_calls", None):
        result["tool_calls"] = tool_calls
    if thinking_enabled:
    # 1. Check Ollama's native property style
    # 2. Fallback to Open-Source/vLLM convention (DeepSeek)
    # 3. Fallback to Anthropic/UI convention
        result["reasoning_content"] = (
            getattr(message, "reasoning", None)          # Ollama standard
            or getattr(message, "reasoning_content", None)  # vLLM / DeepSeek standard
            or getattr(message, "thinking", None)         # Anthropic / Custom standard
            or ""
        )
    return result
