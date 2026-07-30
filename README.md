# 🚀 PayPulse — Multi-Currency Wallet Platform

PayPulse is a production-minded, high-performance multi-currency wallet application. It is engineered with a **FastAPI** backend and a modern **React (Vite + TypeScript)** frontend, containerised via Docker Compose, and configured with enterprise-grade observability using Prometheus and Grafana.

---

## 🎯 Core Features (MVP)

| Feature | Description | Technical Implementation |
|---------|-------------|--------------------------|
| **🔒 Authentication** | Secure user onboarding and login. | Stateless JWT access & refresh rotation; Argon2 password hashing. |
| **💼 Wallet Management** | Multi-currency wallet generation. | Support for ISO currencies (USD, EUR, GBP, JPY, etc.) with unique constraints. |
| **💸 Balance Operations** | Credit and debit funds safely. | Precision validation using PostgreSQL `Numeric(18,6)` to prevent floating point errors. |
| **🧾 Transaction Ledger** | Immutable audit trail of activities. | ACID-compliant transaction snapshots (`balance_after`). |
| **📈 Observability** | Real-time monitoring and alerting. | Prometheus metric instrumentation, 4xx/5xx tracking, and Grafana dashboards. |
| **🛠️ DevOps & CI/CD** | Automated testing and deployment. | Docker Compose environment and GitHub Actions pipeline. |

---

## 🏗️ Technology Stack

Our stack was carefully selected to prioritize developer velocity, scalability, and type safety:

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, Argon2, Pytest
- **Frontend:** React 18, Vite, TypeScript, React Router v6, Zustand, Axios, React Hot Toast
- **Infrastructure:** Docker, Nginx, Prometheus, Grafana
- **Deployment:** Railway (Backend + DB + Redis), Vercel (Frontend)

---

## ⚙️ Local Setup & Development

### Prerequisites
- **Docker & Docker Compose**
- **Node.js 20+** (for local frontend dev)
- **Python 3.12+** (for local backend dev)

### Quick Start (Docker)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd wallet-platform
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

3. **Launch the platform:**
   ```bash
   make up
   ```

4. **Access the services:**
   - 🌐 **Frontend App:** [http://localhost:3000](http://localhost:3000)
   - 📖 **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - 📊 **Prometheus:** [http://localhost:9090](http://localhost:9090)
   - 📈 **Grafana:** [http://localhost:3001](http://localhost:3001) *(Credentials: `admin` / `admin`)*

---

## 📡 API Endpoints Overview

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

---

## 🧪 Testing

The repository contains rigorous test coverage for both the frontend and backend.

**Run all tests via Docker:**
```bash
make test
```

**Run backend tests locally with coverage (Requires `pytest`):**
```bash
cd backend
pytest tests/ -v --cov=app
```
*(For more information, see the `tests/README.md` directory)*

---

## 🚀 Deployment

The application utilizes continuous deployment pipelines triggered by GitHub Actions on merges to the `main` branch.

- **Backend API & PostgreSQL & Redis:** [Railway](https://railway.app/)
- **Frontend App:** [Vercel](https://vercel.com/)

*(Refer to `.github/workflows` for the exact CI/CD pipeline definitions.)*

---

## 💡 Architecture & Design Decisions

- Please review **[ARCHITECTURE.md](./ARCHITECTURE.md)** for detailed sequence diagrams, domain models, and our **Scale Exercise** design notes (handling 500k users / 100 TPS).
- Please review **[AI_USAGE.md](./AI_USAGE.md)** for transparency on how AI was utilized to accelerate the delivery of this platform.
