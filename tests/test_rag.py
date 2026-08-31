from __future__ import annotations

import importlib
from pathlib import Path

rag_module = importlib.import_module("12_rag.rag")
SimpleRAG = rag_module.SimpleRAG
AgenticRAG = rag_module.AgenticRAG


def test_basic_rag_returns_source() -> None:
    rag = SimpleRAG(corpus_dir=Path("data/docs"))
    answer = rag.answer("What is a vector database?")
    assert "source" in answer
    assert answer["source"]


def test_agentic_rag_skips_retrieval_for_simple_math() -> None:
    rag = AgenticRAG(corpus_dir=Path("data/docs"))
    result = rag.answer("What is 2+2?")
    assert result["retrieval_calls"] == 0
