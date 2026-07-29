"""FX Router — exchange rates, currency conversion, and history endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import WalletPlatformError
from app.schemas.fx import (
    ConversionRequest,
    ConversionResponse,
    FXRatesListResponse,
)
from app.services import fx_service

router = APIRouter(prefix="/fx", tags=["Exchange & FX"])


@router.get("/rates", response_model=FXRatesListResponse)
def get_rates(base: str = Query("USD", pattern=r"^[A-Z]{3}$")):
    """Get latest exchange rates for a base currency (backed by Redis cache)."""
    rates, _ = fx_service.get_current_exchange_rates(base)
    from datetime import datetime, timezone

    return FXRatesListResponse(
        base_currency=base.upper(),
        rates={k: str(v) for k, v in rates.items()},
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post(
    "/convert", response_model=ConversionResponse, status_code=status.HTTP_201_CREATED
)
def convert_currency(
    request: ConversionRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Convert funds between user's own wallets with FX rate audit logging."""
    try:
        record = fx_service.convert_wallet_currency(
            db=db,
            user=current_user,
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            from_amount=request.amount,
            idempotency_key=request.idempotency_key,
        )
        return ConversionResponse(
            id=str(record.id),
            from_wallet_id=str(record.from_wallet_id),
            to_wallet_id=str(record.to_wallet_id),
            from_amount=str(record.from_amount),
            to_amount=str(record.to_amount),
            from_currency=record.from_currency,
            to_currency=record.to_currency,
            rate_applied=str(record.rate_applied),
            idempotency_key=record.idempotency_key,
            created_at=record.created_at.isoformat(),
        )
    except WalletPlatformError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/conversions", response_model=list[ConversionResponse])
def list_conversions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List conversion history for the current user."""
    records = fx_service.get_user_conversions(db, current_user.id)
    return [
        ConversionResponse(
            id=str(r.id),
            from_wallet_id=str(r.from_wallet_id),
            to_wallet_id=str(r.to_wallet_id),
            from_amount=str(r.from_amount),
            to_amount=str(r.to_amount),
            from_currency=r.from_currency,
            to_currency=r.to_currency,
            rate_applied=str(r.rate_applied),
            idempotency_key=r.idempotency_key,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]


@router.post("/refresh", status_code=status.HTTP_200_OK)
def trigger_refresh():
    """Manual trigger to fetch external FX rates and update cache (Admin/Dev)."""
    fx_service.refresh_exchange_rates_job()
    return {"message": "Exchange rates refreshed successfully"}
