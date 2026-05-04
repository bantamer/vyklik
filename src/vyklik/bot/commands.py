from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

COMMANDS = [
    BotCommand(command="queues", description="List queues / Список очередей"),
    BotCommand(command="mysubs", description="My subscriptions / Мои подписки"),
    BotCommand(command="lang", description="Change language / Сменить язык"),
    BotCommand(command="help", description="Help / Помощь"),
]


async def set_my_commands(bot: Bot) -> None:
    await bot.set_my_commands(COMMANDS, scope=BotCommandScopeDefault())
