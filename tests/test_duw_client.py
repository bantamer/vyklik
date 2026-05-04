import json
from pathlib import Path

from vyklik.duw_client import parse

FIXTURE = Path(__file__).parent / "fixtures" / "duw_response.json"


def test_parse_extracts_wroclaw_entries():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    snapshots = parse(payload)
    assert len(snapshots) == 3

    by_id = {s.id: s for s in snapshots}
    s14 = by_id[14]
    assert s14.raw_name.startswith("złożenie wniosku")
    assert s14.tickets_served == 84
    assert s14.ticket_value == "A084"
    assert s14.max_tickets == 150
    assert s14.tickets_left == 55
    assert s14.enabled is True
    assert s14.avg_wait == 2958
    assert s14.avg_service == 110


def test_parse_handles_missing_location():
    assert parse({"result": {"Other City": []}}) == []
    assert parse({}) == []
    assert parse({"result": {"Wrocław": None}}) == []


def test_parse_skips_malformed_entries_without_dropping_others():
    payload = {
        "result": {
            "Wrocław": [
                {"id": "not-a-number"},
                {
                    "id": 99,
                    "name": "ok",
                    "ticket_count": 1,
                    "tickets_served": 2,
                    "registered_tickets": 3,
                    "enabled": True,
                },
            ]
        }
    }
    snapshots = parse(payload)
    assert len(snapshots) == 1
    assert snapshots[0].id == 99
