"""Add transfers table

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-02 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transfers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sender_wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("receiver_wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sent_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("received_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("source_currency", sa.String(3), nullable=False),
        sa.Column("target_currency", sa.String(3), nullable=False),
        sa.Column("exchange_rate", sa.Numeric(18, 8), nullable=False, server_default="1.00000000"),
        sa.Column("status", sa.Enum("COMPLETED", "FAILED", name="transferstatus"), nullable=False, index=True, server_default="COMPLETED"),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("transfers")
    op.execute("DROP TYPE IF EXISTS transferstatus")
