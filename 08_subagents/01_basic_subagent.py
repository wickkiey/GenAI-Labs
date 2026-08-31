"""Phase 9: 01 -- a parent spawns one isolated subagent to solve a subtask."""
from __future__ import annotations

import sys

try:
    from .subagent_core import spawn_subagent
except ImportError:
    from subagent_core import spawn_subagent


def main() -> None:
    task = " ".join(sys.argv[1:]) or "Summarize why the sky is blue in one sentence."
    result = spawn_subagent(
        name="helper",
        system_prompt="You are a focused helper. Answer concisely, in one or two sentences.",
        task=task,
    )
    print(f"[{result.name}] {result.output}")


if __name__ == "__main__":
    main()
