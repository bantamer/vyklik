"""Render the weekday×hour heatmap + a one-line recommendation.

Pure functions over rows from ``queue_hourly_stats`` (duck-typed: anything with
``dow``, ``hour``, ``est_wait_min``, ``samples``), so it's unit-testable without
a database.
"""

from typing import Protocol

from vyklik.i18n import t

# Office hours we render: Mon–Fri (Postgres dow 1..5), 08:00–15:00.
DOWS = [1, 2, 3, 4, 5]
HOURS = list(range(8, 16))
# A cell needs at least this many snapshots before we trust/colour it.
MIN_SAMPLES = 30


class HourStatLike(Protocol):
    dow: int
    hour: int
    est_wait_min: float | None
    samples: int


def _fmt_minutes(minutes: float) -> str:
    m = int(round(minutes))
    if m < 60:
        return f"{m} min"
    h, rem = divmod(m, 60)
    return f"{h} h {rem} min" if rem else f"{h} h"


def _colour(value: float, lo: float, hi: float) -> str:
    if hi <= lo:
        return "🟩"
    frac = (value - lo) / (hi - lo)
    if frac < 1 / 3:
        return "🟩"
    if frac < 2 / 3:
        return "🟨"
    return "🟥"


def render_heatmap(name: str, rows: list[HourStatLike], lang: str) -> str:
    by_cell = {(r.dow, r.hour): r for r in rows}
    usable = [
        r
        for r in rows
        if r.dow in DOWS
        and r.hour in HOURS
        and r.samples >= MIN_SAMPLES
        and r.est_wait_min is not None
    ]
    if not usable:
        return t("heatmap_no_data", lang=lang, name=name)

    waits = [r.est_wait_min for r in usable]
    lo, hi = min(waits), max(waits)

    lines = [t("heatmap_title", lang=lang, name=name)]
    for dow in DOWS:
        cells = []
        for hour in HOURS:
            r = by_cell.get((dow, hour))
            if r is None or r.samples < MIN_SAMPLES or r.est_wait_min is None:
                cells.append("⬜")
            else:
                cells.append(_colour(r.est_wait_min, lo, hi))
        lines.append(t(f"dow_{dow}", lang=lang) + " " + "".join(cells))
    lines.append(t("heatmap_legend", lang=lang))

    quiet = min(usable, key=lambda r: r.est_wait_min)
    busy = max(usable, key=lambda r: r.est_wait_min)
    lines.append(
        t(
            "heatmap_advice",
            lang=lang,
            quiet_day=t(f"dow_{quiet.dow}", lang=lang),
            quiet_h=f"{quiet.hour:02d}:00",
            quiet_w=_fmt_minutes(quiet.est_wait_min),
            busy_day=t(f"dow_{busy.dow}", lang=lang),
            busy_h=f"{busy.hour:02d}:00",
            busy_w=_fmt_minutes(busy.est_wait_min),
        )
    )
    return "\n".join(lines)
