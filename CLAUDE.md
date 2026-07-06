# CLAUDE.md

Guidance for Claude Code working in this repo.

## What this is

Public Telegram bot that tracks the [DUW Wrocław](https://rezerwacje.duw.pl/app/webroot/status_kolejek/) queue status API and notifies users about their tickets and queue openings. Public open-source repo, MIT-licensed. Anyone can self-host their own instance.

**Scope is intentionally narrow:** Wrocław city only, the DUW (Dolnośląski Urząd Wojewódzki) API only. Other voivodships and other cities are out of scope for v1.

## Architecture

Three processes, one shared Postgres:

- `poller` — APScheduler job that hits the DUW HTTP API every `POLL_INTERVAL_SECONDS` (only during office hours), upserts queue rows, inserts a snapshot, computes diffs vs. the previous snapshot, and emits `pg_notify('events', json)` for anything that changed.
- `bot` — aiogram 3 process. Listens to `LISTEN events` for fanout. Handles `/start`, `/queues`, `/mysubs`, `/lang`, FSM for entering ticket numbers. No webhooks — long polling for simplicity.
- `postgres` — single source of truth. No Redis, no message broker. LISTEN/NOTIFY does the job for the scale we expect (≪ 10k subscribers).

The poller writes; the bot reads + sends. They never touch each other's data directly — only via Postgres.

## Conventions

- **Language:** all code, comments, commits, docs, and PR titles in **English**. The bot's user-facing strings live in `src/vyklik/i18n/` (PL + RU at MVP, more languages welcome).
- **Tone / address:** address users **formally**, never informal "ty". RU/BE: «вы» (lowercase, polite). PL: formal/impersonal — prefer impersonal polite ("Proszę wybrać…") or Pan/Pani; **avoid** informal `ty`/`Twój`/`Ciebie` forms. This applies to every user-facing string and to update-note broadcasts.
- **Style:** `ruff format` + `ruff check`. Type hints everywhere. `from __future__ import annotations` not needed (3.12 baseline).
- **Async:** everything is async. No sync DB calls in handlers.
- **Secrets:** never committed. Real values go in `.env` (gitignored). `.env.example` lists every variable with safe defaults or empty placeholders.
- **Versions:** pin minor versions in `pyproject.toml` (`>=`), pin exact resolutions in `uv.lock`. No `latest`. Bumps are intentional, not automated.
- **Migrations:** Alembic, autogenerate from models, but **always review the diff** before committing.
- **DUW API:** treat as read-only and unstable. Wrap all field access in defensive `.get()` with sane defaults.

## User-facing update notes (release broadcasts)

When announcing a release to subscribers, follow this format. Keep it short — people skim. One message **per bot language**, formal address (see Tone above), HTML parse mode.

- **Header:** `✨ <b>Vyklik update</b>` — no version number, users don't care.
- **Body:** one line per *user-visible* change, most useful first. Each line = emoji + `<b>/command</b>` (or feature name) + what changed, framed as the benefit. Skip internal/cosmetic changes (schema, refactors, avatar, deploy).
- **Sign-off:** one short friendly line (e.g. "Спасибо, что пользуетесь ботом! 💙").
- **Localize** into every bot language (PL/RU/BE). At send time, cohorts with no users simply receive nothing — no need to drop the text.

Delivery: a one-off script (run in the bot container), *not* i18n keys — these are one-time. Select `telegram_id, language FROM users WHERE NOT blocked`, pick the text by each user's `language` (same fallback chain as the bot: `be→ru→pl`, `ru→pl`), send via the bot token, catch `TelegramForbidden` → mark `blocked`, throttle to ~30 msg/s. Optionally send a test to the owner's id first.

## Layout

```
src/vyklik/
├── config.py        ← pydantic-settings, single source of env
├── db.py            ← engine + session factory + LISTEN helper
├── models.py        ← SQLAlchemy 2.0 declarative
├── duw_client.py    ← thin wrapper around the DUW status endpoint
├── poller/          ← scheduler + ingest (writes snapshots, emits events)
├── bot/             ← handlers, keyboards, FSM, notifier (consumes events)
├── i18n/            ← per-language string dicts
└── stats/           ← own avg_wait calc from snapshot history (phase 2)
queues.yml           ← DUW queue id → curated PL/RU display name
migrations/          ← Alembic
ops/                 ← deployment scripts and runbooks
```

## What's done in this repo vs. via UI

- **Code/config (this repo):** queue display names, alert thresholds, message templates, schema.
- **Telegram (BotFather UI):** bot avatar, description, command list (`/setcommands` from `bot/commands.py`).
- **Postgres (DB only):** users, subscriptions, snapshot history. Nothing the user does in chat needs a code change.

## Definition of Done for a feature

1. Migration if schema changes; reviewed diff.
2. Tests for any DUW-payload parsing or alert-decision logic (golden JSON in `tests/fixtures/`).
3. PL + RU strings in `i18n/`; missing-key fallback chain works (`ru → pl`).
4. `compose up -d` from a fresh `.env.example` boots cleanly.
5. README updated if the user-facing flow changed.
