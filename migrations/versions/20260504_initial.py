"""initial schema

Revision ID: 20260504_initial
Revises:
Create Date: 2026-05-04

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260504_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "queues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("raw_name", sa.Text(), nullable=False),
        sa.Column("display_pl", sa.Text(), nullable=False),
        sa.Column("display_ru", sa.Text(), nullable=False),
        sa.Column(
            "first_seen", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "last_seen", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "snapshots",
        sa.Column("queue_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ticket_count", sa.Integer(), nullable=False),
        sa.Column("tickets_served", sa.Integer(), nullable=False),
        sa.Column("ticket_value", sa.String(length=16), nullable=True),
        sa.Column("registered_tickets", sa.Integer(), nullable=False),
        sa.Column("max_tickets", sa.Integer(), nullable=True),
        sa.Column("tickets_left", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("avg_wait_api", sa.Integer(), nullable=True),
        sa.Column("avg_service_api", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["queue_id"], ["queues.id"]),
        sa.PrimaryKeyConstraint("queue_id", "ts"),
    )

    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "language", sa.String(length=8), nullable=False, server_default=sa.text("'pl'")
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "last_seen", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("telegram_id"),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("queue_id", sa.Integer(), nullable=False),
        sa.Column("my_ticket", sa.String(length=16), nullable=True),
        sa.Column(
            "alert_on_my_call",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("alert_n_before", sa.Integer(), nullable=True),
        sa.Column(
            "alert_on_open",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "alert_on_slots",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["queue_id"], ["queues.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "queue_id", name="uq_subscription_user_queue"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_queue_id", "subscriptions", ["queue_id"])

    op.create_table(
        "sent_alerts",
        sa.Column("subscription_id", sa.BigInteger(), nullable=False),
        sa.Column("event_key", sa.String(length=64), nullable=False),
        sa.Column(
            "sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("subscription_id", "event_key"),
    )


def downgrade() -> None:
    op.drop_table("sent_alerts")
    op.drop_index("ix_subscriptions_queue_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_table("users")
    op.drop_table("snapshots")
    op.drop_table("queues")
