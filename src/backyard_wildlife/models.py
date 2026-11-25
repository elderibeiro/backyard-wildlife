"""Structured result of a vision call."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any


@dataclass
class BoundingBox:
    """Axis-aligned box in Gemini-style 0-1000 coordinates: ymin, xmin, ymax, xmax."""

    ymin: int
    xmin: int
    ymax: int
    xmax: int
    frame: int = 1
    label: str = ""

    def valid(self) -> bool:
        return (
            0 <= self.ymin < self.ymax <= 1000
            and 0 <= self.xmin < self.xmax <= 1000
        )

    def as_list(self) -> list[int]:
        return [self.ymin, self.xmin, self.ymax, self.xmax]


@dataclass
class VisionResult:
    category: str = "none"
    species: str = "none"
    count: int = 0
    confidence: str = "uncertain"
    behavior: str = ""
    title: str = ""
    description: str = ""
    features: str = ""
    regular: str = "none"
    contains_person: bool = False
    contains_vehicle: bool = False
    boxes: list[BoundingBox] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    provider: str = ""
    model: str = ""

    @property
    def is_animal(self) -> bool:
        return self.category not in ("none", "") and not self.contains_person

    def primary_box(self) -> BoundingBox | None:
        for box in self.boxes:
            if box.valid():
                return box
        return None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["boxes"] = [
            {**asdict(b), "box_2d": b.as_list()} for b in self.boxes
        ]
        return data

    @classmethod
    def from_mapping(cls, data: dict[str, Any], *, provider: str = "", model: str = "") -> "VisionResult":
        payload = dict(data or {})
        # Unwrap common provider envelopes.
        if isinstance(payload.get("structured_response"), dict):
            payload = payload["structured_response"]
        boxes: list[BoundingBox] = []
        for item in payload.get("boxes") or []:
            if isinstance(item, dict):
                coords = item.get("box_2d") or item.get("box") or []
                if len(coords) == 4:
                    try:
                        boxes.append(
                            BoundingBox(
                                ymin=int(coords[0]),
                                xmin=int(coords[1]),
                                ymax=int(coords[2]),
                                xmax=int(coords[3]),
                                frame=int(item.get("frame", 1) or 1),
                                label=str(item.get("label") or payload.get("species") or ""),
                            )
                        )
                    except (TypeError, ValueError):
                        continue
        category = str(payload.get("category") or "none").strip().lower()
        species = str(payload.get("species") or category).strip()
        confidence = str(payload.get("confidence") or "uncertain").strip().lower()
        if confidence not in ("certain", "likely", "uncertain"):
            confidence = "uncertain"
        try:
            count = int(payload.get("count") or 0)
        except (TypeError, ValueError):
            count = 0
        if category not in ("none", "") and count < 1:
            count = 1
        if category in ("none", ""):
            count = 0
            species = "none"
        contains_person = bool(payload.get("contains_person")) or category == "person"
        contains_vehicle = bool(payload.get("contains_vehicle"))
        known = {f.name for f in fields(cls)}
        result = cls(
            category=category if category else "none",
            species=species or "none",
            count=count,
            confidence=confidence,
            behavior=str(payload.get("behavior") or "").strip(),
            title=str(payload.get("title") or "").strip(),
            description=str(payload.get("description") or "").strip(),
            features=str(payload.get("features") or "").strip(),
            regular=str(payload.get("regular") or "none").strip() or "none",
            contains_person=contains_person,
            contains_vehicle=contains_vehicle,
            boxes=boxes,
            raw={k: v for k, v in payload.items() if k in known or k in {"boxes", "box_2d"}},
            provider=provider,
            model=model,
        )
        if not result.title:
            prefix = "" if result.confidence == "certain" else result.confidence.capitalize() + " "
            if result.is_animal:
                result.title = f"{prefix}{result.species}".strip()
            else:
                result.title = result.description or "No activity observed"
        return result
