"""Transaction repository — database queries for transaction history."""

from uuid import UUID
from typing import NamedTuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction, TransactionType
from app.models.wallet import Wallet


class PaginatedTransactions(NamedTuple):
    transactions: list[Transaction]
    total: int


def get_paginated(
    db: Session,
    user_id: UUID,
    wallet_id: UUID | None = None,
    tx_type: TransactionType | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedTransactions:
    """Get paginated transactions for a user, optionally filtered by wallet and type."""

    # Base query: all transactions for user's wallets
    query = (
        db.query(Transaction)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .filter(Wallet.user_id == user_id)
    )

    # Apply filters
    if wallet_id:
        query = query.filter(Transaction.wallet_id == wallet_id)
    if tx_type:
        query = query.filter(Transaction.type == tx_type)

    # Get total count
    total = query.count()

    # Paginate
    transactions = (
        query.order_by(Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedTransactions(transactions=transactions, total=total)
