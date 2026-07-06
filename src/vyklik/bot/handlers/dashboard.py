"""Pinned live dashboard: one message listing the status of all the user's
subscriptions, which the bot edits in place as queues change.

Telegram lets a bot edit its own messages with no time limit and no
notification, and pin them in a private chat — so the board stays current and
silent. We store its message id on the user (chat_id == telegram_id in a private
chat) and re-render it on every relevant queue event.
"""

import logging
from contextlib import suppress
from datetime import UTC, datetime

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message

from vyklik.bot import repo
from vyklik.bot.format import dashboard_text
from vyklik.db import session
from vyklik.i18n import t
from vyklik.stats.eta import PACE_WINDOW_MINUTES, compute_pace
from vyklik.work_hours import TZ

router = Router(name="dashboard")
log = logging.getLogger("vyklik.bot.dashboard")


async def _build_rows(s, user_id: int, lang: str):
    """(name, snap, my_ticket, pace) per subscription, ordered by queue id."""
    subs = await repo.list_subscriptions(s, user_id)
    queues = {q.id: q for q in await repo.list_queues(s)}
    rows = []
    for sub in subs:
        queue = queues.get(sub.queue_id)
        if queue is None:
            continue
        name = queue.display_pl if lang == "pl" else queue.display_ru
        snap = await repo.latest_snapshot(s, sub.queue_id)
        pace = None
        # A "closed" queue is closed for *new tickets* only — it keeps calling
        # the numbers already issued, so the pace is still meaningful. Gate on
        # having a snapshot, not on `enabled`.
        if sub.my_ticket and snap is not None:
            samples = await repo.recent_snapshots(s, sub.queue_id, minutes=PACE_WINDOW_MINUTES)
            pace = compute_pace(samples)
        rows.append((name, snap, sub.my_ticket, pace))
    return rows


async def _render(s, user_id: int, lang: str) -> str:
    rows = await _build_rows(s, user_id, lang)
    now_local = datetime.now(UTC).astimezone(TZ)
    return dashboard_text(rows, lang, now_local)


@router.message(Command("dashboard"))
async def cmd_dashboard(message: Message) -> None:
    if message.from_user is None:
        return
    uid = message.from_user.id
    async with session() as s:
        user = await repo.get_or_create_user(s, uid)
        lang = user.language
        old_id = user.dashboard_message_id
        subs = await repo.list_subscriptions(s, uid)
        text = await _render(s, uid, lang) if subs else None
        await s.commit()

    if not subs:
        await message.answer(t("dashboard_empty", lang=lang))
        return

    # Drop the previous board so we don't leave stale pins around.
    if old_id is not None:
        with suppress(Exception):
            await message.bot.unpin_chat_message(uid, message_id=old_id)
        with suppress(Exception):
            await message.bot.delete_message(uid, old_id)

    sent = await message.answer(text)
    with suppress(Exception):
        await message.bot.pin_chat_message(uid, sent.message_id, disable_notification=True)
    async with session() as s:
        await repo.set_dashboard_message(s, uid, sent.message_id)
        await s.commit()
    await message.answer(t("dashboard_pinned", lang=lang))


async def push_dashboard(bot: Bot, user_id: int) -> None:
    """Re-render and edit a user's pinned dashboard in place. Best-effort."""
    async with session() as s:
        user = await repo.get_user(s, user_id)
        if user is None or user.dashboard_message_id is None:
            return
        lang = user.language
        msg_id = user.dashboard_message_id
        text = await _render(s, user_id, lang)
        await s.commit()
    try:
        await bot.edit_message_text(text, chat_id=user_id, message_id=msg_id)
    except TelegramBadRequest as exc:
        if "not modified" in str(exc).lower():
            return
        # message deleted or no longer editable — forget it, user can /dashboard again
        async with session() as s:
            await repo.clear_dashboard_message(s, user_id)
            await s.commit()
    except TelegramForbiddenError:
        async with session() as s:
            await repo.mark_blocked(s, user_id)
            await s.commit()


async def update_dashboards_for_queue(bot: Bot, queue_id: int) -> None:
    """Refresh the dashboards of everyone who pinned one and subscribes to a queue."""
    async with session() as s:
        user_ids = await repo.users_with_dashboard_subscribed_to(s, queue_id)
        await s.commit()
    for uid in user_ids:
        await push_dashboard(bot, uid)
