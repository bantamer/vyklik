from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Queue(Base):
    __tablename__ = "queues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # DUW's id, not autoincrement
    raw_name: Mapped[str] = mapped_column(Text, nullable=False)
    display_pl: Mapped[str] = mapped_column(Text, nullable=False)
    display_ru: Mapped[str] = mapped_column(Text, nullable=False)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Snapshot(Base):
    __tablename__ = "snapshots"

    queue_id: Mapped[int] = mapped_column(Integer, ForeignKey("queues.id"), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    ticket_count: Mapped[int] = mapped_column(Integer, nullable=False)
    tickets_served: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_value: Mapped[str | None] = mapped_column(String(16))
    registered_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    max_tickets: Mapped[int | None] = mapped_column(Integer)
    tickets_left: Mapped[int | None] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    avg_wait_api: Mapped[int | None] = mapped_column(Integer)
    avg_service_api: Mapped[int | None] = mapped_column(Integer)


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="pl")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "queue_id", name="uq_subscription_user_queue"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True
    )
    queue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("queues.id"), nullable=False, index=True
    )
    my_ticket: Mapped[str | None] = mapped_column(String(16))
    alert_on_my_call: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    alert_n_before: Mapped[int | None] = mapped_column(Integer)
    alert_on_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alert_on_slots: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="subscriptions")


class SentAlert(Base):
    __tablename__ = "sent_alerts"

    subscription_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    event_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
