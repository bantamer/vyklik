from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from vyklik.bot import keyboards, repo
from vyklik.db import session
from vyklik.i18n import t

router = Router(name="mysubs")


@router.message(Command("mysubs"))
async def cmd_mysubs(message: Message) -> None:
    if message.from_user is None:
        return
    async with session() as s:
        user = await repo.get_or_create_user(s, message.from_user.id)
        lang = user.language
        subs = await repo.list_subscriptions(s, message.from_user.id)
        queues = {q.id: q for q in await repo.list_queues(s)}
        await s.commit()
    if not subs:
        await message.answer(t("no_subs", lang=lang))
        return
    items = [(sub, queues[sub.queue_id]) for sub in subs if sub.queue_id in queues]
    await message.answer(t("mysubs_header", lang=lang), reply_markup=keyboards.mysubs_list(items, lang))
