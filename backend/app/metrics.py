"""Custom Prometheus metrics for financial operations and platform monitoring."""

from prometheus_client import Counter, Histogram

# HTTP Error Counter
HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total HTTP 4xx/5xx error responses",
    ["status_code", "method", "path"],
)

# Financial Counters
WALLET_TRANSFERS_TOTAL = Counter(
    "wallet_transfers_total",
    "Total user-to-user transfers",
    ["status", "source_currency", "target_currency"],
)

CURRENCY_CONVERSIONS_TOTAL = Counter(
    "currency_conversions_total",
    "Total in-wallet currency conversions",
    ["from_currency", "to_currency"],
)

# Latency Histograms
TRANSACTION_LATENCY_SECONDS = Histogram(
    "transaction_latency_seconds",
    "Latency of wallet credit, debit, and transfer operations",
    ["operation"],
)
