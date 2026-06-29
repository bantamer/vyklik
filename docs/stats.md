# Stats & wait-time estimation

How vyklik turns raw DUW snapshots into useful numbers, and why we don't trust
the wait/service figures DUW hands us.

## What we learned about the DUW data

Validated against ~8 weeks of prod snapshots (23 queues, 30 s granularity):

- **`average_wait_time` is backward-looking and under-reports.** It's the mean
  realized wait `(called − registered)` of recently served tickets, so it climbs
  through the day and *lags* reality while the queue grows. Reconstructed realized
  wait correlates with it at **0.96**, but is consistently higher (e.g. 234 min
  actual vs 165 min reported on one queue). This is the "they said 1 h, I sat 2 h"
  effect.
- **`average_service_time` ignores idle.** It measures only hands-on time at a
  window (e.g. 107–252 s). Our observed inter-service interval (`Δtime ÷ Δserved`)
  is ~260–370 s — the gap between calls is longer than one service because windows
  aren't serving back-to-back. The effective interval is the honest number.
- **Cumulative counters reset overnight.** `tickets_served` starts ~0 each morning
  and grows to ~150–190; resets happen between close and open, never mid-hour, so
  deltas bucketed within `(date, hour)` are clean. Prefer `tickets_served` over
  `registered_tickets` (the latter carries the pre-opening crowd that grabs tickets
  in the gaps between our polls — there is **no** online pre-registration).
- **Units:** `average_wait_time` / `average_service_time` are in **seconds**.
- **Multi-hour waits are normal** for DUW — they are not outliers to filter out.

Takeaway: estimate wait from *our own observed throughput*, forward-looking, not
from DUW's `average_wait_time`.

## Feature B — live "when will I be called" (shipped)

Per-ticket ETA shown in the queue card (when a ticket is set and the queue is
open) and appended to the `alert_n_before` proactive alert.

**Model** (`src/vyklik/stats/eta.py`, pure functions):

```
people_ahead = my_number − now_serving_number        (tickets.distance)
pace         = Δtime ÷ Δ(tickets_served)  over last 120 min, same day
eta_low      = people_ahead × pace                   (current pace holds)
eta_high     = people_ahead × pace × 1.6             (pace slows: lunch, closures)
called_at    = now + eta_low … now + eta_high        (Europe/Warsaw)
```

- `compute_pace` returns `None` if <3 served in the window or the counter went
  backwards (reset inside the window) — then the card shows "pace not known yet".
- End-of-day guard: if even `eta_low` lands past closing, warn "may not be called
  today" (uses `WORK_HOURS`).
- Series guard: if the user's ticket prefix differs from the one being called,
  no estimate (can't compare).

**Files:** `stats/eta.py` (math), `bot/repo.recent_snapshots` (pace samples),
`bot/format.eta_text` / `eta_suffix` (rendering), `bot/handlers/queues.py` (card),
`bot/notifier.py` (alert), `i18n/*` strings, `tests/test_eta.py`.

## Feature A — "when is it best to come" heatmap (shipped)

> Built as described below. `/stats` (or the 📊 button on a queue card) renders a
> Mon–Fri × 08–15 emoji grid normalized per queue, with a quietest/busiest advice
> line. Data comes from the `queue_hourly_stats` matview, refreshed nightly at
> 21:00 Europe/Warsaw by an APScheduler job in the poller.
>
> Known refinement (see open questions): the "quietest" pick can land on the last
> slot before closing (shortest wait, but tickets may be gone) — weighting by
> ticket availability is still phase 2.

A weekday × hour heatmap per queue plus a one-line recommendation, computed from
the same throughput model aggregated over history.

### Data layer — materialized view `queue_hourly_stats`

Aggregate snapshots by `(queue_id, dow, hour)` over a **trailing 8–12 week window**
(older data drifts as staffing/schedule change):

| column | meaning |
|---|---|
| `queue_id, dow, hour` | bucket key (dow 0–6, hour within office hours) |
| `samples` | snapshot count in the bucket — hide cells below a threshold |
| `avg_queue` | mean `ticket_count` (people waiting) |
| `served_rate` | throughput: per-`(date,hour)` `Δtickets_served` (guard `GREATEST(…,0)` for resets), averaged across days |
| `avg_service_sec` | mean `avg_service_api` where present — cross-check only |
| `est_wait_min` | `avg_queue ÷ (served_rate / 60)` — our forward-looking wait |

Unique index on `(queue_id, dow, hour)` so refresh can run `CONCURRENTLY`.

### Refresh

- Daily APScheduler job in the **poller** (it already owns the scheduler and is the
  only writer; the bot stays read-only), ~21:00 local after queues close.
- `REFRESH MATERIALIZED VIEW CONCURRENTLY queue_hourly_stats` (no read lock).
- Initial populate right after the migration / first poller boot.
- Slow-moving data → daily is enough; hourly is a cheap option if wanted.

### Rendering (`src/vyklik/stats/render.py`)

- 5×8 grid of 🟩/🟨/🟥, normalized **per queue** (relative to that queue's own
  min/max `est_wait_min`), weekday labels from i18n.
- Advice line: quietest and busiest slots, e.g. "quietest: Tue/Thu 8–9 (~10 min);
  busiest: Mon 11–13 (~2 h)".
- Pure function over matview rows → golden-fixture testable.

### Surface

- `/stats` command + a "📊 Stats" button on the queue card; pick a queue → grid +
  advice. Reuses the existing queue keyboard.

### Synergy with Feature B

The live ETA falls back to this matview's `served_rate` for the current
`(dow, hour)` when the live pace is unavailable (right after opening, or low
volume). A feeds B's fallback; B is the live read.

### Open questions / phase 2

- Exclude public holidays from the aggregate.
- Weight "best time" by ticket availability (`max_tickets` / `tickets_left`): a
  short queue late in the day is useless if tickets already ran out.
- `avg_service_api` is only ~56% populated — keep it as a cross-check, not primary.

## Roadmap

Product feature requests (refresh button, pinned live dashboard, …) live in
[roadmap.md](roadmap.md).
