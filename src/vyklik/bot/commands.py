from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from vyklik.i18n import t

# Languages we localize the profile texts for (same set as the command menu).
_LANGS = ("pl", "ru", "be")

# English fallback for users whose Telegram language is none of the above.
# Telegram limits: description ≤ 512 chars, short description ≤ 120 chars.
_DEFAULT_DESCRIPTION = (
    "This bot tracks DUW Wrocław queues and notifies you when:\n"
    "• your ticket is called,\n"
    "• the queue gets close to your number,\n"
    "• a registration window opens / new slots appear.\n\n"
    'Set your ticket and it also shows a live "when will I be called" estimate, '
    "a weekday×hour busyness heatmap, and a pinned board of all your queues.\n\n"
    'Press "Start" to begin.'
)
_DEFAULT_SHORT_DESCRIPTION = (
    "Tracks DUW Wrocław queues and pings you when your ticket is called "
    "or a registration slot opens."
)

# (command, i18n description key). Order is what users see in the menu.
_COMMANDS: list[tuple[str, str]] = [
    ("queues", "cmd_queues"),
    ("mysubs", "cmd_mysubs"),
    ("dashboard", "cmd_dashboard"),
    ("stats", "cmd_stats"),
    ("feedback", "cmd_feedback"),
    ("lang", "cmd_lang"),
    ("faq", "cmd_faq"),
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
    "faq": "FAQ",
    "help": "Help",
}


async def set_my_commands(bot: Bot) -> None:
    # Per-language descriptions: Telegram shows the list matching the user's app
    # language, falling back to the no-language_code default otherwise.
    await bot.set_my_commands(
        [BotCommand(command=c, description=_DEFAULT_DESC[c]) for c, _ in _COMMANDS],
        scope=BotCommandScopeDefault(),
    )
    for code in _LANGS:
        await bot.set_my_commands(
            [BotCommand(command=c, description=t(key, lang=code)) for c, key in _COMMANDS],
            scope=BotCommandScopeDefault(),
            language_code=code,
        )


async def set_my_descriptions(bot: Bot) -> None:
    """Set the bot's profile texts, per language.

    - description: the "What can this bot do?" text shown on the empty-chat
      screen before the user presses Start.
    - short description: shown on the bot's profile page and in shares.

    Telegram serves the text matching the user's app language, falling back to
    the no-language default otherwise.
    """
    await bot.set_my_description(_DEFAULT_DESCRIPTION)
    await bot.set_my_short_description(_DEFAULT_SHORT_DESCRIPTION)
    for code in _LANGS:
        await bot.set_my_description(t("bot_description", lang=code), language_code=code)
        await bot.set_my_short_description(
            t("bot_short_description", lang=code), language_code=code
        )
