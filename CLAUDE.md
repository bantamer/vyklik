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

Keep it short — people skim. Follow the established house style (see `release-notes/0.1.0/`):

- **Header:** `📣 What's new`, localized — RU «📣 Что нового в боте», PL «📣 Co nowego w bocie», BE «📣 Што новага ў боце». No version number.
- **Body:** plain text, **no `<b>`** — Telegram auto-links `/commands`. One line per *user-visible* change, most useful first: emoji + `/command` (or feature) + short benefit. Lines are consecutive (no blank line between them), one blank line after the header. Skip internal/cosmetic changes (schema, refactors, avatar, deploy).
- **No sign-off**, no filler.
- Formal address (see Tone above).

**Storage:** commit each release's texts under `release-notes/<version>/<lang>.md` (one file per language, content = the exact message sent). Belarusian file is `by.md` (the script maps the DB code `be` → `by`); also keep `en.md` as an archive even though the bot has no EN users.

**Delivery:** `ops/broadcast.py` (not i18n — one-time). It loads `release-notes/<version>/`, selects `telegram_id, language FROM users WHERE NOT blocked`, picks each user's text (fallback `be→ru→pl`, `ru→pl`), catches `TelegramForbidden` → marks `blocked`, throttles under the rate limit. Run it inside the bot container (`docker compose cp` the script + notes in, then `exec`); do a `dry` run and a `test` to the owner before `all`. See the script's docstring.

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
