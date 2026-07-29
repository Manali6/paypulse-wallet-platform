"""Add exchange_rates and conversion_records tables

Revision ID: 0003
Revises: 0002
Create Date: 2025-01-03 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # exchange_rates table
    op.create_table(
        "exchange_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("base_currency", sa.String(3), nullable=False, index=True),
        sa.Column("target_currency", sa.String(3), nullable=False, index=True),
        sa.Column("rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="external_api"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        sa.UniqueConstraint("base_currency", "target_currency", name="uq_base_target_currency"),
    )

    # conversion_records table
    op.create_table(
        "conversion_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("to_wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("to_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("from_currency", sa.String(3), nullable=False),
        sa.Column("to_currency", sa.String(3), nullable=False),
        sa.Column("rate_applied", sa.Numeric(18, 8), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("conversion_records")
    op.drop_table("exchange_rates")
