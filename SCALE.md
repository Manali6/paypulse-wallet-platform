# Scale Exercise — Design Note (500k Users / 100 TPS)

> **Scenario Assumptions**: 500,000 registered users, 20,000 Daily Active Users (DAU), ~100 Transactions Per Second (TPS) peak throughput.

---

## 1. Scaling Strategy & Architecture Evolution

### Horizontal App Tier Scaling
- Deploy FastAPI application containers across auto-scaling groups (e.g. AWS ECS / Kubernetes HPA) triggered by CPU/Memory (>70%) or request queue depth.
- Stateless JWT authentication avoids sticky sessions, allowing any web pod to handle any request.

### Database Strategy (PostgreSQL)
- **Primary / Replica Topology**: Single primary for writes; multiple read-replicas for balance queries, dashboard loads, and transaction history.
- **Connection Pooling**: Deploy **PgBouncer** in transaction mode in front of PostgreSQL to handle thousands of concurrent client connections without connection overhead spikes.
- **Table Partitioning**: Range-partition `transactions` table by `created_at` (monthly partitions) to maintain query speed and index efficiency as ledger sizes grow.

### Caching Layer (Redis Cluster)
- Cache user balances and active wallet records in Redis with a short TTL (e.g. 5–30s) or invalidate explicitly on credit/debit events to eliminate read load from Postgres.
- Use Redis Cluster to shard keys across nodes.

---

## 2. Asynchronous Processing & Resiliency

- **Transactional Outbox Pattern**: Decouple non-critical paths (e.g. notification emails, audit logs, analytics ingestion) by writing events to an `outbox` DB table in the same transaction, then processing via Celery / RabbitMQ workers.
- **Idempotency Controls**: Require an `Idempotency-Key` HTTP header for all debit/transfer operations stored in Redis (TTL 24h) to avoid duplicate balance deductions on network retries.

---

## 3. Exchange Provider Downtime Strategy

- **Stale Cache Fallback**: If the external FX provider goes down, the background `APScheduler` job will fail. The system is designed to seamlessly fall back to the most recently cached Redis rates. We configure the Redis TTL to outlast typical provider outages (e.g., 24-48 hours) while setting a "stale" flag on the UI.
- **Circuit Breaker Pattern**: If the provider starts throwing 5xx errors, a circuit breaker trip prevents cascading failures and network timeouts, immediately switching the app to fallback cache mode.
- **Rate Spread Adjustment**: During prolonged downtime, the application can programmatically apply a safety margin (e.g., a 2% spread) to stale exchange rates to mitigate the business risk of currency volatility until the provider recovers.

---

## 4. Operational & Cost Optimisation

- **Read Replica Routing**: Direct `GET /transactions` and `GET /wallets` traffic to read replicas.
- **Auto-archiving**: Move transaction records older than 1 year to cold storage (e.g., AWS S3 + Parquet format via AWS Athena) to optimize DB disk costs.
- **Alerting Thresholds**: Configure PagerDuty / Slack alerts on `http_errors_total` rate > 2% or DB connection pool utilization > 80%.
