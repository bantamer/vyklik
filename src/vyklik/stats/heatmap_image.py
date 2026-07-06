"""Render the weekday×hour wait-time heatmap as a PNG, for `sendPhoto`.

The text grid can't align emoji cells under an ASCII hour header, so the image
path draws real cells instead: each cell is coloured on a continuous
green→amber→red scale by its estimated wait, with the wait (in minutes) printed
on it. Pure function over the same duck-typed rows as `heatmap.render_heatmap`
(``dow``, ``hour``, ``est_wait_min``, ``samples``).

Returns PNG bytes, or ``None`` when no cell has enough data to colour — the
caller then falls back to the ``heatmap_no_data`` text.
"""

import io
from functools import lru_cache
from importlib.resources import files

from PIL import Image, ImageDraw, ImageFont

from vyklik.i18n import t
from vyklik.stats.heatmap import DOWS, HOURS, MIN_SAMPLES, HourStatLike

_FONT_FILE = str(files("vyklik.stats").joinpath("fonts", "DejaVuSans.ttf"))

# Rendered at 2× for crisp text on high-DPI screens; Telegram downscales.
_S = 2

# Layout (logical px, before ×_S).
_PAD = 26
_LABEL_W = 46  # weekday-label column
_HEADER_H = 34  # hour-label row
_CELL = 62
_GAP = 7
_TITLE_H = 52
_LEGEND_H = 46
_LEGEND_GAP = 26  # breathing room between the grid and the legend

# Palette.
_BG = (15, 23, 42)  # slate-900 card
_INK = (226, 232, 240)  # slate-200 text
_MUTED = (100, 116, 139)  # slate-500
_EMPTY = (30, 41, 59)  # slate-800 cell with no data
_GREEN = (34, 197, 94)
_AMBER = (245, 158, 11)
_RED = (239, 68, 68)


@lru_cache(maxsize=8)
def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_FONT_FILE, size * _S)


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], f: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(3))  # type: ignore[return-value]


def _heat(frac: float) -> tuple[int, int, int]:
    """Green (short wait) → amber → red (long wait), frac clamped to [0, 1]."""
    frac = max(0.0, min(1.0, frac))
    if frac < 0.5:
        return _lerp(_GREEN, _AMBER, frac / 0.5)
    return _lerp(_AMBER, _RED, (frac - 0.5) / 0.5)


def _text_on(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Black or white, whichever reads better on the given cell colour."""
    luma = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return (17, 24, 39) if luma > 150 else (255, 255, 255)


def _cell_label(minutes: float, lang: str) -> str:
    """Wait time as a compact, localized duration: "45м" / "1ч30м" / "2ч"."""
    m = int(round(minutes))
    min_u = t("dur_min_c", lang=lang)
    if m < 60:
        return f"{m}{min_u}"
    h, mm = divmod(m, 60)
    h_u = t("dur_h_c", lang=lang)
    return f"{h}{h_u}" if mm == 0 else f"{h}{h_u}{mm:02d}{min_u}"


def _centered(draw: ImageDraw.ImageDraw, box, text, font, fill) -> None:
    x0, y0, x1, y1 = box
    bx0, by0, bx1, by1 = draw.textbbox((0, 0), text, font=font)
    tw, th = bx1 - bx0, by1 - by0
    draw.text(
        (x0 + (x1 - x0 - tw) / 2 - bx0, y0 + (y1 - y0 - th) / 2 - by0),
        text,
        font=font,
        fill=fill,
    )


def render_heatmap_png(name: str, rows: list[HourStatLike], lang: str) -> bytes | None:
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
        return None

    waits = [r.est_wait_min for r in usable]
    lo, hi = min(waits), max(waits)
    span = hi - lo

    grid_w = len(HOURS) * _CELL + (len(HOURS) - 1) * _GAP
    grid_h = len(DOWS) * _CELL + (len(DOWS) - 1) * _GAP
    w = _PAD + _LABEL_W + grid_w + _PAD
    h = _PAD + _TITLE_H + _HEADER_H + grid_h + _LEGEND_GAP + _LEGEND_H + _PAD

    img = Image.new("RGB", (w * _S, h * _S), _BG)
    d = ImageDraw.Draw(img)

    def px(v: float) -> int:
        return round(v * _S)

    # Title.
    d.text((px(_PAD), px(_PAD)), name, font=_font(24), fill=_INK)

    grid_x = _PAD + _LABEL_W
    grid_y = _PAD + _TITLE_H + _HEADER_H

    # Hour headers.
    for c, hour in enumerate(HOURS):
        cx = grid_x + c * (_CELL + _GAP)
        _centered(
            d,
            (px(cx), px(_PAD + _TITLE_H), px(cx + _CELL), px(grid_y)),
            f"{hour:02d}",
            _font(15),
            _MUTED,
        )

    # Weekday rows + cells.
    for r_i, dow in enumerate(DOWS):
        cy = grid_y + r_i * (_CELL + _GAP)
        _centered(
            d,
            (px(_PAD), px(cy), px(grid_x - _GAP), px(cy + _CELL)),
            t(f"dow_{dow}", lang=lang),
            _font(15),
            _INK,
        )
        for c, hour in enumerate(HOURS):
            cx = grid_x + c * (_CELL + _GAP)
            box = (px(cx), px(cy), px(cx + _CELL), px(cy + _CELL))
            r = by_cell.get((dow, hour))
            if r is None or r.samples < MIN_SAMPLES or r.est_wait_min is None:
                d.rounded_rectangle(box, radius=10 * _S, fill=_EMPTY)
                continue
            frac = 0.0 if span <= 0 else (r.est_wait_min - lo) / span
            colour = _heat(frac)
            d.rounded_rectangle(box, radius=10 * _S, fill=colour)
            _centered(d, box, _cell_label(r.est_wait_min, lang), _font(15), _text_on(colour))

    # Legend: short → long swatches + the "minutes" hint.
    ly = h - _PAD - _LEGEND_H
    lx = _PAD
    d.text((px(lx), px(ly + 6)), t("heatmap_legend_short", lang=lang), font=_font(14), fill=_MUTED)
    lx += 4 + _measure(d, t("heatmap_legend_short", lang=lang), 14)
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        d.rounded_rectangle(
            (px(lx), px(ly), px(lx + 26), px(ly + 26)), radius=6 * _S, fill=_heat(frac)
        )
        lx += 30
    lx += 4
    d.text((px(lx), px(ly + 6)), t("heatmap_legend_long", lang=lang), font=_font(14), fill=_MUTED)

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def _measure(d: ImageDraw.ImageDraw, text: str, size: int) -> int:
    bx0, _, bx1, _ = d.textbbox((0, 0), text, font=_font(size))
    return round((bx1 - bx0) / _S)
