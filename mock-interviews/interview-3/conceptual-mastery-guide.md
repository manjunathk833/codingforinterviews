## 🧠 Conceptual Mastery Guide — Session #3: Microservices, Pact & Async Kafka

**Milestone:** `Phase 2 Exit Gate` · **Target Bar:** `>= 85 / 100` across all 5 Staff dimensions.

## Core Architectural Mental Models & Benchmark Blueprints

### Q1: Consumer-Driven Pact Contracts vs OpenAPI Schema Validation
- **Problem Core:** 35 teams deploy independently; OpenAPI linters pass, yet Checkout breaks when Pricing renames an optional nested enum.
- **Staff Benchmark Synthesis:** OpenAPI proves syntactic validity on the provider, whereas Pact records exact consumer field/value expectations and gates releases via Pact Broker `can-i-deploy` verification matrices. Seed in-memory/transactional Provider State handlers per interaction and enforce Schema Registry `BACKWARD_TRANSITIVE`/`FULL` rules on Kafka topics.
- ** Trap / Anti-Patterns to Reject:** `test all 35 services only in shared staging`

### Q2: Transactional Outbox, Debezium CDC & Idempotent Payment Sagas
- **Problem Core:** Network blips during `POST /orders` cause duplicate credit-card charges OR DB commits whose `OrderCreated` Kafka event is lost.
- **Staff Benchmark Synthesis:** Eliminate dual-writes by inserting `orders` + `outbox_events` in one local ACID transaction streamed via Debezium WAL CDC, with consumer deduplication on `event_id`. Fire 16 concurrent barrier-synchronized `POST /orders` sharing one `Idempotency-Key` asserting exactly 1 ledger charge, and inject Inventory `503` to assert Payment void/compensation.
- ** Trap / Anti-Patterns to Reject:** `ignore duplicate charges`, `distributed 2pc across 30 services`

### Q3: HTTP/2 Connection Pooling, Token-Bucket Rate Limiting & Full-Jitter Backoff
- **Problem Core:** During flash-sale tests, retry storms amplify a 2-second downstream hiccup into a 20-minute cascading outage.
- **Staff Benchmark Synthesis:** 3 retries across 4 hops multiplies load `4^4 = 256x`! Randomize sleep `uniform(0, min(cap, base * 2^attempt))` (Full Jitter) to desynchronize waves, cap per-client retry budgets at <=10% of active requests + propagate deadlines, and test Token Bucket math deterministically via an injected monotonic clock.
- ** Trap / Anti-Patterns to Reject:** `infinite retries`, `fixed 1s sleep retry across 4 hops`

### Q4: GraphQL N+1 Query Traps & gRPC Protobuf Deadline / Status Contracts
- **Problem Core:** An API gateway exposes GraphQL to web/mobile and talks gRPC internally; nested `flights { crew {certs} }` queries spike DB load 100x.
- **Staff Benchmark Synthesis:** Instrument SQL/OTel span counters in GraphQL tests asserting query count stays `O(1)` (`<= 3` batched DataLoader queries whether returning 2 or 50 flights), assert `response.errors` is empty (since GraphQL returns HTTP 200 on resolver errors) + AST query-depth caps, and lint Protobuf `reserved` field tags with `buf breaking`.
- ** Trap / Anti-Patterns to Reject:** `only assert status_code == 200 on graphql`, `reuse deleted protobuf tag numbers`

### Q5: Statistical Flake Detection (Beta-Binomial / Rolling Pass Rate) & Quarantine Governance
- **Problem Core:** Engineers re-run red GitHub Actions jobs until green; 12% of tests are intermittent flakes with zero accountability.
- **Staff Benchmark Synthesis:** Flag any test exhibiting mixed pass+fail outcomes on the *exact same commit SHA* (or >1% retry rate over 200 runs), auto-move it via quarantine manifest out of blocking PR checks into a monitored quarantine pipeline, page CODEOWNERS with a 7-day fix-or-rewrite SLA, and require 100/100 parallel stress burn-in passes to re-enter the PR gate.
- ** Trap / Anti-Patterns to Reject:** `just click rerun failed jobs`, `comment out failing assertions`

## Deep-Linked Textbook Chapters
- `api-02-rest-idempotency-caching-and-pagination`
- `api-05-rate-limiting-token-buckets-and-timeouts`
- `api-08-async-saga-and-webhook-verification`
- `api-10-pact-consumer-driven-contract-testing`
- `sd-03-kafka-outbox-and-eventual-consistency`
- `sdet-09-statistical-flake-quarantine-governance`
