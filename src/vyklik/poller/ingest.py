import json
import logging
from datetime import UTC, datetime

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from vyklik.duw_client import QueueSnapshot
from vyklik.models import Queue, Snapshot
from vyklik.poller.diff import Event, compute_events
from vyklik.queues_loader import QueueDisplay, display_for

NOTIFY_CHANNEL = "vyklik_events"
log = logging.getLogger("vyklik.poller.ingest")


async def upsert_queues(
    session: AsyncSession,
    snapshots: list[QueueSnapshot],
    catalog: dict[int, QueueDisplay],
) -> None:
    if not snapshots:
        return
    now = datetime.now(UTC)
    rows = []
    for s in snapshots:
        pl, ru = display_for(s.id, s.raw_name, catalog)
        rows.append(
            {
                "id": s.id,
                "raw_name": s.raw_name,
                "display_pl": pl,
                "display_ru": ru,
                "first_seen": now,
                "last_seen": now,
            }
        )
    stmt = pg_insert(Queue).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Queue.id],
        set_={
            "raw_name": stmt.excluded.raw_name,
            "display_pl": stmt.excluded.display_pl,
            "display_ru": stmt.excluded.display_ru,
            "last_seen": stmt.excluded.last_seen,
        },
    )
    await session.execute(stmt)


async def insert_snapshots(
    session: AsyncSession, snapshots: list[QueueSnapshot], ts: datetime
) -> None:
    if not snapshots:
        return
    rows = [
        {
            "queue_id": s.id,
            "ts": ts,
            "ticket_count": s.ticket_count,
            "tickets_served": s.tickets_served,
            "ticket_value": s.ticket_value,
            "registered_tickets": s.registered_tickets,
            "max_tickets": s.max_tickets,
            "tickets_left": s.tickets_left,
            "enabled": s.enabled,
            "avg_wait_api": s.avg_wait,
            "avg_service_api": s.avg_service,
        }
        for s in snapshots
    ]
    stmt = pg_insert(Snapshot).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=[Snapshot.queue_id, Snapshot.ts])
    await session.execute(stmt)


async def fetch_previous(session: AsyncSession, queue_ids: list[int]) -> dict[int, Snapshot]:
    """Most-recent snapshot per queue, BEFORE the one we just inserted.

    Done as a per-queue subselect so we can remain DB-portable; for our scale this is fine.
    """
    if not queue_ids:
        return {}
    out: dict[int, Snapshot] = {}
    for qid in queue_ids:
        stmt = (
            select(Snapshot).where(Snapshot.queue_id == qid).order_by(Snapshot.ts.desc()).limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is not None:
            out[qid] = row
    return out


async def emit_events(session: AsyncSession, events: list[Event]) -> None:
    if not events:
        return
    stmt = text("SELECT pg_notify(:ch, :payload)")
    for event in events:
        payload = json.dumps(
            {"type": event.type, "queue_id": event.queue_id, "payload": event.payload}
        )
        await session.execute(stmt, {"ch": NOTIFY_CHANNEL, "payload": payload})


async def ingest(
    session: AsyncSession,
    snapshots: list[QueueSnapshot],
    catalog: dict[int, QueueDisplay],
) -> list[Event]:
    """Run one ingest cycle. Caller commits."""
    if not snapshots:
        return []

    now = datetime.now(UTC)
    queue_ids = [s.id for s in snapshots]
    prev_map = await fetch_previous(session, queue_ids)

    await upsert_queues(session, snapshots, catalog)
    await insert_snapshots(session, snapshots, now)

    all_events: list[Event] = []
    for s in snapshots:
        all_events.extend(compute_events(prev_map.get(s.id), s, now))

    await emit_events(session, all_events)
    log.info(
        "ingested queues=%d events=%d (%s)",
        len(snapshots),
        len(all_events),
        ",".join(sorted({e.type for e in all_events})) or "no-change",
    )
    return all_events
