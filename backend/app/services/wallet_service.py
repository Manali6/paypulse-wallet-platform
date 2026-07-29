"""Wallet service — business logic for wallet operations."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.transaction import Transaction, TransactionType
from app.currencies import is_valid_currency
from app.exceptions import (
    InsufficientFundsError,
    DuplicateWalletError,
    InvalidCurrencyError,
    WalletNotFoundError,
)


def create_wallet(db: Session, user_id: UUID, currency: str) -> Wallet:
    """Create a new wallet for a user in the specified currency."""
    currency = currency.upper()

    if not is_valid_currency(currency):
        raise InvalidCurrencyError(currency)

    # Check for existing wallet with same currency
    existing = (
        db.query(Wallet)
        .filter(Wallet.user_id == user_id, Wallet.currency == currency)
        .first()
    )
    if existing:
        raise DuplicateWalletError(currency)

    wallet = Wallet(
        user_id=user_id,
        currency=currency,
        balance=Decimal("0.000000"),
        is_active=True,
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def get_user_wallets(db: Session, user_id: UUID) -> list[Wallet]:
    """Get all wallets for a user."""
    return (
        db.query(Wallet)
        .filter(Wallet.user_id == user_id, Wallet.is_active == True)
        .order_by(Wallet.created_at)
        .all()
    )


def get_wallet_by_id(db: Session, wallet_id: UUID, user_id: UUID) -> Wallet:
    """Get a specific wallet, ensuring it belongs to the user."""
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == wallet_id,
            Wallet.user_id == user_id,
            Wallet.is_active == True,
        )
        .first()
    )
    if not wallet:
        raise WalletNotFoundError(str(wallet_id))
    return wallet


def credit_wallet(
    db: Session, wallet_id: UUID, user_id: UUID, amount: Decimal, description: str | None = None
) -> Transaction:
    """Credit (add funds to) a wallet. Returns the created transaction."""
    wallet = get_wallet_by_id(db, wallet_id, user_id)

    wallet.balance += amount
    new_balance = wallet.balance

    transaction = Transaction(
        wallet_id=wallet.id,
        type=TransactionType.CREDIT,
        amount=amount,
        currency=wallet.currency,
        balance_after=new_balance,
        description=description or "Credit",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def debit_wallet(
    db: Session, wallet_id: UUID, user_id: UUID, amount: Decimal, description: str | None = None
) -> Transaction:
    """Debit (withdraw funds from) a wallet. Checks for sufficient balance."""
    wallet = get_wallet_by_id(db, wallet_id, user_id)

    if wallet.balance < amount:
        raise InsufficientFundsError(
            wallet_id=str(wallet_id),
            requested=float(amount),
            available=float(wallet.balance),
        )

    wallet.balance -= amount
    new_balance = wallet.balance

    transaction = Transaction(
        wallet_id=wallet.id,
        type=TransactionType.DEBIT,
        amount=amount,
        currency=wallet.currency,
        balance_after=new_balance,
        description=description or "Debit",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
