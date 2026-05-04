from dataclasses import dataclass
from datetime import datetime

from vyklik.duw_client import QueueSnapshot
from vyklik.models import Snapshot


@dataclass(slots=True, frozen=True)
class Event:
    type: str  # ticket_called | queue_opened | slots_appeared
    queue_id: int
    payload: dict


def compute_events(prev: Snapshot | None, current: QueueSnapshot, now: datetime) -> list[Event]:
    """Decide what changed between two consecutive snapshots of the same queue."""
    if prev is None:
        return []  # baseline, nothing to alert on yet

    events: list[Event] = []

    if current.tickets_served > (prev.tickets_served or 0):
        events.append(
            Event(
                type="ticket_called",
                queue_id=current.id,
                payload={
                    "ticket_value": current.ticket_value,
                    "tickets_served": current.tickets_served,
                    "prev_served": prev.tickets_served,
                },
            )
        )

    if current.enabled and not prev.enabled:
        events.append(
            Event(
                type="queue_opened",
                queue_id=current.id,
                payload={"date": now.date().isoformat()},
            )
        )

    cur_left = current.tickets_left or 0
    prev_left = prev.tickets_left or 0
    if cur_left > 0 and prev_left == 0:
        events.append(
            Event(
                type="slots_appeared",
                queue_id=current.id,
                payload={
                    "tickets_left": cur_left,
                    "date": now.date().isoformat(),
                },
            )
        )

    return events
