from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from .retry import run_retry
except ImportError:
    from retry import run_retry

calculator = import_module("03_tools.tools.calculator").calculator


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"

    def ask_and_calculate(previous_error: str | None) -> str:
        messages = [
            {
                "role": "system",
                "content": "Reply with only a valid arithmetic expression that answers the question.",
            },
            {"role": "user", "content": question},
        ]
        if previous_error:
            messages.append(
                {
                    "role": "user",
                    "content": f"That failed: {previous_error}. Reply again with only a valid expression.",
                }
            )
        response = chat(messages, model=settings.OLLAMA_MODEL)
        expression = response["response_content"].strip()
        result = calculator(expression)
        if result.startswith("Error:"):
            raise ValueError(result)
        return result

    trajectory = run_retry(ask_and_calculate)
    print(trajectory.final)
    print(f"attempts: {trajectory.iterations}")


if __name__ == "__main__":
    main()
