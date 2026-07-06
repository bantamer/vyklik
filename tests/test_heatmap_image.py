import io
from types import SimpleNamespace

from PIL import Image

from vyklik.stats.heatmap_image import render_heatmap_png


def _r(dow: int, hour: int, wait: float | None, samples: int = 100) -> SimpleNamespace:
    return SimpleNamespace(dow=dow, hour=hour, est_wait_min=wait, samples=samples)


def test_none_without_usable_data():
    assert render_heatmap_png("Q", [], "ru") is None
    # a cell below the sample threshold doesn't count
    assert render_heatmap_png("Q", [_r(1, 8, 10, samples=5)], "ru") is None


def test_returns_a_png():
    png = render_heatmap_png("Q", [_r(1, 8, 10), _r(1, 9, 200), _r(2, 8, 100)], "ru")
    assert isinstance(png, bytes)
    img = Image.open(io.BytesIO(png))
    assert img.format == "PNG"
    assert img.width > 0 and img.height > 0


def test_equal_values_do_not_divide_by_zero():
    # lo == hi (span 0) must not blow up the frac calculation
    png = render_heatmap_png("Q", [_r(1, 8, 50), _r(2, 9, 50)], "pl")
    assert isinstance(png, bytes)


def test_renders_for_every_language():
    rows = [_r(1, 8, 10), _r(3, 12, 120)]
    for lang in ("pl", "ru", "be"):
        assert isinstance(render_heatmap_png("Q", rows, lang), bytes)
