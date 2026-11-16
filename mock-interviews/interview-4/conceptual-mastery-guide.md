## 🧠 Conceptual Mastery Guide — Session #4: SQL MVCC, Docker & LPT Sharding

**Milestone:** `Phase 3 Exit Gate` · **Target Bar:** `>= 85 / 100` across all 5 Staff dimensions.

## Core Architectural Mental Models & Benchmark Blueprints

### Q1: PostgreSQL MVCC Isolation Anomaly & 64-Thread Seat `12A` Double-Booking
- **Problem Core:** Under `READ COMMITTED`, `SELECT available FROM seats WHERE seat='12A'` followed by `UPDATE` double-books Seat `12A` under 64 concurrent requests.
- **Staff Benchmark Synthesis:** In `READ COMMITTED`, two transactions both read `available=true` from the committed snapshot before either commits. Use `UPDATE seats SET booked_by=:u, version=version+1 WHERE seat='12A' AND booked_by IS NULL` (atomic single-statement CAS) for named seats or `FOR UPDATE SKIP LOCKED` for next-available seat queues, verified via a 64-thread `threading.Barrier` test.
- ** Trap / Anti-Patterns to Reject:** `synchronize in python memory across multiple pods`, `ignore 409 conflicts`

### Q2: 1:N Join Fan-Out Financial Inflation & Double-Entry Ledger Reconciliation
- **Problem Core:** Joining `orders` (`1` row, `$500`) to `baggage_items` (`3` rows) and `tax_lines` (`2` rows) inflates `SUM(orders.total_cents)` to `$3,000` (`6x`!).
- **Staff Benchmark Synthesis:** Never sum parent metrics after joining `1:N` child tables (`3 * 2 = 6x` row multiplication); pre-aggregate each child table to `order_id` grain inside separate CTEs before joining, store money in integer cents/NUMERIC with `SUM(debit_cents) - SUM(credit_cents) = 0` checks, and assert `Index Only Scan` / zero `Seq Scan` via `EXPLAIN (ANALYZE, BUFFERS)`.
- ** Trap / Anti-Patterns to Reject:** `use float64 for currency`, `distinct sum(total) hack`

### Q3: Multi-Stage Dockerfiles, BuildKit Layer Caching & Testcontainers Ryuk Reaper
- **Problem Core:** Your E2E runner Docker image is `2.9 GB`, rebuilds `pip/maven` from scratch on every 1-line test edit (`9 min`), and leaks zombie Postgres containers on CI.
- **Staff Benchmark Synthesis:** Copy lockfiles (`pyproject.toml`/`pom.xml`) and install dependencies with `--mount=type=cache` *before* `COPY . .`, copy artifacts into a minimal runtime stage running as non-root `USER 10001` (using Debian-slim/glibc for Playwright browser compatibility), and keep Testcontainers' `Ryuk` TCP heartbeat sidecar enabled to garbage-collect labeled containers/networks on socket disconnect.
- ** Trap / Anti-Patterns to Reject:** `COPY . . before pip install`, `ENV API_SECRET in Dockerfile`, `run as root`

### Q4: Kubernetes Ephemeral PR Environments, Probes & `OOMKilled (Exit 137)` Forensics
- **Problem Core:** Ephemeral PR namespaces suffer sporadic `502 Bad Gateway` during rollout and test pods die with `Exit Code 137` despite JVM `-Xmx6g` on an `8Gi` pod.
- **Staff Benchmark Synthesis:** Total pod RSS = Heap (`6Gi`) + Metaspace + Thread stacks + Direct NIO buffers + glibc arenas + Chromium/native sidecars (>8Gi -> cgroup OOMKill 137); cap JVM at `-XX:MaxRAMPercentage=70.0`. Never check downstream DBs in `livenessProbe` (causes cascading restarts); gate traffic with `readinessProbe` + `preStop` sleep so kube-proxy updates Endpoints before `SIGTERM`.
- ** Trap / Anti-Patterns to Reject:** `put downstream db check inside livenessProbe`, `set Xmx == pod memory limit`

### Q5: Longest-Processing-Time (LPT) CI Shard Bin-Packing & AST Test Impact Analysis
- **Problem Core:** Alphabetical sharding puts all slow Checkout E2E specs onto Shard #3 (`28 min`) while Shards #1, #2, and #4 finish in `5 min`.
- **Staff Benchmark Synthesis:** Sort test files descending by rolling p90 duration and greedily assign each file to the lightest shard via a `K`-element Min-Heap (`O(N log K)`, proven `<= 4/3 - 1/(3K)` optimal makespan), collapsing 28m skew down to balanced ~10m shards. Pair AST/coverage TIA on PRs with mandatory full runs when shared config/Dockerfile/fixtures change.
- ** Trap / Anti-Patterns to Reject:** `split files alphabetically`, `never run full suite on main/nightly`

## Deep-Linked Textbook Chapters
- `sql-02-joins-set-operations-and-fanout-traps`
- `sql-07-acid-mvcc-isolation-and-seat-double-booking`
- `sql-10-event-to-warehouse-reconciliation-and-data-qa`
- `infra-02-multistage-dockerfiles-layer-caching-and-buildkit`
- `infra-04-testcontainers-ephemeral-deps-and-ryuk-reaper`
- `infra-07-dynamic-ci-matrix-sharding-and-bin-packing`
