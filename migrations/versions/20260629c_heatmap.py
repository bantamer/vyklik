"""queue_hourly_stats materialized view (heatmap)

Revision ID: 20260629c_heatmap
Revises: 20260629b_every_call
Create Date: 2026-06-29

Aggregates snapshots by (queue_id, weekday, hour) over a trailing window so the
bot can show a "when is it quietest" heatmap. Wait time is estimated from our own
observed throughput (delta of tickets_served within each day-hour, guarded against
the overnight counter reset), not DUW's optimistic average_wait_time.

dow follows Postgres EXTRACT(dow): 0=Sunday .. 6=Saturday. Times are bucketed in
Europe/Warsaw so the hours line up with office hours.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "20260629c_heatmap"
down_revision: str | None = "20260629b_every_call"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Trailing window: recent enough to reflect current staffing, long enough for
# every weekday/hour bucket to have several days of data.
WINDOW_DAYS = 84

CREATE_SQL = f"""
CREATE MATERIALIZED VIEW queue_hourly_stats AS
WITH hourly AS (
    SELECT
        queue_id,
        (ts AT TIME ZONE 'Europe/Warsaw')::date            AS d,
        EXTRACT(dow  FROM ts AT TIME ZONE 'Europe/Warsaw')::int AS dow,
        EXTRACT(hour FROM ts AT TIME ZONE 'Europe/Warsaw')::int AS hour,
        sum(ticket_count)                                  AS sum_tc,
        count(*)                                           AS samples,
        GREATEST(max(tickets_served) - min(tickets_served), 0) AS served
    FROM snapshots
    WHERE ts >= now() - interval '{WINDOW_DAYS} days'
      AND enabled
    GROUP BY queue_id, d, dow, hour
)
SELECT
    queue_id,
    dow,
    hour,
    sum(samples)                                           AS samples,
    sum(sum_tc)::numeric / NULLIF(sum(samples), 0)         AS avg_queue,
    avg(served)                                            AS served_rate,
    CASE WHEN avg(served) > 0
         THEN (sum(sum_tc)::numeric / NULLIF(sum(samples), 0)) / (avg(served) / 60.0)
         ELSE NULL END                                     AS est_wait_min
FROM hourly
GROUP BY queue_id, dow, hour
WITH DATA
"""


def upgrade() -> None:
    op.execute(CREATE_SQL)
    # Unique index is required for REFRESH MATERIALIZED VIEW CONCURRENTLY.
    op.execute(
        "CREATE UNIQUE INDEX ix_queue_hourly_stats_key "
        "ON queue_hourly_stats (queue_id, dow, hour)"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS queue_hourly_stats")
