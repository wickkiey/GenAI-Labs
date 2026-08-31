from __future__ import annotations


class ArenaResult:
    def __init__(self, agent_a: str, agent_b: str, verdict: str) -> None:
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.verdict = verdict


class AgentArena:
    """A minimal project scaffold for benchmarking two agents on the same task."""

    def __init__(self) -> None:
        self.results: list[ArenaResult] = []

    def run(self, task: str, agent_a: str, agent_b: str) -> ArenaResult:
        verdict = "agent_a" if len(agent_a) <= len(agent_b) else "agent_b"
        result = ArenaResult(agent_a, agent_b, verdict)
        self.results.append(result)
        return result
