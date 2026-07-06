"""One-off release-announcement broadcast (see CLAUDE.md -> "User-facing update notes").

The message texts live in ``release-notes/<version>/<lang>.md`` (one file per
language, content is the exact Telegram-HTML that gets sent). This script loads
them and fans them out to subscribers in their own language.

It needs the live token, DSN and Postgres — so it runs *inside* the bot
container. The container doesn't ship ``release-notes/`` or ``ops/``, so copy
both in first, then exec (run on the server, in /opt/vyklik):

    docker compose cp ops/broadcast.py       bot:/tmp/broadcast.py
    docker compose cp release-notes/0.2.0     bot:/tmp/notes

    # dry run: recipient counts + the texts, sends nothing (default)
    docker compose exec -T bot python /tmp/broadcast.py dry  --notes /tmp/notes

    # test: send every language variant to the owner (FEEDBACK_CHAT_ID) or an id
    docker compose exec -T bot python /tmp/broadcast.py test --notes /tmp/notes
    docker compose exec -T bot python /tmp/broadcast.py test --notes /tmp/notes --id 12345

    # real: send to every non-blocked user, each in their own language
    docker compose exec -T bot python /tmp/broadcast.py all  --notes /tmp/notes

Picks the text by each user's `language` (fallback be->ru->pl, ru->pl), throttles
under Telegram's rate limit, and marks anyone who has blocked the bot.
"""

import argparse
import asyncio
from collections import Counter
from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy import select

from vyklik.bot import repo
from vyklik.config import settings
from vyklik.db import engine, session
from vyklik.models import User

# Bot language codes (as stored in users.language) → release-note filename stem.
# The DB uses ISO "be" for Belarusian; the note file is named "by" per the repo's
# release-notes convention.
LANG_FILE = {"pl": "pl", "ru": "ru", "be": "by"}
_FALLBACK = {"pl": ["pl"], "ru": ["ru", "pl"], "be": ["be", "ru", "pl"]}


def load_messages(notes_dir: str) -> dict[str, str]:
    base = Path(notes_dir)
    msgs: dict[str, str] = {}
    for lang, stem in LANG_FILE.items():
        path = base / f"{stem}.md"
        if path.exists():
            msgs[lang] = path.read_text(encoding="utf-8").strip()
    if not msgs:
        raise SystemExit(f"no note files found under {base}/ ({list(LANG_FILE.values())})")
    return msgs


def pick(messages: dict[str, str], lang: str) -> str:
    for code in _FALLBACK.get(lang, ["pl"]):
        if code in messages:
            return messages[code]
    return messages.get("pl") or next(iter(messages.values()))


async def recipients() -> list[tuple[int, str]]:
    async with session() as s:
        rows = (
            await s.execute(select(User.telegram_id, User.language).where(User.blocked.is_(False)))
        ).all()
    return [(int(tid), lang or "pl") for tid, lang in rows]


async def send_one(bot: Bot, chat_id: int, text: str) -> str:
    try:
        await bot.send_message(chat_id, text)
        return "sent"
    except TelegramForbiddenError:
        async with session() as s:
            await repo.mark_blocked(s, chat_id)
            await s.commit()
        return "blocked"
    except TelegramRetryAfter as exc:
        await asyncio.sleep(exc.retry_after)
        await bot.send_message(chat_id, text)
        return "sent"
    except Exception as exc:
        print(f"  ! {chat_id}: {type(exc).__name__}: {exc}")
        return "failed"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Broadcast a release note to subscribers.")
    parser.add_argument("mode", choices=["dry", "test", "all"], nargs="?", default="dry")
    parser.add_argument("--notes", default="release-notes/0.2.0", help="dir with <lang>.md files")
    parser.add_argument("--id", type=int, default=None, help="test recipient (default: owner)")
    args = parser.parse_args()

    messages = load_messages(args.notes)

    if args.mode == "dry":
        recips = await recipients()
        by = Counter(lang for _, lang in recips)
        print(f"DRY RUN — {len(recips)} active recipients by language: {dict(by)}")
        print(f"loaded texts: {sorted(messages)}")
        for lang in sorted(messages):
            print(f"\n===== {lang} — {by.get(lang, 0)} users =====\n{messages[lang]}")
        await engine().dispose()
        return

    bot = Bot(
        settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        if args.mode == "test":
            chat_id = args.id or settings.feedback_chat_id
            if not chat_id:
                print("no test chat id — pass --id or set FEEDBACK_CHAT_ID")
                return
            print(f"TEST → {chat_id}: sending {len(messages)} language variants")
            for lang, text in messages.items():
                print(f"  {lang}: {await send_one(bot, chat_id, text)}")
                await asyncio.sleep(0.3)
        else:  # all
            recips = await recipients()
            print(f"BROADCAST → {len(recips)} users")
            stats = {"sent": 0, "blocked": 0, "failed": 0}
            for i, (chat_id, lang) in enumerate(recips, 1):
                stats[await send_one(bot, chat_id, pick(messages, lang))] += 1
                await asyncio.sleep(0.05)  # ~20 msg/s, safely under Telegram's limit
                if i % 10 == 0:
                    print(f"  {i}/{len(recips)} ...")
            print(f"done: {stats}")
    finally:
        await bot.session.close()
        await engine().dispose()


if __name__ == "__main__":
    asyncio.run(main())
