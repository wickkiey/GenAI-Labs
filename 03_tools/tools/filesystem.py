from __future__ import annotations

from pathlib import Path

try:
    from .registry import register_tool
except ImportError:
    from registry import register_tool

SANDBOX_ROOT = (Path(__file__).resolve().parents[2] / "data" / "sandbox").resolve()
SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)

LIST_FILES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List file names available in the sandbox directory.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

READ_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a text file's contents from the sandbox directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File name inside the sandbox, e.g. 'notes.txt'."}
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
}


def _resolve_in_sandbox(name: str) -> Path:
    candidate = (SANDBOX_ROOT / name).resolve()
    if candidate != SANDBOX_ROOT and SANDBOX_ROOT not in candidate.parents:
        raise ValueError("path escapes the sandbox")
    return candidate


@register_tool(LIST_FILES_SCHEMA)
def list_files() -> str:
    names = sorted(p.name for p in SANDBOX_ROOT.iterdir() if p.is_file())
    return ", ".join(names) if names else "(no files)"


@register_tool(READ_FILE_SCHEMA)
def read_file(path: str) -> str:
    try:
        target = _resolve_in_sandbox(path)
    except ValueError as error:
        return f"Error: {error}"
    if not target.is_file():
        return f"Error: '{path}' not found in sandbox"
    return target.read_text(encoding="utf-8")
