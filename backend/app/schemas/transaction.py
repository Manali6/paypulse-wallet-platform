from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    id: str
    wallet_id: str
    type: str
    amount: str
    currency: str
    balance_after: str
    description: str | None
    reference_id: str | None
    created_at: str

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
