"""Two agents debate a question for N rounds; a third Judge agent then picks a
winner. Unlike the Phase 6 critique loop, the debate always runs the full
max_rounds and always terminates via an explicit judge call, not self-agreement.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from ..trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory


def _ask(system: str, user: str) -> str:
    return chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        model=settings.OLLAMA_MODEL,
    )["response_content"].strip()


def run_debate(question: str, max_rounds: int = 3) -> Trajectory:
    """Agent A and Agent B argue opposing positions for max_rounds, then a Judge decides."""
    trajectory = Trajectory()

    position_a = _ask("You are Agent A. State your position on the question in 1-2 sentences.", question)
    position_b = _ask(
        "You are Agent B. State an opposing position on the question in 1-2 sentences.",
        f"Question: {question}\nAgent A said: {position_a}",
    )
    trajectory.steps.append({"round": 0, "agent": "A", "position": position_a})
    trajectory.steps.append({"round": 0, "agent": "B", "position": position_b})

    for round_num in range(1, max_rounds + 1):
        trajectory.iterations = round_num
        position_a = _ask(
            "You are Agent A. Rebut Agent B and restate your position in 1-2 sentences.",
            f"Question: {question}\nAgent B said: {position_b}",
        )
        position_b = _ask(
            "You are Agent B. Rebut Agent A and restate your position in 1-2 sentences.",
            f"Question: {question}\nAgent A said: {position_a}",
        )
        trajectory.steps.append({"round": round_num, "agent": "A", "position": position_a})
        trajectory.steps.append({"round": round_num, "agent": "B", "position": position_b})

    verdict = _ask(
        "You are a Judge. Reply with exactly 'A' or 'B' on the first line naming "
        "whichever position is better supported, then one sentence of reasoning.",
        f"Question: {question}\nPosition A: {position_a}\nPosition B: {position_b}",
    )
    winner = "A" if verdict.strip().upper().startswith("A") else "B"
    trajectory.steps.append({"agent": "judge", "verdict": verdict, "winner": winner})
    trajectory.final = position_a if winner == "A" else position_b
    return trajectory


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Should new agent projects default to LangGraph or PydanticAI?"
    trajectory = run_debate(question)
    print(trajectory.final)
    print(f"rounds: {trajectory.iterations}")


if __name__ == "__main__":
    main()
