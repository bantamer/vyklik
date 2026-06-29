import logging
from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from vyklik.bot import keyboards, repo, tickets
from vyklik.bot.format import eta_text, queue_card_text
from vyklik.bot.fsm import TicketEntry
from vyklik.config import settings
from vyklik.db import session
from vyklik.i18n import t
from vyklik.stats.eta import PACE_WINDOW_MINUTES, compute_pace
from vyklik.work_hours import parse_schedule

router = Router(name="queues")
log = logging.getLogger("vyklik.bot.queues")
_SCHEDULE = parse_schedule(settings.work_hours)


async def _user_lang(s, tg_id: int) -> str:
    user = await repo.get_or_create_user(s, tg_id)
    return user.language


async def _card_data(s, qid: int, user_id: int):
    """Fetch everything a queue card needs, including pace samples when relevant."""
    snap = await repo.latest_snapshot(s, qid)
    sub = await repo.get_subscription(s, user_id, qid)
    samples = (
        await repo.recent_snapshots(s, qid, minutes=PACE_WINDOW_MINUTES)
        if sub and sub.my_ticket
        else []
    )
    return snap, sub, samples


def _render_card(queue, snap, sub, samples, lang: str):
    text = queue_card_text(queue, snap, lang)
    my = sub.my_ticket if sub else None
    if snap is not None and snap.enabled:
        section = eta_text(snap, my, compute_pace(samples), lang, datetime.now(UTC), _SCHEDULE)
        if section:
            text += "\n\n" + section
    return text, keyboards.queue_card(queue, sub, lang)


async def _show_card(cb: CallbackQuery, text: str, kb) -> None:
    """Edit the card in place; tolerate an unchanged refresh; fall back to a new
    message only on a real edit failure (e.g. the original was deleted).

    Does not answer the callback — the caller decides (some paths already did)."""
    if cb.message is None:
        return
    try:
        await cb.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest as exc:
        if "not modified" not in str(exc).lower():
            await cb.message.answer(text, reply_markup=kb)


async def _send_queue_list(target: Message | CallbackQuery, lang: str) -> None:
    async with session() as s:
        queues = await repo.list_queues(s)
        snaps = {q.id: await repo.latest_snapshot(s, q.id) for q in queues}
    if not queues:
        text = t("no_queues", lang=lang)
        kb = None
    else:
        text = t("queues_header", lang=lang)
        kb = keyboards.queues_list(queues, snaps, lang)
    if isinstance(target, CallbackQuery):
        if target.message is not None:
            try:
                await target.message.edit_text(text, reply_markup=kb)
            except Exception:
                await target.message.answer(text, reply_markup=kb)
        await target.answer()
    else:
        await target.answer(text, reply_markup=kb)


@router.message(Command("queues"))
async def cmd_queues(message: Message) -> None:
    if message.from_user is None:
        return
    async with session() as s:
        lang = await _user_lang(s, message.from_user.id)
        await s.commit()
    await _send_queue_list(message, lang)


@router.callback_query(F.data == "queues")
async def cb_queues(cb: CallbackQuery) -> None:
    if cb.from_user is None:
        return
    async with session() as s:
        lang = await _user_lang(s, cb.from_user.id)
        await s.commit()
    await _send_queue_list(cb, lang)


@router.callback_query(F.data.startswith("q:"))
async def cb_queue_card(cb: CallbackQuery) -> None:
    if cb.from_user is None or cb.data is None:
        return
    qid = int(cb.data.split(":", 1)[1])
    async with session() as s:
        lang = await _user_lang(s, cb.from_user.id)
        queues = await repo.list_queues(s)
        queue = next((q for q in queues if q.id == qid), None)
        if queue is None:
            await cb.answer("?")
            return
        snap, sub, samples = await _card_data(s, qid, cb.from_user.id)
        await s.commit()
    text, kb = _render_card(queue, snap, sub, samples, lang)
    await _show_card(cb, text, kb)
    await cb.answer()


@router.callback_query(F.data.startswith("sub:"))
async def cb_subscribe(cb: CallbackQuery) -> None:
    if cb.from_user is None or cb.data is None:
        return
    qid = int(cb.data.split(":", 1)[1])
    async with session() as s:
        await repo.get_or_create_user(s, cb.from_user.id)
        await repo.upsert_subscription(s, cb.from_user.id, qid)
        await s.commit()
        lang = await _user_lang(s, cb.from_user.id)
    await cb.answer(t("sub_added", lang=lang), show_alert=False)
    await _refresh_queue_card(cb, qid)


@router.callback_query(F.data.startswith("unsub:"))
async def cb_unsubscribe(cb: CallbackQuery) -> None:
    if cb.from_user is None or cb.data is None:
        return
    sub_id = int(cb.data.split(":", 1)[1])
    qid: int | None = None
    async with session() as s:
        sub = await repo.get_subscription_by_id(s, sub_id)
        if sub is not None:
            qid = sub.queue_id
            await repo.delete_subscription(s, sub_id)
        await s.commit()
        lang = await _user_lang(s, cb.from_user.id)
    await cb.answer(t("sub_removed", lang=lang))
    if qid is not None:
        await _refresh_queue_card(cb, qid)


@router.callback_query(F.data.startswith("toggle_open:"))
async def cb_toggle_open(cb: CallbackQuery) -> None:
    await _toggle_field(cb, "alert_on_open")


@router.callback_query(F.data.startswith("toggle_slots:"))
async def cb_toggle_slots(cb: CallbackQuery) -> None:
    await _toggle_field(cb, "alert_on_slots")


@router.callback_query(F.data.startswith("toggle_every:"))
async def cb_toggle_every(cb: CallbackQuery) -> None:
    await _toggle_field(cb, "alert_every_call")


@router.callback_query(F.data.startswith("rearm:"))
async def cb_rearm(cb: CallbackQuery) -> None:
    """One-tap re-arm of the threshold alert from a button on the alert itself."""
    if cb.from_user is None or cb.data is None:
        return
    _, sub_id_s, n_s = cb.data.split(":")
    sub_id, n = int(sub_id_s), int(n_s)
    async with session() as s:
        sub = await repo.get_subscription_by_id(s, sub_id)
        if sub is not None:
            sub.alert_n_before = n
        lang = await _user_lang(s, cb.from_user.id)
        await s.commit()
    await cb.answer(t("rearm_set", lang=lang, n=n))


async def _toggle_field(cb: CallbackQuery, field: str) -> None:
    if cb.from_user is None or cb.data is None:
        return
    sub_id = int(cb.data.split(":", 1)[1])
    qid: int | None = None
    async with session() as s:
        sub = await repo.get_subscription_by_id(s, sub_id)
        if sub is not None:
            setattr(sub, field, not getattr(sub, field))
            qid = sub.queue_id
        await s.commit()
    await cb.answer()
    if qid is not None:
        await _refresh_queue_card(cb, qid)


@router.callback_query(F.data.startswith("ticket_set:"))
async def cb_ticket_set(cb: CallbackQuery, state: FSMContext) -> None:
    if cb.from_user is None or cb.data is None:
        return
    sub_id = int(cb.data.split(":", 1)[1])
    async with session() as s:
        lang = await _user_lang(s, cb.from_user.id)
        await s.commit()
    await state.set_state(TicketEntry.waiting_for_value)
    await state.update_data(sub_id=sub_id)
    if cb.message is not None:
        await cb.message.answer(t("ticket_prompt", lang=lang))
    await cb.answer()


@router.callback_query(F.data.startswith("ticket_clear:"))
async def cb_ticket_clear(cb: CallbackQuery) -> None:
    if cb.from_user is None or cb.data is None:
        return
    sub_id = int(cb.data.split(":", 1)[1])
    qid: int | None = None
    async with session() as s:
        sub = await repo.get_subscription_by_id(s, sub_id)
        if sub is not None:
            sub.my_ticket = None
            sub.alert_n_before = None
            qid = sub.queue_id
        lang = await _user_lang(s, cb.from_user.id)
        await s.commit()
    await cb.answer(t("ticket_cleared", lang=lang))
    if qid is not None:
        await _refresh_queue_card(cb, qid)


@router.message(TicketEntry.waiting_for_value)
async def on_ticket_value(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not message.text:
        return
    async with session() as s:
        lang = await _user_lang(s, message.from_user.id)
        await s.commit()
    if not tickets.is_valid(message.text):
        await message.answer(t("ticket_invalid", lang=lang))
        return
    value = tickets.normalize(message.text)
    data = await state.get_data()
    sub_id = data.get("sub_id")
    async with session() as s:
        sub = await repo.get_subscription_by_id(s, sub_id) if sub_id else None
        expected = await repo.queue_ticket_prefix(s, sub.queue_id) if sub is not None else None
        if tickets.wrong_series(value, expected):
            await s.commit()
            await message.answer(t("ticket_wrong_series", lang=lang, prefix=expected, ticket=value))
            return  # stay in waiting_for_value so they can re-enter
        if sub is not None:
            sub.my_ticket = value
        await s.commit()
    await message.answer(t("ticket_set", lang=lang, ticket=value))
    await message.answer(t("threshold_prompt", lang=lang))
    await state.set_state(TicketEntry.waiting_for_threshold)


@router.message(TicketEntry.waiting_for_threshold)
async def on_threshold(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not message.text:
        return
    async with session() as s:
        lang = await _user_lang(s, message.from_user.id)
        await s.commit()
    text = message.text.strip().lower()
    n: int | None
    if text in {"nie", "нет", "не", "off", "no", "0"}:
        n = None
    else:
        try:
            n = int(text)
            if n < 1 or n > 100:
                raise ValueError
        except ValueError:
            await message.answer(t("ticket_invalid", lang=lang))
            return
    data = await state.get_data()
    sub_id = data.get("sub_id")
    async with session() as s:
        sub = await repo.get_subscription_by_id(s, sub_id) if sub_id else None
        if sub is not None:
            sub.alert_n_before = n
        await s.commit()
    await message.answer(
        t("threshold_off", lang=lang) if n is None else t("threshold_set", lang=lang, n=n)
    )
    await state.clear()


async def _refresh_queue_card(cb: CallbackQuery, qid: int) -> None:
    if cb.from_user is None:
        return
    async with session() as s:
        lang = await _user_lang(s, cb.from_user.id)
        queues = await repo.list_queues(s)
        queue = next((q for q in queues if q.id == qid), None)
        if queue is None:
            return
        snap, sub, samples = await _card_data(s, qid, cb.from_user.id)
        await s.commit()
    text, kb = _render_card(queue, snap, sub, samples, lang)
    await _show_card(cb, text, kb)
