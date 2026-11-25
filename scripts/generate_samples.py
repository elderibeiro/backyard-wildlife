#!/usr/bin/env python3
"""Create synthetic sample frames for dry-run demos. No real camera photos."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
WIDTH, HEIGHT = 960, 640


def _font(size: int):
    for name in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def canvas(sky=(170, 200, 230), grass=(70, 120, 55)) -> Image.Image:
    im = Image.new("RGB", (WIDTH, HEIGHT), sky)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 340, WIDTH, HEIGHT), fill=grass)
    draw.rectangle((0, 300, WIDTH, 350), fill=(90, 130, 60))
    # fence
    for x in range(20, WIDTH, 70):
        draw.rectangle((x, 240, x + 14, 400), fill=(110, 80, 45))
    draw.rectangle((0, 270, WIDTH, 286), fill=(110, 80, 45))
    return im


def label(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.rectangle((8, 8, 360, 40), fill=(20, 20, 20, 180))
    draw.text((16, 12), text, fill=(255, 255, 255), font=_font(18))


def box_from_pixels(left, top, right, bottom) -> list[int]:
    return [
        int(top / HEIGHT * 1000),
        int(left / WIDTH * 1000),
        int(bottom / HEIGHT * 1000),
        int(right / WIDTH * 1000),
    ]


def make_rabbit() -> dict:
    im = canvas()
    d = ImageDraw.Draw(im)
    body = (420, 390, 600, 500)
    d.ellipse(body, fill=(196, 168, 130), outline=(90, 60, 30), width=2)
    d.ellipse((560, 370, 640, 450), fill=(196, 168, 130), outline=(90, 60, 30), width=2)
    d.ellipse((600, 430, 628, 456), fill=(80, 50, 30))  # eye
    d.polygon([(580, 370), (555, 260), (600, 370)], fill=(196, 168, 130), outline=(90, 60, 30))
    d.polygon([(610, 370), (640, 250), (640, 375)], fill=(196, 168, 130), outline=(90, 60, 30))
    d.ellipse((410, 450, 445, 485), fill=(240, 240, 230))  # tail
    label(d, "SAMPLE · eastern cottontail (synthetic)")
    path = SAMPLES / "01-rabbit.jpg"
    im.save(path, quality=92)
    return {
        "file": path.name,
        "category": "rabbit",
        "species": "eastern cottontail",
        "count": 1,
        "confidence": "certain",
        "behavior": "sitting in the grass",
        "title": "Eastern cottontail",
        "description": "A cottontail rabbit is sitting in the grass near a fence.",
        "features": "",
        "regular": "none",
        "contains_person": False,
        "contains_vehicle": False,
        "boxes": [{"frame": 1, "box_2d": box_from_pixels(410, 250, 645, 505), "label": "eastern cottontail"}],
    }


def make_squirrel() -> dict:
    im = canvas()
    d = ImageDraw.Draw(im)
    d.ellipse((150, 200, 280, 280), fill=(130, 90, 50), outline=(60, 35, 15), width=2)
    d.ellipse((240, 175, 310, 245), fill=(130, 90, 50), outline=(60, 35, 15), width=2)
    d.ellipse((285, 200, 300, 216), fill=(20, 15, 10))
    d.polygon([(255, 180), (250, 120), (280, 180)], fill=(130, 90, 50))
    # bushy tail
    d.ellipse((80, 150, 190, 280), fill=(150, 105, 60), outline=(60, 35, 15), width=2)
    label(d, "SAMPLE · eastern gray squirrel (synthetic)")
    path = SAMPLES / "02-squirrel.jpg"
    im.save(path, quality=92)
    return {
        "file": path.name,
        "category": "squirrel",
        "species": "eastern gray squirrel",
        "count": 1,
        "confidence": "certain",
        "behavior": "perched on the fence",
        "title": "Eastern gray squirrel",
        "description": "A squirrel is perched on the fence rail.",
        "features": "",
        "regular": "none",
        "contains_person": False,
        "contains_vehicle": False,
        "boxes": [{"frame": 1, "box_2d": box_from_pixels(80, 115, 315, 285), "label": "eastern gray squirrel"}],
    }


def make_bird() -> dict:
    im = canvas(sky=(130, 180, 220))
    d = ImageDraw.Draw(im)
    # branch
    d.line((200, 180, 700, 220), fill=(80, 50, 30), width=8)
    d.ellipse((430, 140, 530, 200), fill=(180, 25, 30), outline=(80, 10, 10), width=2)
    d.polygon([(530, 160), (575, 155), (530, 175)], fill=(230, 160, 40))
    d.ellipse((515, 150, 528, 162), fill=(20, 20, 20))
    d.polygon([(450, 145), (420, 100), (470, 145)], fill=(30, 30, 30))
    label(d, "SAMPLE · northern cardinal (synthetic)")
    path = SAMPLES / "03-bird.jpg"
    im.save(path, quality=92)
    return {
        "file": path.name,
        "category": "bird",
        "species": "northern cardinal",
        "count": 1,
        "confidence": "likely",
        "behavior": "perched on a branch",
        "title": "Likely northern cardinal",
        "description": "A red bird is perched on a branch.",
        "features": "",
        "regular": "none",
        "contains_person": False,
        "contains_vehicle": False,
        "boxes": [{"frame": 1, "box_2d": box_from_pixels(415, 95, 580, 205), "label": "northern cardinal"}],
    }


def make_person() -> dict:
    """A faceless silhouette, used to test the privacy filter. Not a real person."""
    im = canvas()
    d = ImageDraw.Draw(im)
    # silhouette only
    d.ellipse((470, 160, 530, 225), fill=(20, 20, 25))
    d.polygon([(500, 220), (430, 420), (570, 420)], fill=(20, 20, 25))
    d.rectangle((455, 420, 485, 540), fill=(20, 20, 25))
    d.rectangle((515, 420, 545, 540), fill=(20, 20, 25))
    label(d, "SAMPLE · person silhouette (synthetic, should be skipped)")
    path = SAMPLES / "04-person.jpg"
    im.save(path, quality=92)
    return {
        "file": path.name,
        "category": "none",
        "species": "none",
        "count": 0,
        "confidence": "certain",
        "behavior": "",
        "title": "Person walking",
        "description": "A person is in the frame; no animal is clearly visible.",
        "features": "",
        "regular": "none",
        "contains_person": True,
        "contains_vehicle": False,
        "boxes": [],
    }


def make_empty() -> dict:
    im = canvas()
    d = ImageDraw.Draw(im)
    label(d, "SAMPLE · empty yard (synthetic)")
    path = SAMPLES / "05-empty.jpg"
    im.save(path, quality=92)
    return {
        "file": path.name,
        "category": "none",
        "species": "none",
        "count": 0,
        "confidence": "certain",
        "behavior": "",
        "title": "No activity observed",
        "description": "An empty yard with no animal visible.",
        "features": "",
        "regular": "none",
        "contains_person": False,
        "contains_vehicle": False,
        "boxes": [],
    }


def make_pest() -> dict:
    """Garden-center style close-up, still synthetic."""
    im = Image.new("RGB", (WIDTH, HEIGHT), (70, 130, 55))
    d = ImageDraw.Draw(im)
    d.ellipse((200, 80, 820, 560), fill=(40, 110, 40), outline=(20, 70, 20), width=4)
    # beetle
    d.ellipse((430, 250, 560, 400), fill=(30, 80, 45), outline=(10, 30, 15), width=3)
    d.ellipse((400, 270, 455, 340), fill=(20, 20, 20))
    for y in (280, 320, 360):
        d.line((430, y, 350, y - 20), fill=(10, 10, 10), width=3)
        d.line((560, y, 640, y - 20), fill=(10, 10, 10), width=3)
    label(d, "SAMPLE · Japanese beetle on a leaf (synthetic)")
    path = SAMPLES / "06-pest.jpg"
    im.save(path, quality=92)
    return {
        "file": path.name,
        "category": "other animal",
        "species": "Japanese beetle",
        "count": 1,
        "confidence": "likely",
        "behavior": "on a leaf",
        "title": "Likely Japanese beetle",
        "description": "A small metallic beetle is sitting on a leaf.",
        "features": "",
        "regular": "none",
        "contains_person": False,
        "contains_vehicle": False,
        "boxes": [{"frame": 1, "box_2d": box_from_pixels(340, 240, 650, 415), "label": "Japanese beetle"}],
    }


def main() -> None:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    entries = [make_rabbit(), make_squirrel(), make_bird(), make_person(), make_empty(), make_pest()]
    manifest = {
        "note": "Synthetic demo frames only. Not photographs of a real yard or people.",
        "images": {e.pop("file"): e for e in entries},
    }
    (SAMPLES / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(manifest['images'])} sample images to {SAMPLES}")


if __name__ == "__main__":
    main()
