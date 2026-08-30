from __future__ import annotations

import sys

try:
    from .tool_agent import MultiToolAgent
    from .tools.registry import register_tool
except ImportError:
    from tool_agent import MultiToolAgent
    from tools.registry import register_tool

FLAKY_LOOKUP_SCHEMA = {
    "type": "function",
    "function": {
        "name": "flaky_lookup",
        "description": "Look up a fact about a topic. Fails on the first attempt, succeeds after.",
        "parameters": {
            "type": "object",
            "properties": {"topic": {"type": "string"}},
            "required": ["topic"],
            "additionalProperties": False,
        },
    },
}

_attempts: dict[str, int] = {}


@register_tool(FLAKY_LOOKUP_SCHEMA)
def flaky_lookup(topic: str) -> str:
    """Raise on the first call per topic so the agent must recover from a tool error."""
    _attempts[topic] = _attempts.get(topic, 0) + 1
    if _attempts[topic] == 1:
        raise RuntimeError("temporary lookup failure, please retry the same call")
    return f"'{topic}' is a well-known GenAI concept."


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "Use flaky_lookup to find out about 'agents'."
    agent = MultiToolAgent(
        "You have a flaky_lookup tool. If it returns an error, call it again with the "
        "same arguments before giving up.",
        tool_names=["flaky_lookup"],
    )
    print(agent.run(prompt))
    print(f"tool calls made: {agent.tool_calls_made}")


if __name__ == "__main__":
    main()
