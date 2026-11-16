# 🎙️ Mock Technical Interview Session #3: Microservices, Async Kafka & Flake Governance — Pact, Outbox & Quarantine (Phase 2 Exit Gate)

**Target Role:** Staff Microservices & Backend Quality Architect  
**Roadmap Milestone:** Phase 2 Exit Gate  
**Session Guidelines:** Draft structured Staff-level architectural responses for all 5 questions in the **Candidate Architectural Response Studio** (`Q1`–`Q5`) and click **`▶ Evaluate Session (100-Pt Rubric)`** for instant deterministic Bar-Raiser scoring across *Mechanisms (30)*, *Math & SLAs (20)*, *Trade-Offs & Failure Modes (25)*, *Operability (15)*, and *Clarity (10)*.

---

### Question 1: Consumer-Driven Pact Contracts vs OpenAPI Schema Validation
**Scenario:**  
35 teams deploy independently; OpenAPI linters pass, yet Checkout breaks when Pricing renames an optional nested enum.

**Your Task as Staff Architect:**
1. Contrast provider-side OpenAPI schema validation against Consumer-Driven Contracts (Pact Broker + `can-i-deploy`).
2. Handle Provider States (`given('Flight AC-101 has 2 seats left')`) deterministically without shared staging DBs.
3. Contract-test asynchronous Kafka / Avro / Protobuf event schemas (`BACKWARD` vs `FULL` compatibility).

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 2: Transactional Outbox, Debezium CDC & Idempotent Payment Sagas
**Scenario:**  
Network blips during `POST /orders` cause duplicate credit-card charges OR DB commits whose `OrderCreated` Kafka event is lost.

**Your Task as Staff Architect:**
1. Explain the Dual-Write bug (Postgres commit + Kafka publish) and verify the Transactional Outbox + Debezium CDC fix.
2. Design automated chaos tests proving `Idempotency-Key` safety under concurrent duplicate POST retries.
3. Test multi-step Saga compensation when Inventory reservation fails after Payment pre-auth succeeds.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 3: HTTP/2 Connection Pooling, Token-Bucket Rate Limiting & Full-Jitter Backoff
**Scenario:**  
During flash-sale tests, retry storms amplify a 2-second downstream hiccup into a 20-minute cascading outage.

**Your Task as Staff Architect:**
1. Explain retry amplification across 4 microservice hops and prove why Exponential Backoff + **Full Jitter** beats fixed intervals.
2. Verify Token-Bucket rate limiters (`capacity`, `refill_rate`, `429 Retry-After`) without wall-clock sleeps.
3. Prevent client-side retry budgets from exhausting HTTP connection pools.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 4: GraphQL N+1 Query Traps & gRPC Protobuf Deadline / Status Contracts
**Scenario:**  
An API gateway exposes GraphQL to web/mobile and talks gRPC internally; nested `flights { crew {certs} }` queries spike DB load 100x.

**Your Task as Staff Architect:**
1. Detect and fail GraphQL `N+1` resolver regressions automatically inside integration CI.
2. Test GraphQL AST depth/cost limits and partial-data `errors[]` envelopes (`HTTP 200` trap!).
3. Verify gRPC deadline propagation (`DEADLINE_EXCEEDED`), wire-compatibility (field tags), and status codes.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 5: Statistical Flake Detection (Beta-Binomial / Rolling Pass Rate) & Quarantine Governance
**Scenario:**  
Engineers re-run red GitHub Actions jobs until green; 12% of tests are intermittent flakes with zero accountability.

**Your Task as Staff Architect:**
1. Define an objective statistical flake detector distinguishing true code regressions from non-deterministic tests.
2. Architect automated quarantine routing (blocking PR lane vs non-blocking quarantine lane) via JUnit/Allure telemetry.
3. Enforce CODEOWNERS SLAs and strict un-quarantine graduation gates (e.g., 100 consecutive parallel burn-in passes).

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---
