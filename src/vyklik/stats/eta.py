"""Live "when will I be called" estimate.

We don't trust DUW's ``average_wait_time`` — it's a backward-looking mean of
already-served tickets, so it lags (and under-reports) while the queue grows.
Instead we measure the *current* serving pace from our own snapshot history
(how fast ``tickets_served`` advances) and project it forward over the number
of people still ahead of the user's ticket.

Pure functions only — no I/O, so the math is unit-testable.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

# How far back to look for the live serving pace.
PACE_WINDOW_MINUTES = 120
# Need at least this many tickets served in the window before the pace is
# meaningful — two or three serves is too noisy to extrapolate from.
PACE_MIN_SERVED = 3
# Reality skews slower than the recent pace (lunch, windows closing), so the
# upper bound of the estimate stretches the observed pace by this factor.
SLOW_FACTOR = 1.6


def compute_pace(
    samples: list[tuple[datetime, int]], *, min_served: int = PACE_MIN_SERVED
) -> float | None:
    """Seconds between consecutive calls, from recent (ts, tickets_served) samples.

    Returns ``None`` when there isn't enough movement to extrapolate, or when
    the cumulative counter went backwards — meaning a daily reset fell inside
    the window and the delta would be garbage.
    """
    if len(samples) < 2:
        return None
    ordered = sorted(samples, key=lambda s: s[0])
    first_ts, first_served = ordered[0]
    last_ts, last_served = ordered[-1]
    served = last_served - first_served
    if served < min_served:
        return None
    span = (last_ts - first_ts).total_seconds()
    if span <= 0:
        return None
    return span / served


@dataclass(frozen=True)
class Eta:
    people_ahead: int
    pace_seconds: float | None
    low_seconds: int | None  # optimistic: current pace holds
    high_seconds: int | None  # pessimistic: pace slows down
    eta_at_low: datetime | None  # earliest expected call time (local tz)
    eta_at_high: datetime | None  # latest expected call time (local tz)
    already_called: bool  # the called number reached or passed the user's
    today_unlikely: bool  # even the optimistic call time is past closing


def estimate_eta(
    people_ahead: int,
    pace_seconds: float | None,
    *,
    now_local: datetime,
    closing: datetime | None,
    slow_factor: float = SLOW_FACTOR,
) -> Eta:
    """Project the serving pace forward over the people still ahead."""
    if people_ahead <= 0:
        return Eta(people_ahead, pace_seconds, 0, 0, now_local, now_local, True, False)
    if pace_seconds is None:
        return Eta(people_ahead, None, None, None, None, None, False, False)
    low = round(people_ahead * pace_seconds)
    high = round(people_ahead * pace_seconds * slow_factor)
    at_low = now_local + timedelta(seconds=low)
    at_high = now_local + timedelta(seconds=high)
    today_unlikely = closing is not None and at_low > closing
    return Eta(people_ahead, pace_seconds, low, high, at_low, at_high, False, today_unlikely)
