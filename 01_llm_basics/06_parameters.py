from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.llm import chat

PROMPT = "Write a one-line tagline for a bookstore."


def ask(temp: float, max_tokens: int, seed: int) -> str:
    resp = chat(
        [{"role": "user", "content": PROMPT}],
        temperature=temp,
        max_tokens=max_tokens,
        seed=seed,
    )
    return resp["response_content"].strip()


def main() -> None:
    print("temperature=0:", ask(0, 24, 7))
    print("temperature=1:", ask(1, 24, 7))


if __name__ == "__main__":
    main()
