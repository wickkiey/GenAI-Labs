"""PydanticAI: Agent A <-> Agent B argue, then a Judge agent decides."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from common.config import settings


def _model() -> OpenAIChatModel:
    return OpenAIChatModel(
        settings.OLLAMA_MODEL,
        provider=OpenAIProvider(base_url=settings.OLLAMA_BASE_URL, api_key=settings.OLLAMA_API_KEY),
    )


def _ask(system_prompt: str, user_prompt: str) -> str:
    return Agent(model=_model(), system_prompt=system_prompt).run_sync(user_prompt).output.strip()


def run_debate(question: str, max_rounds: int = 3) -> str:
    position_a = _ask("You are Agent A. State your position on the question in 1-2 sentences.", question)
    position_b = _ask(
        "You are Agent B. State an opposing position on the question in 1-2 sentences.",
        f"Question: {question}\nAgent A said: {position_a}",
    )

    for _ in range(max_rounds):
        position_a = _ask(
            "You are Agent A. Rebut Agent B and restate your position in 1-2 sentences.",
            f"Question: {question}\nAgent B said: {position_b}",
        )
        position_b = _ask(
            "You are Agent B. Rebut Agent A and restate your position in 1-2 sentences.",
            f"Question: {question}\nAgent A said: {position_a}",
        )

    verdict = _ask(
        "You are a Judge. Reply with exactly 'A' or 'B' on the first line naming whichever "
        "position is better supported, then one sentence of reasoning.",
        f"Question: {question}\nPosition A: {position_a}\nPosition B: {position_b}",
    )
    winner = "A" if verdict.strip().upper().startswith("A") else "B"
    return position_a if winner == "A" else position_b


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Should new agent projects default to LangGraph or PydanticAI?"
    print(run_debate(question))


if __name__ == "__main__":
    main()
