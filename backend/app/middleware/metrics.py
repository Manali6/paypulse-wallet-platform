"""Custom Prometheus metrics for the Wallet Platform."""

from prometheus_client import Counter, Histogram

# HTTP error counter — tracks 4xx/5xx responses by status code, path, and method.
# This is the primary metric for detecting increased error rates.
http_errors_total = Counter(
    "http_errors_total",
    "Total HTTP error responses (4xx/5xx)",
    ["status_code", "path", "method"],
)

# Business metrics
wallets_created_total = Counter(
    "wallets_created_total",
    "Total wallets created",
    ["currency"],
)

transactions_total = Counter(
    "transactions_total",
    "Total transactions processed",
    ["type"],  # CREDIT, DEBIT, TRANSFER_IN, etc.
)

# FX rate fetch duration (for future use)
fx_rate_fetch_duration_seconds = Histogram(
    "fx_rate_fetch_duration_seconds",
    "Time to fetch exchange rates from external API",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)
