"""Offline provider that reads a samples/manifest.json entry, or a stub result."""

from __future__ import annotations

import json
from pathlib import Path

from backyard_wildlife.models import VisionResult


def _manifest_path(image_path: Path) -> Path | None:
    candidates: list[Path] = []
    for parent in (image_path.parent, *image_path.parents):
        candidates.append(parent / "manifest.json")
        candidates.append(parent / "samples" / "manifest.json")
    repo_samples = Path(__file__).resolve().parents[3] / "samples" / "manifest.json"
    candidates.append(repo_samples)
    candidates.append(Path.cwd() / "samples" / "manifest.json")
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if candidate.is_file():
            return candidate
    return None



def _lookup_entry(image_path: Path, manifest: dict) -> dict:
    images = manifest.get("images") if isinstance(manifest.get("images"), dict) else manifest
    if not isinstance(images, dict):
        return {}
    stem = image_path.stem
    # pipeline resizes to tmp/vision-<original-stem>.jpg
    if stem.startswith("vision-"):
        stem = stem[len("vision-"):]
    candidates = [
        image_path.name,
        f"{stem}{image_path.suffix}",
        f"{stem}.jpg",
        stem,
    ]
    for key in candidates:
        if key in images and isinstance(images[key], dict):
            return images[key]
    for key, value in images.items():
        if not isinstance(value, dict) or not isinstance(key, str):
            continue
        key_stem = Path(key).stem
        if key == image_path.name or key_stem == stem or stem.endswith(key_stem):
            return value
    return {}


class DryRunProvider:
    name = "dry_run"

    def __init__(self, model: str = "dry-run"):
        self.model = model

    def analyze(self, image_path: Path, prompt: str) -> VisionResult:
        del prompt  # unused; this provider never calls a network API
        path = Path(image_path)
        manifest_file = _manifest_path(path)
        entry: dict = {}
        if manifest_file:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            entry = _lookup_entry(path, manifest)
        if not entry:
            # Filename fallback: 01-rabbit.jpg or person.png
            stem = path.stem.lower()
            for token in (
                "rabbit",
                "squirrel",
                "bird",
                "cat",
                "opossum",
                "person",
                "empty",
                "pest",
                "vehicle",
            ):
                if token in stem:
                    if token == "person":
                        entry = {
                            "category": "none",
                            "species": "none",
                            "count": 0,
                            "confidence": "certain",
                            "behavior": "",
                            "title": "Person walking",
                            "description": "A person is in the frame; no animal is clearly visible.",
                            "contains_person": True,
                            "contains_vehicle": False,
                            "boxes": [],
                        }
                    elif token == "empty":
                        entry = {
                            "category": "none",
                            "species": "none",
                            "count": 0,
                            "confidence": "certain",
                            "title": "No activity observed",
                            "description": "Empty yard, no animal visible.",
                            "contains_person": False,
                            "contains_vehicle": False,
                            "boxes": [],
                        }
                    elif token == "vehicle":
                        entry = {
                            "category": "none",
                            "species": "none",
                            "count": 0,
                            "confidence": "certain",
                            "title": "Vehicle in frame",
                            "description": "A vehicle is visible; no animal is clearly visible.",
                            "contains_person": False,
                            "contains_vehicle": True,
                            "boxes": [],
                        }
                    elif token == "pest":
                        entry = {
                            "category": "other animal",
                            "species": "Japanese beetle",
                            "count": 1,
                            "confidence": "likely",
                            "behavior": "on a leaf",
                            "title": "Likely Japanese beetle",
                            "description": "A small metallic beetle is sitting on a leaf.",
                            "contains_person": False,
                            "contains_vehicle": False,
                            "boxes": [{"frame": 1, "box_2d": [350, 400, 700, 700], "label": "Japanese beetle"}],
                        }
                    else:
                        entry = {
                            "category": token,
                            "species": token,
                            "count": 1,
                            "confidence": "likely",
                            "behavior": "in the frame",
                            "title": f"Likely {token}",
                            "description": f"A {token} is visible in the sample frame.",
                            "contains_person": False,
                            "contains_vehicle": False,
                            "boxes": [{"frame": 1, "box_2d": [250, 250, 800, 800], "label": token}],
                        }
                    break
        if not entry:
            entry = {
                "category": "none",
                "species": "none",
                "count": 0,
                "confidence": "uncertain",
                "title": "No activity observed",
                "description": "Dry-run had no manifest entry for this file.",
                "contains_person": False,
                "contains_vehicle": False,
                "boxes": [],
            }
        return VisionResult.from_mapping(entry, provider=self.name, model=self.model)
