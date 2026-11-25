"""Extract a JSON object from a model response string."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json(text: str) -> dict[str, Any]:
    if not text:
        return {}
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.S)
    if fence:
        stripped = fence.group(1)
    try:
        data = json.loads(stripped)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(stripped[start : end + 1])
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {}
    return {}
