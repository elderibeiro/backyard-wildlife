from __future__ import annotations

import base64
from pathlib import Path

from backyard_wildlife.config import api_key
from backyard_wildlife.models import VisionResult
from backyard_wildlife.prompts import JSON_SCHEMA
from backyard_wildlife.providers.http import post_json
from backyard_wildlife.providers.parse import extract_json


class GeminiProvider:
    name = "gemini"

    def __init__(self, model: str = "gemini-3.5-flash-lite"):
        self.model = model

    def analyze(self, image_path: Path, prompt: str) -> VisionResult:
        key = api_key("gemini")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        blob = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={key}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": blob}},
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 512,
                "responseMimeType": "application/json",
                "responseSchema": JSON_SCHEMA,
            },
        }
        data = post_json(url, payload, {})
        text = ""
        for candidate in data.get("candidates") or []:
            parts = ((candidate.get("content") or {}).get("parts") or [])
            for part in parts:
                if part.get("text"):
                    text += part["text"]
        parsed = extract_json(text)
        return VisionResult.from_mapping(parsed, provider=self.name, model=self.model)
