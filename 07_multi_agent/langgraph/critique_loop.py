"""LangGraph: Drafter extracts an expression+answer, verified deterministically
against the real calculator() tool via a conditional edge that loops back to the
drafter on mismatch, or ends once correct / max_rounds is hit.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from common.config import settings

spec = import_module("07_multi_agent.spec")
DraftAnswer = spec.DraftAnswer

calculator = import_module("03_tools.tools.calculator").calculator


def _llm() -> ChatOllama:
    return ChatOllama(base_url=settings.OLLAMA_HOST, model=settings.OLLAMA_MODEL, temperature=float(settings.TEMPERATURE))


class CritiqueState(TypedDict):
    question: str
    max_rounds: int
    round: int
    feedback: str
    draft: DraftAnswer
    correct: bool
    final: str


def _draft_node(state: CritiqueState) -> CritiqueState:
    drafter = _llm().with_structured_output(DraftAnswer)
    prompt = f"{state['feedback']}\n\n{state['question']}" if state["feedback"] else state["question"]
    draft: DraftAnswer = drafter.invoke(
        [
            (
                "system",
                "Identify the arithmetic expression the question is asking for and state "
                "your computed answer to it.",
            ),
            ("user", prompt),
        ]
    )
    return {**state, "draft": draft, "round": state["round"] + 1}


def _verify_node(state: CritiqueState) -> CritiqueState:
    draft = state["draft"]
    correct = calculator(draft.expression)
    is_correct = draft.answer.strip() == str(correct).strip()
    feedback = "" if is_correct else (
        f"Your previous answer '{draft.answer}' for the expression '{draft.expression}' is "
        f"wrong. calculator('{draft.expression}') = {correct}. Try again."
    )
    final = draft.answer if is_correct else state.get("final", "")
    return {**state, "correct": is_correct, "feedback": feedback, "final": final}


def _should_retry(state: CritiqueState) -> str:
    if state["correct"] or state["round"] >= state["max_rounds"]:
        return "end"
    return "retry"


def run_critique_loop(question: str, max_rounds: int = 3) -> str:
    graph = StateGraph(CritiqueState)
    graph.add_node("draft", _draft_node)
    graph.add_node("verify", _verify_node)
    graph.set_entry_point("draft")
    graph.add_edge("draft", "verify")
    graph.add_conditional_edges("verify", _should_retry, {"retry": "draft", "end": END})
    compiled = graph.compile()
    result = compiled.invoke(
        {
            "question": question,
            "max_rounds": max_rounds,
            "round": 0,
            "feedback": "",
            "draft": DraftAnswer(expression="", answer=""),
            "correct": False,
            "final": "",
        }
    )
    return result["final"] or result["draft"].answer


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    print(run_critique_loop(question))


if __name__ == "__main__":
    main()
