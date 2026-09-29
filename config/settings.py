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
    together_api_key: str
    pinecone_api_key: str
    llm_model: str
    embed_model: str
    pinecone_index: str
    port: int
    app_version: str
    prompt_version: str
    observability_store_input: bool
    cors_origins: str


def load_settings(require_providers: bool = True) -> Settings:
    return Settings(
        together_api_key=_required("TOGETHER_API_KEY") if require_providers else os.getenv("TOGETHER_API_KEY", ""),
        pinecone_api_key=_required("PINECONE_API_KEY") if require_providers else os.getenv("PINECONE_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
        embed_model=os.getenv("EMBED_MODEL", "togethercomputer/m2-bert-80M-8k-retrieval"),
        pinecone_index=os.getenv("PINECONE_INDEX", "conversation-memory"),
        port=_positive_int("PORT", "8000"),
        app_version=os.getenv("APP_VERSION", "unknown"),
        prompt_version=os.getenv("PROMPT_VERSION", "v1"),
        observability_store_input=os.getenv("OBSERVABILITY_STORE_INPUT", "false").lower() == "true",
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000"),
    )
