import importlib
from types import SimpleNamespace

import pytest

from common.config import settings

agent_core = importlib.import_module("02_agents.agent_core")


def _tool_call(call_id: str, expression: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name="calculator", arguments=f'{{"expression": "{expression}"}}'),
    )


def test_calculator_evaluates_arithmetic() -> None:
    assert agent_core.calculator("2+2") == "4"
    assert agent_core.calculator("1234 * 5678") == "7006652"


def test_calculator_rejects_code() -> None:
    assert agent_core.calculator("__import__('os').system('echo unsafe')").startswith("Error:")


def test_agent_does_not_call_tool_for_greeting(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = [{"response_content": "Hello! I am a helpful assistant."}]
    monkeypatch.setattr(agent_core, "chat", lambda *args, **kwargs: responses.pop(0))

    agent = agent_core.ToolAgent("Be helpful.")
    assert agent.run("Hello, who are you?").startswith("Hello")
    assert agent.tool_call_count == 0


def test_loop_terminates_at_max_iterations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        agent_core,
        "chat",
        lambda *args, **kwargs: {"response_content": "", "tool_calls": [_tool_call("call-1", "2+2")]},
    )

    agent = agent_core.LoopingToolAgent("Use tools.", max_iterations=2)
    with pytest.raises(RuntimeError, match="2-iteration"):
        agent.run("Keep calculating.")
    assert agent.iterations == 2
    assert agent.tool_call_count == 2


def test_local_ollama_model_is_configured() -> None:
    assert settings.OLLAMA_BASE_URL.startswith("http://localhost")
    assert settings.OLLAMA_MODEL.strip()
