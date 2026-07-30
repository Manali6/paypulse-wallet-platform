"""Unit tests for wallet_service — wallet creation, credit, and debit logic."""

from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.exceptions import (
    DuplicateWalletError,
    InsufficientFundsError,
    InvalidCurrencyError,
    WalletNotFoundError,
)
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.services.wallet_service import create_wallet, credit_wallet, debit_wallet


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    db.commit = MagicMock()
    db.add = MagicMock()
    db.refresh = MagicMock()
    return db


class TestCreateWallet:
    """Tests for wallet creation."""

    def test_create_wallet_invalid_currency(self, mock_db):
        with pytest.raises(InvalidCurrencyError):
            create_wallet(mock_db, uuid4(), "XYZ")

    def test_create_wallet_duplicate_currency(self, mock_db):
        # Simulate existing wallet found
        mock_db.query.return_value.filter.return_value.first.return_value = Wallet()
        with pytest.raises(DuplicateWalletError):
            create_wallet(mock_db, uuid4(), "USD")

    def test_create_wallet_success(self, mock_db):
        # No existing wallet
        mock_db.query.return_value.filter.return_value.first.return_value = None

        def refresh_side_effect(obj):
            obj.id = uuid4()
            obj.balance = Decimal("0.000000")
            obj.is_active = True
            from datetime import datetime, timezone

            obj.created_at = datetime.now(timezone.utc)

        mock_db.refresh.side_effect = refresh_side_effect

        create_wallet(mock_db, uuid4(), "USD")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestCreditWallet:
    """Tests for wallet credit operations."""

    def test_credit_wallet_not_found(self, mock_db):
        # Wallet query returns None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
        with pytest.raises(WalletNotFoundError):
            credit_wallet(mock_db, uuid4(), uuid4(), Decimal(100))

    def test_credit_wallet_success(self, mock_db):
        wallet = Wallet()
        wallet.id = uuid4()
        wallet.balance = Decimal("50.000000")
        wallet.currency = "USD"
        wallet.is_active = True

        mock_db.query.return_value.filter.return_value.first.return_value = wallet
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = wallet

        def refresh_side_effect(obj):
            if isinstance(obj, Transaction):
                obj.id = uuid4()
                from datetime import datetime, timezone

                obj.created_at = datetime.now(timezone.utc)

        mock_db.refresh.side_effect = refresh_side_effect

        credit_wallet(mock_db, wallet.id, uuid4(), Decimal(100))
        assert wallet.balance == Decimal("150.000000")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestDebitWallet:
    """Tests for wallet debit operations."""

    def test_debit_wallet_insufficient_funds(self, mock_db):
        wallet = Wallet()
        wallet.id = uuid4()
        wallet.balance = Decimal("10.000000")
        wallet.currency = "USD"
        wallet.is_active = True

        mock_db.query.return_value.filter.return_value.first.return_value = wallet
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = wallet

        with pytest.raises(InsufficientFundsError):
            debit_wallet(mock_db, wallet.id, uuid4(), Decimal(100))

    def test_debit_wallet_exact_balance(self, mock_db):
        wallet = Wallet()
        wallet.id = uuid4()
        wallet.balance = Decimal("100.000000")
        wallet.currency = "USD"
        wallet.is_active = True

        mock_db.query.return_value.filter.return_value.first.return_value = wallet
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = wallet

        def refresh_side_effect(obj):
            if isinstance(obj, Transaction):
                obj.id = uuid4()
                from datetime import datetime, timezone

                obj.created_at = datetime.now(timezone.utc)

        mock_db.refresh.side_effect = refresh_side_effect

        debit_wallet(mock_db, wallet.id, uuid4(), Decimal(100))
        assert wallet.balance == Decimal("0.000000")

    def test_debit_wallet_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
        with pytest.raises(WalletNotFoundError):
            debit_wallet(mock_db, uuid4(), uuid4(), Decimal(50))
