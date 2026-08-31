"""CrewAI: Drafter extracts an expression+answer as plain text (parsed), verified
deterministically against the real calculator() tool, revise on mismatch.
"""

from __future__ import annotations

import re
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from crewai import LLM, Agent, Crew, Process, Task

from common.config import settings

calculator = import_module("03_tools.tools.calculator").calculator

_EXPRESSION_RE = re.compile(r"expression\s*:\s*(.+)", re.IGNORECASE)
_ANSWER_RE = re.compile(r"answer\s*:\s*(.+)", re.IGNORECASE)


def _llm() -> LLM:
    return LLM(model=f"ollama/{settings.OLLAMA_MODEL}", base_url=settings.OLLAMA_HOST, temperature=float(settings.TEMPERATURE))


def _parse(raw: str) -> tuple[str, str]:
    expr_match = _EXPRESSION_RE.search(raw)
    ans_match = _ANSWER_RE.search(raw)
    expression = expr_match.group(1).strip() if expr_match else ""
    answer = ans_match.group(1).strip() if ans_match else raw.strip()
    return expression, answer


def run_critique_loop(question: str, max_rounds: int = 3) -> str:
    llm = _llm()
    drafter = Agent(
        role="Drafter",
        goal="Identify the arithmetic expression and compute an answer.",
        backstory="A drafter who replies in the exact 'expression: ...' / 'answer: ...' format.",
        llm=llm,
    )

    feedback = ""
    expression, answer = "", ""
    for _ in range(max_rounds):
        description = (
            f"{feedback}\n\n" if feedback else ""
        ) + (
            f"Question: {question}\nReply with exactly two lines:\nexpression: <the arithmetic expression>\n"
            "answer: <your computed answer>"
        )
        task = Task(description=description, expected_output="Two lines: expression and answer.", agent=drafter)
        crew = Crew(agents=[drafter], tasks=[task], process=Process.sequential)
        expression, answer = _parse(str(crew.kickoff()))

        correct = calculator(expression)
        if answer.strip() == str(correct).strip():
            return answer

        feedback = (
            f"Your previous answer '{answer}' for the expression '{expression}' is wrong. "
            f"calculator('{expression}') = {correct}. Try again."
        )

    return answer


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    print(run_critique_loop(question))


if __name__ == "__main__":
    main()
