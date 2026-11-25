"""Shared analyze path used by the CLI, tests, and the live watcher."""

from __future__ import annotations

import shutil
from pathlib import Path

from backyard_wildlife.crop import crop_around, resize_for_vision
from backyard_wildlife.limits import check_limits
from backyard_wildlife.models import VisionResult
from backyard_wildlife.prompts import render_species_prompt
from backyard_wildlife.providers.base import VisionProvider
from backyard_wildlife.store import VisitStore


def should_keep(result: VisionResult, *, skip_persons: bool, skip_empty: bool, skip_vehicles: bool) -> bool:
    if skip_persons and result.contains_person:
        return False
    if skip_empty and not result.is_animal:
        return False
    if skip_vehicles and result.contains_vehicle and not result.is_animal:
        return False
    return result.is_animal


def analyze_image(
    image_path: Path,
    *,
    provider: VisionProvider,
    store: VisitStore,
    data_dir: Path,
    camera: str = "sample",
    cooldown_seconds: int = 0,
    daily_cap: int = 10_000,
    target_width: int = 1024,
    local_tips: str = "",
    skip_persons: bool = True,
    skip_empty: bool = True,
    skip_vehicles: bool = True,
    enforce_limits: bool = True,
) -> dict:
    """Analyze one still. Returns a dict describing what happened."""
    image_path = Path(image_path)
    if enforce_limits:
        decision = check_limits(store, camera, cooldown_seconds, daily_cap)
        if not decision:
            store.record_call(camera, provider.name, skipped_reason=decision.reason)
            return {"status": "skipped", "reason": decision.reason, "path": str(image_path)}

    work_dir = data_dir / "tmp"
    resized = resize_for_vision(image_path, work_dir / f"vision-{image_path.stem}.jpg", target_width)
    prompt = render_species_prompt(local_tips=local_tips)
    result = provider.analyze(resized, prompt)
    store.record_call(camera, provider.name, skipped_reason="")

    kept = should_keep(
        result,
        skip_persons=skip_persons,
        skip_empty=skip_empty,
        skip_vehicles=skip_vehicles,
    )
    crop_path = ""
    source_saved = ""
    visit_id = None
    if kept:
        stamp = store.now().strftime("%Y%m%d-%H%M%S")
        visits_dir = data_dir / "visits"
        source_saved = str(visits_dir / f"{stamp}-{camera}-{image_path.stem}.jpg")
        Path(source_saved).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, source_saved)
        crop_dest = visits_dir / "crops" / f"{stamp}-{camera}-{image_path.stem}.jpg"
        crop_around(image_path, result.primary_box(), crop_dest)
        crop_path = str(crop_dest)
        visit_id = store.add_visit(result, camera=camera, source_path=source_saved, crop_path=crop_path)

    return {
        "status": "kept" if kept else "filtered",
        "visit_id": visit_id,
        "path": str(image_path),
        "crop_path": crop_path,
        "source_path": source_saved,
        "result": result.to_dict(),
    }
