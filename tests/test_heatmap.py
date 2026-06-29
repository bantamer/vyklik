from types import SimpleNamespace

from vyklik.stats.heatmap import render_heatmap


def _r(dow: int, hour: int, wait: float | None, samples: int = 100) -> SimpleNamespace:
    return SimpleNamespace(dow=dow, hour=hour, est_wait_min=wait, samples=samples)


def test_no_data_when_empty():
    assert "недостаточно данных" in render_heatmap("Q", [], "ru")


def test_low_sample_cells_ignored():
    out = render_heatmap("Q", [_r(1, 8, 10, samples=5)], "ru")
    assert "недостаточно данных" in out


def test_colours_and_advice():
    rows = [
        _r(1, 8, 10),  # quietest -> green
        _r(1, 9, 200),  # busiest -> red
        _r(2, 8, 100),  # mid -> yellow
    ]
    out = render_heatmap("Q", rows, "ru")
    assert "🟩" in out and "🟨" in out and "🟥" in out
    assert "⬜" in out  # most of the grid has no data
    assert "Меньше всего ждать: Пн 08:00 (~10 мин)" in out
    assert "Дольше всего: Пн 09:00 (~3 ч 20 мин)" in out


def test_grid_has_all_weekday_rows():
    out = render_heatmap("Q", [_r(1, 8, 10)], "ru")
    for day in ("Пн", "Вт", "Ср", "Чт", "Пт"):
        assert day in out


def test_polish_labels():
    out = render_heatmap("Q", [_r(1, 8, 10)], "pl")
    assert "Pn" in out and "Najkrócej" in out
