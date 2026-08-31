"""CrewAI: Agent A <-> Agent B argue via sequential Crews, then a Judge decides."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from crewai import LLM, Agent, Crew, Process, Task

from common.config import settings


def _llm() -> LLM:
    return LLM(model=f"ollama/{settings.OLLAMA_MODEL}", base_url=settings.OLLAMA_HOST, temperature=float(settings.TEMPERATURE))


def _run_single_task(llm: LLM, role: str, goal: str, description: str) -> str:
    agent = Agent(role=role, goal=goal, backstory=f"You argue as {role}.", llm=llm)
    task = Task(description=description, expected_output="1-2 sentences.", agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    return str(crew.kickoff()).strip()


def run_debate(question: str, max_rounds: int = 3) -> str:
    llm = _llm()

    position_a = _run_single_task(
        llm, "Agent A", "State a position", f"State your position on: {question}"
    )
    position_b = _run_single_task(
        llm,
        "Agent B",
        "State an opposing position",
        f"Question: {question}\nAgent A said: {position_a}\nState an opposing position.",
    )

    for _ in range(max_rounds):
        position_a = _run_single_task(
            llm,
            "Agent A",
            "Rebut and restate",
            f"Question: {question}\nAgent B said: {position_b}\nRebut Agent B and restate your position.",
        )
        position_b = _run_single_task(
            llm,
            "Agent B",
            "Rebut and restate",
            f"Question: {question}\nAgent A said: {position_a}\nRebut Agent A and restate your position.",
        )

    verdict = _run_single_task(
        llm,
        "Judge",
        "Pick a winner",
        (
            f"Question: {question}\nPosition A: {position_a}\nPosition B: {position_b}\n"
            "Reply with exactly 'A' or 'B' on the first line naming the better supported "
            "position, then one sentence of reasoning."
        ),
    )
    winner = "A" if verdict.strip().upper().startswith("A") else "B"
    return position_a if winner == "A" else position_b


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Should new agent projects default to LangGraph or PydanticAI?"
    print(run_debate(question))


if __name__ == "__main__":
    main()
