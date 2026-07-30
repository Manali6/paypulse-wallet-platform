# PayPulse — Multi-Currency Wallet Platform

PayPulse is a production-minded multi-currency wallet application built with FastAPI (Python) backend and React (Vite + TypeScript) frontend, containerised with Docker Compose and configured for observability with Prometheus + Grafana.

---

## Features (Flow 1 MVP)

- **Authentication**: JWT access & refresh token rotation, Argon2 password hashing
- **Wallet Management**: Create wallets across multiple ISO currencies (USD, EUR, GBP, JPY, etc.)
- **Balance Operations**: Credit and debit funds with precision validation (Numeric 18,6)
- **Transaction History**: Audit trail of every credit/debit transaction
- **Observability**: Prometheus metric instrumentation & custom 4xx/5xx error tracking + Grafana dashboard
- **DevOps**: Docker Compose setup + GitHub Actions CI/CD pipeline

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, Argon2, Pytest
- **Frontend**: React 18, Vite, TypeScript, React Router v6, Zustand, Axios, React Hot Toast, Lucide Icons
- **Infrastructure**: Docker, Nginx, Prometheus, Grafana
- **Deployment**: Railway (Backend + DB + Redis), Vercel (Frontend)

---

## Local Setup & Development

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### Running with Docker Compose

1. Clone repository:
   ```bash
   git clone <repo-url>
   cd wallet-platform
   ```

2. Copy environment template:
   ```bash
   cp .env.example .env
   ```

3. Launch all services:
   ```bash
   make up
   ```

4. Access services:
   - **Frontend App**: http://localhost:3000
   - **Backend API Docs**: http://localhost:8000/docs
   - **Prometheus**: http://localhost:9090
   - **Grafana**: http://localhost:3001 (Credentials: `admin` / `admin`)

---

## API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register user + create default wallet |
| `POST` | `/auth/login` | Authenticate & get JWT tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/auth/me` | Fetch user profile |
| `GET` | `/wallets` | List current user's wallets |
| `POST` | `/wallets` | Create new wallet for a currency |
| `POST` | `/wallets/{id}/credit` | Credit funds to wallet |
| `POST` | `/wallets/{id}/debit` | Debit funds from wallet |
| `GET` | `/transactions` | Paginated transaction history |
| `GET` | `/health` | Liveness check (Postgres + Redis) |
| `GET` | `/metrics` | Prometheus metrics endpoint |

---

## Testing

Run unit & integration tests via Docker:
```bash
make test
```

Or locally in `backend/`:
```bash
pytest tests/ -v --cov=app
```

## Deployment

The application is deployed on:
- **Backend API & PostgreSQL & Redis**: Railway
- **Frontend App**: Vercel

*Note: For detailed deployment instructions or CI/CD usage, refer to the `.github/workflows` which automate the Vercel and Railway deployments on merge to main.*

---

## Assumptions

- Currency exchange rates are fetched dynamically from a third-party API (mocked/integrated in the exchange service).
- Users are limited to one wallet per currency.
- JWT tokens are stored securely in memory/localStorage (stateless auth).

---

## Trade-offs

- **SQLAlchemy ORM vs Raw SQL**: Selected SQLAlchemy for rapid domain modeling and Alembic migrations, trading slight performance overhead for developer velocity and maintainability.
- **PostgreSQL vs NoSQL**: Chose PostgreSQL for strong ACID compliance and transaction guarantees which are strictly required for a wallet ledger.
- **Stateless JWT vs Sessions**: Chose stateless JWTs with refresh token rotation instead of server-side sessions to make scaling the backend easier, although it trades off immediate token revocation capabilities (unless a blacklist is maintained in Redis).

---

## Known Limitations

- **Currency Support**: Only a fixed subset of fiat currencies are currently seeded.
- **Exchange Rate Caching**: Exchange rates might be slightly delayed based on the refresh interval.
- **Token Storage**: Storing access tokens in localStorage (Frontend) is susceptible to XSS. A production-ready evolution would migrate to `HttpOnly` cookies.

---

## Architecture & Design

See [ARCHITECTURE.md](./ARCHITECTURE.md) for sequence diagrams, domain models, and the Scale Exercise design note (500k users / 100 TPS).
See [AI_USAGE.md](./AI_USAGE.md) for details on AI acceleration.
