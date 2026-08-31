# Phase 12: Memory

This lab demonstrates the difference between short-term, state, long-term, and semantic memory.

What I built: a lightweight in-memory storage layer for conversations, task state, durable facts, and document recall.
What surprised me: the simplest JSON-backed memory is often enough for lab prototypes before a database is introduced.
What broke: naive retrieval and persistence code can silently lose state if it is not written atomically.
