# PayPulse — Multi-Currency Wallet Platform

## Core Features (MVP)

| Feature | Description | Technical Implementation |
|---------|-------------|--------------------------|
| **Authentication** | Secure user onboarding and login. | Stateless JWT access & refresh rotation; Argon2 password hashing. |
| **Wallet Management** | Multi-currency wallet generation. | Support for ISO currencies (USD, EUR, GBP, JPY, etc.) with unique constraints. |
| **Balance Operations** | Credit and debit funds safely. | Precision validation using PostgreSQL `Numeric(18,6)` to prevent floating point errors. |
| **Transaction Ledger** | Immutable audit trail of activities. | ACID-compliant transaction snapshots (`balance_after`). |
| **Observability** | Real-time monitoring and alerting. | Prometheus metric instrumentation, 4xx/5xx tracking, and Grafana dashboards. |
| **DevOps & CI/CD** | Automated testing and deployment. | Docker Compose environment and GitHub Actions pipeline. |

## Technology Stack

Our stack was carefully selected to prioritize developer velocity, scalability, and type safety.

- **Backend:** FastAPI, PostgreSQL, Redis
- **Frontend:** React, Vite
- **Infrastructure & Observability:** Docker Compose, Prometheus, Grafana
- **Deployment & CI/CD:** Railway (Backend), Vercel (Frontend), GitHub Actions

## API Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/auth/signup` | Register a new user and create their default currency wallet. |
| `POST` | `/auth/login` | Authenticate user and retrieve JWT tokens. |
| `POST` | `/auth/refresh` | Issue a new access token using a valid refresh token. |
| `GET`  | `/auth/me` | Fetch the authenticated user's profile profile. |
| `GET`  | `/wallets` | Retrieve a list of the user's active wallets. |
| `POST` | `/wallets` | Provision a new wallet for a specific currency. |
| `POST` | `/wallets/{id}/credit` | Safely credit funds to a specific wallet. |
| `POST` | `/wallets/{id}/debit` | Safely debit funds (with insufficient funds validation). |
| `GET`  | `/transactions` | Retrieve paginated transaction ledger history. |
| `GET`  | `/health` | Liveness and readiness checks (Postgres + Redis). |
| `GET`  | `/metrics` | Prometheus metrics scraping endpoint. |

## Setup

### Prerequisites
- **Docker & Docker Compose**
- **Node.js 20+** (for local frontend dev)
- **Python 3.12+** (for local backend dev)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd wallet-platform
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

## Run steps

1. **Launch the platform:**
   ```bash
   make up
   ```

2. **Access the services:**
   - **Frontend App:** [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Prometheus:** [http://localhost:9090](http://localhost:9090)
   - **Grafana:** [http://localhost:3001](http://localhost:3001) *(Credentials: `admin` / `admin`)*

3. **Run tests via Docker:**
   ```bash
   make test
   ```

## Deployment

The application utilizes continuous deployment pipelines triggered by GitHub Actions on merges to the `main` branch.

- **Frontend App (Vercel):** [https://paypulse-wallet-platform.vercel.app/](https://paypulse-wallet-platform.vercel.app/)
- **Backend API (Railway):** [https://paypulse-wallet-platform-production.up.railway.app/health](https://paypulse-wallet-platform-production.up.railway.app/health)

*(Refer to `.github/workflows` for the exact CI/CD pipeline definitions.)*

## Assumptions

- PostgreSQL is the primary database for state persistence.
- Currency conversions use a fixed/mocked exchange rate model for this iteration.
- All monetary values are handled using precise `Decimal` (Python) and `Numeric(18,6)` (PostgreSQL) structures to prevent floating-point inaccuracies.
- The environment is structured strictly around Docker Compose for local orchestration.

## Trade-offs

- **React SPA vs SSR**: Opted for a React + Vite Single Page Application over Next.js SSR, as Server-Side Rendering overhead isn't justified for a heavily gated, client-side dashboard where SEO is irrelevant.
- **Pessimistic Locking vs Event Sourcing**: Used PostgreSQL `SELECT FOR UPDATE` for ensuring balance consistency under high concurrency rather than building a full event-sourced append-only ledger (like Kafka). This prioritizes development speed for MVP while retaining ACID safety.
- **Stateless JWT vs Sessions**: Selected stateless JWTs with refresh token rotation instead of Redis-backed server-side sessions to reduce state bottlenecking and improve horizontal scalability.

## Known limitations

- **Live FX Rates**: Currency exchange rates are mocked and not actively fetched from live oracle APIs.
- **Advanced Auth**: WebAuthn/Passkeys authentication (biometrics) is planned for future UX improvements but currently unsupported.
- **Ledger Auditability**: While balances are safe, an immutable, event-driven ledger for perfect regulatory auditability is not included in V1.
