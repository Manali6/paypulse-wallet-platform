"""Transaction router — paginated transaction history."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.transaction import TransactionType
from app.repositories import transaction_repo
from app.schemas.transaction import TransactionListResponse, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    wallet_id: UUID | None = Query(None, description="Filter by wallet ID"),
    type: TransactionType | None = Query(
        None, description="Filter by transaction type"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated transaction history for the current user."""

    result = transaction_repo.get_paginated(
        db=db,
        user_id=current_user.id,
        wallet_id=wallet_id,
        tx_type=type,
        page=page,
        page_size=page_size,
    )

    transactions = [
        TransactionResponse(
            id=str(tx.id),
            wallet_id=str(tx.wallet_id),
            type=tx.type.value,
            amount=str(tx.amount),
            currency=tx.currency,
            balance_after=str(tx.balance_after),
            description=tx.description,
            reference_id=str(tx.reference_id) if tx.reference_id else None,
            created_at=tx.created_at.isoformat(),
        )
        for tx in result.transactions
    ]

    return TransactionListResponse(
        transactions=transactions,
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size) < result.total,
    )
