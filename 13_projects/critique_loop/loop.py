from __future__ import annotations


class CritiqueLoop:
    """A minimal bounded critique loop: answer, critique, revise."""

    def __init__(self, max_rounds: int = 3) -> None:
        self.max_rounds = max_rounds

    def run(self, question: str) -> str:
        answer = f"Initial answer for: {question}"
        for _ in range(self.max_rounds):
            critique = "needs a clearer final sentence" if "answer" in answer.lower() else "ok"
            if critique == "ok":
                return answer
            answer = f"Revised answer for: {question}"
        return answer
