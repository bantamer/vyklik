# Roadmap

Requested product features, with implementation sketches. Stats/wait-time work
lives in [stats.md](stats.md).

## 1. Refresh button on the queue card (quick win)

**Pain:** getting fresh info means re-running `/mysubs` (or going back + re-tapping),
which posts a brand-new message each time instead of updating in place.

**Do:**
- Add a `🔄 Refresh` button to `keyboards.queue_card`, `callback_data=f"q:{queue.id}"`
  — it already routes to `cb_queue_card`, which edits the message in place.
- Add an "updated at HH:MM" (Europe/Warsaw) footer line to the card text, so a
  re-render always differs and the `editMessageText` isn't rejected with
  `message is not modified`. Bonus: makes freshness explicit.

**Effort:** tiny. No schema change.

## 2. Pinned live dashboard of all subscriptions

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

## 3. _Further features — to be added._
