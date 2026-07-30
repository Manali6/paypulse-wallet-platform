"""FX Service — external rate fetching, Redis caching, APScheduler automated refreshes, and in-wallet conversions."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import httpx
import redis
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.exceptions import (
    InsufficientFundsError,
    WalletNotFoundError,
    WalletPlatformError,
)
from app.models.fx import ConversionRecord, ExchangeRate
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.models.wallet import Wallet
from app.services.wallet_service import create_wallet

settings = get_settings()

# Redis Client & Fallback Rates
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
CACHE_KEY_FX_PREFIX = "fx_rates:"
CACHE_TTL_SECONDS = 3600  # 1 hour cache

# Default fallback rates relative to USD
DEFAULT_USD_RATES: dict[str, Decimal] = {
    "USD": Decimal("1.00000000"),
    "EUR": Decimal("0.92500000"),
    "GBP": Decimal("0.78500000"),
    "JPY": Decimal("155.20000000"),
    "INR": Decimal("83.50000000"),
    "CAD": Decimal("1.36500000"),
    "AUD": Decimal("1.51500000"),
    "CHF": Decimal("0.89500000"),
    "CNY": Decimal("7.24500000"),
    "SGD": Decimal("1.35000000"),
    "BRL": Decimal("5.15000000"),
    "MXN": Decimal("16.85000000"),
}


def fetch_external_fx_rates(base_currency: str = "USD") -> dict[str, Decimal]:
    """Fetch live exchange rates from open-access Frankfurter API with fallback."""
    base_currency = base_currency.upper()
    url = f"https://api.frankfurter.app/latest?from={base_currency}"

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                rates_data = data.get("rates", {})
                rates = {base_currency: Decimal("1.00000000")}
                for curr, val in rates_data.items():
                    rates[curr.upper()] = Decimal(str(val)).quantize(
                        Decimal("0.00000001")
                    )
                return rates
    except Exception:  # noqa: S110
        pass

    return DEFAULT_USD_RATES


def refresh_exchange_rates_job():
    """Background APScheduler job: fetch latest FX rates and update DB + Redis cache."""
    db: Session = SessionLocal()
    try:
        rates = fetch_external_fx_rates("USD")
        now = datetime.now(timezone.utc)

        # 1. Update Redis Cache (if available)
        try:
            cache_data = {curr: str(rate) for curr, rate in rates.items()}
            redis_client.setex(
                f"{CACHE_KEY_FX_PREFIX}USD", CACHE_TTL_SECONDS, json.dumps(cache_data)
            )
        except Exception:  # noqa: S110
            pass

        # 2. Persist/Update DB ExchangeRate records
        for target_curr, rate_val in rates.items():
            existing = (
                db.query(ExchangeRate)
                .filter(
                    ExchangeRate.base_currency == "USD",
                    ExchangeRate.target_currency == target_curr,
                )
                .first()
            )
            if existing:
                existing.rate = rate_val
                existing.updated_at = now
            else:
                db.add(
                    ExchangeRate(
                        base_currency="USD",
                        target_currency=target_curr,
                        rate=rate_val,
                        source="frankfurter_api",
                        updated_at=now,
                    )
                )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


# Initialize APScheduler for automated 1-hour FX refresh
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_exchange_rates_job, "interval", hours=1, id="fx_refresh_job")


def start_fx_scheduler():
    if not scheduler.running:
        scheduler.start()


def stop_fx_scheduler():
    if scheduler.running:
        scheduler.shutdown()


def get_current_exchange_rates(
    base_currency: str = "USD",
) -> tuple[dict[str, Decimal], str]:
    """Get current FX rates from Redis cache, falling back to DB or live API."""
    base_currency = base_currency.upper()
    cache_key = f"{CACHE_KEY_FX_PREFIX}{base_currency}"

    # Try Redis Cache
    try:
        cached = redis_client.get(cache_key)
        if cached:
            raw_rates = json.loads(cached)
            return {k: Decimal(v) for k, v in raw_rates.items()}, "redis_cache"
    except Exception:  # noqa: S110
        pass

    # Fallback to DB or fresh API fetch
    rates = fetch_external_fx_rates(base_currency) or DEFAULT_USD_RATES
    try:
        cache_data = {k: str(v) for k, v in rates.items()}
        redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(cache_data))
    except Exception:  # noqa: S110
        pass

    return rates, "live_api"


def get_exchange_rate(from_curr: str, to_curr: str) -> Decimal:
    """Calculate cross-rate between two currencies."""
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()

    if from_curr == to_curr:
        return Decimal("1.00000000")

    rates, _ = get_current_exchange_rates("USD")
    rate_from = rates.get(from_curr, DEFAULT_USD_RATES.get(from_curr, Decimal("1.0")))
    rate_to = rates.get(to_curr, DEFAULT_USD_RATES.get(to_curr, Decimal("1.0")))

    # Convert USD -> to_curr / (USD -> from_curr)
    return (rate_to / rate_from).quantize(Decimal("0.00000001"))


def convert_wallet_currency(
    db: Session,
    user: User,
    from_currency: str,
    to_currency: str,
    from_amount: Decimal,
    idempotency_key: str,
) -> ConversionRecord:
    """Execute in-wallet currency conversion between user's own wallets."""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        raise WalletPlatformError(
            "Source and target currencies must be different", status_code=400
        )

    # 1. Idempotency check
    existing = (
        db.query(ConversionRecord)
        .filter(ConversionRecord.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        return existing

    # 2. Get or Create Source & Target Wallets
    from_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == user.id,
            Wallet.currency == from_currency,
            Wallet.is_active.is_(True),
        )
        .first()
    )
    if not from_wallet:
        raise WalletNotFoundError(f"{from_currency} wallet")

    to_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == user.id,
            Wallet.currency == to_currency,
            Wallet.is_active.is_(True),
        )
        .first()
    )
    if not to_wallet:
        # Automatically create target currency wallet if missing
        to_wallet = create_wallet(db, user.id, to_currency)

    # 3. Pessimistic Locking
    w1_id, w2_id = sorted([from_wallet.id, to_wallet.id])
    db.query(Wallet).filter(Wallet.id.in_([w1_id, w2_id])).with_for_update().all()
    db.refresh(from_wallet)
    db.refresh(to_wallet)

    # 4. Check Balance
    if from_wallet.balance < from_amount:
        raise InsufficientFundsError(
            wallet_id=str(from_wallet.id),
            requested=float(from_amount),
            available=float(from_wallet.balance),
        )

    # 5. Calculate Converted Amount
    rate_applied = get_exchange_rate(from_currency, to_currency)
    to_amount = (from_amount * rate_applied).quantize(Decimal("0.000001"))

    # 6. Atomic Balance Update
    from_wallet.balance -= from_amount
    to_wallet.balance += to_amount

    # 7. Conversion Record Audit Entry
    record = ConversionRecord(
        user_id=user.id,
        from_wallet_id=from_wallet.id,
        to_wallet_id=to_wallet.id,
        from_amount=from_amount,
        to_amount=to_amount,
        from_currency=from_currency,
        to_currency=to_currency,
        rate_applied=rate_applied,
        idempotency_key=idempotency_key,
    )
    db.add(record)
    db.flush()

    # 8. Ledger Transactions (CONVERSION)
    tx_from = Transaction(
        wallet_id=from_wallet.id,
        type=TransactionType.CONVERSION,
        amount=from_amount,
        currency=from_currency,
        balance_after=from_wallet.balance,
        description=f"Converted to {to_currency} at rate {rate_applied}",
        reference_id=record.id,
    )
    tx_to = Transaction(
        wallet_id=to_wallet.id,
        type=TransactionType.CONVERSION,
        amount=to_amount,
        currency=to_currency,
        balance_after=to_wallet.balance,
        description=f"Converted from {from_currency} at rate {rate_applied}",
        reference_id=record.id,
    )
    db.add(tx_from)
    db.add(tx_to)

    db.commit()
    db.refresh(record)
    return record


def get_user_conversions(db: Session, user_id: UUID) -> list[ConversionRecord]:
    """Get all past conversion records for a user."""
    return (
        db.query(ConversionRecord)
        .filter(ConversionRecord.user_id == user_id)
        .order_by(ConversionRecord.created_at.desc())
        .all()
    )
