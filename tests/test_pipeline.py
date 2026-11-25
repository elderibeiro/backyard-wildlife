from __future__ import annotations

import json
from pathlib import Path

import pytest

from backyard_wildlife.crop import crop_around
from backyard_wildlife.limits import check_limits
from backyard_wildlife.models import BoundingBox, VisionResult
from backyard_wildlife.pipeline import analyze_image, should_keep
from backyard_wildlife.prompts import JSON_SCHEMA, render_species_prompt
from backyard_wildlife.providers.base import get_provider
from backyard_wildlife.providers.dry_run import DryRunProvider
from backyard_wildlife.store import VisitStore

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


@pytest.fixture
def samples_ready() -> None:
    if not (SAMPLES / "manifest.json").is_file():
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generate_samples", ROOT / "scripts" / "generate_samples.py"
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        mod.main()
    assert (SAMPLES / "01-rabbit.jpg").is_file()


@pytest.fixture
def store(tmp_path: Path) -> VisitStore:
    return VisitStore(tmp_path / "visits.sqlite", timezone="America/Chicago")


def test_dry_run_keeps_animals_and_skips_people(samples_ready, store, tmp_path):
    provider = DryRunProvider()
    results = []
    for name in (
        "01-rabbit.jpg",
        "02-squirrel.jpg",
        "03-bird.jpg",
        "04-person.jpg",
        "05-empty.jpg",
        "06-pest.jpg",
    ):
        results.append(
            analyze_image(
                SAMPLES / name,
                provider=provider,
                store=store,
                data_dir=tmp_path,
                camera="sample",
                enforce_limits=False,
            )
        )
    statuses = {Path(r["path"]).name: r["status"] for r in results}
    assert statuses["01-rabbit.jpg"] == "kept"
    assert statuses["02-squirrel.jpg"] == "kept"
    assert statuses["03-bird.jpg"] == "kept"
    assert statuses["06-pest.jpg"] == "kept"
    assert statuses["04-person.jpg"] == "filtered"
    assert statuses["05-empty.jpg"] == "filtered"

    rabbit = next(r for r in results if r["path"].endswith("01-rabbit.jpg"))
    assert rabbit["result"]["species"] == "eastern cottontail"
    assert rabbit["result"]["count"] == 1
    assert rabbit["result"]["confidence"] == "certain"
    assert rabbit["crop_path"] and Path(rabbit["crop_path"]).is_file()
    # Crop should be smaller than the original frame.
    from PIL import Image

    with Image.open(SAMPLES / "01-rabbit.jpg") as orig, Image.open(rabbit["crop_path"]) as crop:
        assert crop.size[0] * crop.size[1] < orig.size[0] * orig.size[1]

    animals = store.recent_animals()
    assert all(v["contains_person"] == 0 for v in animals)
    assert {v["species"] for v in animals} >= {"eastern cottontail", "eastern gray squirrel", "northern cardinal", "Japanese beetle"}


def test_limits_cooldown_and_cap(store):
    store.record_call("backyard", "dry_run")
    blocked = check_limits(store, "backyard", cooldown_seconds=300, daily_cap=150)
    assert not blocked
    assert "cooldown" in blocked.reason
    # A different camera still has headroom on the shared daily cap, but this
    # camera is in cooldown.
    other = check_limits(store, "garden", cooldown_seconds=300, daily_cap=150)
    assert other.allowed

    for _ in range(149):
        store.record_call("garden", "dry_run")
    capped = check_limits(store, "garden", cooldown_seconds=0, daily_cap=150)
    assert not capped
    assert "daily cap" in capped.reason


def test_privacy_filter_rules():
    person = VisionResult(category="none", contains_person=True, title="Person walking")
    empty = VisionResult(category="none")
    car = VisionResult(category="none", contains_vehicle=True)
    rabbit = VisionResult(category="rabbit", species="eastern cottontail", count=1)
    assert not should_keep(person, skip_persons=True, skip_empty=True, skip_vehicles=True)
    assert not should_keep(empty, skip_persons=True, skip_empty=True, skip_vehicles=True)
    assert not should_keep(car, skip_persons=True, skip_empty=True, skip_vehicles=True)
    assert should_keep(rabbit, skip_persons=True, skip_empty=True, skip_vehicles=True)


def test_invalid_box_falls_back_to_full_frame(tmp_path):
    src = tmp_path / "full.jpg"
    from PIL import Image

    Image.new("RGB", (400, 300), (10, 80, 10)).save(src)
    dest = tmp_path / "crop.jpg"
    crop_around(src, BoundingBox(0, 0, 0, 0), dest)
    assert dest.is_file()
    from PIL import Image as Im

    with Im.open(dest) as out:
        assert out.size == (400, 300)


def test_prompt_and_schema_include_required_fields():
    prompt = render_species_prompt(local_tips="cottontails are common")
    for word in ("category", "species", "count", "confidence", "behavior", "boxes", "contains_person"):
        assert word in prompt
    assert "cottontails are common" in prompt
    required = set(JSON_SCHEMA["required"])
    assert required >= {"species", "count", "confidence", "behavior", "boxes"}
    # Schema is plain JSON, so it can be dumped for providers.
    json.dumps(JSON_SCHEMA)


def test_get_provider_names():
    assert get_provider("dry-run").name == "dry_run"
    assert get_provider("gemini").name == "gemini"
    assert get_provider("openai").name == "openai"
    assert get_provider("xai").name == "xai"
    assert get_provider("ollama").name == "ollama"
    with pytest.raises(ValueError):
        get_provider("unknown")


def test_digest_does_not_invent_counts(store, tmp_path, samples_ready):
    from backyard_wildlife.digest import build_digest

    provider = DryRunProvider()
    analyze_image(SAMPLES / "01-rabbit.jpg", provider=provider, store=store, data_dir=tmp_path, enforce_limits=False)
    analyze_image(SAMPLES / "01-rabbit.jpg", provider=provider, store=store, data_dir=tmp_path, enforce_limits=False)
    analyze_image(SAMPLES / "04-person.jpg", provider=provider, store=store, data_dir=tmp_path, enforce_limits=False)
    text = build_digest(store)
    assert "2 animal visits" in text
    assert "eastern cottontail: 2" in text
    assert "Person" not in text


def test_motion_detects_a_moving_blob():
    import numpy as np

    from backyard_wildlife.motion import MotionDetector

    detector = MotionDetector(min_area=200, threshold=20, warmup_frames=2)
    blank = np.zeros((240, 320, 3), dtype=np.uint8)
    moving = blank.copy()
    moving[80:140, 100:180] = 255
    assert not detector.update(blank).detected
    assert not detector.update(blank).detected  # warmup
    assert not detector.update(blank).detected  # still scene
    event = detector.update(moving)
    assert event.detected
    assert event.area >= 200
