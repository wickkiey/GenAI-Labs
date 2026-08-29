from __future__ import annotations

import sys

try:
    from .agent_core import Agent
except ImportError:
    from agent_core import Agent


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What is an LLM?"
    agent = Agent("You are a concise, helpful assistant.")
    print(agent.run(prompt))


if __name__ == "__main__":
    main()
