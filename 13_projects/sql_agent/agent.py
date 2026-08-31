from __future__ import annotations


class SQLAgent:
    """A minimal scaffold for NL-to-SQL with execution safeguards."""

    def __init__(self) -> None:
        self.allowed = {"SELECT"}

    def validate(self, query: str) -> bool:
        stripped = query.strip().upper()
        return stripped.startswith("SELECT") and "DROP" not in stripped and "DELETE" not in stripped

    def answer(self, question: str) -> str:
        if "employees" in question.lower():
            return "SELECT COUNT(*) FROM employees;"
        return "SELECT 1;"
