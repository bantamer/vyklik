from datetime import datetime
from types import SimpleNamespace

from vyklik.bot.format import dashboard_text

NOON = datetime(2026, 6, 29, 12, 0)


def _snap(enabled: bool = True, ticket_value: str = "K014") -> SimpleNamespace:
    return SimpleNamespace(enabled=enabled, ticket_value=ticket_value)


def test_dashboard_mixed():
    rows = [
        ("PDP", _snap(enabled=False), None, None),
        ("Karta — odbiór", _snap(ticket_value="K054"), "K090", 300.0),
        ("FAMI", _snap(ticket_value="C020"), None, None),
    ]
    out = dashboard_text(rows, "ru", NOON)
    assert "обновлено 12:00" in out
    # Closed for new tickets, but the current number is still shown.
    assert "🔴 PDP: <b>K014</b> · запись закрыта" in out
    assert "🟢 Karta — odbiór: <b>K054</b>" in out
    assert "впереди 36" in out  # 90 - 54
    assert "~4 ч 48 мин" in out  # 36 * 300 * 1.6 = 17280 s
    assert "🟢 FAMI: <b>C020</b>" in out


def test_dashboard_no_pace():
    rows = [("Q", _snap(ticket_value="K010"), "K020", None)]
    out = dashboard_text(rows, "ru", NOON)
    assert "впереди 10" in out
    assert "~" not in out  # no ETA without a pace


def test_dashboard_already_called():
    rows = [("Q", _snap(ticket_value="K025"), "K020", 60.0)]
    out = dashboard_text(rows, "ru", NOON)
    assert "✅" in out
    assert "впереди" not in out


def test_dashboard_different_series():
    rows = [("Q", _snap(ticket_value="K010"), "A020", 60.0)]
    out = dashboard_text(rows, "ru", NOON)
    assert "ваш A020" in out
    assert "впереди" not in out


def test_dashboard_no_snapshot():
    rows = [("Q", None, "K020", None)]
    out = dashboard_text(rows, "ru", NOON)
    assert "⚪ Q — нет данных" in out


def test_dashboard_closed_still_shows_position():
    # A "closed" queue keeps calling issued numbers, so a subscriber with a
    # ticket must still see the current number and how many are ahead.
    rows = [("Q", _snap(enabled=False, ticket_value="K010"), "K020", 60.0)]
    out = dashboard_text(rows, "ru", NOON)
    assert "🔴 Q: <b>K010</b> · запись закрыта" in out
    assert "впереди 10" in out
