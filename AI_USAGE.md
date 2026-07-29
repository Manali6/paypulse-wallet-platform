# AI Usage & Development Acceleration Log

## Tools Used

- **Antigravity AI Agent (Gemini 3.6 / Claude Sonnet & Opus)**: Used for architecture design, boilerplate generation, unit/integration test suite setup, Docker & CI/CD pipeline drafting.

## Where AI Accelerated Delivery

1. **Scaffold & Infrastructure**: Accelerated Docker Compose, Prometheus scrape rules, Grafana dashboard JSON, and GitHub Actions workflow generation.
2. **Database Models & Alembic**: Rapid creation of SQLAlchemy 2.0 declarative models and initial Alembic migration scripts.
3. **Frontend UI Components**: Automated styling using custom CSS design tokens (glassmorphism theme) and React component layout boilerplate.
4. **Test Suite Generation**: Quickly produced comprehensive unit tests for `auth_service` and `wallet_service`, alongside integration fixtures.

## AI Suggestions Modified or Rejected

1. **Next.js vs React Vite**: Initially suggested Next.js for frontend SSR; shifted to React + Vite SPA as requested to simplify client deployment and reduce SSR overhead.
2. **Structlog vs Prometheus-only**: Streamlined observability by removing custom structured logging dependencies in favor of lightweight Prometheus HTTP error counters.
3. **Session vs JWT**: Selected stateless JWT token pair with refresh rotation over server-side session stores for easier scale-out readiness.
