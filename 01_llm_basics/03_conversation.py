from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.llm import chat


def main() -> None:
    messages = [{"role": "system", "content": "You are concise and helpful."}]
    print("Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        messages.append({"role": "user", "content": user_input})
        resp = chat(messages, max_tokens=2000)
        reply = resp["response_content"].strip()
        messages.append({"role": "assistant", "content": reply})
        print(f"Assistant: {reply}")


if __name__ == "__main__":
    main()
