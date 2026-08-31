# Phase 12: RAG

This lab wraps a local corpus with a tiny retrieval pipeline and a simple agentic gate.

What I built: a local document store that ranks relevant files and an agent that skips retrieval for simple arithmetic.
What surprised me: retrieval quality is dominated by chunk selection and query phrasing, not by the LLM itself.
What broke: the first version of the agentic gate was too eager and retrieved even for trivial questions.
