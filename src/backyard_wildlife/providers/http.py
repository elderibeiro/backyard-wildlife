"""Minimal stdlib HTTP helpers. Used by live providers only."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 60) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    for key, value in headers.items():
        req.add_header(key, value)
    if "Content-Type" not in {k.title(): v for k, v in headers.items()}:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail[:800]}") from exc
    return json.loads(raw) if raw else {}
