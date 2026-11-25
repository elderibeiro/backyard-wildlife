"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from backyard_wildlife.config import deep_get, load_config
from backyard_wildlife.digest import write_digest
from backyard_wildlife.pipeline import analyze_image
from backyard_wildlife.providers.base import get_provider
from backyard_wildlife.store import VisitStore


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _data_dir(cfg: dict, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    return Path(deep_get(cfg, "privacy.data_dir", "./data"))


def _store(cfg: dict, data_dir: Path) -> VisitStore:
    tz = deep_get(cfg, "limits.timezone", "America/Chicago")
    return VisitStore(data_dir / "visits.sqlite", timezone=tz)


def _privacy(cfg: dict) -> dict:
    return {
        "skip_persons": bool(deep_get(cfg, "privacy.skip_persons", True)),
        "skip_empty": bool(deep_get(cfg, "privacy.skip_empty", True)),
        "skip_vehicles": bool(deep_get(cfg, "privacy.skip_vehicles", True)),
    }


def cmd_analyze(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    data_dir = _data_dir(cfg, args.data_dir)
    store = _store(cfg, data_dir)
    provider_name = "dry_run" if args.dry_run else (args.provider or deep_get(cfg, "vision.provider", "gemini"))
    model = args.model or deep_get(cfg, "vision.model", "gemini-3.5-flash-lite")
    provider = get_provider(provider_name, model)
    images: list[Path] = []
    for item in args.images:
        path = Path(item)
        if path.is_dir():
            images.extend(sorted(p for p in path.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}))
        else:
            images.append(path)
    if not images:
        samples = _repo_root() / "samples"
        images = sorted(p for p in samples.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not images:
        print("No images found. Pass paths or run scripts/generate_samples.py first.", file=sys.stderr)
        return 2

    results = []
    for image in images:
        out = analyze_image(
            image,
            provider=provider,
            store=store,
            data_dir=data_dir,
            camera=args.camera,
            cooldown_seconds=0 if args.dry_run or args.no_limits else int(deep_get(cfg, "limits.cooldown_seconds", 300)),
            daily_cap=10_000 if args.dry_run or args.no_limits else int(deep_get(cfg, "limits.daily_cap", 150)),
            target_width=int(deep_get(cfg, "vision.target_width", 1024)),
            local_tips=str(deep_get(cfg, "vision.local_tips", "") or ""),
            enforce_limits=not (args.dry_run or args.no_limits),
            **_privacy(cfg),
        )
        results.append(out)
        status = out["status"]
        result = out.get("result") or {}
        label = result.get("title") or result.get("species") or status
        print(f"{image.name}: {status} — {label}")
    if args.json:
        print(json.dumps(results, indent=2))
    kept = sum(1 for r in results if r["status"] == "kept")
    filtered = sum(1 for r in results if r["status"] == "filtered")
    print(f"\n{len(results)} frame(s): {kept} kept, {filtered} filtered. Log: {store.db_path}")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    data_dir = _data_dir(cfg, args.data_dir)
    store = _store(cfg, data_dir)
    dest = write_digest(store, data_dir, args.day)
    print(dest.read_text(encoding="utf-8"))
    print(f"Wrote {dest}")
    return 0


def cmd_gallery(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    data_dir = _data_dir(cfg, args.data_dir)
    store = _store(cfg, data_dir)
    from backyard_wildlife.gallery import serve

    host = args.host or deep_get(cfg, "gallery.host", "127.0.0.1")
    port = int(args.port or deep_get(cfg, "gallery.port", 8080))
    serve(store, data_dir, host=host, port=port)
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    import cv2

    from backyard_wildlife.motion import MotionDetector

    cfg = load_config(args.config)
    data_dir = _data_dir(cfg, args.data_dir)
    store = _store(cfg, data_dir)
    provider_name = "dry_run" if args.dry_run else (args.provider or deep_get(cfg, "vision.provider", "gemini"))
    model = args.model or deep_get(cfg, "vision.model", "gemini-3.5-flash-lite")
    provider = get_provider(provider_name, model)
    cam_type = args.camera_type or deep_get(cfg, "camera.type", "rtsp")
    source: str | int
    if cam_type == "picamera" or str(deep_get(cfg, "camera.url", "")).startswith("picamera"):
        source = int(deep_get(cfg, "camera.index", 0) or 0)
    elif cam_type == "images":
        print("Use the analyze command for still images.", file=sys.stderr)
        return 2
    else:
        source = args.url or deep_get(cfg, "camera.url")
        if not source:
            print("No camera URL configured.", file=sys.stderr)
            return 2
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Could not open camera source: {source}", file=sys.stderr)
        return 1
    detector = MotionDetector(
        min_area=int(deep_get(cfg, "motion.min_area", 1200)),
        threshold=int(deep_get(cfg, "motion.threshold", 25)),
        warmup_frames=int(deep_get(cfg, "motion.warmup_frames", 8)),
    )
    interval = float(deep_get(cfg, "camera.frame_interval", 0.4))
    camera_name = args.camera
    print(f"Watching {source!r} with provider={provider.name}. Ctrl+C to stop.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(1)
                cap.release()
                cap = cv2.VideoCapture(source)
                continue
            event = detector.update(frame)
            if event.detected:
                snap = data_dir / "tmp" / "live-frame.jpg"
                snap.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(snap), frame)
                out = analyze_image(
                    snap,
                    provider=provider,
                    store=store,
                    data_dir=data_dir,
                    camera=camera_name,
                    cooldown_seconds=int(deep_get(cfg, "limits.cooldown_seconds", 300)),
                    daily_cap=int(deep_get(cfg, "limits.daily_cap", 150)),
                    target_width=int(deep_get(cfg, "vision.target_width", 1024)),
                    local_tips=str(deep_get(cfg, "vision.local_tips", "") or ""),
                    enforce_limits=not args.dry_run,
                    **_privacy(cfg),
                )
                result = out.get("result") or {}
                print(f"{out['status']}: {result.get('title') or out.get('reason')}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        cap.release()
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", help="Path to config.yaml")
    common.add_argument("--data-dir", help="Override privacy.data_dir")
    parser = argparse.ArgumentParser(
        prog="backyard-wildlife",
        description="Identify backyard animals in camera frames, skip people, and log visits locally.",
        parents=[common],
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", parents=[common], help="Analyze still images (use --dry-run for sample images, no API key)")
    analyze.add_argument("images", nargs="*", help="Image files or a directory. Defaults to ./samples")
    analyze.add_argument("--dry-run", action="store_true", help="Use the offline sample provider; no API key needed")
    analyze.add_argument("--no-limits", action="store_true", help="Ignore cooldown and daily cap")
    analyze.add_argument("--provider", help="gemini, openai, xai, ollama, or dry_run")
    analyze.add_argument("--model", help="Provider model id")
    analyze.add_argument("--camera", default="sample")
    analyze.add_argument("--json", action="store_true", help="Print full JSON results")
    analyze.set_defaults(func=cmd_analyze)

    digest = sub.add_parser("digest", parents=[common], help="Write a Markdown daily digest from the local log")
    digest.add_argument("--day", help="YYYY-MM-DD (defaults to today in the configured timezone)")
    digest.set_defaults(func=cmd_digest)

    gallery = sub.add_parser("gallery", parents=[common], help="Serve a local Recent Visits gallery")
    gallery.add_argument("--host", help="Bind address (default 127.0.0.1)")
    gallery.add_argument("--port", type=int, help="Bind port (default 8080)")
    gallery.set_defaults(func=cmd_gallery)

    watch = sub.add_parser("watch", parents=[common], help="Watch an RTSP or Pi camera, detect motion, and identify animals")
    watch.add_argument("--dry-run", action="store_true", help="Use the offline provider (still opens the camera)")
    watch.add_argument("--provider")
    watch.add_argument("--model")
    watch.add_argument("--url", help="RTSP URL or camera index override")
    watch.add_argument("--camera-type", choices=["rtsp", "picamera"])
    watch.add_argument("--camera", default="backyard")
    watch.set_defaults(func=cmd_watch)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
