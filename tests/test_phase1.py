from types import SimpleNamespace

import httpx
import pytest
from pydantic import BaseModel

from common.config import settings
from common.llm import chat


class Person(BaseModel):
    name: str
    age: int
    occupation: str


class FakeCompletions:
    def __init__(self, message: SimpleNamespace) -> None:
        self.message = message

    def create(self, **kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=self.message)])


class FakeClient:
    def __init__(self, message: SimpleNamespace) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions(message))


def _require_ollama() -> None:
    try:
        response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=2)
    except httpx.TransportError:
        pytest.skip("Ollama is not reachable at configured host")
    if response.status_code != 200:
        pytest.skip("Ollama tag endpoint is unavailable")


def test_chat_returns_response_content_only_without_thinking() -> None:
    response = chat(
        [{"role": "user", "content": "Hello"}],
        client=FakeClient(SimpleNamespace(content="Hi", reasoning_content="Hidden")),
        extra_body={"think": False},
    )
    assert response == {"response_content": "Hi"}


def test_chat_returns_reasoning_content_when_thinking_enabled() -> None:
    response = chat(
        [{"role": "user", "content": "Hello"}],
        client=FakeClient(SimpleNamespace(content="Hi", reasoning_content="Because.")),
        extra_body={"think": True},
    )
    assert response == {"response_content": "Hi", "reasoning_content": "Because."}


def test_structured_output_parses() -> None:
    _require_ollama()
    schema = Person.model_json_schema()
    response = chat(
        [{"role": "user", "content": "Return JSON for a fictional person with name, age, occupation."}],
        response_format={"type": "json_schema", "json_schema": {"name": "person", "schema": schema}},
        max_tokens=120,
    )
    person = Person.model_validate_json(response["response_content"] or "{}")
    assert person.name and person.occupation


def test_temperature_zero_is_repeatable() -> None:
    _require_ollama()
    message = [{"role": "user", "content": "Respond with exactly: DETERMINISTIC"}]
    a = chat(message, temperature=0, max_tokens=8, seed=42)["response_content"]
    b = chat(message, temperature=0, max_tokens=8, seed=42)["response_content"]
    assert (a or "").strip() == (b or "").strip()


def test_streaming_emits_multiple_chunks() -> None:
    _require_ollama()
    stream = chat(
        [{"role": "user", "content": "Count from 1 to 20 with commas."}],
        stream=True,
        max_tokens=80,
    )
    chunks = [c.choices[0].delta.content for c in stream if c.choices and c.choices[0].delta.content]
    assert len(chunks) > 1
