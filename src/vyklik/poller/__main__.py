import asyncio
import logging

from vyklik.config import settings


async def main() -> None:
    logging.basicConfig(level=settings.log_level)
    log = logging.getLogger("vyklik.poller")
    log.info(
        "poller scaffolded — poll_interval=%ss work_hours=%s",
        settings.poll_interval_seconds,
        settings.work_hours,
    )
    log.info("not implemented yet — see https://github.com/bantamer/vyklik/issues")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
