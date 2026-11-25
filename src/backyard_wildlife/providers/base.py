from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backyard_wildlife.models import VisionResult


class VisionProvider(Protocol):
    name: str
    model: str

    def analyze(self, image_path: Path, prompt: str) -> VisionResult:
        ...


def get_provider(name: str, model: str | None = None) -> VisionProvider:
    key = (name or "gemini").strip().lower()
    if key in {"dry-run", "dry_run", "dryrun", "sample"}:
        from backyard_wildlife.providers.dry_run import DryRunProvider

        return DryRunProvider(model=model or "dry-run")
    if key == "gemini":
        from backyard_wildlife.providers.gemini import GeminiProvider

        return GeminiProvider(model=model or "gemini-3.5-flash-lite")
    if key == "openai":
        from backyard_wildlife.providers.openai import OpenAIProvider

        return OpenAIProvider(model=model or "gpt-4.1-mini")
    if key in {"xai", "grok"}:
        from backyard_wildlife.providers.xai import XAIProvider

        return XAIProvider(model=model or "grok-4-fast")
    if key == "ollama":
        from backyard_wildlife.providers.ollama import OllamaProvider

        return OllamaProvider(model=model or "llava")
    raise ValueError(f"Unknown vision provider: {name}")
