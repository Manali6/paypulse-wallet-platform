"""Transfers router — user-to-user transfer endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import WalletPlatformError
from app.schemas.transfer import TransferRequest, TransferResponse
from app.services import transfer_service

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def initiate_transfer(
    request: TransferRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initiate a user-to-user transfer with idempotency control."""
    try:
        transfer = transfer_service.create_transfer(
            db=db,
            sender_user=current_user,
            recipient_email=request.recipient_email,
            sent_amount=request.amount,
            currency=request.currency,
            idempotency_key=request.idempotency_key,
            description=request.description,
        )
        return TransferResponse(
            id=str(transfer.id),
            sender_wallet_id=str(transfer.sender_wallet_id),
            receiver_wallet_id=str(transfer.receiver_wallet_id),
            sent_amount=str(transfer.sent_amount),
            received_amount=str(transfer.received_amount),
            source_currency=transfer.source_currency,
            target_currency=transfer.target_currency,
            exchange_rate=str(transfer.exchange_rate),
            status=transfer.status.value,
            idempotency_key=transfer.idempotency_key,
            description=transfer.description,
            created_at=transfer.created_at.isoformat(),
        )
    except WalletPlatformError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("", response_model=list[TransferResponse])
def list_transfers(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List sent and received transfers for the current user."""
    transfers = transfer_service.get_user_transfers(db, current_user.id)
    return [
        TransferResponse(
            id=str(t.id),
            sender_wallet_id=str(t.sender_wallet_id),
            receiver_wallet_id=str(t.receiver_wallet_id),
            sent_amount=str(t.sent_amount),
            received_amount=str(t.received_amount),
            source_currency=t.source_currency,
            target_currency=t.target_currency,
            exchange_rate=str(t.exchange_rate),
            status=t.status.value,
            idempotency_key=t.idempotency_key,
            description=t.description,
            created_at=t.created_at.isoformat(),
        )
        for t in transfers
    ]
