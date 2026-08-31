from __future__ import annotations

import re
from collections import Counter


class SemanticMemory:
    """A tiny in-memory semantic retriever for local lab exercises."""

    def __init__(self) -> None:
        self.documents: dict[str, str] = {}

    def add_document(self, doc_id: str, content: str) -> None:
        self.documents[doc_id] = content

    def search(self, query: str, limit: int = 3) -> list[dict[str, float | str]]:
        tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored: list[tuple[str, int]] = []
        for doc_id, content in self.documents.items():
            content_tokens = re.findall(r"[a-z0-9]+", content.lower())
            overlap = sum(1 for token in tokens if token in content_tokens)
            if overlap:
                scored.append((doc_id, overlap))
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:limit]
        return [{"id": doc_id, "score": score} for doc_id, score in ranked]
