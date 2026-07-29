# System Architecture — PayPulse Wallet Platform

```
┌────────────────────────────────────────────────────────┐
│               React (Vite + TS) Frontend                │
│   Auth · Dashboard · Wallets · Transaction History     │
└────────────────────┬───────────────────────────────────┘
                     │ REST (HTTPS)
┌────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   Auth   │ │  Wallet  │ │Transact. │ │ Metrics  │  │
│  │  Router  │ │  Router  │ │  Router  │ │Middleware│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       └────────────┴────────────┴─────────────┘        │
│                   Service Layer                         │
│       ┌───────────────┐     ┌───────────────┐          │
│       │ AuthService   │     │ WalletService │          │
│       └───────┬───────┘     └───────┬───────┘          │
│               └──────────┬──────────┘                  │
│                   Repository Layer                      │
└──────────┬──────────────────────────┬──────────────────┘
           │                          │
    ┌──────▼──────┐           ┌───────▼──────┐
    │ PostgreSQL  │           │    Redis     │
    │  (primary)  │           │  (sessions)  │
    └─────────────┘           └──────────────┘
```

## Domain Model

- **User**: Core identity (email, password hash, display name, default currency).
- **Wallet**: One user can have multiple wallets, bounded by `(user_id, currency)` unique constraint. Balance is represented using `Numeric(18,6)` to prevent floating point inaccuracies.
- **Transaction**: Immutable ledger entry recording `CREDIT` or `DEBIT` events, storing `balance_after` snapshot for consistency checks.

## Key Design & Security Decisions

1. **Precision Math**: All financial balances use PostgreSQL `Numeric(18,6)` and Python `Decimal` to eliminate rounding errors.
2. **Stateless JWT Auth**: Access tokens (15m expiry) and Refresh tokens (7d expiry) hashed with HS256; Argon2 for password hashing.
3. **Atomic Operations**: Credit and Debit actions execute within a single database transaction updating balance and inserting ledger entry together.
4. **Observability First**: Instrumented with `prometheus-fastapi-instrumentator` and custom error counter `http_errors_total{status_code, path}` for instant 4xx/5xx spike detection.
