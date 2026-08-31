from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StateMemory:
    """Simple JSON-backed state store for short-lived agent memory."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path("data/state_memory.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")
        self._data = json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
