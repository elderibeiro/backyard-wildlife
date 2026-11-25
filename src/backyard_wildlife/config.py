"""Load YAML config and environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def deep_get(data: dict[str, Any], dotted: str, default: Any = None) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load config.example.yaml defaults, then an optional config file, then env."""
    root = Path(__file__).resolve().parents[2]
    _load_dotenv(Path.cwd() / ".env")
    _load_dotenv(root / ".env")

    config: dict[str, Any] = {}
    example = root / "config.example.yaml"
    if example.is_file():
        config = yaml.safe_load(example.read_text(encoding="utf-8")) or {}

    chosen = path or os.environ.get("BACKYARD_WILDLIFE_CONFIG")
    if chosen:
        cfg_path = Path(chosen)
        if not cfg_path.is_file():
            raise FileNotFoundError(f"Config file not found: {cfg_path}")
        overlay = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        config = _merge(config, overlay)

    return config


def _merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def api_key(provider: str) -> str:
    mapping = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "xai": "XAI_API_KEY",
        "grok": "XAI_API_KEY",
    }
    env = mapping.get(provider, "")
    return (os.environ.get(env) or "").strip() if env else ""
