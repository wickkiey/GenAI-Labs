from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LongTermMemory:
    """Lightweight durable memory backed by a local JSON file."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path("data/long_term_memory.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")
        self._data = json.loads(self.path.read_text(encoding="utf-8"))

    def store(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
