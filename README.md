# PayPulse — Multi-Currency Wallet Platform

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
