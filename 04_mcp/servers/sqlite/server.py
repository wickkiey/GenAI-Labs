from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from mcp.server.fastmcp import FastMCP

_db = import_module("03_tools.tools.sqlite_tool")

mcp = FastMCP("sqlite")


@mcp.tool()
def list_tables() -> str:
    """List all table names in the labs database."""
    return _db.list_tables()


@mcp.tool()
def describe_table(table: str) -> str:
    """Describe the columns of a table in the labs database."""
    result = _db.describe_table(table)
    if result.startswith("Error:"):
        raise ValueError(result)
    return result


@mcp.tool()
def query_database(query: str) -> str:
    """Run a single read-only SELECT query against the labs database."""
    result = _db.query_database(query)
    if result.startswith("Error:"):
        raise ValueError(result)
    return result


if __name__ == "__main__":
    mcp.run()
