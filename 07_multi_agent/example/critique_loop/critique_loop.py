"""Productionised version of Phase 6's critique loop: instead of two agents
self-judging agreement, a drafter extracts the arithmetic implied by the
question and the critic verifies it with the real calculator tool (deterministic,
not another LLM call). Any mismatch is fed back to the drafter for revision.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from ..trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory

calculator = import_module("03_tools.tools.calculator").calculator


class DraftAnswer(BaseModel):
    expression: str
    answer: str


def _draft(question: str, feedback: str | None) -> DraftAnswer:
    messages = [
        {
            "role": "system",
            "content": (
                "Identify the arithmetic expression the question is asking for and "
                "state your computed answer to it."
            ),
        }
    ]
    if feedback:
        messages.append({"role": "user", "content": feedback})
    messages.append({"role": "user", "content": question})
    response = chat(
        messages,
        model=settings.OLLAMA_MODEL,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "draft_answer", "schema": DraftAnswer.model_json_schema()},
        },
    )
    return DraftAnswer.model_validate_json(response["response_content"])


def run_critique_loop(question: str, max_rounds: int = 3) -> Trajectory:
    """Draft -> deterministic tool verification -> revise, until correct or max_rounds."""
    trajectory = Trajectory()
    feedback: str | None = None
    draft = DraftAnswer(expression="", answer="")

    for round_num in range(1, max_rounds + 1):
        trajectory.iterations = round_num
        draft = _draft(question, feedback)
        trajectory.steps.append(
            {"round": round_num, "agent": "drafter", "expression": draft.expression, "answer": draft.answer}
        )

        correct = calculator(draft.expression)
        trajectory.tool_calls.append(
            {"name": "calculator", "arguments": {"expression": draft.expression}, "result": correct}
        )

        if draft.answer.strip() == str(correct).strip():
            trajectory.final = draft.answer
            return trajectory

        feedback = (
            f"Your previous answer '{draft.answer}' for the expression '{draft.expression}' "
            f"is wrong. calculator('{draft.expression}') = {correct}. Try again."
        )
        trajectory.steps.append({"round": round_num, "agent": "critic", "verdict": feedback})

    trajectory.final = draft.answer
    return trajectory


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    trajectory = run_critique_loop(question)
    print(trajectory.final)
    print(f"rounds: {trajectory.iterations}")


if __name__ == "__main__":
    main()
