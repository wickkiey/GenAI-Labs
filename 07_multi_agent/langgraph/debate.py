"""LangGraph: Agent A <-> Agent B argue for max_rounds via conditional edges,
then a Judge node picks a winner.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from common.config import settings


def _llm() -> ChatOllama:
    return ChatOllama(base_url=settings.OLLAMA_HOST, model=settings.OLLAMA_MODEL, temperature=float(settings.TEMPERATURE))


def _ask(system_prompt: str, user_prompt: str) -> str:
    return _llm().invoke([("system", system_prompt), ("user", user_prompt)]).content.strip()


class DebateState(TypedDict):
    question: str
    max_rounds: int
    round: int
    position_a: str
    position_b: str
    final: str


def _opening_node(state: DebateState) -> DebateState:
    position_a = _ask("You are Agent A. State your position on the question in 1-2 sentences.", state["question"])
    position_b = _ask(
        "You are Agent B. State an opposing position on the question in 1-2 sentences.",
        f"Question: {state['question']}\nAgent A said: {position_a}",
    )
    return {**state, "position_a": position_a, "position_b": position_b, "round": 0}


def _round_node(state: DebateState) -> DebateState:
    position_a = _ask(
        "You are Agent A. Rebut Agent B and restate your position in 1-2 sentences.",
        f"Question: {state['question']}\nAgent B said: {state['position_b']}",
    )
    position_b = _ask(
        "You are Agent B. Rebut Agent A and restate your position in 1-2 sentences.",
        f"Question: {state['question']}\nAgent A said: {position_a}",
    )
    return {**state, "position_a": position_a, "position_b": position_b, "round": state["round"] + 1}


def _judge_node(state: DebateState) -> DebateState:
    verdict = _ask(
        "You are a Judge. Reply with exactly 'A' or 'B' on the first line naming whichever "
        "position is better supported, then one sentence of reasoning.",
        f"Question: {state['question']}\nPosition A: {state['position_a']}\nPosition B: {state['position_b']}",
    )
    winner = "A" if verdict.upper().startswith("A") else "B"
    return {**state, "final": state["position_a"] if winner == "A" else state["position_b"]}


def _should_continue(state: DebateState) -> str:
    return "round" if state["round"] < state["max_rounds"] else "judge"


def run_debate(question: str, max_rounds: int = 3) -> str:
    graph = StateGraph(DebateState)
    graph.add_node("opening", _opening_node)
    graph.add_node("round", _round_node)
    graph.add_node("judge", _judge_node)
    graph.set_entry_point("opening")
    graph.add_conditional_edges("opening", _should_continue, {"round": "round", "judge": "judge"})
    graph.add_conditional_edges("round", _should_continue, {"round": "round", "judge": "judge"})
    graph.add_edge("judge", END)
    compiled = graph.compile()
    result = compiled.invoke(
        {"question": question, "max_rounds": max_rounds, "round": 0, "position_a": "", "position_b": "", "final": ""}
    )
    return result["final"]


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Should new agent projects default to LangGraph or PydanticAI?"
    print(run_debate(question))


if __name__ == "__main__":
    main()
