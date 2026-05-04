from vyklik.i18n import t
from vyklik.models import Queue, Snapshot


def fmt_seconds(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    s = int(seconds)
    if s < 60:
        return f"{s} s"
    m, _ = divmod(s, 60)
    if m < 60:
        return f"{m} min"
    h, m = divmod(m, 60)
    return f"{h} h {m} min" if m else f"{h} h"


def queue_card_text(queue: Queue, snap: Snapshot | None, lang: str) -> str:
    name = queue.display_pl if lang == "pl" else queue.display_ru
    if snap is None:
        return f"<b>{name}</b>\n\n{t('queue_no_data', lang=lang)}"
    status = t("status_open", lang=lang) if snap.enabled else t("status_closed", lang=lang)
    return t(
        "queue_card",
        lang=lang,
        name=name,
        status=status,
        ticket=snap.ticket_value or "—",
        served=snap.tickets_served,
        max_t=snap.max_tickets if snap.max_tickets is not None else "∞",
        ticket_count=snap.ticket_count,
        tickets_left=snap.tickets_left if snap.tickets_left is not None else "—",
        wait=fmt_seconds(snap.avg_wait_api),
        service=fmt_seconds(snap.avg_service_api),
    )
