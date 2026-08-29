from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.llm import chat


def main() -> None:
    stream = chat(
        [{"role": "user", "content": "Explain streaming responses in two short sentences."}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            print(delta, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
