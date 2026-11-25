"""Crop a still around a 0-1000 bounding box, with padding."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from backyard_wildlife.models import BoundingBox


def crop_around(
    image_path: Path | str,
    box: BoundingBox,
    dest: Path | str,
    *,
    padding: float = 0.18,
    min_side: int = 160,
) -> Path:
    """Write a square-ish crop around `box`. Returns the output path.

    If the box is missing or invalid, a copy of the full frame is saved instead.
    """
    src = Path(image_path)
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        width, height = im.size
        if box is None or not box.valid():
            im.save(dest_path, format="JPEG", quality=90)
            return dest_path
        pad_y = int((box.ymax - box.ymin) * padding)
        pad_x = int((box.xmax - box.xmin) * padding)
        top = max(0, int(height * (box.ymin - pad_y) / 1000))
        left = max(0, int(width * (box.xmin - pad_x) / 1000))
        bottom = min(height, int(height * (box.ymax + pad_y) / 1000))
        right = min(width, int(width * (box.xmax + pad_x) / 1000))
        side = max(bottom - top, right - left, min_side)
        cx = (left + right) // 2
        cy = (top + bottom) // 2
        left = max(0, min(width - side, cx - side // 2))
        top = max(0, min(height - side, cy - side // 2))
        right = min(width, left + side)
        bottom = min(height, top + side)
        cropped = im.crop((left, top, right, bottom))
        cropped.save(dest_path, format="JPEG", quality=90)
    return dest_path


def resize_for_vision(image_path: Path | str, dest: Path | str, target_width: int = 1024) -> Path:
    src = Path(image_path)
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        if im.width > target_width and target_width > 0:
            ratio = target_width / im.width
            im = im.resize((target_width, max(1, int(im.height * ratio))), Image.Resampling.LANCZOS)
        im.save(dest_path, format="JPEG", quality=90)
    return dest_path
