from __future__ import annotations

import sys

try:
    from .verification import run_verification
except ImportError:
    from verification import run_verification


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 17 * 23?"
    trajectory = run_verification(question)
    print(trajectory.final)
    print(f"rounds: {trajectory.iterations}")


if __name__ == "__main__":
    main()
