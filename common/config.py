from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"
    OLLAMA_MODEL: str = "qwen3:8b"
    EMBED_MODEL: str = "nomic-embed-text"
    TEMPERATURE: float = 0.0

    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8")


settings = Settings()
