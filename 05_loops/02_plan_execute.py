from __future__ import annotations

import sys

try:
    from .plan_execute import run_plan_execute
except ImportError:
    from plan_execute import run_plan_execute


def main() -> None:
    question = " ".join(sys.argv[1:]) or (
        "Which department has the highest total sales, and what is 10% of it?"
    )
    trajectory = run_plan_execute(question)
    print(trajectory.final)
    print(f"tasks: {trajectory.iterations}")


if __name__ == "__main__":
    main()
