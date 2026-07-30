"""Transfer service — user-to-user transfers with pessimistic locking and idempotency controls."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import (
    InsufficientFundsError,
    UserNotFoundError,
    WalletNotFoundError,
    WalletPlatformError,
)
from app.models.transaction import Transaction, TransactionType
from app.models.transfer import Transfer, TransferStatus
from app.models.user import User
from app.models.wallet import Wallet
from app.services.fx_service import get_exchange_rate


def create_transfer(
    db: Session,
    sender_user: User,
    recipient_email: str,
    sent_amount: Decimal,
    currency: str,
    idempotency_key: str,
    description: str | None = None,
) -> Transfer:
    """Execute atomic user-to-user transfer with pessimistic locking & idempotency."""
    currency = currency.upper()

    # 1. Prevent self-transfer by email
    if sender_user.email.lower() == recipient_email.lower():
        raise WalletPlatformError("Cannot transfer funds to yourself", status_code=400)

    # 2. Idempotency Check: Return existing transfer if idempotency_key was already processed
    existing_transfer = (
        db.query(Transfer).filter(Transfer.idempotency_key == idempotency_key).first()
    )
    if existing_transfer:
        return existing_transfer

    # 3. Lookup Recipient User (case-insensitive)
    recipient = db.query(User).filter(User.email.ilike(recipient_email)).first()
    if not recipient:
        raise UserNotFoundError(recipient_email)

    # 4. Find Sender & Receiver Wallets
    sender_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == sender_user.id,
            Wallet.currency == currency,
            Wallet.is_active.is_(True),
        )
        .first()
    )
    if not sender_wallet:
        raise WalletNotFoundError(f"{currency} wallet for sender")

    # Find recipient wallet in requested currency, fallback to recipient's default currency wallet
    receiver_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == recipient.id,
            Wallet.currency == currency,
            Wallet.is_active.is_(True),
        )
        .first()
    )
    if not receiver_wallet:
        receiver_wallet = (
            db.query(Wallet)
            .filter(
                Wallet.user_id == recipient.id,
                Wallet.currency == recipient.default_currency,
                Wallet.is_active.is_(True),
            )
            .first()
        )

    if not receiver_wallet:
        raise WalletNotFoundError(f"Active wallet for recipient {recipient_email}")

    # 5. Pessimistic Locking: Lock both wallets using SELECT FOR UPDATE
    # Order wallet IDs lexicographically to prevent deadlocks when concurrent inverse transfers occur
    first_id, second_id = sorted([sender_wallet.id, receiver_wallet.id])
    db.query(Wallet).filter(
        Wallet.id.in_([first_id, second_id])
    ).with_for_update().all()

    # Refresh in-memory wallet states after acquiring lock
    db.refresh(sender_wallet)
    db.refresh(receiver_wallet)

    # 6. Check Sender Balance
    if sender_wallet.balance < sent_amount:
        raise InsufficientFundsError(
            wallet_id=str(sender_wallet.id),
            requested=float(sent_amount),
            available=float(sender_wallet.balance),
        )

    # 7. Calculate Received Amount
    exchange_rate = get_exchange_rate(
        from_curr=sender_wallet.currency,
        to_curr=receiver_wallet.currency,
    )
    received_amount = (sent_amount * exchange_rate).quantize(Decimal("0.000001"))

    # 8. Update Balances
    sender_wallet.balance -= sent_amount
    receiver_wallet.balance += received_amount

    # 9. Create Transfer Audit Record
    transfer = Transfer(
        sender_wallet_id=sender_wallet.id,
        receiver_wallet_id=receiver_wallet.id,
        sent_amount=sent_amount,
        received_amount=received_amount,
        source_currency=sender_wallet.currency,
        target_currency=receiver_wallet.currency,
        exchange_rate=exchange_rate,
        status=TransferStatus.COMPLETED,
        idempotency_key=idempotency_key,
        description=description,
    )
    db.add(transfer)
    db.flush()  # Generate transfer.id

    # 10. Record Ledger Transactions for Sender (TRANSFER_OUT) and Receiver (TRANSFER_IN)
    tx_sender = Transaction(
        wallet_id=sender_wallet.id,
        type=TransactionType.TRANSFER_OUT,
        amount=sent_amount,
        currency=sender_wallet.currency,
        balance_after=sender_wallet.balance,
        description=f"Transfer to {recipient.email}: {description or ''}".strip(),
        reference_id=transfer.id,
    )
    tx_receiver = Transaction(
        wallet_id=receiver_wallet.id,
        type=TransactionType.TRANSFER_IN,
        amount=received_amount,
        currency=receiver_wallet.currency,
        balance_after=receiver_wallet.balance,
        description=f"Transfer from {sender_user.email}: {description or ''}".strip(),
        reference_id=transfer.id,
    )
    db.add(tx_sender)
    db.add(tx_receiver)

    db.commit()
    db.refresh(transfer)
    return transfer


def get_user_transfers(db: Session, user_id: UUID) -> list[Transfer]:
    """Get all transfers sent or received by a user."""
    user_wallet_ids = (
        db.query(Wallet.id).filter(Wallet.user_id == user_id, Wallet.is_active).all()
    )
    wallet_id_list = [w_id for (w_id,) in user_wallet_ids]

    if not wallet_id_list:
        return []

    return (
        db.query(Transfer)
        .filter(
            (Transfer.sender_wallet_id.in_(wallet_id_list))
            | (Transfer.receiver_wallet_id.in_(wallet_id_list))
        )
        .order_by(Transfer.created_at.desc())
        .all()
    )
