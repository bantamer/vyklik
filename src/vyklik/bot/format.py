from datetime import datetime

from vyklik.bot import tickets
from vyklik.i18n import t
from vyklik.models import Queue, Snapshot
from vyklik.stats.eta import SLOW_FACTOR, estimate_eta
from vyklik.work_hours import TZ


def fmt_seconds(seconds: int | None, lang: str) -> str:
    if seconds is None:
        return "—"
    s = int(seconds)
    if s < 60:
        return f"{s} {t('dur_s', lang=lang)}"
    m, _ = divmod(s, 60)
    if m < 60:
        return f"{m} {t('dur_min', lang=lang)}"
    h, m = divmod(m, 60)
    if m:
        return f"{h} {t('dur_h', lang=lang)} {m} {t('dur_min', lang=lang)}"
    return f"{h} {t('dur_h', lang=lang)}"


def fmt_range(low_seconds: int, high_seconds: int, lang: str) -> str:
    """A compact duration range with a single unit, e.g. "5–9 мин"."""
    if high_seconds < 3600:
        return f"{low_seconds // 60}–{high_seconds // 60} {t('dur_min', lang=lang)}"
    return f"{fmt_seconds(low_seconds, lang)} – {fmt_seconds(high_seconds, lang)}"


def queue_card_text(queue: Queue, snap: Snapshot | None, lang: str) -> str:
    name = queue.display_pl if lang == "pl" else queue.display_ru
    if snap is None:
        return f"<b>{name}</b>\n\n{t('queue_no_data', lang=lang)}"
    status = t("status_open", lang=lang) if snap.enabled else t("status_closed", lang=lang)
    text = t(
        "queue_card",
        lang=lang,
        name=name,
        status=status,
        ticket=snap.ticket_value or "—",
        served=snap.tickets_served,
        max_t=snap.max_tickets if snap.max_tickets is not None else "∞",
        ticket_count=snap.ticket_count,
        tickets_left=snap.tickets_left if snap.tickets_left is not None else "—",
        wait=fmt_seconds(snap.avg_wait_api, lang),
        service=fmt_seconds(snap.avg_service_api, lang),
    )
    return text + "\n" + t("card_updated", lang=lang, time=snap.ts.astimezone(TZ).strftime("%H:%M"))


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
        range=fmt_range(est.low_seconds, est.high_seconds, lang),
        at_low=est.eta_at_low.strftime("%H:%M"),
        at_high=est.eta_at_high.strftime("%H:%M"),
    )
    if est.today_unlikely:
        line += "\n" + t("eta_today_unlikely", lang=lang)
    return line


def dashboard_text(
    rows: list[tuple[str, Snapshot | None, str | None, float | None]],
    lang: str,
    now_local: datetime,
) -> str:
    """One-line-per-subscription status board. Rows are (name, snap, my_ticket, pace)."""
    lines = [t("dashboard_header", lang=lang, time=now_local.strftime("%H:%M"))]
    for name, snap, my_ticket, pace in rows:
        if snap is None or not snap.enabled:
            lines.append(t("dashboard_line_closed", lang=lang, name=name))
            continue
        line = t("dashboard_line_open", lang=lang, name=name, ticket=snap.ticket_value or "—")
        if my_ticket:
            ahead = tickets.distance(my_ticket, snap.ticket_value)
            if ahead is None:
                line += t("dashboard_mine_plain", lang=lang, my=my_ticket)
            elif ahead <= 0:
                line += t("dashboard_mine_called", lang=lang, my=my_ticket)
            elif pace:
                eta = fmt_seconds(round(ahead * pace * SLOW_FACTOR), lang)
                line += t("dashboard_mine_eta", lang=lang, my=my_ticket, n=ahead, eta=eta)
            else:
                line += t("dashboard_mine", lang=lang, my=my_ticket, n=ahead)
        lines.append(line)
    return "\n".join(lines)


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
        range=fmt_range(est.low_seconds, est.high_seconds, lang),
        at_low=est.eta_at_low.strftime("%H:%M"),
        at_high=est.eta_at_high.strftime("%H:%M"),
    )
    if est.today_unlikely:
        line += " " + t("eta_today_unlikely", lang=lang)
    return line
