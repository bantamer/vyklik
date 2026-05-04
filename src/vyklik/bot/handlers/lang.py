from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vyklik.bot import keyboards, repo
from vyklik.db import session
from vyklik.i18n import t

router = Router(name="lang")


@router.message(Command("lang"))
async def cmd_lang(message: Message) -> None:
    if message.from_user is None:
        return
    async with session() as s:
        user = await repo.get_or_create_user(s, message.from_user.id)
        lang = user.language
        await s.commit()
    await message.answer(t("choose_language", lang=lang), reply_markup=keyboards.language_picker())


@router.callback_query(F.data.startswith("lang:"))
async def on_pick_lang(cb: CallbackQuery) -> None:
    if cb.data is None or cb.from_user is None:
        return
    chosen = cb.data.split(":", 1)[1]
    if chosen not in {"pl", "ru"}:
        await cb.answer("?")
        return
    async with session() as s:
        await repo.get_or_create_user(s, cb.from_user.id)
        await repo.set_user_language(s, cb.from_user.id, chosen)
        await s.commit()
    await cb.answer(t("language_set", lang=chosen))
    if cb.message is not None and hasattr(cb.message, "edit_text"):
        try:
            await cb.message.edit_text(t("language_set", lang=chosen))
        except Exception:
            pass
