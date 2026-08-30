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


def run_critique_loop(question: str, max_rounds: int = 4) -> Trajectory:
    """Agent A and Agent B argue until one agrees with the other, or max_rounds."""
    trajectory = Trajectory()
    position_a = chat(
        [
            {"role": "system", "content": "You are Agent A. State your position in one or two sentences."},
            {"role": "user", "content": question},
        ],
        model=settings.OLLAMA_MODEL,
    )["response_content"].strip()
    trajectory.steps.append({"round": 0, "agent": "A", "position": position_a})

    for round_num in range(1, max_rounds + 1):
        trajectory.iterations = round_num
        position_b = chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are Agent B. Reply with exactly AGREE if you agree with "
                        "Agent A's position, otherwise state your counter-position briefly."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\nAgent A says: {position_a}"},
            ],
            model=settings.OLLAMA_MODEL,
        )["response_content"].strip()
        trajectory.steps.append({"round": round_num, "agent": "B", "position": position_b})

        if position_b.upper().startswith("AGREE"):
            trajectory.final = position_a
            return trajectory

        position_a = chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are Agent A. Reply with exactly AGREE if you now agree with "
                        "Agent B, otherwise restate your position considering B's point."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\nAgent B says: {position_b}"},
            ],
            model=settings.OLLAMA_MODEL,
        )["response_content"].strip()
        trajectory.steps.append({"round": round_num, "agent": "A", "position": position_a})

        if position_a.upper().startswith("AGREE"):
            trajectory.final = position_b
            return trajectory

    trajectory.final = position_a
    return trajectory
