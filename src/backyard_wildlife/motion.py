"""Simple OpenCV frame-difference motion detector."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class MotionEvent:
    detected: bool
    area: int
    contour_box: tuple[int, int, int, int] | None  # x, y, w, h in pixels


class MotionDetector:
    def __init__(self, min_area: int = 1200, threshold: int = 25, warmup_frames: int = 8):
        self.min_area = min_area
        self.threshold = threshold
        self.warmup_frames = warmup_frames
        self._prev: np.ndarray | None = None
        self._seen = 0

    def reset(self) -> None:
        self._prev = None
        self._seen = 0

    def update(self, frame) -> MotionEvent:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        self._seen += 1
        if self._prev is None or self._seen <= self.warmup_frames:
            self._prev = gray
            return MotionEvent(False, 0, None)
        delta = cv2.absdiff(self._prev, gray)
        self._prev = gray
        _, mask = cv2.threshold(delta, self.threshold, 255, cv2.THRESH_BINARY)
        mask = cv2.dilate(mask, None, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best = 0
        box = None
        for contour in contours:
            area = int(cv2.contourArea(contour))
            if area > best:
                best = area
                box = tuple(int(v) for v in cv2.boundingRect(contour))
        if best >= self.min_area:
            return MotionEvent(True, best, box)
        return MotionEvent(False, best, None)
