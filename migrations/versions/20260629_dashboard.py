"""add users.dashboard_message_id

Revision ID: 20260629_dashboard
Revises: 20260504_initial
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260629_dashboard"
down_revision: str | None = "20260504_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("dashboard_message_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "dashboard_message_id")
