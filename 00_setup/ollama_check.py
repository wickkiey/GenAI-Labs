from __future__ import annotations

import subprocess

import httpx

from common.config import settings
from common.llm import chat


def _print_cmd(cmd: list[str]) -> None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        text = out.stdout.strip() or out.stderr.strip() or "(no output)"
        print(f"$ {' '.join(cmd)}\n{text}\n")
    except FileNotFoundError:
        print(f"$ {' '.join(cmd)}\ncommand not found\n")


def main() -> None:
    _print_cmd(["ollama", "--version"])
    _print_cmd(["ollama", "list"])

    tags = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=15)
    tags.raise_for_status()
    models = [m.get("name", "") for m in tags.json().get("models", [])]
    print("Available models:", ", ".join(models) or "none")

    res = chat([{"role": "user", "content": "Reply with one short greeting."}], max_tokens=12)
    print("Sample completion:", (res.choices[0].message.content or "").strip())


if __name__ == "__main__":
    main()
