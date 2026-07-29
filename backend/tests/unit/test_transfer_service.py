"""Unit tests for transfer_service — same-currency, cross-currency, idempotency, and balance checks."""

from decimal import Decimal
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from app.exceptions import (
    InsufficientFundsError,
    UserNotFoundError,
    WalletNotFoundError,
    WalletPlatformError,
)
from app.models.user import User
from app.models.wallet import Wallet
from app.services.transfer_service import (
    calculate_exchange_rate,
    create_transfer,
)


class TestExchangeRateCalculation:
    def test_same_currency_rate(self):
        assert calculate_exchange_rate("USD", "USD") == Decimal("1.00000000")
        assert calculate_exchange_rate("EUR", "EUR") == Decimal("1.00000000")

    def test_cross_currency_rate(self):
        # EUR (1.08) to USD (1.00) => 1.08
        rate = calculate_exchange_rate("EUR", "USD")
        assert rate == Decimal("1.08000000")


class TestCreateTransferValidation:
    def test_self_transfer_fails(self):
        db = MagicMock()
        sender = User()
        sender.email = "sender@example.com"

        with pytest.raises(WalletPlatformError) as exc_info:
            create_transfer(
                db=db,
                sender_user=sender,
                recipient_email="sender@example.com",
                sent_amount=Decimal("100"),
                currency="USD",
                idempotency_key="key-1234567890",
            )
        assert exc_info.value.status_code == 400

    def test_recipient_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.side_effect = [
            None,  # Idempotency check returns None
            None,  # User lookup by email returns None
        ]

        sender = User()
        sender.id = uuid4()
        sender.email = "sender@example.com"

        with pytest.raises(UserNotFoundError):
            create_transfer(
                db=db,
                sender_user=sender,
                recipient_email="nobody@example.com",
                sent_amount=Decimal("100"),
                currency="USD",
                idempotency_key="key-1234567890",
            )

    def test_sender_wallet_not_found(self):
        db = MagicMock()

        sender = User()
        sender.id = uuid4()
        sender.email = "sender@example.com"

        recipient = User()
        recipient.id = uuid4()
        recipient.email = "recipient@example.com"

        db.query.return_value.filter.return_value.first.side_effect = [
            None,  # Idempotency check
            recipient,  # User lookup
            None,  # Sender wallet lookup returns None
        ]

        with pytest.raises(WalletNotFoundError):
            create_transfer(
                db=db,
                sender_user=sender,
                recipient_email="recipient@example.com",
                sent_amount=Decimal("100"),
                currency="USD",
                idempotency_key="key-1234567890",
            )

    def test_insufficient_funds_fails(self):
        db = MagicMock()

        sender = User()
        sender.id = uuid4()
        sender.email = "sender@example.com"

        recipient = User()
        recipient.id = uuid4()
        recipient.email = "recipient@example.com"

        sender_wallet = Wallet()
        sender_wallet.id = uuid4()
        sender_wallet.user_id = sender.id
        sender_wallet.currency = "USD"
        sender_wallet.balance = Decimal("20.000000")

        receiver_wallet = Wallet()
        receiver_wallet.id = uuid4()
        receiver_wallet.user_id = recipient.id
        receiver_wallet.currency = "USD"
        receiver_wallet.balance = Decimal("0.000000")

        db.query.return_value.filter.return_value.first.side_effect = [
            None,  # Idempotency check
            recipient,  # User lookup
            sender_wallet,  # Sender wallet
            receiver_wallet,  # Receiver wallet
        ]
        db.query.return_value.filter.return_value.with_for_update.return_value.all.return_value = [
            sender_wallet,
            receiver_wallet,
        ]

        with pytest.raises(InsufficientFundsError):
            create_transfer(
                db=db,
                sender_user=sender,
                recipient_email="recipient@example.com",
                sent_amount=Decimal("100"),
                currency="USD",
                idempotency_key="key-1234567890",
            )
