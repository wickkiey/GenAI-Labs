"""Phase 9: 03 -- role-specific subagents, routed to by task type."""
from __future__ import annotations

import sys
from importlib import import_module

try:
    from .subagent_core import SubagentResult, spawn_subagent
except ImportError:
    from subagent_core import SubagentResult, spawn_subagent

_tools = import_module("03_tools.tools")
TOOL_REGISTRY = _tools.TOOL_REGISTRY

ROLES = {
    "researcher": {
        "system_prompt": (
            "You are a researcher. Use the sqlite/search tools to find facts, "
            "then answer with the facts you found, citing numbers."
        ),
        "tool_names": ["list_tables", "describe_table", "query_database", "search_documents"],
    },
    "coder": {
        "system_prompt": (
            "You are a coder. Use the filesystem tools to inspect files, "
            "then answer based on what you read."
        ),
        "tool_names": ["list_files", "read_file"],
    },
    "reviewer": {
        "system_prompt": "You are a reviewer. Answer directly and concisely, no tools needed.",
        "tool_names": [],
    },
}

_RESEARCH_KEYWORDS = ("how many", "database", "employees", "sales", "department", "document", "search")
_CODE_KEYWORDS = ("file", "notes.txt", "read", "sandbox")


def classify(task: str) -> str:
    """A tiny keyword router -- picks which specialized subagent should handle a task."""
    lowered = task.lower()
    if any(keyword in lowered for keyword in _CODE_KEYWORDS):
        return "coder"
    if any(keyword in lowered for keyword in _RESEARCH_KEYWORDS):
        return "researcher"
    return "reviewer"


def dispatch(task: str) -> SubagentResult:
    role = classify(task)
    spec = ROLES[role]
    tools = {name: TOOL_REGISTRY[name] for name in spec["tool_names"] if name in TOOL_REGISTRY}
    return spawn_subagent(name=role, system_prompt=spec["system_prompt"], task=task, tools=tools)


def main() -> None:
    task = " ".join(sys.argv[1:]) or "How many employees are in the Sales department?"
    result = dispatch(task)
    print(f"[{result.name}] {result.output}")


if __name__ == "__main__":
    main()
