from aiogram import Router

from vyklik.bot.handlers import dashboard, feedback, lang, mysubs, queues, start, stats


def all_routers() -> list[Router]:
    # Order matters: FSM-driven text handlers in `queues` (ticket entry) must come
    # before the generic command handlers in `start`.
    return [
        start.router,
        lang.router,
        queues.router,
        mysubs.router,
        dashboard.router,
        stats.router,
        feedback.router,
    ]
