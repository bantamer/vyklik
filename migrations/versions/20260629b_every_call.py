"""add subscriptions.alert_every_call

Revision ID: 20260629b_every_call
Revises: 20260629_dashboard
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260629b_every_call"
down_revision: str | None = "20260629_dashboard"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column(
            "alert_every_call",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "alert_every_call")
