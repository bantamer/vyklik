import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vyklik.bot import keyboards, repo
from vyklik.db import session
from vyklik.i18n import t
from vyklik.stats.aggregate import fetch_queue_heatmap
from vyklik.stats.heatmap import render_heatmap

router = Router(name="stats")
log = logging.getLogger("vyklik.bot.stats")


async def _user_lang(s, tg_id: int) -> str:
    user = await repo.get_or_create_user(s, tg_id)
    return user.language


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if message.from_user is None:
        return
    async with session() as s:
        lang = await _user_lang(s, message.from_user.id)
        queues = await repo.list_queues(s)
        snaps = {q.id: await repo.latest_snapshot(s, q.id) for q in queues}
        await s.commit()
    if not queues:
        await message.answer(t("no_queues", lang=lang))
        return
    await message.answer(
        t("stats_pick", lang=lang),
        reply_markup=keyboards.queues_list(queues, snaps, lang, action="stats"),
    )


@router.callback_query(F.data.startswith("stats:"))
async def cb_stats(cb: CallbackQuery) -> None:
    if cb.from_user is None or cb.data is None:
        return
    qid = int(cb.data.split(":", 1)[1])
    async with session() as s:
        lang = await _user_lang(s, cb.from_user.id)
        queues = await repo.list_queues(s)
        queue = next((q for q in queues if q.id == qid), None)
        rows = await fetch_queue_heatmap(s, qid) if queue is not None else []
        await s.commit()
    if queue is None:
        await cb.answer("?")
        return
    name = queue.display_pl if lang == "pl" else queue.display_ru
    text = render_heatmap(name, rows, lang)
    kb = keyboards.heatmap_nav(qid, lang)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb)
        except TelegramBadRequest:
            await cb.message.answer(text, reply_markup=kb)
    await cb.answer()
