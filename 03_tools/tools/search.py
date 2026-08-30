from __future__ import annotations

from pathlib import Path

try:
    from .registry import register_tool
except ImportError:
    from registry import register_tool

DOCS_ROOT = (Path(__file__).resolve().parents[2] / "data" / "docs").resolve()
DOCS_ROOT.mkdir(parents=True, exist_ok=True)

SEARCH_DOCUMENTS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "Keyword search over local text documents in data/docs/.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Word or phrase to search for."}
            },
            "required": ["keyword"],
            "additionalProperties": False,
        },
    },
}


@register_tool(SEARCH_DOCUMENTS_SCHEMA)
def search_documents(keyword: str) -> str:
    matches = [
        path.name
        for path in sorted(DOCS_ROOT.glob("*.txt"))
        if keyword.lower() in path.read_text(encoding="utf-8").lower()
    ]
    return ", ".join(matches) if matches else "(no matches)"
