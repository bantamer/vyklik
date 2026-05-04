from datetime import datetime, timezone

from vyklik.work_hours import is_working, parse_schedule


def test_parse_schedule_basic():
    s = parse_schedule("mon=8-16,tue=8-16,fri=9-17")
    assert s == {0: (8, 16), 1: (8, 16), 4: (9, 17)}


def test_parse_schedule_empty():
    assert parse_schedule("") == {}
    assert parse_schedule("   ") == {}


def test_parse_schedule_rejects_garbage():
    import pytest

    with pytest.raises(ValueError):
        parse_schedule("monday=8-16")


def test_is_working_inside_window():
    schedule = {0: (8, 16)}  # Mon 08:00–16:00 Warsaw
    # Mon 2026-05-04 10:00 UTC = 12:00 Warsaw (CEST, +2)
    assert is_working(datetime(2026, 5, 4, 10, 0, tzinfo=timezone.utc), schedule) is True


def test_is_working_outside_hours():
    schedule = {0: (8, 16)}
    # 06:00 UTC = 08:00 Warsaw — start is inclusive
    assert is_working(datetime(2026, 5, 4, 6, 0, tzinfo=timezone.utc), schedule) is True
    # 14:00 UTC = 16:00 Warsaw — end is exclusive
    assert is_working(datetime(2026, 5, 4, 14, 0, tzinfo=timezone.utc), schedule) is False


def test_is_working_off_day():
    schedule = {0: (8, 16)}  # only Monday
    # Tuesday
    assert is_working(datetime(2026, 5, 5, 10, 0, tzinfo=timezone.utc), schedule) is False
