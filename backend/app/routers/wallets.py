"""Wallet router — wallet CRUD, credit, and debit endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.wallet import WalletCreate, WalletResponse, CreditDebitRequest, CreditDebitResponse
from app.services import wallet_service
from app.exceptions import WalletPlatformError

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get("", response_model=list[WalletResponse])
def list_wallets(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all wallets for the current user."""
    wallets = wallet_service.get_user_wallets(db, current_user.id)
    return [
        WalletResponse(
            id=str(w.id),
            currency=w.currency,
            balance=str(w.balance),
            is_active=w.is_active,
            created_at=w.created_at.isoformat(),
        )
        for w in wallets
    ]


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def create_wallet(
    request: WalletCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new wallet for a specific currency."""
    try:
        wallet = wallet_service.create_wallet(db, current_user.id, request.currency)
        return WalletResponse(
            id=str(wallet.id),
            currency=wallet.currency,
            balance=str(wallet.balance),
            is_active=wallet.is_active,
            created_at=wallet.created_at.isoformat(),
        )
    except WalletPlatformError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{wallet_id}/credit", response_model=CreditDebitResponse)
def credit_wallet(
    wallet_id: UUID,
    request: CreditDebitRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Credit (add funds to) a wallet."""
    try:
        tx = wallet_service.credit_wallet(
            db, wallet_id, current_user.id, request.amount, request.description
        )
        return CreditDebitResponse(
            transaction_id=str(tx.id),
            wallet_id=str(tx.wallet_id),
            type=tx.type.value,
            amount=str(tx.amount),
            balance_after=str(tx.balance_after),
            currency=tx.currency,
            description=tx.description,
            created_at=tx.created_at.isoformat(),
        )
    except WalletPlatformError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{wallet_id}/debit", response_model=CreditDebitResponse)
def debit_wallet(
    wallet_id: UUID,
    request: CreditDebitRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Debit (withdraw funds from) a wallet. Returns 422 if insufficient funds."""
    try:
        tx = wallet_service.debit_wallet(
            db, wallet_id, current_user.id, request.amount, request.description
        )
        return CreditDebitResponse(
            transaction_id=str(tx.id),
            wallet_id=str(tx.wallet_id),
            type=tx.type.value,
            amount=str(tx.amount),
            balance_after=str(tx.balance_after),
            currency=tx.currency,
            description=tx.description,
            created_at=tx.created_at.isoformat(),
        )
    except WalletPlatformError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
