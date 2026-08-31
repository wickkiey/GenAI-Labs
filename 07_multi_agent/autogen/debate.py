"""AutoGen: Agent A <-> Agent B argue, then a Judge agent decides."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent

try:
    from ._client import make_client
except ImportError:
    from _client import make_client


async def _ask(client, system_message: str, user_message: str) -> str:
    agent = AssistantAgent("agent", model_client=client, system_message=system_message)
    result = await agent.run(task=user_message)
    return result.messages[-1].content.strip()


async def _run(question: str, max_rounds: int) -> str:
    client = make_client()

    position_a = await _ask(client, "You are Agent A. State your position on the question in 1-2 sentences.", question)
    position_b = await _ask(
        client,
        "You are Agent B. State an opposing position on the question in 1-2 sentences.",
        f"Question: {question}\nAgent A said: {position_a}",
    )

    for _ in range(max_rounds):
        position_a = await _ask(
            client,
            "You are Agent A. Rebut Agent B and restate your position in 1-2 sentences.",
            f"Question: {question}\nAgent B said: {position_b}",
        )
        position_b = await _ask(
            client,
            "You are Agent B. Rebut Agent A and restate your position in 1-2 sentences.",
            f"Question: {question}\nAgent A said: {position_a}",
        )

    verdict = await _ask(
        client,
        "You are a Judge. Reply with exactly 'A' or 'B' on the first line naming whichever "
        "position is better supported, then one sentence of reasoning.",
        f"Question: {question}\nPosition A: {position_a}\nPosition B: {position_b}",
    )
    winner = "A" if verdict.upper().startswith("A") else "B"
    return position_a if winner == "A" else position_b


def run_debate(question: str, max_rounds: int = 3) -> str:
    return asyncio.run(_run(question, max_rounds))


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Should new agent projects default to LangGraph or PydanticAI?"
    print(run_debate(question))


if __name__ == "__main__":
    main()
