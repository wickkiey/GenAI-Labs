from __future__ import annotations

import importlib
from pathlib import Path

short_term = importlib.import_module("11_memory.short_term")
state = importlib.import_module("11_memory.state")
long_term = importlib.import_module("11_memory.long_term")
semantic = importlib.import_module("11_memory.semantic")

ShortTermMemory = short_term.ShortTermMemory
StateMemory = state.StateMemory
LongTermMemory = long_term.LongTermMemory
SemanticMemory = semantic.SemanticMemory


def test_short_term_memory_windowing() -> None:
    memory = ShortTermMemory(max_messages=2)
    memory.add("user", "one")
    memory.add("assistant", "two")
    memory.add("user", "three")
    assert memory.messages[-1]["content"] == "three"
    assert len(memory.messages) == 2


def test_state_memory_persists_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    a = StateMemory(path)
    a.set("last_task", "write report")
    b = StateMemory(path)
    assert b.get("last_task") == "write report"


def test_long_term_memory_roundtrip() -> None:
    memory = LongTermMemory()
    memory.store("user_profile", {"name": "Ada", "role": "researcher"})
    assert memory.get("user_profile")["name"] == "Ada"


def test_semantic_memory_top_result() -> None:
    memory = SemanticMemory()
    memory.add_document("doc-1", "vector databases are useful for retrieval")
    memory.add_document("doc-2", "python is a programming language")
    results = memory.search("vector database retrieval")
    assert results[0]["id"] == "doc-1"
