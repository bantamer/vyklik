import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from vyklik.bot.commands import set_my_commands
from vyklik.bot.handlers import all_routers
from vyklik.bot.notifier import notifier_loop
from vyklik.config import settings


async def main_async() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("vyklik.bot")

    bot = Bot(
        settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    for router in all_routers():
        dp.include_router(router)

    await set_my_commands(bot)
    log.info("bot starting (long polling)")

    notifier_task = asyncio.create_task(notifier_loop(bot))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        notifier_task.cancel()
        try:
            await notifier_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
