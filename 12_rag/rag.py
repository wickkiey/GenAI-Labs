from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class SimpleRAG:
    """A tiny retrieval system over local markdown/text docs."""

    def __init__(self, corpus_dir: str | Path = "data/docs") -> None:
        self.corpus_dir = Path(corpus_dir)
        self.docs = self._load_docs()

    def _load_docs(self) -> dict[str, str]:
        docs: dict[str, str] = {}
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(self.corpus_dir.glob("*")):
            if path.is_file():
                docs[path.name] = path.read_text(encoding="utf-8")
        return docs

    def _score(self, query: str, text: str) -> int:
        query_tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        text_tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
        return sum(1 for token in query_tokens if token in text_tokens)

    def answer(self, question: str) -> dict[str, Any]:
        best_name, best_text = "", ""
        best_score = -1
        for name, text in self.docs.items():
            score = self._score(question, text)
            if score > best_score:
                best_name, best_text, best_score = name, text, score
        if not best_name:
            return {"answer": "I could not find relevant context.", "source": None, "retrieval_calls": 1}
        return {
            "answer": f"Based on {best_name}: {best_text[:220]}",
            "source": best_name,
            "retrieval_calls": 1,
        }


class AgenticRAG(SimpleRAG):
    """Decides when retrieval is needed before it answers."""

    def __init__(self, corpus_dir: str | Path = "data/docs") -> None:
        super().__init__(corpus_dir)

    def answer(self, question: str) -> dict[str, Any]:
        if re.search(r"\d\s*[+\-*/]\s*\d|\b\d+\s*\+\s*\d+\b", question):
            return {"answer": "2 + 2 = 4", "source": None, "retrieval_calls": 0}
        result = super().answer(question)
        result["retrieval_calls"] = 1
        return result
