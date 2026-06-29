"""/feedback — let a user send a message to the bot owner.

The owner's Telegram is never exposed: we deliver to a chat id kept in config
(FEEDBACK_CHAT_ID) and the user only ever talks to the bot.
"""

import html
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from vyklik.bot import repo
from vyklik.bot.fsm import FeedbackEntry
from vyklik.config import settings
from vyklik.db import session
from vyklik.i18n import t

router = Router(name="feedback")
log = logging.getLogger("vyklik.bot.feedback")

MAX_LEN = 2000


async def _user_lang(tg_id: int) -> str:
    async with session() as s:
        lang = (await repo.get_or_create_user(s, tg_id)).language
        await s.commit()
    return lang


@router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    lang = await _user_lang(message.from_user.id)
    if settings.feedback_chat_id is None:
        await message.answer(t("feedback_unavailable", lang=lang))
        return
    await state.set_state(FeedbackEntry.waiting_for_text)
    await message.answer(t("feedback_prompt", lang=lang))


@router.message(FeedbackEntry.waiting_for_text)
async def on_feedback_text(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    lang = await _user_lang(message.from_user.id)
    text = (message.text or "").strip()

    # Any command (incl. /cancel) aborts the feedback flow.
    if text.startswith("/"):
        await state.clear()
        await message.answer(t("feedback_cancel", lang=lang))
        return
    if not text:
        await message.answer(t("feedback_prompt", lang=lang))
        return

    if settings.feedback_chat_id is None:  # disabled mid-flow; just bail
        await state.clear()
        await message.answer(t("feedback_unavailable", lang=lang))
        return

    u = message.from_user
    handle = f" @{u.username}" if u.username else ""
    body = (
        f"📨 <b>Feedback</b> from {html.escape(u.full_name or '')}{html.escape(handle)} "
        f"(id <code>{u.id}</code>, lang {lang})\n\n{html.escape(text[:MAX_LEN])}"
    )
    try:
        await message.bot.send_message(settings.feedback_chat_id, body)
        await message.answer(t("feedback_sent", lang=lang))
    except Exception:
        log.exception("failed to deliver feedback from %s", u.id)
        await message.answer(t("feedback_error", lang=lang))
    await state.clear()
