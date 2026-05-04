from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from vyklik.models import Queue, SentAlert, Snapshot, Subscription, User


async def get_or_create_user(session: AsyncSession, tg_id: int, lang_hint: str = "pl") -> User:
    # Atomic upsert: avoids a race when two updates from the same user land
    # concurrently and both see "no row yet" between SELECT and INSERT.
    stmt = (
        pg_insert(User)
        .values(telegram_id=tg_id, language=lang_hint, blocked=False)
        .on_conflict_do_update(
            index_elements=[User.telegram_id],
            set_={"last_seen": datetime.now(UTC), "blocked": False},
        )
    )
    await session.execute(stmt)
    user = await session.get(User, tg_id)
    assert user is not None  # just upserted
    return user


async def set_user_language(session: AsyncSession, tg_id: int, lang: str) -> None:
    user = await session.get(User, tg_id)
    if user is not None:
        user.language = lang


async def mark_blocked(session: AsyncSession, tg_id: int) -> None:
    user = await session.get(User, tg_id)
    if user is not None:
        user.blocked = True


async def list_queues(session: AsyncSession) -> list[Queue]:
    stmt = select(Queue).order_by(Queue.id)
    result = await session.execute(stmt)
    return list(result.scalars())


async def latest_snapshot(session: AsyncSession, queue_id: int) -> Snapshot | None:
    stmt = (
        select(Snapshot).where(Snapshot.queue_id == queue_id).order_by(Snapshot.ts.desc()).limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_subscription(
    session: AsyncSession, user_id: int, queue_id: int
) -> Subscription | None:
    stmt = select(Subscription).where(
        Subscription.user_id == user_id, Subscription.queue_id == queue_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_subscription_by_id(session: AsyncSession, sub_id: int) -> Subscription | None:
    return await session.get(Subscription, sub_id)


async def upsert_subscription(session: AsyncSession, user_id: int, queue_id: int) -> Subscription:
    sub = await get_subscription(session, user_id, queue_id)
    if sub is None:
        sub = Subscription(user_id=user_id, queue_id=queue_id, alert_on_my_call=True)
        session.add(sub)
        await session.flush()
    return sub


async def delete_subscription(session: AsyncSession, sub_id: int) -> None:
    sub = await session.get(Subscription, sub_id)
    if sub is not None:
        await session.delete(sub)


async def list_subscriptions(session: AsyncSession, user_id: int) -> list[Subscription]:
    stmt = (
        select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.queue_id)
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def list_subscriptions_for_fanout(
    session: AsyncSession, queue_id: int, *, only_alert_field: str
) -> list[Subscription]:
    """Active (non-blocked user) subscriptions to a queue with a specific alert flag set."""
    field = getattr(Subscription, only_alert_field)
    stmt = (
        select(Subscription)
        .join(User, User.telegram_id == Subscription.user_id)
        .where(Subscription.queue_id == queue_id, field.is_(True), User.blocked.is_(False))
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def list_subs_with_my_ticket(session: AsyncSession, queue_id: int) -> list[Subscription]:
    stmt = (
        select(Subscription)
        .join(User, User.telegram_id == Subscription.user_id)
        .where(
            Subscription.queue_id == queue_id,
            Subscription.my_ticket.isnot(None),
            User.blocked.is_(False),
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def record_sent(session: AsyncSession, sub_id: int, event_key: str) -> bool:
    """Insert a sent_alerts row. Returns True if inserted, False if already there (dedup)."""
    stmt = (
        pg_insert(SentAlert)
        .values(subscription_id=sub_id, event_key=event_key)
        .on_conflict_do_nothing(index_elements=["subscription_id", "event_key"])
    )
    result = await session.execute(stmt)
    return (result.rowcount or 0) > 0
