"""Backyard Wildlife: identify animals in camera frames, skip people, log visits."""

__version__ = "0.1.0"

CATEGORIES = (
    "squirrel",
    "opossum",
    "rabbit",
    "bird",
    "cat",
    "other animal",
    "none",
)
CONFIDENCE_LEVELS = ("certain", "likely", "uncertain")
SKIP_LABELS = ("person", "delivery", "car", "bicycle", "vehicle", "none")
