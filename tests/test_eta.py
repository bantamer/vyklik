from datetime import UTC, datetime, timedelta

from vyklik.stats.eta import compute_pace, estimate_eta

T0 = datetime(2026, 6, 29, 10, 0, tzinfo=UTC)


def _samples(points: list[tuple[int, int]]) -> list[tuple[datetime, int]]:
    """(minutes_after_T0, tickets_served) -> snapshot sample tuples."""
    return [(T0 + timedelta(minutes=m), served) for m, served in points]


# --- compute_pace -----------------------------------------------------------


def test_pace_basic():
    # 10 served over 60 min -> 6 min (360 s) per person
    pace = compute_pace(_samples([(0, 100), (60, 110)]))
    assert pace == 360.0


def test_pace_unordered_input():
    pace = compute_pace(_samples([(60, 110), (0, 100), (30, 105)]))
    assert pace == 360.0


def test_pace_none_when_too_few_served():
    assert compute_pace(_samples([(0, 100), (60, 102)])) is None


def test_pace_none_on_counter_reset():
    # cumulative counter went backwards (overnight reset inside the window)
    assert compute_pace(_samples([(0, 180), (60, 5)])) is None


def test_pace_none_with_single_sample():
    assert compute_pace(_samples([(0, 100)])) is None


# --- estimate_eta -----------------------------------------------------------

NOON = datetime(2026, 6, 29, 12, 0, tzinfo=UTC)
CLOSING = datetime(2026, 6, 29, 16, 0, tzinfo=UTC)


def test_eta_range_and_clock():
    # 10 ahead, 60 s/person -> low 600 s (10 min), high 960 s (16 min, x1.6)
    est = estimate_eta(10, 60.0, now_local=NOON, closing=CLOSING)
    assert est.low_seconds == 600
    assert est.high_seconds == 960
    assert est.eta_at_low == NOON + timedelta(seconds=600)
    assert est.eta_at_high == NOON + timedelta(seconds=960)
    assert not est.already_called
    assert not est.today_unlikely


def test_eta_already_called():
    est = estimate_eta(0, 60.0, now_local=NOON, closing=CLOSING)
    assert est.already_called
    est_passed = estimate_eta(-3, 60.0, now_local=NOON, closing=CLOSING)
    assert est_passed.already_called


def test_eta_no_pace():
    est = estimate_eta(10, None, now_local=NOON, closing=CLOSING)
    assert est.pace_seconds is None
    assert est.low_seconds is None
    assert not est.already_called


def test_eta_today_unlikely():
    # 100 ahead at 5 min/person = 500 min ~ 8 h, well past 16:00 closing
    est = estimate_eta(100, 300.0, now_local=NOON, closing=CLOSING)
    assert est.today_unlikely


def test_eta_no_closing_guard():
    est = estimate_eta(100, 300.0, now_local=NOON, closing=None)
    assert not est.today_unlikely
