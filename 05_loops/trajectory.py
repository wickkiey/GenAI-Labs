from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Trajectory:
    """The common return type every loop in this phase produces."""

    steps: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    final: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
