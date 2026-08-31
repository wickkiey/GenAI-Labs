"""AutoGen: Drafter extracts an expression+answer, verified deterministically
against the real calculator() tool (not another LLM call), revise on mismatch.
"""

from __future__ import annotations

import asyncio
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent

try:
    from ._client import make_client
except ImportError:
    from _client import make_client

spec = import_module("07_multi_agent.spec")
DraftAnswer = spec.DraftAnswer

calculator = import_module("03_tools.tools.calculator").calculator


async def _run(question: str, max_rounds: int) -> str:
    client = make_client()
    drafter = AssistantAgent(
        "drafter",
        model_client=client,
        output_content_type=DraftAnswer,
        system_message=(
            "Identify the arithmetic expression the question is asking for and state your "
            "computed answer to it."
        ),
    )

    feedback: str | None = None
    draft = DraftAnswer(expression="", answer="")
    for _ in range(max_rounds):
        prompt = f"{feedback}\n\n{question}" if feedback else question
        result = await drafter.run(task=prompt)
        draft = result.messages[-1].content

        correct = calculator(draft.expression)
        if draft.answer.strip() == str(correct).strip():
            return draft.answer

        feedback = (
            f"Your previous answer '{draft.answer}' for the expression '{draft.expression}' "
            f"is wrong. calculator('{draft.expression}') = {correct}. Try again."
        )

    return draft.answer


def run_critique_loop(question: str, max_rounds: int = 3) -> str:
    return asyncio.run(_run(question, max_rounds))


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    print(run_critique_loop(question))


if __name__ == "__main__":
    main()
