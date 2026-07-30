# AI Usage & Development Acceleration Log

This document details how Artificial Intelligence was intelligently leveraged to accelerate the delivery of this project, ensuring high-quality output while focusing human engineering effort on core architecture and business logic.

---

## 🛠 Tools Utilized

| AI Tool | Primary Use Cases |
|---------|-------------------|
| **Antigravity AI IDE** | End-to-end pair programming, scaffolding the repository, debugging Docker container path issues, refactoring FastAPI backend routes, and fixing frontend React bugs. |
| **Gemini (via Antigravity)** | Brainstorming the financial domain model, debugging race conditions with pessimistic locking, and rewriting complex CSS for the premium glassmorphism UI. |
| **Claude 3.5 Sonnet** | Architecture design brainstorming, domain modeling, API contract definitions, and scaling strategies. |
| **Gemini 1.5 Pro** | Deep refactoring discussions, debugging complex asynchronous React state bugs, and PostgreSQL indexing. |
| **MCP Tools** | Reading `.har` files to diagnose API network bottlenecks, automatically searching files (`grep_search`), executing local bash commands (`run_command`), editing files (`replace_file_content`), and automating UI testing via the `chrome-devtools-mcp`. |

---

## ⚡ Where AI Accelerated Delivery

AI was instrumental in eliminating boilerplate overhead, acting as a massive accelerator for the following components:

| Area | Acceleration Details |
|------|----------------------|
| **Infrastructure & DevOps** | Scaffolded complex `docker-compose.yml` (6 services), `prometheus.yml`, Grafana dashboard JSON, and GitHub Actions `ci.yml`. |
| **Database & Migrations** | Translated domain models into SQLAlchemy 2.0 classes (e.g., `Numeric(18,6)` to `Decimal`) and generated Alembic migrations. |
| **Advanced Debugging** | Analyzed Chrome `.har` files autonomously to identify CORS bottlenecks and JSON deserialization errors rapidly. |
| **Frontend UI & State** | Generated glassmorphism UI layouts, customized CSS tokens, and wrote the initial boilerplate for Zustand stores. |
| **Testing & Mocking** | Produced unit tests for core services (`auth`, `wallet`), generated Pytest fixtures, and configured Vite/jsdom testing environments. |
| **Proactive Security (Fraud Detection)** | AI provided the foundational logic to implement a background worker using Scikit-Learn to flag anomalous transfer patterns, drastically accelerating our anti-fraud pipeline. |

---

## 🛑 Where AI Suggestions Were Rejected or Modified

AI is a powerful assistant, but engineering judgment always takes precedence. Here is where AI suggestions were explicitly overruled or modified to fit our architectural vision:

| Topic | AI Suggestion | Human Decision & Rationale |
|-------|---------------|----------------------------|
| **Next.js vs Vite** | Use Next.js for SSR and built-in API routes. | **Rejected**: Chose React + Vite SPA. SSR overhead wasn't justified since the app relies heavily on client-side state and requires authentication. |
| **Logging (ELK)** | Integrate `structlog` and pipe logs to Elasticsearch. | **Modified**: Streamlined observability by using lightweight Prometheus HTTP error counters for pragmatic, cost-effective MVP alerting. |
| **Session State** | Use Redis-backed server-side sessions. | **Rejected**: Selected stateless JWTs with refresh rotation to prioritize horizontal scalability and eliminate session state bottlenecks. |
| **Redux vs Zustand**| Use Redux Toolkit for complex global state. | **Rejected**: Redux adds excessive boilerplate. Zustand provided the exact same flux-like predictability with significantly less code. |
| **Ledger Architecture** | Use Kafka to append immutable ledger events instead of mutating balances directly in Postgres (Event Sourcing). | **Rejected**: We opted for pessimistic row locking (`SELECT FOR UPDATE`) in Postgres instead. |
| **Authentication** | Integrate WebAuthn/Passkeys for biometric login instead of traditional passwords. | **Modified**: Out of scope for the MVP launch, but added to the immediate roadmap as it drastically improves UX and eliminates credential stuffing. |
| **Cross-Border Settlement** | Bridge fiat wallets with a Layer 2 blockchain (like Base or Arbitrum) using USDC smart contracts. | **Rejected**: Introducing blockchain settlement adds immense regulatory and compliance overhead that we are not prepared to handle for V1. |
