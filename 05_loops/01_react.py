from __future__ import annotations

import sys

try:
    from .react import run_react
except ImportError:
    from react import run_react


def main() -> None:
    question = " ".join(sys.argv[1:]) or (
        "Which department has the highest total sales, and what is 10% of it?"
    )
    trajectory = run_react(question)
    print(trajectory.final)
    print(f"iterations: {trajectory.iterations}, tool_calls: {len(trajectory.tool_calls)}")


if __name__ == "__main__":
    main()
