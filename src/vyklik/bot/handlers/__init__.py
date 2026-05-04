from aiogram import Router

from vyklik.bot.handlers import lang, mysubs, queues, start


def all_routers() -> list[Router]:
    # Order matters: FSM-driven text handlers in `queues` (ticket entry) must come
    # before the generic command handlers in `start`.
    return [start.router, lang.router, queues.router, mysubs.router]
