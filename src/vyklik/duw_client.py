from dataclasses import dataclass

import httpx

from vyklik.config import settings

_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://rezerwacje.duw.pl/app/webroot/status_kolejek/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
    ),
}

LOCATION = "Wrocław"


@dataclass(slots=True, frozen=True)
class QueueSnapshot:
    id: int
    raw_name: str
    ticket_count: int
    tickets_served: int
    ticket_value: str | None
    registered_tickets: int
    max_tickets: int | None
    tickets_left: int | None
    enabled: bool
    avg_wait: int | None
    avg_service: int | None


def parse(payload: dict) -> list[QueueSnapshot]:
    """Pull Wrocław entries out of the DUW status payload."""
    out: list[QueueSnapshot] = []
    for entry in payload.get("result", {}).get(LOCATION, []) or []:
        try:
            out.append(
                QueueSnapshot(
                    id=int(entry["id"]),
                    raw_name=str(entry.get("name", "")).strip() or f"queue {entry['id']}",
                    ticket_count=int(entry.get("ticket_count") or 0),
                    tickets_served=int(entry.get("tickets_served") or 0),
                    ticket_value=(entry.get("ticket_value") or None),
                    registered_tickets=int(entry.get("registered_tickets") or 0),
                    max_tickets=_int_or_none(entry.get("max_tickets")),
                    tickets_left=_int_or_none(entry.get("tickets_left")),
                    enabled=bool(entry.get("enabled", False)),
                    avg_wait=_int_or_none(entry.get("average_wait_time")),
                    avg_service=_int_or_none(entry.get("average_service_time")),
                )
            )
        except (KeyError, TypeError, ValueError):
            # Skip malformed rows; we do not want one bad entry to nuke a poll.
            continue
    return out


def _int_or_none(v: object) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


async def fetch_wroclaw() -> list[QueueSnapshot]:
    verify = not settings.insecure_tls
    async with httpx.AsyncClient(headers=_HEADERS, timeout=20.0, verify=verify) as client:
        resp = await client.get(settings.duw_status_url)
        resp.raise_for_status()
        return parse(resp.json())
