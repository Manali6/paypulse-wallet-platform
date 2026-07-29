from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class UserSearchResult(BaseModel):
    id: str
    email: str
    display_name: str
    default_currency: str

    model_config = {"from_attributes": True}


class TransferRequest(BaseModel):
    recipient_email: EmailStr = Field(..., description="Email address of the recipient")
    amount: Decimal = Field(
        ..., gt=0, max_digits=18, decimal_places=6, description="Amount to send"
    )
    currency: str = Field(..., pattern=r"^[A-Z]{3}$", description="Source currency")
    idempotency_key: str = Field(
        ..., min_length=10, max_length=255, description="Unique idempotency key"
    )
    description: str | None = Field(None, max_length=500, description="Optional note")


class TransferResponse(BaseModel):
    id: str
    sender_wallet_id: str
    receiver_wallet_id: str
    sent_amount: str
    received_amount: str
    source_currency: str
    target_currency: str
    exchange_rate: str
    status: str
    idempotency_key: str
    description: str | None
    created_at: str

    model_config = {"from_attributes": True}
