# 🤖 AI Usage & Development Acceleration Log

This document details how Artificial Intelligence was intelligently leveraged to accelerate the delivery of this project, ensuring high-quality output while focusing human engineering effort on core architecture and business logic.

---

## 🛠️ Tools Utilized

| AI Tool | Primary Use Cases |
|---------|-------------------|
| **Antigravity AI Agent** | Automated scaffold generation, test suite writing, and infrastructure setup (Docker/CI). |
| **Claude 3.5 Sonnet / Gemini** | Architecture design brainstorming, domain modeling, and refactoring discussions. |

---

## 🚀 Where AI Accelerated Delivery

AI was instrumental in eliminating boilerplate overhead, acting as an accelerator for the following components:

1. **Infrastructure & DevOps (10x Speedup):** 
   - Accelerated the generation of the `docker-compose.yml` orchestrating 6 interdependent services.
   - Generated the Prometheus scrape rules (`prometheus.yml`) and the JSON structure for the Grafana dashboard.
   - Drafted the initial GitHub Actions (`ci.yml`) workflows for automated Vercel and Railway deployments.
2. **Database Models & Alembic Migrations:** 
   - Assisted in the rapid translation of domain models into SQLAlchemy 2.0 declarative classes.
   - Scaffolded the initial Alembic migration scripts.
3. **Frontend UI Components & Styling:** 
   - Automated the repetitive generation of JSX layouts using custom CSS design tokens.
   - Instantly generated the glassmorphism theme and styling logic.
4. **Test Suite Generation:** 
   - Quickly produced comprehensive unit test coverage for complex logic like `auth_service` and `wallet_service`.
   - Scaffolded integration testing fixtures.

---

## 🛑 Where AI Suggestions Were Rejected or Modified

AI is a powerful assistant, but engineering judgment always takes precedence. Here is where AI suggestions were explicitly overruled to better fit the platform's constraints:

- **Next.js vs React Vite:** 
  - *AI Suggestion:* Use Next.js for the frontend to benefit from SSR. 
  - *Human Decision:* **Rejected**. Shifted to a React + Vite SPA to significantly simplify client deployment and reduce unnecessary SSR overhead for an application heavily dependent on client-side state (Zustand).
- **Structlog vs Prometheus-only:** 
  - *AI Suggestion:* Integrate `structlog` for deep structured JSON logging across the app.
  - *Human Decision:* **Modified**. Streamlined observability by removing custom structured logging dependencies in favor of lightweight, hyper-focused Prometheus HTTP error counters, which is more pragmatic for a 6-10 hour MVP.
- **Server-Side Sessions vs JWT:** 
  - *AI Suggestion:* Use Redis-backed server-side sessions for maximum security.
  - *Human Decision:* **Rejected**. Selected a stateless JWT token pair with refresh rotation. This trades immediate token revocation for vastly easier scale-out readiness without session-state bottlenecks.
