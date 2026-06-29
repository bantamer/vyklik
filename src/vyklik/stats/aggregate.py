"""Read/refresh the queue_hourly_stats materialized view (heatmap data)."""

import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from vyklik.db import asyncpg_connect

log = logging.getLogger("vyklik.stats.aggregate")

# CONCURRENTLY keeps reads unblocked during the refresh; it needs the unique
# index created in the migration and must run outside a transaction (asyncpg
# autocommits a bare execute), hence a dedicated raw connection.
REFRESH_SQL = "REFRESH MATERIALIZED VIEW CONCURRENTLY queue_hourly_stats"


@dataclass(frozen=True)
class HourStat:
    dow: int  # Postgres EXTRACT(dow): 0=Sunday .. 6=Saturday
    hour: int
    avg_queue: float | None
    est_wait_min: float | None
    samples: int


async def refresh_heatmap() -> None:
    conn = await asyncpg_connect()
    try:
        await conn.execute(REFRESH_SQL)
    finally:
        await conn.close()


async def fetch_queue_heatmap(session: AsyncSession, queue_id: int) -> list[HourStat]:
    stmt = text(
        "SELECT dow, hour, avg_queue, est_wait_min, samples "
        "FROM queue_hourly_stats WHERE queue_id = :qid ORDER BY dow, hour"
    )
    result = await session.execute(stmt, {"qid": queue_id})
    return [
        HourStat(
            dow=row.dow,
            hour=row.hour,
            avg_queue=float(row.avg_queue) if row.avg_queue is not None else None,
            est_wait_min=float(row.est_wait_min) if row.est_wait_min is not None else None,
            samples=row.samples,
        )
        for row in result
    ]
