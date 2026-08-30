from __future__ import annotations

import sys

try:
    from .reflection import run_reflection
except ImportError:
    from reflection import run_reflection


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What are the three key risks of building agentic systems?"
    trajectory = run_reflection(question)
    print(trajectory.final)
    print(f"rounds: {trajectory.iterations}")


if __name__ == "__main__":
    main()
