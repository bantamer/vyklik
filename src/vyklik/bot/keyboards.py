from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from vyklik.i18n import t
from vyklik.models import Queue, Snapshot, Subscription


def language_picker() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang:pl"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            ]
        ]
    )


def queues_list(queues: list[Queue], snapshots: dict[int, Snapshot], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for q in queues:
        snap = snapshots.get(q.id)
        status = (
            t("status_open", lang=lang)
            if snap and snap.enabled
            else t("status_closed", lang=lang)
        )
        name = q.display_pl if lang == "pl" else q.display_ru
        rows.append(
            [InlineKeyboardButton(text=f"{status[0]} {name}", callback_data=f"q:{q.id}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def queue_card(queue: Queue, sub: Subscription | None, lang: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if sub is None:
        rows.append(
            [InlineKeyboardButton(text=t("btn_subscribe", lang=lang), callback_data=f"sub:{queue.id}")]
        )
    else:
        rows.append(
            [
                InlineKeyboardButton(
                    text=t("btn_unsubscribe", lang=lang), callback_data=f"unsub:{sub.id}"
                )
            ]
        )
        if sub.my_ticket:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"{t('btn_clear_ticket', lang=lang)} ({sub.my_ticket})",
                        callback_data=f"ticket_clear:{sub.id}",
                    )
                ]
            )
        else:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=t("btn_set_ticket", lang=lang),
                        callback_data=f"ticket_set:{sub.id}",
                    )
                ]
            )
        rows.append(
            [
                InlineKeyboardButton(
                    text=t(
                        "btn_toggle_open",
                        lang=lang,
                        state=t("on", lang=lang) if sub.alert_on_open else t("off", lang=lang),
                    ),
                    callback_data=f"toggle_open:{sub.id}",
                )
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text=t(
                        "btn_toggle_slots",
                        lang=lang,
                        state=t("on", lang=lang) if sub.alert_on_slots else t("off", lang=lang),
                    ),
                    callback_data=f"toggle_slots:{sub.id}",
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(text=t("btn_back", lang=lang), callback_data="queues")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def mysubs_list(items: list[tuple[Subscription, Queue]], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for sub, q in items:
        name = q.display_pl if lang == "pl" else q.display_ru
        suffix = f" · {sub.my_ticket}" if sub.my_ticket else ""
        rows.append(
            [InlineKeyboardButton(text=f"{name}{suffix}", callback_data=f"q:{q.id}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
