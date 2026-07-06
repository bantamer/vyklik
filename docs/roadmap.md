# Roadmap

Requested product features, with implementation sketches. Stats/wait-time work
lives in [stats.md](stats.md).

> **Status:** features 1 and 2 are **shipped** (the sketches below describe what
> was built). Section 3 is open.

## 1. Refresh button on the queue card (quick win) — shipped

**Pain:** getting fresh info means re-running `/mysubs` (or going back + re-tapping),
which posts a brand-new message each time instead of updating in place.

**Do:**
- Add a `🔄 Refresh` button to `keyboards.queue_card`, `callback_data=f"q:{queue.id}"`
  — it already routes to `cb_queue_card`, which edits the message in place.
- Add an "updated at HH:MM" (Europe/Warsaw) footer line to the card text, so a
  re-render always differs and the `editMessageText` isn't rejected with
  `message is not modified`. Bonus: makes freshness explicit.

**Effort:** tiny. No schema change.

## 2. Pinned live dashboard of all subscriptions — shipped

**Pain:** to see the status of every queue at a glance you have to open each card.

**Idea:** one message the bot keeps up to date and pins, e.g.

```
📌 My queues · updated 10:17
🔴 PDP — closed
🟢 Karta pobytu — odbiór: K054 · your K090 · 36 ahead · ~3 h
```

**Telegram mechanics** (this is the "special functionality"):
- `editMessageText` — a bot can edit its own message anytime, with no time limit
  and no notification → silent live updates.
- `pinChatMessage` (with `disable_notification`) — works in private chats; keeps
  the dashboard at the top.
- Re-editing with identical text raises `message is not modified` → include the
  "updated HH:MM" line (and it changes as data/ETA move) or catch and skip.

**Implementation sketch:**
- *Schema:* add `dashboard_message_id BIGINT NULL` to `users` (chat_id == telegram_id
  in private chats, so no separate chat column). Migration.
- *Repo:* `set_dashboard_message` / `clear_dashboard_message`;
  `users_with_dashboard_subscribed_to(queue_id)` for the update fanout.
- *Render:* `dashboard_text(items, lang)` — one line per subscription: status dot,
  queue name, called number, and the live ETA (reuse `eta_suffix` / `compute_pace`).
  Pure function → testable.
- *Command:* `/dashboard` → render from the user's subs + latest snapshots, send,
  `pinChatMessage(disable_notification=True)`, store `dashboard_message_id`.
- *Updates:* in `notifier`, on each relevant event (`ticket_called`, `queue_opened`,
  `slots_appeared`) find users who have a dashboard *and* subscribe to that queue,
  re-render their whole dashboard (latest snapshot of each of their queues) and
  `editMessageText`. Handle:
  - `message is not modified` → skip silently.
  - message deleted by user (`message to edit not found`) → clear stored id; the
    user re-runs `/dashboard`.
- *Volume:* edits fire only on change events, not every poll → fine at our scale
  (≪ 10k users). If we later want ETA to tick down between events, add a slow
  periodic refresh (e.g. every few minutes during office hours).

**Open question:** auto-pin on `/dashboard`, or send + let the user pin? And update
on every change event (most live) vs a lighter periodic edit.

**Effort:** medium — one migration, a render fn, a command, and a notifier hook.

## 3. Threshold alert quality-of-life — shipped

**Pain:** re-arming the "N tickets left" alert meant re-entering the ticket and a
new threshold through the whole FSM; and anxious users want every update.

**Shipped:**
- **One-tap re-arm** — the threshold alert carries inline buttons (`🔔 5 / 3 / 2 / 1`,
  only values below the current distance) that set a tighter `alert_n_before` in
  one tap, no ticket re-entry. `keyboards.rearm_threshold` + `cb_rearm`. No schema
  change (event_key includes the threshold, so a new value re-fires).
- **Anxious mode** — `subscriptions.alert_every_call` (+ migration) with a
  `🔔 Every call` toggle on the card; pings on every newly called number with
  people-ahead + ETA, deduped per called value. Takes precedence over the single
  threshold alert when on.

## 4. /feedback — message the author — shipped

`/feedback` starts a short FSM: the user types a message, the bot delivers it to
`FEEDBACK_CHAT_ID` (config, server-side) so the owner's Telegram is never exposed.
The owner sees the sender's name/username/id + language for follow-up; any command
(incl. `/cancel`) aborts the flow. Empty `FEEDBACK_CHAT_ID` disables the command.

## 5. Unify "you can register now" alerts — designed, not built

**Pain:** we have two independent events and two toggles that mean almost the
same thing to a user who wants to *book an appointment*:
- `queue_opened` — `enabled` flips false→true (📢 "opened" toggle).
- `slots_appeared` — `tickets_left` goes 0→>0 (🪑 "new slots" toggle).

When a queue opens it usually also has slots, so both fire → a double ping.
And the "queue already open, slots topped up" case only fires the second one.
Two toggles for one intent is confusing.

**Do:** collapse both into a single **"bookable now"** signal:

```
bookable = enabled AND tickets_left > 0
```

Emit when a queue transitions **not-bookable → bookable**. An open queue with
0 slots is not actionable → stay silent until slots appear.

- *diff.py:* replace `queue_opened` + `slots_appeared` with one `bookable`
  event carrying `tickets_left`; fire on `cur_bookable and not prev_bookable`.
- *Dedup:* fire on **every** 0→bookable transition (decided). Slots are grabbed
  in seconds and can reappear in the afternoon, so per-day dedup would miss real
  openings. Event key ties to the transition, not the date. (Watch for flicker
  0→1→0→1 within one poll cycle — if it becomes a problem, add a short cooldown.)
- *Schema:* migrate `alert_on_open` + `alert_on_slots` → one `alert_on_bookable`
  (`OR` the two on the way in), drop the old columns. One toggle on the card.
- *notifier / i18n / keyboards / tests:* one template ("you can register now,
  N slots"), one toggle, update fanout + fixtures.

**Effort:** medium — one migration, poller + notifier + keyboards + i18n + tests.

## 6. /faq + "closed" semantics in the dashboard — shipped

**Fixed:** a "closed" queue is closed **for new tickets only** — it keeps calling
already-issued numbers. The dashboard used to drop the number, the user's
position, and the ETA when `enabled` was false. Now it keeps all of them and only
swaps the marker/label ("registration closed"); a truly missing snapshot shows a
distinct `⚪ … no data` line.

**Shipped:** a separate `/faq` command (kept out of `/help` so that stays short)
explaining what "closed" means and how often data refreshes (~30 s poll during
office hours Mon–Fri 8–16; dashboard self-updates, alerts are event-driven).

## 7. User "report" / case timeline — idea only

See the local (gitignored) `FEATURE-report.md`: a form for users to report real
milestone dates (submit → summons → Przybysz status → pickup SMS → card printed)
so we can aggregate "how long each stage really takes." Not scoped yet.

## 8. _Further features — to be added._
