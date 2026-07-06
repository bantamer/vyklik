from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from vyklik.i18n import t
from vyklik.models import Queue, Snapshot, Subscription


def language_picker() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Polski", callback_data="lang:pl"),
                InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="Беларуская", callback_data="lang:be"),
            ]
        ]
    )


def queues_list(
    queues: list[Queue], snapshots: dict[int, Snapshot], lang: str, action: str = "q"
) -> InlineKeyboardMarkup:
    rows = []
    for q in queues:
        snap = snapshots.get(q.id)
        status = (
            t("status_open", lang=lang) if snap and snap.enabled else t("status_closed", lang=lang)
        )
        name = q.display_pl if lang == "pl" else q.display_ru
        rows.append(
            [InlineKeyboardButton(text=f"{status[0]} {name}", callback_data=f"{action}:{q.id}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def heatmap_nav(queue_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_back", lang=lang), callback_data=f"q:{queue_id}")]
        ]
    )


def heatmap_close(lang: str) -> InlineKeyboardMarkup:
    """Back button for the heatmap *photo* — deletes it (can't edit a photo back
    into the text card), revealing the card/picker still above it."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_back", lang=lang), callback_data="heatmap_close")]
        ]
    )


def queue_card(queue: Queue, sub: Subscription | None, lang: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if sub is None:
        rows.append(
            [
                InlineKeyboardButton(
                    text=t("btn_subscribe", lang=lang),
                    callback_data=f"sub:{queue.id}",
                )
            ]
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
            rows.append(
                [
                    InlineKeyboardButton(
                        text=t(
                            "btn_toggle_every",
                            lang=lang,
                            state=t("on", lang=lang)
                            if sub.alert_every_call
                            else t("off", lang=lang),
                        ),
                        callback_data=f"toggle_every:{sub.id}",
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
        [InlineKeyboardButton(text=t("btn_stats", lang=lang), callback_data=f"stats:{queue.id}")]
    )
    rows.append(
        [
            InlineKeyboardButton(text=t("btn_refresh", lang=lang), callback_data=f"q:{queue.id}"),
            InlineKeyboardButton(text=t("btn_back", lang=lang), callback_data="queues"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Tighter thresholds offered as one-tap re-arm buttons on a "N tickets left" alert.
_REARM_LADDER = [5, 3, 1]


def rearm_threshold(sub_id: int, dist: int, lang: str) -> InlineKeyboardMarkup | None:
    """Buttons to re-arm the threshold alert at a tighter value, in one tap.

    Offers only values strictly below the current distance (a value ≥ dist would
    fire again immediately). Returns None when there's nothing tighter to offer.
    One button per row so the full verb label stays readable."""
    values = [n for n in _REARM_LADDER if n < dist]
    if not values:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_rearm", lang=lang, n=n), callback_data=f"rearm:{sub_id}:{n}"
                )
            ]
            for n in values
        ]
    )


# FAQ question ids → i18n keys `faq_q_<id>` (button) and `faq_a_<id>` (answer).
# Order is the display order in the menu.
FAQ_IDS = ("closed", "refresh", "alerts", "persist")


def faq_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(f"faq_q_{qid}", lang=lang), callback_data=f"faq:{qid}")]
            for qid in FAQ_IDS
        ]
    )


def faq_back(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_back", lang=lang), callback_data="faq:menu")]
        ]
    )


def mysubs_list(items: list[tuple[Subscription, Queue]], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for sub, q in items:
        name = q.display_pl if lang == "pl" else q.display_ru
        suffix = f" · {sub.my_ticket}" if sub.my_ticket else ""
        rows.append([InlineKeyboardButton(text=f"{name}{suffix}", callback_data=f"q:{q.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
