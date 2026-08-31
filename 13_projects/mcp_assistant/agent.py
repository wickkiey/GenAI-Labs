from __future__ import annotations


class MCPAssistant:
    """A simple orchestrator scaffold for routing requests to MCP-backed tools."""

    def __init__(self) -> None:
        self.server_map = {
            "calculator": ["multiply", "add"],
            "filesystem": ["read_file", "list_files"],
            "sqlite": ["query_database"],
        }

    def route(self, request: str) -> str:
        lowered = request.lower()
        if "calculate" in lowered or "multiply" in lowered or "add" in lowered:
            return "calculator"
        if "file" in lowered or "folder" in lowered:
            return "filesystem"
        if "employee" in lowered or "sql" in lowered or "database" in lowered:
            return "sqlite"
        return "calculator"
