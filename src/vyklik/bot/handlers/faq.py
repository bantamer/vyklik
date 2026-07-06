"""Interactive FAQ: /faq shows a list of questions as inline buttons; tapping a
question edits the message in place to show the answer with a "back" button that
returns to the list. One message, no chat clutter."""

import contextlib

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vyklik.bot import keyboards, repo
from vyklik.bot.keyboards import FAQ_IDS
from vyklik.db import session
from vyklik.i18n import t

router = Router(name="faq")


async def _language(user_id: int) -> str:
    async with session() as s:
        user = await repo.get_or_create_user(s, user_id)
        lang = user.language
        await s.commit()
    return lang


@router.message(Command("faq"))
async def cmd_faq(message: Message) -> None:
    if message.from_user is None:
        return
    lang = await _language(message.from_user.id)
    await message.answer(t("faq_intro", lang=lang), reply_markup=keyboards.faq_menu(lang))


@router.callback_query(F.data.startswith("faq:"))
async def on_faq(cb: CallbackQuery) -> None:
    if cb.data is None or cb.from_user is None:
        return
    key = cb.data.split(":", 1)[1]
    lang = await _language(cb.from_user.id)
    await cb.answer()
    if cb.message is None or not hasattr(cb.message, "edit_text"):
        return
    if key == "menu":
        text, markup = t("faq_intro", lang=lang), keyboards.faq_menu(lang)
    elif key in FAQ_IDS:
        text, markup = t(f"faq_a_{key}", lang=lang), keyboards.faq_back(lang)
    else:
        return
    with contextlib.suppress(Exception):
        await cb.message.edit_text(text, reply_markup=markup)
