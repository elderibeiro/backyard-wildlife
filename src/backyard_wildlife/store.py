"""SQLite visit log and local call-limit counters."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from backyard_wildlife.models import VisionResult


SCHEMA = """
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    camera TEXT,
    category TEXT,
    species TEXT,
    count INTEGER,
    confidence TEXT,
    behavior TEXT,
    title TEXT,
    description TEXT,
    features TEXT,
    regular TEXT,
    contains_person INTEGER,
    contains_vehicle INTEGER,
    provider TEXT,
    model TEXT,
    source_path TEXT,
    crop_path TEXT,
    box_json TEXT
);
CREATE TABLE IF NOT EXISTS api_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    called_at TEXT NOT NULL,
    camera TEXT,
    provider TEXT,
    skipped_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_visits_created ON visits(created_at);
CREATE INDEX IF NOT EXISTS idx_calls_called ON api_calls(called_at);
"""


class VisitStore:
    def __init__(self, db_path: Path | str, timezone: str = "America/Chicago"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.tz = ZoneInfo(timezone)
        with self._connect() as con:
            con.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def now(self) -> datetime:
        return datetime.now(self.tz)

    def record_call(self, camera: str, provider: str, skipped_reason: str = "") -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO api_calls(called_at, camera, provider, skipped_reason) VALUES (?,?,?,?)",
                (self.now().isoformat(), camera, provider, skipped_reason),
            )

    def calls_today(self, camera: str | None = None) -> int:
        start = self.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        sql = "SELECT COUNT(*) FROM api_calls WHERE called_at >= ? AND skipped_reason = ''"
        args: list = [start]
        if camera:
            sql += " AND camera = ?"
            args.append(camera)
        with self._connect() as con:
            return int(con.execute(sql, args).fetchone()[0])

    def seconds_since_last_call(self, camera: str) -> float | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT called_at FROM api_calls WHERE camera = ? AND skipped_reason = '' "
                "ORDER BY id DESC LIMIT 1",
                (camera,),
            ).fetchone()
        if not row:
            return None
        then = datetime.fromisoformat(row["called_at"])
        if then.tzinfo is None:
            then = then.replace(tzinfo=self.tz)
        return (self.now() - then).total_seconds()

    def add_visit(
        self,
        result: VisionResult,
        *,
        camera: str,
        source_path: str,
        crop_path: str,
    ) -> int:
        payload = result.to_dict()
        with self._connect() as con:
            cur = con.execute(
                """
                INSERT INTO visits(
                    created_at, camera, category, species, count, confidence, behavior,
                    title, description, features, regular, contains_person, contains_vehicle,
                    provider, model, source_path, crop_path, box_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    self.now().isoformat(),
                    camera,
                    result.category,
                    result.species,
                    result.count,
                    result.confidence,
                    result.behavior,
                    result.title,
                    result.description,
                    result.features,
                    result.regular,
                    int(result.contains_person),
                    int(result.contains_vehicle),
                    result.provider,
                    result.model,
                    source_path,
                    crop_path,
                    json.dumps(payload.get("boxes") or []),
                ),
            )
            return int(cur.lastrowid)

    def recent_animals(self, limit: int = 50) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT * FROM visits
                WHERE contains_person = 0 AND category NOT IN ('none', '')
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def visits_on(self, day: str | None = None) -> list[dict]:
        if not day:
            day = self.now().date().isoformat()
        start = f"{day}T00:00:00"
        end = f"{day}T23:59:59.999999"
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT * FROM visits
                WHERE created_at >= ? AND created_at <= ?
                  AND contains_person = 0 AND category NOT IN ('none', '')
                ORDER BY id ASC
                """,
                (start, end),
            ).fetchall()
        return [dict(r) for r in rows]
