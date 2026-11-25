"""Local daily digest from the SQLite log. No API call required."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from backyard_wildlife.store import VisitStore


def build_digest(store: VisitStore, day: str | None = None) -> str:
    day = day or store.now().date().isoformat()
    visits = store.visits_on(day)
    if not visits:
        return (
            f"# Backyard Wildlife digest — {day}\n\n"
            "No animal visits were logged on this day "
            "(people and empty frames are omitted by design).\n"
        )
    counts = Counter(v["species"] or v["category"] for v in visits)
    lines = [f"# Backyard Wildlife digest — {day}", ""]
    lines.append(
        f"{len(visits)} animal visit{'s' if len(visits) != 1 else ''} logged, "
        f"across {len(counts)} species."
    )
    lines.append("")
    lines.append("## Species")
    for species, n in counts.most_common():
        lines.append(f"- {species}: {n}")
    lines.append("")
    lines.append("## Visits")
    for visit in visits:
        when = visit["created_at"]
        try:
            when = datetime.fromisoformat(when).strftime("%-I:%M %p")
        except ValueError:
            pass
        behavior = f" — {visit['behavior']}" if visit.get("behavior") else ""
        conf = visit.get("confidence") or ""
        lines.append(
            f"- {when}: {visit['title'] or visit['species']} "
            f"({conf}{behavior})"
        )
    lines.append("")
    lines.append(
        "Counts come only from the local log. This digest does not invent "
        "metrics or re-identify people."
    )
    return "\n".join(lines) + "\n"


def write_digest(store: VisitStore, data_dir: Path, day: str | None = None) -> Path:
    day = day or store.now().date().isoformat()
    text = build_digest(store, day)
    dest = Path(data_dir) / "digests" / f"{day}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return dest
