# vyklik

Telegram bot that watches the [DUW Wrocław](https://rezerwacje.duw.pl/app/webroot/status_kolejek/) queue API and notifies you when:

- your ticket is being called,
- the queue gets close to your ticket,
- a closed registration window opens up / new slots appear.

> **Status:** scaffolding. Not deployed yet. See [open issues](https://github.com/bantamer/vyklik/issues) for the roadmap.

## How it works

```
DUW HTTP API  ─every 30s─►  poller  ──snapshot──►  Postgres  ──LISTEN/NOTIFY──►  bot  ──►  Telegram
```

A single poller polls DUW once per interval (during office hours only), writes a snapshot row per queue, and emits a `pg_notify` event whenever something changes. The bot fans out alerts to subscribed users, with per-user dedup and language preferences.

The poller is **shared** — there is one HTTP request to DUW regardless of how many users are subscribed.

## Stack

- Python 3.12
- [aiogram 3](https://docs.aiogram.dev/) (Telegram Bot)
- [APScheduler](https://apscheduler.readthedocs.io/) (cron)
- Postgres 16, [asyncpg](https://magicstack.github.io/asyncpg/), SQLAlchemy 2.0, Alembic
- Docker Compose

## Run locally

```bash
cp .env.example .env       # fill in TELEGRAM_BOT_TOKEN
docker compose up -d
docker compose logs -f
```

## Deploy

See [`ops/oracle-cloud.md`](ops/oracle-cloud.md) for an Oracle Always Free walkthrough.

## License

MIT — see [LICENSE](LICENSE).
