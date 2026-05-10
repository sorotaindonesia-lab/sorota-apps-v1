"""add customer conversation state

Revision ID: 20260510_0002
Revises: 20260510_0001
Create Date: 2026-05-10 00:00:01.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260510_0002"
down_revision: str | None = "20260510_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("conversation_state", sa.String(), nullable=False, server_default="NEW"),
    )


def downgrade() -> None:
    op.drop_column("customers", "conversation_state")
