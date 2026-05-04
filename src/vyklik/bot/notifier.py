import asyncio
import json
import logging

import asyncpg
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from vyklik.bot import repo, tickets
from vyklik.db import asyncpg_connect, session
from vyklik.i18n import t
from vyklik.poller.ingest import NOTIFY_CHANNEL

log = logging.getLogger("vyklik.bot.notifier")


async def notifier_loop(bot: Bot) -> None:
    """Listen for pg_notify events and fan them out to subscribed users.

    Reconnects on transient asyncpg failures.
    """
    while True:
        try:
            await _run(bot)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("notifier crashed; reconnecting in 5s")
            await asyncio.sleep(5)


async def _run(bot: Bot) -> None:
    conn = await asyncpg_connect()
    queue: asyncio.Queue[dict] = asyncio.Queue()

    def listener(_conn, _pid, _channel, payload):
        try:
            queue.put_nowait(json.loads(payload))
        except Exception:
            log.exception("bad pg_notify payload: %r", payload)

    await conn.add_listener(NOTIFY_CHANNEL, listener)
    log.info("notifier listening on channel=%s", NOTIFY_CHANNEL)

    try:
        while True:
            event = await queue.get()
            try:
                await _handle(bot, event)
            except Exception:
                log.exception("error handling event %r", event)
    finally:
        await conn.remove_listener(NOTIFY_CHANNEL, listener)
        await conn.close()


async def _handle(bot: Bot, event: dict) -> None:
    etype = event.get("type")
    qid = event.get("queue_id")
    payload = event.get("payload") or {}
    if etype is None or qid is None:
        return
    log.info("event %s queue=%s payload=%s", etype, qid, payload)

    if etype == "ticket_called":
        await _handle_ticket_called(bot, qid, payload)
    elif etype == "queue_opened":
        await _fanout_flag(
            bot, qid, "alert_on_open", "alert_opened", payload, key=f"open:{payload.get('date')}"
        )
    elif etype == "slots_appeared":
        await _fanout_flag(
            bot,
            qid,
            "alert_on_slots",
            "alert_slots",
            payload,
            key=f"slots:{payload.get('date')}",
            extra={"n": payload.get("tickets_left")},
        )


async def _handle_ticket_called(bot: Bot, qid: int, payload: dict) -> None:
    current_ticket = payload.get("ticket_value")
    async with session() as s:
        queues = await repo.list_queues(s)
        queue = next((q for q in queues if q.id == qid), None)
        subs = await repo.list_subs_with_my_ticket(s, qid)
        await s.commit()
    if queue is None:
        return

    for sub in subs:
        if not current_ticket or not sub.my_ticket:
            continue
        dist = tickets.distance(sub.my_ticket, current_ticket)
        if dist is None:
            continue
        async with session() as s:
            user = await repo.get_or_create_user(s, sub.user_id)
            lang = user.language
            await s.commit()
        name = queue.display_pl if lang == "pl" else queue.display_ru

        if dist <= 0 and sub.alert_on_my_call:
            event_key = f"called:{sub.my_ticket}"
            async with session() as s:
                inserted = await repo.record_sent(s, sub.id, event_key)
                await s.commit()
            if inserted:
                await _send(
                    bot,
                    sub.user_id,
                    t("alert_called", lang=lang, name=name, ticket=sub.my_ticket),
                )
                # Ticket considered "redeemed" — clear it so a new series tomorrow
                # doesn't trigger spurious alerts. Threshold goes with it (no
                # ticket → nothing to threshold).
                async with session() as s:
                    sub_db = await repo.get_subscription_by_id(s, sub.id)
                    if sub_db is not None:
                        sub_db.my_ticket = None
                        sub_db.alert_n_before = None
                    await s.commit()
        elif sub.alert_n_before is not None and 0 < dist <= sub.alert_n_before:
            event_key = f"before:{sub.my_ticket}:{sub.alert_n_before}"
            async with session() as s:
                inserted = await repo.record_sent(s, sub.id, event_key)
                await s.commit()
            if inserted:
                await _send(
                    bot,
                    sub.user_id,
                    t(
                        "alert_close",
                        lang=lang,
                        name=name,
                        my=sub.my_ticket,
                        n=dist,
                        current=current_ticket,
                    ),
                )


async def _fanout_flag(
    bot: Bot,
    qid: int,
    field: str,
    template: str,
    payload: dict,
    *,
    key: str,
    extra: dict | None = None,
) -> None:
    async with session() as s:
        queues = await repo.list_queues(s)
        queue = next((q for q in queues if q.id == qid), None)
        subs = await repo.list_subscriptions_for_fanout(s, qid, only_alert_field=field)
        await s.commit()
    if queue is None:
        return
    for sub in subs:
        async with session() as s:
            user = await repo.get_or_create_user(s, sub.user_id)
            lang = user.language
            inserted = await repo.record_sent(s, sub.id, key)
            await s.commit()
        if not inserted:
            continue
        name = queue.display_pl if lang == "pl" else queue.display_ru
        text = t(template, lang=lang, name=name, **(extra or {}))
        await _send(bot, sub.user_id, text)


async def _send(bot: Bot, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id, text)
    except TelegramForbiddenError:
        async with session() as s:
            await repo.mark_blocked(s, chat_id)
            await s.commit()
        log.info("user %s blocked the bot, marked as blocked", chat_id)
    except TelegramRetryAfter as exc:
        log.warning("telegram rate-limit, sleeping %ss", exc.retry_after)
        await asyncio.sleep(exc.retry_after)
        try:
            await bot.send_message(chat_id, text)
        except Exception:
            log.exception("retry after rate-limit also failed for chat %s", chat_id)
    except asyncpg.exceptions.PostgresError:
        raise
    except Exception:
        log.exception("send to chat %s failed", chat_id)
