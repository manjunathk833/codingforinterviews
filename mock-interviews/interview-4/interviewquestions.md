# 🎙️ Mock Technical Interview Session #4: SQL Data Integrity, Containers & CI Sharding — MVCC, Ryuk & LPT (Phase 3 Exit Gate)

**Target Role:** Staff Data, Infrastructure & CI Systems Architect  
**Roadmap Milestone:** Phase 3 Exit Gate  
**Session Guidelines:** Draft structured Staff-level architectural responses for all 5 questions in the **Candidate Architectural Response Studio** (`Q1`–`Q5`) and click **`▶ Evaluate Session (100-Pt Rubric)`** for instant deterministic Bar-Raiser scoring across *Mechanisms (30)*, *Math & SLAs (20)*, *Trade-Offs & Failure Modes (25)*, *Operability (15)*, and *Clarity (10)*.

---

### Question 1: PostgreSQL MVCC Isolation Anomaly & 64-Thread Seat `12A` Double-Booking
**Scenario:**  
Under `READ COMMITTED`, `SELECT available FROM seats WHERE seat='12A'` followed by `UPDATE` double-books Seat `12A` under 64 concurrent requests.

**Your Task as Staff Architect:**
1. Explain why PostgreSQL `READ COMMITTED` permits Lost Updates / Read-Modify-Write races across concurrent transactions.
2. Compare Pessimistic Locking (`SELECT ... FOR UPDATE` vs `SKIP LOCKED`), Optimistic CAS (`version = version + 1`), and `SERIALIZABLE` SSI.
3. Write the concurrency test harness (cyclic barrier + 64 threads) proving exactly 1 winner and 63 clean `409 Conflict` responses.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 2: 1:N Join Fan-Out Financial Inflation & Double-Entry Ledger Reconciliation
**Scenario:**  
Joining `orders` (`1` row, `$500`) to `baggage_items` (`3` rows) and `tax_lines` (`2` rows) inflates `SUM(orders.total_cents)` to `$3,000` (`6x`!).

**Your Task as Staff Architect:**
1. Explain the Cartesian `1:M:N` join grain trap and rewrite the SQL using pre-aggregated CTEs.
2. Enforce double-entry ledger invariants (`SUM(debits) == SUM(credits)`, zero orphan journal postings, idempotent webhook replay).
3. Verify query scalability via `EXPLAIN (ANALYZE, BUFFERS)` SARGable composite B-Tree indexes.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 3: Multi-Stage Dockerfiles, BuildKit Layer Caching & Testcontainers Ryuk Reaper
**Scenario:**  
Your E2E runner Docker image is `2.9 GB`, rebuilds `pip/maven` from scratch on every 1-line test edit (`9 min`), and leaks zombie Postgres containers on CI.

**Your Task as Staff Architect:**
1. Redesign a Multi-Stage BuildKit Dockerfile cutting image size >65% and keeping dependency layers cached across code edits.
2. Harden container security (non-root `USER`, pinned digests, zero build-arg secrets in image history).
3. Explain how Testcontainers `Ryuk` sidecar reaps orphan containers/volumes even when CI runners receive `SIGKILL`.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 4: Kubernetes Ephemeral PR Environments, Probes & `OOMKilled (Exit 137)` Forensics
**Scenario:**  
Ephemeral PR namespaces suffer sporadic `502 Bad Gateway` during rollout and test pods die with `Exit Code 137` despite JVM `-Xmx6g` on an `8Gi` pod.

**Your Task as Staff Architect:**
1. Explain why `-Xmx6g` inside an `8Gi` cgroup v2 pod still triggers Linux OOMKiller (`Exit 137`).
2. Differentiate Kubernetes `startupProbe`, `readinessProbe`, and `livenessProbe` to eliminate rollout `502`s and restart loops.
3. Design graceful `SIGTERM` connection draining (`preStop` + `terminationGracePeriodSeconds`).

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 5: Longest-Processing-Time (LPT) CI Shard Bin-Packing & AST Test Impact Analysis
**Scenario:**  
Alphabetical sharding puts all slow Checkout E2E specs onto Shard #3 (`28 min`) while Shards #1, #2, and #4 finish in `5 min`.

**Your Task as Staff Architect:**
1. Write/explain the `O(N log K)` Longest-Processing-Time (LPT) Min-Heap bin-packing algorithm using historical p90 test durations.
2. Calculate wall-clock speedup and machine-minute savings across `K = 8` shards.
3. Combine static AST import-graph + coverage Test Impact Analysis (TIA) on PRs with full nightly safety nets.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---
