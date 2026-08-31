from __future__ import annotations

from collections import deque


class ShortTermMemory:
    """Keep a bounded rolling conversation history."""

    def __init__(self, max_messages: int = 20) -> None:
        self.max_messages = max_messages
        self.messages: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = list(deque(self.messages, maxlen=self.max_messages))

    def as_prompt(self) -> list[dict[str, str]]:
        return list(self.messages)
