from __future__ import annotations

import sys

try:
    from .agent_core import LoopingToolAgent
except ImportError:
    from agent_core import LoopingToolAgent

__all__ = ["LoopingToolAgent"]


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What is 1234 * 5678, then subtract 1000?"
    agent = LoopingToolAgent(
        "You are a helpful assistant. Use the calculator tool for every arithmetic operation."
    )
    print(agent.run(prompt))


if __name__ == "__main__":
    main()
