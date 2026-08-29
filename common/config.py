from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class Settings(BaseModel):
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"
    OLLAMA_MODEL: str = "qwen3:8b"
    EMBED_MODEL: str = "nomic-embed-text"
    TEMPERATURE: float = 0.0


settings = Settings(
    OLLAMA_HOST=os.getenv("OLLAMA_HOST", Settings.model_fields["OLLAMA_HOST"].default),
    OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", Settings.model_fields["OLLAMA_BASE_URL"].default),
    OLLAMA_API_KEY=os.getenv("OLLAMA_API_KEY", Settings.model_fields["OLLAMA_API_KEY"].default),
    OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", Settings.model_fields["OLLAMA_MODEL"].default),
    EMBED_MODEL=os.getenv("EMBED_MODEL", Settings.model_fields["EMBED_MODEL"].default),
    TEMPERATURE=float(os.getenv("TEMPERATURE", str(Settings.model_fields["TEMPERATURE"].default))),
)
