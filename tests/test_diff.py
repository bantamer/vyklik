from datetime import UTC, datetime
from types import SimpleNamespace

from vyklik.duw_client import QueueSnapshot
from vyklik.poller.diff import compute_events

NOW = datetime(2026, 5, 4, 12, 0, tzinfo=UTC)


def _q(**overrides) -> QueueSnapshot:
    base = dict(
        id=20,
        raw_name="UE /zaproszenia/PDP",
        ticket_count=10,
        tickets_served=20,
        ticket_value="G021",
        registered_tickets=30,
        max_tickets=45,
        tickets_left=15,
        enabled=True,
        avg_wait=300,
        avg_service=120,
    )
    base.update(overrides)
    return QueueSnapshot(**base)


def _prev(**overrides):
    base = dict(
        tickets_served=20,
        ticket_value="G021",
        enabled=True,
        tickets_left=15,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_baseline_emits_no_events():
    assert compute_events(None, _q(), NOW) == []


def test_no_change_emits_nothing():
    assert compute_events(_prev(), _q(), NOW) == []


def test_ticket_called_when_served_increments():
    events = compute_events(_prev(tickets_served=19), _q(tickets_served=20), NOW)
    assert [e.type for e in events] == ["ticket_called"]
    assert events[0].payload["tickets_served"] == 20
    assert events[0].payload["prev_served"] == 19


def test_queue_opened_when_enabled_flips_true():
    events = compute_events(_prev(enabled=False), _q(enabled=True), NOW)
    assert "queue_opened" in [e.type for e in events]


def test_slots_appeared_when_left_goes_above_zero():
    events = compute_events(_prev(tickets_left=0), _q(tickets_left=5), NOW)
    assert "slots_appeared" in [e.type for e in events]


def test_slots_not_emitted_when_already_positive():
    events = compute_events(_prev(tickets_left=3), _q(tickets_left=5), NOW)
    assert "slots_appeared" not in [e.type for e in events]


def test_multiple_events_can_fire_together():
    prev = _prev(tickets_served=18, enabled=False, tickets_left=0)
    cur = _q(tickets_served=20, enabled=True, tickets_left=5)
    types = {e.type for e in compute_events(prev, cur, NOW)}
    assert types == {"ticket_called", "queue_opened", "slots_appeared"}
