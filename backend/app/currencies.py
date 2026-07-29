"""Supported currencies for the platform."""

SUPPORTED_CURRENCIES: set[str] = {
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY",
    "INR", "MXN", "BRL", "KRW", "SGD", "HKD", "NOK", "SEK",
    "DKK", "NZD", "ZAR", "THB", "PLN", "TWD", "TRY", "AED",
    "SAR", "PHP", "MYR", "IDR", "RUB", "CZK",
}


def is_valid_currency(currency: str) -> bool:
    """Check if a currency code is supported."""
    return currency.upper() in SUPPORTED_CURRENCIES
