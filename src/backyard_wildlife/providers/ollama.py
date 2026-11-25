from __future__ import annotations

import base64
import os
from pathlib import Path

from backyard_wildlife.models import VisionResult
from backyard_wildlife.providers.http import post_json
from backyard_wildlife.providers.parse import extract_json


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str = "llava", host: str | None = None):
        self.model = model
        self.host = (host or os.environ.get("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")

    def analyze(self, image_path: Path, prompt: str) -> VisionResult:
        blob = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [blob],
            "stream": False,
            "format": "json",
        }
        data = post_json(f"{self.host}/api/generate", payload, {})
        text = data.get("response") or ""
        return VisionResult.from_mapping(extract_json(text), provider=self.name, model=self.model)
