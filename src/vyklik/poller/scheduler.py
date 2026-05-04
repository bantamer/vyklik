import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from vyklik.config import settings
from vyklik.db import session
from vyklik.duw_client import fetch_wroclaw
from vyklik.poller.ingest import ingest
from vyklik.queues_loader import QueueDisplay, load
from vyklik.work_hours import is_working, parse_schedule

log = logging.getLogger("vyklik.poller.scheduler")


async def _run_once(catalog: dict[int, QueueDisplay], schedule: dict[int, tuple[int, int]]) -> None:
    now = datetime.now(timezone.utc)
    if not is_working(now, schedule):
        log.debug("outside work hours, skipping poll")
        return
    try:
        snapshots = await fetch_wroclaw()
    except Exception as exc:
        log.warning("fetch failed: %s", exc)
        return
    try:
        async with session() as s:
            await ingest(s, snapshots, catalog)
            await s.commit()
    except Exception:
        log.exception("ingest failed")


async def run() -> None:
    catalog = load()
    schedule = parse_schedule(settings.work_hours)
    log.info(
        "poller starting: interval=%ss work_hours=%s curated_queues=%d",
        settings.poll_interval_seconds,
        settings.work_hours,
        len(catalog),
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _run_once,
        trigger=IntervalTrigger(seconds=settings.poll_interval_seconds),
        kwargs={"catalog": catalog, "schedule": schedule},
        next_run_time=datetime.now(timezone.utc),
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    finally:
        scheduler.shutdown(wait=False)
