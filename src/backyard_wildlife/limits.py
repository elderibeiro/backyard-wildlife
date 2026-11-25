"""Cooldown and daily-cap checks."""

from __future__ import annotations

from backyard_wildlife.store import VisitStore


class LimitDecision:
    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason

    def __bool__(self) -> bool:
        return self.allowed


def check_limits(store: VisitStore, camera: str, cooldown_seconds: int, daily_cap: int) -> LimitDecision:
    used = store.calls_today()
    if used >= daily_cap:
        return LimitDecision(False, f"daily cap reached ({used}/{daily_cap})")
    elapsed = store.seconds_since_last_call(camera)
    if elapsed is not None and elapsed < cooldown_seconds:
        wait = int(cooldown_seconds - elapsed)
        return LimitDecision(False, f"cooldown ({wait}s remaining for {camera})")
    return LimitDecision(True, "")
