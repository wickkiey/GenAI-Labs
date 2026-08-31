"""Phase 9: 02 -- an orchestrator fans out N subagents concurrently and merges results in order."""
from __future__ import annotations

import asyncio
import sys

try:
    from .subagent_core import SubagentResult, spawn_subagent
except ImportError:
    from subagent_core import SubagentResult, spawn_subagent

DEFAULT_TASKS = [
    "What is 12 * 8?",
    "What is the capital of France?",
    "Name one prime number greater than 100.",
]


async def run_parallel(tasks: list[str]) -> list[SubagentResult]:
    """Spawn one subagent per task, run them concurrently, return results in request order."""
    coros = [
        asyncio.to_thread(
            spawn_subagent,
            name=f"worker-{i}",
            system_prompt="Answer the question in one short sentence.",
            task=task,
        )
        for i, task in enumerate(tasks)
    ]
    return list(await asyncio.gather(*coros))


def main() -> None:
    tasks = sys.argv[1:] or DEFAULT_TASKS
    results = asyncio.run(run_parallel(tasks))
    for result in results:
        print(f"[{result.name}] {result.task} -> {result.output}")


if __name__ == "__main__":
    main()
