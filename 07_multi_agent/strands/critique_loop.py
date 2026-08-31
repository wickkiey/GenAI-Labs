"""Strands: Drafter extracts an expression+answer via structured output,
verified deterministically against the real calculator() tool, revise on mismatch.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from strands import Agent
from strands.models.ollama import OllamaModel

from common.config import settings

spec = import_module("07_multi_agent.spec")
DraftAnswer = spec.DraftAnswer

calculator = import_module("03_tools.tools.calculator").calculator


def _model() -> OllamaModel:
    return OllamaModel(host=settings.OLLAMA_HOST, model_id=settings.OLLAMA_MODEL)


def run_critique_loop(question: str, max_rounds: int = 3) -> str:
    drafter = Agent(
        model=_model(),
        system_prompt=(
            "Identify the arithmetic expression the question is asking for and state your "
            "computed answer to it."
        ),
    )

    feedback: str | None = None
    draft = DraftAnswer(expression="", answer="")
    for _ in range(max_rounds):
        prompt = f"{feedback}\n\n{question}" if feedback else question
        draft = drafter.structured_output(DraftAnswer, prompt)

        correct = calculator(draft.expression)
        if draft.answer.strip() == str(correct).strip():
            return draft.answer

        feedback = (
            f"Your previous answer '{draft.answer}' for the expression '{draft.expression}' "
            f"is wrong. calculator('{draft.expression}') = {correct}. Try again."
        )

    return draft.answer


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    print(run_critique_loop(question))


if __name__ == "__main__":
    main()
