from decimal import Decimal

from pydantic import BaseModel, Field


class ExchangeRateResponse(BaseModel):
    base_currency: str
    target_currency: str
    rate: str
    source: str
    updated_at: str

    model_config = {"from_attributes": True}


class FXRatesListResponse(BaseModel):
    base_currency: str
    rates: dict[str, str]
    updated_at: str


class ConversionRequest(BaseModel):
    from_currency: str = Field(
        ..., pattern=r"^[A-Z]{3}$", description="Source currency code"
    )
    to_currency: str = Field(
        ..., pattern=r"^[A-Z]{3}$", description="Target currency code"
    )
    amount: Decimal = Field(
        ..., gt=0, max_digits=18, decimal_places=6, description="Amount to convert"
    )
    idempotency_key: str = Field(
        ..., min_length=10, max_length=255, description="Unique idempotency key"
    )


class ConversionResponse(BaseModel):
    id: str
    from_wallet_id: str
    to_wallet_id: str
    from_amount: str
    to_amount: str
    from_currency: str
    to_currency: str
    rate_applied: str
    idempotency_key: str
    created_at: str

    model_config = {"from_attributes": True}
