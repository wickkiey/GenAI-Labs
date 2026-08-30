from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from mcp.server.fastmcp import FastMCP

_search = import_module("03_tools.tools.search")

mcp = FastMCP("knowledge")


@mcp.tool()
def search_knowledge(keyword: str) -> str:
    """Keyword search over local text documents in data/docs/."""
    return _search.search_documents(keyword)


@mcp.tool()
def get_document(name: str) -> str:
    """Read the full contents of a document by file name from data/docs/."""
    target = (_search.DOCS_ROOT / name).resolve()
    if target != _search.DOCS_ROOT and _search.DOCS_ROOT not in target.parents:
        raise ValueError("path escapes the knowledge directory")
    if not target.is_file():
        raise ValueError(f"document '{name}' not found")
    return target.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
