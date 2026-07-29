"""Custom domain exceptions for the Wallet Platform."""


class WalletPlatformError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InsufficientFundsError(WalletPlatformError):
    """Raised when a wallet doesn't have enough balance for a debit."""

    def __init__(self, wallet_id: str, requested: float, available: float):
        super().__init__(
            message=f"Insufficient funds in wallet {wallet_id}. "
            f"Requested: {requested}, Available: {available}",
            status_code=422,
        )
        self.wallet_id = wallet_id
        self.requested = requested
        self.available = available


class WalletNotFoundError(WalletPlatformError):
    """Raised when a wallet is not found."""

    def __init__(self, wallet_id: str):
        super().__init__(
            message=f"Wallet not found: {wallet_id}",
            status_code=404,
        )


class DuplicateWalletError(WalletPlatformError):
    """Raised when a user tries to create a wallet for a currency they already have."""

    def __init__(self, currency: str):
        super().__init__(
            message=f"Wallet already exists for currency: {currency}",
            status_code=409,
        )


class InvalidCurrencyError(WalletPlatformError):
    """Raised when an unsupported currency code is provided."""

    def __init__(self, currency: str):
        super().__init__(
            message=f"Unsupported currency: {currency}",
            status_code=400,
        )


class UserNotFoundError(WalletPlatformError):
    """Raised when a user is not found."""

    def __init__(self, identifier: str):
        super().__init__(
            message=f"User not found: {identifier}",
            status_code=404,
        )


class AuthenticationError(WalletPlatformError):
    """Raised for authentication failures."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, status_code=401)


class DuplicateEmailError(WalletPlatformError):
    """Raised when a user tries to sign up with an existing email."""

    def __init__(self, email: str):
        super().__init__(
            message=f"Email already registered: {email}",
            status_code=409,
        )
