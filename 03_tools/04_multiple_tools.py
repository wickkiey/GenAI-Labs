from __future__ import annotations

import sys

try:
    from .tool_agent import MultiToolAgent
except ImportError:
    from tool_agent import MultiToolAgent

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to calculator, get_current_time, "
    "list_files, read_file, search_documents, list_tables, describe_table, and "
    "query_database tools. Use the single best tool for each request, or answer "
    "directly if no tool is needed."
)


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "How many employees are in the Sales department?"
    agent = MultiToolAgent(SYSTEM_PROMPT)
    print(agent.run(prompt))
    print(f"tools called: {agent.tool_calls_made}")


if __name__ == "__main__":
    main()
