"""Unit tests for fx_service — exchange rate calculations, conversion logic, and idempotency."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import WalletPlatformError
from app.models.user import User
from app.services.fx_service import (
    convert_wallet_currency,
    get_exchange_rate,
)


class TestFXRates:
    def test_same_currency_exchange_rate(self):
        assert get_exchange_rate("USD", "USD") == Decimal("1.00000000")
        assert get_exchange_rate("EUR", "EUR") == Decimal("1.00000000")

    @patch("app.services.fx_service.get_current_exchange_rates")
    def test_cross_currency_exchange_rate(self, mock_rates):
        mock_rates.return_value = (
            {
                "USD": Decimal("1.0"),
                "EUR": Decimal("0.90"),
                "GBP": Decimal("0.80"),
            },
            "redis_cache",
        )
        # EUR to GBP => 0.80 / 0.90 = 0.88888889
        rate = get_exchange_rate("EUR", "GBP")
        assert rate == Decimal("0.88888889")


class TestCurrencyConversionValidation:
    def test_same_currency_conversion_fails(self):
        db = MagicMock()
        user = User()

        with pytest.raises(WalletPlatformError) as exc_info:
            convert_wallet_currency(
                db=db,
                user=user,
                from_currency="USD",
                to_currency="USD",
                from_amount=Decimal(50),
                idempotency_key="key-1234567890",
            )
        assert exc_info.value.status_code == 400
