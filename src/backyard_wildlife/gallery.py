"""Tiny local gallery for recent animal visits."""

from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from backyard_wildlife.store import VisitStore


def _page(title: str, body: str) -> bytes:
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light dark; --bg: #10140f; --card: #1b2319; --ink: #e8f0e4; --muted: #9aa886; --accent: #7d9a5a; }}
    @media (prefers-color-scheme: light) {{
      :root {{ --bg: #f4f1e8; --card: #fff; --ink: #1c2418; --muted: #5c6854; --accent: #3d5a27; }}
    }}
    body {{ margin: 0; font-family: Georgia, serif; background: var(--bg); color: var(--ink); }}
    header {{ padding: 1.5rem 1.25rem 0.5rem; max-width: 1100px; margin: auto; }}
    h1 {{ font-weight: normal; margin: 0 0 .25rem; }}
    p.lede {{ color: var(--muted); margin: 0 0 1rem; }}
    main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; padding: 1rem 1.25rem 3rem; max-width: 1100px; margin: auto; }}
    article {{ background: var(--card); border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px #0002; }}
    article img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; background: #0002; }}
    article div {{ padding: .7rem .85rem 1rem; }}
    article h2 {{ font-size: 1.05rem; margin: 0 0 .2rem; font-weight: normal; }}
    article p {{ margin: 0; color: var(--muted); font-size: .9rem; }}
  </style>
</head>
<body>
  <header>
    <h1>Recent Visits</h1>
    <p class="lede">Animals only. People, vehicles, and empty frames are hidden. Photos stay on this computer.</p>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""
    return doc.encode("utf-8")


def make_handler(store: VisitStore, data_dir: Path):
    data_dir = data_dir.resolve()

    class GalleryHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                cards = []
                for visit in store.recent_animals(60):
                    img = visit.get("crop_path") or visit.get("source_path") or ""
                    src = f"/media/{Path(img).name}" if img else ""
                    title = html.escape(visit.get("title") or visit.get("species") or "Visit")
                    meta = html.escape(
                        " · ".join(
                            x
                            for x in (
                                visit.get("species"),
                                visit.get("confidence"),
                                visit.get("behavior"),
                                (visit.get("created_at") or "")[:16].replace("T", " "),
                            )
                            if x
                        )
                    )
                    cards.append(
                        f'<article><img src="{html.escape(src)}" alt="{title}">'
                        f"<div><h2>{title}</h2><p>{meta}</p></div></article>"
                    )
                body = "".join(cards) or "<p>No animal visits yet.</p>"
                payload = _page("Recent Visits", body)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if parsed.path == "/api/visits":
                payload = json.dumps(store.recent_animals(100), indent=2).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if parsed.path.startswith("/media/"):
                name = unquote(parsed.path.removeprefix("/media/"))
                # Only serve files inside the data directory, by basename match.
                target = None
                for visit in store.recent_animals(200):
                    for key in ("crop_path", "source_path"):
                        p = Path(visit.get(key) or "")
                        if p.name == name:
                            target = p.resolve()
                            break
                    if target:
                        break
                if not target or not str(target).startswith(str(data_dir)) or not target.is_file():
                    self.send_error(404)
                    return
                data = target.read_bytes()
                ctype = "image/jpeg" if target.suffix.lower() in {".jpg", ".jpeg"} else "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            self.send_error(404)

    return GalleryHandler


def serve(store: VisitStore, data_dir: Path, host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), make_handler(store, data_dir))
    print(f"Recent Visits gallery: http://{host}:{port}/  (Ctrl+C to stop)")
    server.serve_forever()
