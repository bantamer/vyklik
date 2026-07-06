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


def _fmt_minutes(minutes: float, lang: str) -> str:
    m = int(round(minutes))
    if m < 60:
        return f"{m} {t('dur_min', lang=lang)}"
    h, rem = divmod(m, 60)
    if rem:
        return f"{h} {t('dur_h', lang=lang)} {rem} {t('dur_min', lang=lang)}"
    return f"{h} {t('dur_h', lang=lang)}"


# Wait-time buckets, shared by the text grid and the PNG renderer so both colour
# a cell identically.
BUCKET_LOW = "low"
BUCKET_MID = "mid"
BUCKET_HIGH = "high"


def bucket(value: float, lo: float, hi: float) -> str:
    """Which third of the [lo, hi] wait-time range a value falls in."""
    if hi <= lo:
        return BUCKET_LOW
    frac = (value - lo) / (hi - lo)
    if frac < 1 / 3:
        return BUCKET_LOW
    if frac < 2 / 3:
        return BUCKET_MID
    return BUCKET_HIGH


_BUCKET_EMOJI = {BUCKET_LOW: "🟩", BUCKET_MID: "🟨", BUCKET_HIGH: "🟥"}


def _colour(value: float, lo: float, hi: float) -> str:
    return _BUCKET_EMOJI[bucket(value, lo, hi)]


def usable_cells(rows: list[HourStatLike]) -> list[HourStatLike]:
    """Cells inside office hours with enough samples and a wait estimate."""
    return [
        r
        for r in rows
        if r.dow in DOWS
        and r.hour in HOURS
        and r.samples >= MIN_SAMPLES
        and r.est_wait_min is not None
    ]


def advice_line(rows: list[HourStatLike], lang: str) -> str | None:
    """The "quietest / busiest slot" recommendation, or None without data."""
    usable = usable_cells(rows)
    if not usable:
        return None
    quiet = min(usable, key=lambda r: r.est_wait_min)
    busy = max(usable, key=lambda r: r.est_wait_min)
    return t(
        "heatmap_advice",
        lang=lang,
        quiet_day=t(f"dow_{quiet.dow}", lang=lang),
        quiet_h=f"{quiet.hour:02d}:00",
        quiet_w=_fmt_minutes(quiet.est_wait_min, lang),
        busy_day=t(f"dow_{busy.dow}", lang=lang),
        busy_h=f"{busy.hour:02d}:00",
        busy_w=_fmt_minutes(busy.est_wait_min, lang),
    )


def render_heatmap(name: str, rows: list[HourStatLike], lang: str) -> str:
    by_cell = {(r.dow, r.hour): r for r in rows}
    usable = usable_cells(rows)
    if not usable:
        return t("heatmap_no_data", lang=lang, name=name)

    waits = [r.est_wait_min for r in usable]
    lo, hi = min(waits), max(waits)

    # Grid goes in a <pre> block so the weekday labels are monospace and the
    # columns line up; the hour header (08..15) sits above, cells spaced to
    # match its two-digit width.
    grid = ["   " + " ".join(f"{h:02d}" for h in HOURS)]
    for dow in DOWS:
        cells = []
        for hour in HOURS:
            r = by_cell.get((dow, hour))
            if r is None or r.samples < MIN_SAMPLES or r.est_wait_min is None:
                cells.append("⬜")
            else:
                cells.append(_colour(r.est_wait_min, lo, hi))
        grid.append(f"{t(f'dow_{dow}', lang=lang)} " + " ".join(cells))
    block = "<pre>" + "\n".join(grid) + "</pre>"

    return "\n".join(
        [
            t("heatmap_title", lang=lang, name=name),
            block,
            "",
            t("heatmap_legend", lang=lang),
            "",
            advice_line(rows, lang) or "",
        ]
    )
