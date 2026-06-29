from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from vyklik.i18n import t

# (command, i18n description key). Order is what users see in the menu.
_COMMANDS: list[tuple[str, str]] = [
    ("queues", "cmd_queues"),
    ("mysubs", "cmd_mysubs"),
    ("dashboard", "cmd_dashboard"),
    ("stats", "cmd_stats"),
    ("feedback", "cmd_feedback"),
    ("lang", "cmd_lang"),
    ("help", "cmd_help"),
]

# English fallback shown to users whose Telegram language is neither PL nor RU.
_DEFAULT_DESC: dict[str, str] = {
    "queues": "List queues",
    "mysubs": "My subscriptions",
    "dashboard": "Pinned status board",
    "stats": "Best time to come",
    "feedback": "Message the author",
    "lang": "Change language",
    "help": "Help",
}


async def set_my_commands(bot: Bot) -> None:
    # Per-language descriptions: Telegram shows the list matching the user's app
    # language, falling back to the no-language_code default otherwise.
    await bot.set_my_commands(
        [BotCommand(command=c, description=_DEFAULT_DESC[c]) for c, _ in _COMMANDS],
        scope=BotCommandScopeDefault(),
    )
    for code in ("pl", "ru"):
        await bot.set_my_commands(
            [BotCommand(command=c, description=t(key, lang=code)) for c, key in _COMMANDS],
            scope=BotCommandScopeDefault(),
            language_code=code,
        )
