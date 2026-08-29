import httpx
import pytest

from common.config import settings
from common.llm import chat


def _ollama_available() -> bool:
    try:
        response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except httpx.TransportError:
        return False


def test_settings_model_present() -> None:
    assert settings.OLLAMA_MODEL.strip()


def test_ollama_tags_contains_qwen3() -> None:
    if not _ollama_available():
        pytest.skip("Ollama is not reachable at configured host")
    response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=20)
    names = [m.get("name", "") for m in response.json().get("models", [])]
    assert any("qwen3" in n for n in names)


def test_short_completion_non_empty() -> None:
    if not _ollama_available():
        pytest.skip("Ollama is not reachable at configured host")
    result = chat([{"role": "user", "content": "Reply with one word."}], max_tokens=5)
    text = result["response_content"].strip()
    assert text
