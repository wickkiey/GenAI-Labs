from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from mcp.server.fastmcp import FastMCP

_fs = import_module("03_tools.tools.filesystem")

mcp = FastMCP("filesystem")


@mcp.tool()
def list_files() -> str:
    """List file names available in the sandbox directory."""
    return _fs.list_files()


@mcp.tool()
def read_file(path: str) -> str:
    """Read a text file's contents from the sandbox directory."""
    result = _fs.read_file(path)
    if result.startswith("Error:"):
        raise ValueError(result)
    return result


@mcp.tool()
def search_files(keyword: str) -> str:
    """Search sandbox file names and contents for a keyword."""
    matches = [
        path.name
        for path in sorted(_fs.SANDBOX_ROOT.glob("*.txt"))
        if keyword.lower() in path.name.lower()
        or keyword.lower() in path.read_text(encoding="utf-8").lower()
    ]
    return ", ".join(matches) if matches else "(no matches)"


if __name__ == "__main__":
    mcp.run()
