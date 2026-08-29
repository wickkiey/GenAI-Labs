from __future__ import annotations

import sys

try:
    from .agent_core import ToolAgent, calculator
except ImportError:
    from agent_core import ToolAgent, calculator

__all__ = ["ToolAgent", "calculator"]


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    agent = ToolAgent(
        "You are a helpful assistant. Use the calculator tool for arithmetic; do not calculate mentally."
    )
    print(agent.run(prompt))


if __name__ == "__main__":
    main()
