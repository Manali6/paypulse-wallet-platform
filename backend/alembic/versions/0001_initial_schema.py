"""Initial schema — users, wallets, transactions

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column(
            "default_currency", sa.String(3), nullable=False, server_default="USD"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Wallets table
    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column(
            "balance", sa.Numeric(18, 6), nullable=False, server_default="0.000000"
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("user_id", "currency", name="uq_user_currency"),
    )

    # Transactions table
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "wallet_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wallets.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "type",
            sa.Enum(
                "CREDIT",
                "DEBIT",
                "TRANSFER_IN",
                "TRANSFER_OUT",
                "CONVERSION",
                name="transactiontype",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column("amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("balance_after", sa.Numeric(18, 6), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_extra", postgresql.JSON(), nullable=True),
        sa.Column(
            "reference_id", postgresql.UUID(as_uuid=True), nullable=True, index=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("wallets")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS transactiontype")
