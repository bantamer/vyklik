import asyncio
import logging

from vyklik.config import settings


async def main() -> None:
    logging.basicConfig(level=settings.log_level)
    log = logging.getLogger("vyklik.bot")
    log.info("bot scaffolded — token loaded (...%s)", settings.telegram_bot_token[-6:])
    log.info("not implemented yet — see https://github.com/bantamer/vyklik/issues")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
