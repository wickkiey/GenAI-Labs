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


def run_verification(question: str, max_rounds: int = 3) -> Trajectory:
    """Solution -> Verifier -> PASS/FAIL -> retry loop, stops on PASS or max_rounds."""
    trajectory = Trajectory()
    feedback: str | None = None
    solution = ""

    for round_num in range(1, max_rounds + 1):
        trajectory.iterations = round_num
        messages = [
            {"role": "system", "content": "Solve the problem."},
            {"role": "user", "content": question},
        ]
        if feedback:
            messages.append(
                {"role": "user", "content": f"Your previous solution was rejected: {feedback}. Try again."}
            )
        solution = chat(messages, model=settings.OLLAMA_MODEL)["response_content"].strip()
        trajectory.steps.append({"round": round_num, "solution": solution})

        verdict = chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a strict verifier. Reply with exactly PASS if the "
                        "solution is correct and complete, otherwise reply FAIL: <reason>."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\nSolution: {solution}"},
            ],
            model=settings.OLLAMA_MODEL,
        )["response_content"].strip()
        trajectory.steps.append({"round": round_num, "verdict": verdict})

        if verdict.upper().startswith("PASS"):
            trajectory.final = solution
            return trajectory
        feedback = verdict

    trajectory.final = solution
    return trajectory
