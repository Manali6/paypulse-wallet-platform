# AI Usage & Development Acceleration Log

This document details how Artificial Intelligence was intelligently leveraged to accelerate the delivery of this project, ensuring high-quality output while focusing human engineering effort on core architecture and business logic.

---

## Tools Utilized

| AI Tool | Primary Use Cases |
|---------|-------------------|
| **Antigravity AI Agent** | Automated scaffold generation, test suite writing, and infrastructure setup (Docker/CI). |
| **Claude 3.5 Sonnet** | Architecture design brainstorming, domain modeling, API contract definitions, and scaling strategies. |
| **Gemini 1.5 Pro** | Deep refactoring discussions, debugging complex asynchronous React state bugs, and identifying optimal index strategies for PostgreSQL. |
| **GitHub Copilot** | Inline code completion for repetitive tasks, such as generating the initial SQLAlchemy model fields, parsing environment variables, and writing standard Vitest assertions. |

---

## Where AI Accelerated Delivery

AI was instrumental in eliminating boilerplate overhead, acting as a massive accelerator for the following components:

1. **Infrastructure & DevOps (10x Speedup):** 
   - Accelerated the generation of the complex `docker-compose.yml` orchestrating 6 interdependent services (Frontend, Backend, PostgreSQL, Redis, Prometheus, Grafana).
   - Generated the Prometheus scrape rules (`prometheus.yml`) and the JSON structure for the initial Grafana dashboard.
   - Drafted the GitHub Actions (`ci.yml`) workflows for automated testing, linting, and continuous integration pipeline structure.
   
2. **Database Models & Alembic Migrations:** 
   - Assisted in the rapid translation of domain models into SQLAlchemy 2.0 declarative classes, mapping exact data types like `Numeric(18,6)` to Python `Decimal`.
   - Scaffolded the initial Alembic migration environment (`env.py`) and generated the baseline migration scripts, handling the initial foreign key bindings perfectly.

3. **Frontend UI Components & Zustand State:** 
   - Automated the repetitive generation of JSX layouts using custom CSS design tokens.
   - Instantly generated the structural skeleton for the glassmorphism theme and provided a robust starting point for responsive sidebar navigation.
   - Assisted in writing the initial boilerplate for the Zustand stores (`authStore.ts` and `walletStore.ts`), cutting down time spent on generic state management logic.

4. **Test Suite Generation & Mocking:** 
   - Quickly produced comprehensive unit test coverage for complex logic like `auth_service` and `wallet_service`, allowing the engineer to focus on the edge cases.
   - Scaffolded integration testing fixtures using Pytest, setting up the mocked database sessions and test user factories.
   - Generated the Vite and jsdom environment configuration to get React component tests running seamlessly within minutes.

---

## Where AI Suggestions Were Rejected or Modified

AI is a powerful assistant, but engineering judgment always takes precedence. Here is where AI suggestions were explicitly overruled to better fit the platform's constraints:

- **Next.js vs React Vite:** 
  - *AI Suggestion:* Use Next.js for the frontend to benefit from Server-Side Rendering (SSR) and built-in API routes. 
  - *Human Decision:* **Rejected**. Shifted to a React + Vite Single Page Application (SPA). The wallet platform is heavily dependent on real-time client-side state (via Zustand), and introducing SSR overhead would unnecessarily complicate client deployment without providing significant SEO benefits (as the entire app is gated behind authentication).

- **Structlog vs Prometheus-only:** 
  - *AI Suggestion:* Integrate `structlog` for deep structured JSON logging across the app, and pipe logs into Elasticsearch.
  - *Human Decision:* **Modified**. Streamlined observability by removing custom structured logging dependencies in favor of lightweight, hyper-focused Prometheus HTTP error counters. This is far more pragmatic for a rapid MVP, providing instant alerting without the infrastructure cost of an ELK stack.

- **Server-Side Sessions vs Stateless JWT:** 
  - *AI Suggestion:* Use Redis-backed server-side sessions for maximum security and immediate session revocation capabilities.
  - *Human Decision:* **Rejected**. Selected a stateless JWT token pair with refresh rotation (Access Token TTL: 15m, Refresh Token TTL: 7d). This trades immediate global revocation for vastly easier horizontal scale-out readiness without session-state bottlenecks in the API gateway layer.

- **Redux vs Zustand:**
  - *AI Suggestion:* Use Redux Toolkit for managing the complex global state of wallets and transactions.
  - *Human Decision:* **Rejected**. Redux introduces excessive boilerplate for this scale of application. Zustand provides the exact same predictable flux-like state updates with a fraction of the code, significantly increasing development velocity.

- **Tailwind CSS vs Custom CSS Modules:**
  - *AI Suggestion:* Use Tailwind CSS to rapidly style the application.
  - *Human Decision:* **Rejected**. We utilized custom CSS variables and pure CSS to maintain absolute granular control over the glassmorphism UI aesthetics, ensuring a premium, tailored design rather than a generic utility-class look.
