from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from .trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory


def run_reflection(question: str, max_rounds: int = 3) -> Trajectory:
    """Answer -> Critic -> Improve loop that stops when the critic says OK or max_rounds."""
    trajectory = Trajectory()
    answer = chat(
        [
            {"role": "system", "content": "Answer the question as best you can."},
            {"role": "user", "content": question},
        ],
        model=settings.OLLAMA_MODEL,
    )["response_content"].strip()
    trajectory.steps.append({"round": 0, "answer": answer})

    for round_num in range(1, max_rounds + 1):
        trajectory.iterations = round_num
        critique = chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a strict critic. If the answer is fully correct and "
                        "complete, reply with exactly OK. Otherwise, explain what's wrong."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\nAnswer: {answer}"},
            ],
            model=settings.OLLAMA_MODEL,
        )["response_content"].strip()
        trajectory.steps.append({"round": round_num, "critique": critique})

        if critique.upper().startswith("OK"):
            trajectory.final = answer
            return trajectory

        answer = chat(
            [
                {"role": "system", "content": "Revise the answer to address the critique."},
                {
                    "role": "user",
                    "content": f"Question: {question}\nPrevious answer: {answer}\nCritique: {critique}",
                },
            ],
            model=settings.OLLAMA_MODEL,
        )["response_content"].strip()
        trajectory.steps.append({"round": round_num, "revised_answer": answer})

    trajectory.final = answer
    return trajectory
