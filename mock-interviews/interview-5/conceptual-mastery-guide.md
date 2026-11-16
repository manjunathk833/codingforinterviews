## 🧠 Conceptual Mastery Guide — Session #5: Perf, Chaos SRE & AppSec

**Milestone:** `Phase 4 Exit Gate` · **Target Bar:** `>= 85 / 100` across all 5 Staff dimensions.

## Core Architectural Mental Models & Benchmark Blueprints

### Q1: Little's Law (`L = λW`), Connection Pool Sizing & Coordinated Omission
- **Problem Core:** A closed-loop 50-VU load test reports `p99 = 45ms`, yet production users hit `4.2s` freezes during 1.5-second JVM/DB pauses at `500 RPS`.
- **Staff Benchmark Synthesis:** Closed-loop VUs wait for a stalled request before firing the next, measuring only 1 slow sample instead of the 750 requests queued behind a 1.5s stall (Coordinated Omission)—use open-loop constant-arrival executors. By Little's Law, `500 RPS * 0.4s = 200` concurrent in-flight requests, while DB connections per Postgres core stay bounded (`~2 * cores + spindle`) via async I/O + fast `503` load shedding.
- ** Trap / Anti-Patterns to Reject:** `report average latency only`, `set db pool size to 2000 per pod`

### Q2: Scientific Chaos Engineering (`Toxiproxy`), Circuit Breakers & Soak Leak Detection
- **Problem Core:** Injecting a Redis timeout in staging brings down Flight Search completely instead of falling back cleanly.
- **Staff Benchmark Synthesis:** Define quantitative steady-state SLIs first, inject deterministic TCP latency/reset via Toxiproxy on the Redis upstream, and assert the Circuit Breaker trips `OPEN` within threshold—serving degraded uncached search (`200 OK`) inside an isolated thread/semaphore Bulkhead. Gate soak runs on post-GC RSS and open-FD slope (`~0 MB/hr` after warmup).
- ** Trap / Anti-Patterns to Reject:** `kill random prod nodes without steady-state metrics`

### Q3: Multi-Window Multi-Burn-Rate SLO Gates (`14.4x` / `6x`) & Canary Rollbacks
- **Problem Core:** Static `> 1% error rate for 5m` alerts page engineers on harmless blips yet miss slow 3-day error-budget exhaustion.
- **Staff Benchmark Synthesis:** A `99.9%` 30-day SLO grants `0.1%` error budget (`43.2 min`). A `14.4x` burn consumes `2%` of the monthly budget in `1 hour` (paired with a `5m` short window so alerts clear immediately once mitigated), while `6x` catches `5%` burn over `6h/30m`. Compare canary pods side-by-side against simultaneous baseline pods to avoid diurnal traffic bias.
- ** Trap / Anti-Patterns to Reject:** `page on every single 500 error`, `compare canary against last week instead of live baseline`

### Q4: Automated OWASP API Security — BOLA (`IDOR`), Mass Assignment & RFC 8725 JWT
- **Problem Core:** A user swaps `/api/v1/orders/ORD-99` with Tenant A's valid JWT and reads Tenant B's passport details (`200 OK`).
- **Staff Benchmark Synthesis:** Provision Alice (`Tenant A`) and Bob (`Tenant B`) fixtures and replay Alice's resource IDs across `GET/PUT/DELETE` using Bob's valid JWT asserting `403/404` (never `200`). Fuzz JWT headers for `alg:none`, RS256->HS256 key confusion, and expired/wrong-`aud` claims while enforcing server-side algorithm pinning, and assert `extra='forbid'` DTOs reject injected privilege/price fields.
- ** Trap / Anti-Patterns to Reject:** `check authn middleware without object-level owner check`, `jwt.decode verify=False`

### Q5: Cloud Metadata SSRF (`169.254.169.254` / IMDSv2), Webhook HMAC Replay & Race-Condition Double-Spend
- **Problem Core:** An invoice-logo URL previewer fetches user-supplied URLs, and a Stripe refund webhook lacks timestamp replay protection.
- **Staff Benchmark Synthesis:** Resolve DNS once in a custom socket dialer and block RFC1918/link-local/loopback IPs (`169.254.0.0/16`, `127.0.0.0/8`, `10.0.0.0/8`) with redirects disabled + AWS IMDSv2 `HttpPutResponseHopLimit=1`. Verify webhooks over raw body bytes using `hmac.compare_digest` + `<=300s` timestamp skew + nonce cache, and fire 20 barrier-synced redemptions asserting balance never goes negative.
- ** Trap / Anti-Patterns to Reject:** `blacklist string '169.254' only before dns resolution`, `use == for hmac comparison`

## Deep-Linked Textbook Chapters
- `perf-01-day0-littles-law-percentiles-and-load-taxonomy`
- `perf-02-coordinated-omission-and-open-vs-closed-loops`
- `perf-07-chaos-engineering-scientific-method-and-toxiproxy`
- `perf-09-sli-slo-error-budgets-and-burn-rate-alerts`
- `sec-02-owasp-api-top10-bola-bfla-and-mass-assignment`
- `sec-06-ssrf-cloud-metadata-imdsv2-and-webhook-hmac`
