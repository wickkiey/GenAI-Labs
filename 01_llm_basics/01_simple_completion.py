from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.llm import chat


def main() -> None:
    resp = chat([{"role": "user", "content": "In one sentence, what is an LLM?"}])
    print(resp["response_content"].strip())


if __name__ == "__main__":
    main()
