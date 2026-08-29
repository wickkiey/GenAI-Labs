from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.llm import chat

QUESTION = "What is prompt engineering?"
PROMPTS = [
    "You are a teacher. Explain simply.",
    "You are a pirate. Answer briefly.",
    "You are a strict technical writer. Be precise.",
]


def main() -> None:
    for prompt in PROMPTS:
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": QUESTION}]
        resp = chat(messages, max_tokens=2_000, extra_body={"think": False})
        print(f"\nSystem: {prompt}\n{resp['response_content'].strip()}")


if __name__ == "__main__":
    main()
