"""Centralized, validated application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def _positive_int(name: str, default: str) -> int:
    value = os.getenv(name, default)
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return parsed


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    llm_model: str
    embed_model: str
    memory_store_path: str
    port: int
    app_version: str
    prompt_version: str
    observability_store_input: bool
    cors_origins: str


def load_settings(require_runtime: bool = True) -> Settings:
    return Settings(
        ollama_base_url=_required("OLLAMA_BASE_URL") if require_providers else os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        llm_model=os.getenv("LLM_MODEL", "llama3.2:3b"),
        embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        memory_store_path=os.getenv("MEMORY_STORE_PATH", "data/memory.json"),
        port=_positive_int("PORT", "8000"),
        app_version=os.getenv("APP_VERSION", "unknown"),
        prompt_version=os.getenv("PROMPT_VERSION", "v1"),
        observability_store_input=os.getenv("OBSERVABILITY_STORE_INPUT", "false").lower() == "true",
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000"),
    )
