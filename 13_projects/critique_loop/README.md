# Critique Loop

This project is the final capstone pattern: one agent answers, another critiques, and the first revises.

What I built: a bounded critique loop with explicit revision and agreement checks.
What surprised me: a single critique pass often fixes obvious errors without heavy prompt engineering.
What broke: loops that do not cap turns can drift, repeat, or oscillate forever.
