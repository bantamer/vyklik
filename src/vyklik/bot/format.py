from datetime import datetime

from vyklik.bot import tickets
from vyklik.i18n import t
from vyklik.models import Queue, Snapshot
from vyklik.stats.eta import estimate_eta
from vyklik.work_hours import TZ


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


def _closing_today(now_local: datetime, schedule: dict[int, tuple[int, int]]) -> datetime | None:
    window = schedule.get(now_local.weekday())
    if window is None:
        return None
    return now_local.replace(hour=window[1], minute=0, second=0, microsecond=0)


def eta_text(
    snap: Snapshot | None,
    my_ticket: str | None,
    pace_seconds: float | None,
    lang: str,
    now_utc: datetime,
    schedule: dict[int, tuple[int, int]],
) -> str | None:
    """Live "when will I be called" line for a queue card, or None if N/A.

    None when there's no ticket set, no snapshot, or the user's ticket is in a
    different series than the one currently being called (can't compare).
    """
    if snap is None or not my_ticket or not snap.ticket_value:
        return None
    ahead = tickets.distance(my_ticket, snap.ticket_value)
    if ahead is None:
        return None
    now_local = now_utc.astimezone(TZ)
    est = estimate_eta(
        ahead, pace_seconds, now_local=now_local, closing=_closing_today(now_local, schedule)
    )
    if est.already_called:
        return t("eta_called", lang=lang)
    if est.pace_seconds is None or est.eta_at_low is None or est.eta_at_high is None:
        return t("eta_no_pace", lang=lang, ahead=ahead)
    line = t(
        "eta_line",
        lang=lang,
        ahead=ahead,
        low=fmt_seconds(est.low_seconds),
        high=fmt_seconds(est.high_seconds),
        at_low=est.eta_at_low.strftime("%H:%M"),
        at_high=est.eta_at_high.strftime("%H:%M"),
    )
    if est.today_unlikely:
        line += "\n" + t("eta_today_unlikely", lang=lang)
    return line


def eta_suffix(
    people_ahead: int,
    pace_seconds: float | None,
    lang: str,
    now_utc: datetime,
    schedule: dict[int, tuple[int, int]],
) -> str | None:
    """Just the "≈ in X–Y (≈ HH:MM–HH:MM)" line, for alerts that already state
    how many tickets are ahead. None when the pace can't be estimated."""
    if pace_seconds is None or people_ahead <= 0:
        return None
    now_local = now_utc.astimezone(TZ)
    est = estimate_eta(
        people_ahead, pace_seconds, now_local=now_local, closing=_closing_today(now_local, schedule)
    )
    if est.eta_at_low is None or est.eta_at_high is None:
        return None
    line = t(
        "alert_eta",
        lang=lang,
        low=fmt_seconds(est.low_seconds),
        high=fmt_seconds(est.high_seconds),
        at_low=est.eta_at_low.strftime("%H:%M"),
        at_high=est.eta_at_high.strftime("%H:%M"),
    )
    if est.today_unlikely:
        line += " " + t("eta_today_unlikely", lang=lang)
    return line
