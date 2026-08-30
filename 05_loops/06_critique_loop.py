from __future__ import annotations

import sys

try:
    from .critique_loop import run_critique_loop
except ImportError:
    from critique_loop import run_critique_loop


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Should new agent projects default to LangGraph or PydanticAI?"
    trajectory = run_critique_loop(question)
    print(trajectory.final)
    print(f"rounds: {trajectory.iterations}")


if __name__ == "__main__":
    main()
