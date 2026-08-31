from __future__ import annotations


class LocalResearchAgent:
    """A minimal scaffold for a research agent that answers from local sources."""

    def __init__(self, sources: list[str] | None = None) -> None:
        self.sources = sources or []

    def answer(self, question: str) -> str:
        source_text = ", ".join(self.sources) if self.sources else "local corpus"
        return f"Answering '{question}' using {source_text}."
