from decimal import Decimal

from pydantic import BaseModel, Field


class WalletCreate(BaseModel):
    currency: str = Field(
        ..., pattern=r"^[A-Z]{3}$", description="ISO 4217 currency code"
    )


class WalletResponse(BaseModel):
    id: str
    currency: str
    balance: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class CreditDebitRequest(BaseModel):
    amount: Decimal = Field(
        ..., gt=0, max_digits=18, decimal_places=6, description="Amount to credit/debit"
    )
    description: str | None = Field(
        None, max_length=500, description="Optional description"
    )


class CreditDebitResponse(BaseModel):
    transaction_id: str
    wallet_id: str
    type: str
    amount: str
    balance_after: str
    currency: str
    description: str | None
    created_at: str
