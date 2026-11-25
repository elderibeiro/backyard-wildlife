from __future__ import annotations

import base64
from pathlib import Path

from backyard_wildlife.config import api_key
from backyard_wildlife.models import VisionResult
from backyard_wildlife.providers.http import post_json
from backyard_wildlife.providers.parse import extract_json


class XAIProvider:
    name = "xai"

    def __init__(self, model: str = "grok-4-fast"):
        self.model = model

    def analyze(self, image_path: Path, prompt: str) -> VisionResult:
        key = api_key("xai")
        if not key:
            raise RuntimeError("XAI_API_KEY is not set")
        blob = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{blob}"},
                        },
                    ],
                }
            ],
        }
        data = post_json(
            "https://api.x.ai/v1/chat/completions",
            payload,
            {"Authorization": f"Bearer {key}"},
        )
        text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content")) or ""
        return VisionResult.from_mapping(extract_json(text), provider=self.name, model=self.model)
