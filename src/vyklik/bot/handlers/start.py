from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from vyklik.bot import keyboards, repo
from vyklik.db import session
from vyklik.i18n import t

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if message.from_user is None:
        return
    lang_hint = (message.from_user.language_code or "pl")[:2]
    if lang_hint not in {"pl", "ru"}:
        lang_hint = "pl"
    async with session() as s:
        user = await repo.get_or_create_user(s, message.from_user.id, lang_hint=lang_hint)
        lang = user.language
        await s.commit()
    await message.answer(t("welcome", lang=lang))
    await message.answer(t("choose_language", lang=lang), reply_markup=keyboards.language_picker())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    if message.from_user is None:
        return
    async with session() as s:
        user = await repo.get_or_create_user(s, message.from_user.id)
        lang = user.language
        await s.commit()
    await message.answer(t("help", lang=lang))
