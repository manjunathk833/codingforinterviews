---
slug: "sql-04-window-functions-ranking-lag-and-dedup"
course_id: "09-sql-and-data-engineering"
track: "system-design"
volume: "09. SQL, PostgreSQL & Data Validation Engineering"
module_number: 1
module_title: "Module 1: Day-0 Relational Foundations, Joins & Analytical Windowing"
chapter_number: 4
level_tag: "Absolute Zero → Senior/Staff"
title: "Window Functions: ROW_NUMBER Deduplication, LAG/LEAD State Audits & Frame Traps"
summary: "Compute rankings, deduplicate at-least-once Kafka/webhook deliveries with `ROW_NUMBER()`, audit illegal `CANCELLED -> CONFIRMED` order state transitions via `LAG()`, and avoid the silent `RANGE` vs `ROWS` window frame bug."
reading_time_minutes: 16
visualizer_id: "sql-mvcc-seat-locking"
lab_path: "frameworks/data-validation/01-sql-reconciliation-and-isolation"
tags: ["sql", "window-functions", "row-number", "lag-lead", "deduplication", "state-machine"]
prerequisites: ["sql-03-aggregations-having-ctes-and-cohort-assertions"]
primary_sources: ["https://www.postgresql.org/docs/current/tutorial-window.html", "https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS", "https://www.sqlite.org/windowfunctions.html"]
---

# Window Functions: ROW_NUMBER Deduplication, LAG/LEAD State Audits & Frame Traps

```json continuity
{
  "previously": "In Chapter 03 (`AeroLedger v0.3`), we grouped millions of rows into route-level SLA buckets using `GROUP BY` and `FILTER (WHERE ...)`.",
  "painPoint": "Payment gateways and Kafka topics deliver webhooks 'at-least-once'—so `AeroLedger` receives duplicate `idem-99` events and occasional out-of-order state flips (`CANCELLED` jumping back to `CONFIRMED`). `GROUP BY` squashes individual rows into one summary number, destroying the exact `event_id` and neighboring row history we need to quarantine bad events!",
  "unlock": "Build AeroLedger v0.4 with SQL Window Functions (`OVER (PARTITION BY ... ORDER BY ...)`): deduplicate retries via `ROW_NUMBER()`, audit state machines via `LAG()`, and master `ROWS` vs `RANGE` sliding frames."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Mental Model",
    "title": "`GROUP BY` Crushes Rows Together; `OVER (...)` Looks Sideways While Keeping Every Row!",
    "caption": "Imagine 5 runners finishing a race. GROUP BY squashes all 5 into 1 row ('Avg time: 11s'). A Window Function (`OVER`) hands each runner a badge ('Rank #1', '0.2s faster than previous runner') while all 5 runners stay in the table!",
    "nodes": ["5 Event Rows", "PARTITION BY booking_id", "ORDER BY event_id", "5 Annotated Rows"],
    "activeIndex": 3,
    "code": "SELECT event_id, booking_id, status,\n       ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id) AS rn\nFROM webhook_events;"
  },
  {
    "time": "0:25",
    "badge": "Webhook Dedup",
    "title": "`ROW_NUMBER() = 1` Is the Universal At-Least-Once Deduplication Filter",
    "caption": "Partitioning by `idempotency_key` and ordering by `received_at ASC, event_id ASC` assigns `rn = 1` to the original webhook and `rn = 2, 3...` to retries—letting QA isolate or purge duplicates deterministically.",
    "nodes": ["idem-1 (#101)", "idem-1 Retry (#102)", "rn=1 (Keep)", "rn=2 (Quarantine)"],
    "activeIndex": 2,
    "code": "WITH ranked AS (\n  SELECT *, ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id) rn\n  FROM webhook_events\n)\nSELECT * FROM ranked WHERE rn = 1;"
  },
  {
    "time": "0:50",
    "badge": "State Machine QA",
    "title": "`LAG(status)` Audits Every Order State Transition Without Self-Joins",
    "caption": "Before window functions, comparing row N to row N-1 required slow, brittle self-joins. `LAG(status) OVER (PARTITION BY booking_id ORDER BY event_id)` peeks directly at the previous state in O(N log N) time!",
    "nodes": ["PENDING", "CANCELLED", "CONFIRMED (Illegal!)", "LAG Catches Regression"],
    "activeIndex": 3,
    "code": "LAG(status) OVER (PARTITION BY booking_id ORDER BY event_id) AS prev_status"
  },
  {
    "time": "1:15",
    "badge": "Frame Gotcha",
    "title": "Why `LAST_VALUE()` Fails Unless You Override the Default `RANGE` Frame",
    "caption": "Whenever you write `ORDER BY` inside `OVER(...)`, SQL silently defaults to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`—meaning `LAST_VALUE` only sees up to the current row, and tied timestamps lump together!",
    "nodes": ["Default RANGE Frame", "Tied Timestamps Lumped!", "Explicit ROWS Frame", "Exact Running Sum"],
    "activeIndex": 2,
    "code": "SUM(cents) OVER (\n  PARTITION BY account_id ORDER BY ts, id\n  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW\n)"
  }
]
```

```json pretraining
[
  {
    "term": "Window Partition (`PARTITION BY`)",
    "formula": "Independent sub-bucket without collapsing rows",
    "meaning": "Splits the table into isolated logical islands (for example, one island per `booking_id`) so window calculations reset cleanly for each booking."
  },
  {
    "term": "`ROW_NUMBER` vs. `RANK` vs. `DENSE_RANK`",
    "formula": "`1,2,3,4` vs. `1,2,2,4` vs. `1,2,2,3` on Ties",
    "meaning": "`ROW_NUMBER` always assigns unique sequential integers even on ties; `RANK` gives ties the same number and skips a slot (`1,2,2,4`); `DENSE_RANK` gives ties the same number with zero gaps (`1,2,2,3`)."
  },
  {
    "term": "Offset Functions (`LAG` / `LEAD`)",
    "formula": "Peek k rows backward (`LAG`) or forward (`LEAD`)",
    "meaning": "Reads a column from the previous or next row inside the same partition—ideal for checking state transitions (`prev_status -> status`) or inter-event latency."
  },
  {
    "term": "Window Frame (`ROWS` vs. `RANGE`)",
    "formula": "Physical Row Count (`ROWS`) vs. Peer Value Ties (`RANGE`)",
    "meaning": "Controls which subset of rows inside a partition enters a running `SUM` or `AVG`. `RANGE` groups tied `ORDER BY` values together; `ROWS` steps strictly one physical row at a time."
  }
]
```

## 🌱 Step 1: Plain-English Mental Model — Annotating Rows Without Crushing Them

In Chapter 03, `GROUP BY` worked like a trash compactor: feed in 100 events for booking `BK-201`, and out comes **1 summary row**—wiping out the individual event timestamps and IDs.

A **Window Function (`OVER (...)`)** works like a security camera watching a line of passengers at boarding: every passenger keeps their own row in line, *and* gets a sticky note showing their position in line (`ROW_NUMBER`), who stood right ahead of them (`LAG`), or the running weight of bags boarded so far (`SUM(...) OVER (...)`).

```mermaid
flowchart LR
    In["4 Webhook Rows (BK-201)"] --> P["PARTITION BY booking_id"]
    P --> O["ORDER BY event_id ASC"]
    O --> Out["Still 4 Rows + rn & prev_status Columns!"]
```

Notice why Window Functions are the **#1 most-tested Senior/Staff SQL interview topic**:
- Need the **latest status per booking**? `ROW_NUMBER() = 1` sorted newest-first.
- Need **duplicate Kafka/webhook detection**? `ROW_NUMBER() > 1` partitioned by `idempotency_key`.
- Need **illegal state-machine transition QA** (`CANCELLED -> CONFIRMED`)? Compare `LAG(status)` to `status`.

---

## 🔨 Step 2: Zero-to-Running Starter & CLI — Webhook Dedup & State Machine QA (`AeroLedger v0.4`)

Both `PostgreSQL 17` and `SQLite 3.25+` support full ANSI window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `ROWS BETWEEN`):

```bash
# Quick CLI check of ROW_NUMBER vs RANK vs DENSE_RANK on tied fares (100, 200, 200, 300):
sqlite3 :memory: "WITH t(v) AS (VALUES (100),(200),(200),(300)) SELECT v, ROW_NUMBER() OVER (ORDER BY v), RANK() OVER (ORDER BY v), DENSE_RANK() OVER (ORDER BY v) FROM t;"
```

Let's implement **`AeroLedger v0.4`** to strip duplicate webhook deliveries and catch an illegal `CANCELLED -> CONFIRMED` resurrection bug:

```python
from __future__ import annotations
import sqlite3

# Subgoal 1: Seed raw at-least-once webhook stream (event 2 is a duplicate of event 1!)
conn = sqlite3.connect(":memory:")
conn.executescript("""
    CREATE TABLE webhook_events (
        event_id        INTEGER PRIMARY KEY,
        booking_id      TEXT NOT NULL,
        idempotency_key TEXT NOT NULL,
        status          TEXT NOT NULL
    );
    INSERT INTO webhook_events VALUES
        (1, 'BK-201', 'idem-a', 'PENDING'),
        (2, 'BK-201', 'idem-a', 'PENDING'),
        (3, 'BK-201', 'idem-b', 'CANCELLED'),
        (4, 'BK-201', 'idem-c', 'CONFIRMED');
""")

# Subgoal 2: Deduplicate retries (rn = 1) in CTE 1, then peek backward with LAG() in CTE 2
violations = conn.execute("""
    WITH deduped AS (
        SELECT event_id, booking_id, status,
               ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id ASC) AS rn
        FROM webhook_events
    ),
    transitions AS (
        SELECT booking_id, event_id,
               LAG(status) OVER (PARTITION BY booking_id ORDER BY event_id ASC) AS prev_status,
               status AS next_status
        FROM deduped
        WHERE rn = 1
    )
    SELECT booking_id, event_id, prev_status, next_status
    FROM transitions
    WHERE prev_status = 'CANCELLED' AND next_status = 'CONFIRMED'
""").fetchall()

# Subgoal 3: Confirm duplicate event #2 was ignored and illegal transition at event #4 was caught
assert violations == [("BK-201", 4, "CANCELLED", "CONFIRMED")]
print(f"AeroLedger v0.4 caught state-machine bug: {violations}")
```

### Java 17 Equivalent

```java
import java.sql.*;
import java.util.*;

public class AeroLedgerV04WindowAudit {
    // Subgoal 1: Two-stage CTE combining ROW_NUMBER() deduplication + LAG() state audit
    private static final String STATE_AUDIT_SQL = """
        WITH deduped AS (
            SELECT event_id, booking_id, status,
                   ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id ASC) AS rn
            FROM webhook_events
        ),
        transitions AS (
            SELECT booking_id, event_id,
                   LAG(status) OVER (PARTITION BY booking_id ORDER BY event_id ASC) AS prev_status,
                   status AS next_status
            FROM deduped
            WHERE rn = 1
        )
        SELECT booking_id, event_id, prev_status, next_status
        FROM transitions
        WHERE prev_status = 'CANCELLED' AND next_status = 'CONFIRMED'
        """;

    // Subgoal 2: Execute deterministically via JDBC PreparedStatement
    public static List<String> findIllegalResurrections(Connection conn) throws SQLException {
        List<String> violations = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(STATE_AUDIT_SQL);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                violations.add(rs.getString("booking_id") + ":" + rs.getInt("event_id"));
            }
        }
        return violations;
    }

    public static void main(String[] args) {
        assert STATE_AUDIT_SQL.contains("LAG(status) OVER");
    }
}
```

**Starter Walkthrough:**
- **Why wrap `ROW_NUMBER()` inside a CTE instead of `WHERE ROW_NUMBER() OVER (...) = 1`?** Remember Chapter 03's execution conveyor! Window functions execute inside **`SELECT` (Phase 5)**, *after* `WHERE` (Phase 2) and `GROUP BY` (Phase 3) have already finished! Wrapping in a CTE lets the outer `WHERE rn = 1` filter cleanly.

---

## 🛠️ Step 3: Everyday Practitioner Workflows & Where Naive Code Breaks

### Two Classic Window Bugs in Financial & Event Pipelines

1. **Non-Deterministic Tie-Breaking in `ROW_NUMBER()`**:
   - Suppose two webhooks arrive in the exact same millisecond (`received_at = '10:00:00.123'`). Writing `ORDER BY received_at DESC` without a unique tie-breaker (`ORDER BY received_at DESC, event_id DESC`) makes `rn = 1` **non-deterministic** across runs, causing flaky tests!
2. **The Default `RANGE` Frame Trap on Running Balances**:
   - When you write `SUM(amount_cents) OVER (ORDER BY created_at)` *without* a frame clause, ANSI SQL silently injects **`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`**. If two `$100` charges share the exact same `created_at` timestamp, `RANGE` treats them as peers and displays `$200` on **both** rows instead of `$100` then `$200`! Always specify **`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`** (or include a unique tie-breaker column in `ORDER BY`).

```json contrast
{
  "title": "Running Ledger Balance & Top-N Per Group",
  "leftLabel": "❌ Naive Window (`RANGE` Default + Non-Unique Sort)",
  "leftCode": "-- 1. Tied timestamps jump from $0 straight to $200 on both rows!\nSELECT tx_id,\n  SUM(cents) OVER (PARTITION BY acct_id ORDER BY created_at)\nFROM ledger_tx;\n\n-- 2. Flaky tie-break when two rows share `created_at`:\nROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)",
  "rightLabel": "✅ Staff Window (Explicit `ROWS` Frame + Tie-Breaker PK)",
  "rightCode": "-- 1. Strict row-by-row running balance ($100 -> $200):\nSELECT tx_id,\n  SUM(cents) OVER (\n    PARTITION BY acct_id ORDER BY created_at, tx_id\n    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW\n  ) AS running_cents\nFROM ledger_tx;\n\n-- 2. Deterministic tie-breaking via monotonic PK:\nROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC, tx_id DESC)"
}
```

```json poe
{
  "question": "Four flights have ticket prices `$200`, `$300`, `$300`, and `$500`. If we order ascending (`ORDER BY price ASC`), what values do `(ROW_NUMBER, RANK, DENSE_RANK)` assign to the `$500` flight?",
  "options": [
    "`(4, 4, 3)` — `ROW_NUMBER` is 4th row, `RANK` skips 3 after the two tied 2s (`1,2,2,4`), and `DENSE_RANK` has no gap (`1,2,2,3`)",
    "`(4, 3, 4)`",
    "`(3, 3, 3)`",
    "`(4, 4, 4)`"
  ],
  "answerIndex": 0,
  "explanation": "On `$200, $300, $300, $500`: `ROW_NUMBER` outputs `1, 2, 3, 4`; `RANK` outputs `1, 2, 2, 4` (olympic podium style—two silvers means no bronze, next is 4th); `DENSE_RANK` outputs `1, 2, 2, 3` (distinct price tiers!). Therefore `'Top 3 distinct highest salaries'` always requires `DENSE_RANK() <= 3`!"
}
```

---

## 🏢 Step 4: How Big Tech Runs It at Scale, Staff Math & Production Blueprint

### 🏢 In the Wild: Uber & Airbnb Lakehouse Deduplication (`ROW_NUMBER` vs `DISTINCT ON`)

In **Uber's Kafka-to-Hudi/Pinot** ingestion pipelines and **Airbnb's Minerva** metric layer, raw event streams always contain duplicate retries from mobile reconnects and Kafka consumer rebalances:
- **In Warehouse/ANSI SQL (`BigQuery`, `Snowflake`, `Spark`, `PostgreSQL`, `SQLite`)**: Staging views apply `ROW_NUMBER() OVER (PARTITION BY event_uuid ORDER BY ingested_at ASC) = 1` (or `QUALIFY ROW_NUMBER() ... = 1` in Snowflake/BigQuery/DuckDB) before downstream joins.
- **In OLTP `PostgreSQL 17` Point-Latest Queries**: When fetching *only* the single latest row per partition (`latest checkpoint per flight`), PostgreSQL's native **`SELECT DISTINCT ON (flight_id) * FROM telemetry ORDER BY flight_id, recorded_at DESC, id DESC`** executes faster than a full `ROW_NUMBER()` window sort when backed by an index on `(flight_id, recorded_at DESC, id DESC)`, because it skips straight to the first index entry per flight!

### Window Sort & Memory Complexity Math

Evaluating a window function with `PARTITION BY p ORDER BY o` without a matching composite index `(p, o)` requires an external/in-memory sort of $N$ rows:

$$T_{\text{window}} = \begin{cases} \mathcal{O}(N) \text{ streaming pass} & \text{if B+Tree index exists on } (p, o) \\ \mathcal{O}(N \log N) \text{ + temp disk spill} & \text{if no matching index or } \text{Mem}(N) > \texttt{work\_mem} \end{cases}$$

| Task | Best Function / Idiom | Why It Wins |
| :--- | :--- | :--- |
| **Deduplicate retries (`1` winner per key)** | `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts, id) = 1` | Guarantees exactly 1 surviving row even when timestamps tie |
| **Top-K distinct tiers (e.g. Top 3 Fares)** | `DENSE_RANK() OVER (ORDER BY fare DESC) <= 3` | Never skips rank `3` when two flights tie for rank `2` |
| **State-machine / Latency delta (`t_i - t_{i-1}`)** | `LAG(col, 1) OVER (PARTITION BY id ORDER BY seq)` | Eliminates $\mathcal{O}(N^2)$ inequality self-joins |
| **Sliding N-row moving average** | `AVG(ms) OVER (ORDER BY seq ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)` | Strict 5-sample window immune to timestamp ties |

### Production Blueprint: Deterministic Running Wallet & Rolling Latency Detector

```python
from __future__ import annotations
import sqlite3


def audit_wallet_and_top_tiers() -> tuple[list[tuple[int, int]], list[tuple[str, int]]]:
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE wallet_postings (
            tx_id      INTEGER PRIMARY KEY,
            user_id    TEXT NOT NULL,
            posted_at  TEXT NOT NULL,
            delta_cents INTEGER NOT NULL
        );
        INSERT INTO wallet_postings VALUES
            (1, 'U-1', '2026-11-11T10:00:00Z',  50000),
            (2, 'U-1', '2026-11-11T10:05:00Z', -20000),
            (3, 'U-1', '2026-11-11T10:05:00Z', -35000); -- Same timestamp as tx 2, dips to -5000!
    """)

    # 1. Explicit ROWS frame + tx_id tie-breaker catches mid-second negative overdraft (-5000)!
    overdrafts = conn.execute("""
        WITH ledger_balances AS (
            SELECT tx_id,
                   SUM(delta_cents) OVER (
                       PARTITION BY user_id
                       ORDER BY posted_at ASC, tx_id ASC
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                   ) AS running_balance_cents
            FROM wallet_postings
        )
        SELECT tx_id, running_balance_cents
        FROM ledger_balances
        WHERE running_balance_cents < 0
    """).fetchall()

    # 2. DENSE_RANK for Top-2 distinct spend tiers
    conn.execute("CREATE TABLE route_fares (flight_id TEXT, fare_cents INT)")
    conn.executemany(
        "INSERT INTO route_fares VALUES (?, ?)",
        [("F1", 90000), ("F2", 90000), ("F3", 75000), ("F4", 40000)],
    )
    top_two_tiers = conn.execute("""
        WITH tiered AS (
            SELECT flight_id, fare_cents,
                   DENSE_RANK() OVER (ORDER BY fare_cents DESC) AS dr
            FROM route_fares
        )
        SELECT flight_id, fare_cents FROM tiered WHERE dr <= 2 ORDER BY fare_cents DESC, flight_id ASC
    """).fetchall()
    return overdrafts, top_two_tiers


if __name__ == "__main__":
    od, top = audit_wallet_and_top_tiers()
    assert od == [(3, -5000)]
    assert top == [("F1", 90000), ("F2", 90000), ("F3", 75000)]
```

### Java 17 Equivalent

```java
import java.sql.*;
import java.util.*;

public final class WalletOverdraftWindowAuditor {
    public record OverdraftEvent(long txId, long runningBalanceCents) {}

    public static List<OverdraftEvent> findIntradayOverdrafts(Connection conn, String userId) throws SQLException {
        String sql = """
            WITH ledger_balances AS (
                SELECT tx_id,
                       SUM(delta_cents) OVER (
                           PARTITION BY user_id
                           ORDER BY posted_at ASC, tx_id ASC
                           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                       ) AS running_balance_cents
                FROM wallet_postings
                WHERE user_id = ?
            )
            SELECT tx_id, running_balance_cents
            FROM ledger_balances
            WHERE running_balance_cents < 0
            ORDER BY tx_id ASC
            """;
        List<OverdraftEvent> events = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, userId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    events.add(new OverdraftEvent(rs.getLong(1), rs.getLong(2)));
                }
            }
        }
        return events;
    }
}
```

> [!WARNING]
> **Hiring Bar-Raiser Gotcha — Never Use `LAST_VALUE(col) OVER (PARTITION BY x ORDER BY y)` Without Extending the Frame!**
> Almost every candidate gets tripped up by `LAST_VALUE`: because adding `ORDER BY y` sets the default window frame to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, `LAST_VALUE(status)` simply returns **the current row's own `status`**! Either use `FIRST_VALUE(status) OVER (PARTITION BY x ORDER BY y DESC)` or explicitly write `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

*Up Next in Chapter 05*: Module 1 gave us expressive, rock-solid SQL queries—but on **20 million bookings**, our queries now take `800ms`! Module 2 opens the storage hood: **B+Tree Composite Indexes, Leftmost Prefixes & Sargability**.

```json quiz
[
  {
    "id": "sql04-q1",
    "question": "Why does `SELECT event_id FROM webhooks WHERE ROW_NUMBER() OVER (PARTITION BY idem_key ORDER BY event_id) = 1` fail in standard PostgreSQL and SQLite?",
    "options": [
      "`ROW_NUMBER()` requires at least one argument",
      "Window functions are evaluated logically during the `SELECT` phase—after `WHERE` and `GROUP BY` have already completed—so you must filter `rn = 1` in an outer query or CTE",
      "`PARTITION BY` cannot be used on `TEXT` columns",
      "`ROW_NUMBER()` starts counting at `0`"
    ],
    "answerIndex": 1,
    "explanation": "Window functions only execute after `FROM`, `WHERE`, `GROUP BY`, and `HAVING` complete. Wrap the window projection in a `WITH` CTE and apply `WHERE rn = 1` in the outer `SELECT`."
  },
  {
    "id": "sql04-q2",
    "question": "A user deposits `+$100` at `10:00:00Z`, then two charges of `-$80` and `-$50` both settle at the exact same timestamp `10:01:00Z` (leaving `-$30`). Why might `SUM(delta) OVER (ORDER BY ts)` miss the intermediate `+20` state and jump straight from `+100` to `-30` on both rows?",
    "options": [
      "`SUM` cannot sum negative numbers inside window functions",
      "Omitting a frame clause with `ORDER BY` defaults to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, which merges all peer rows sharing the same `ts` timestamp!",
      "PostgreSQL sorts timestamps randomly",
      "`OVER` automatically deduplicates rows"
    ],
    "answerIndex": 1,
    "explanation": "`RANGE` groups equal `ORDER BY` peer values together. Adding a unique tie-breaker (`ORDER BY ts, tx_id`) and explicit `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` processes strictly one transaction at a time."
  },
  {
    "id": "sql04-q3",
    "question": "An interviewer asks for 'all employees earning one of the Top 3 highest distinct salary amounts in each department (if two tie for #1, the next distinct salary is #2, not #3).' Which function is required?",
    "options": [
      "`ROW_NUMBER()`",
      "`RANK()`",
      "`DENSE_RANK()`",
      "`NTILE(3)`"
    ],
    "answerIndex": 2,
    "explanation": "`DENSE_RANK()` assigns identical ranks to ties without skipping subsequent rank numbers (`1, 1, 2, 3`), whereas `RANK()` skips (`1, 1, 3`) and `ROW_NUMBER()` arbitrarily breaks ties (`1, 2, 3`)."
  }
]
```

---

## 📋 Step 5: Master Cheat-Sheet, 60-Second Interview Pitch & Verified Sources

| Analytical Need | Exact Window Expression | Critical Detail |
| :--- | :--- | :--- |
| **At-Least-Once Dedup** | `ROW_NUMBER() OVER (PARTITION BY idem_key ORDER BY ts, id) = 1` | Always include unique `id` tie-breaker! |
| **Top-K Distinct Tiers** | `DENSE_RANK() OVER (PARTITION BY dept ORDER BY score DESC) <= K` | Zero rank gaps when values tie |
| **State Transition Audit** | `LAG(status, 1, 'INIT') OVER (PARTITION BY id ORDER BY seq)` | 3rd arg `'INIT'` replaces leading `NULL`! |
| **Exact Running Balance** | `SUM(x) OVER (PARTITION BY acct ORDER BY ts, id ROWS UNBOUNDED PRECEDING)` | Explicit `ROWS` avoids `RANGE` peer lumping |
| **Postgres Latest-1 Fast Path** | `SELECT DISTINCT ON (flight_id) * FROM t ORDER BY flight_id, ts DESC, id DESC` | Uses `(flight_id, ts DESC, id DESC)` index directly |

### 🎙️ 60-Second Interview Soundbite

> *"Whenever I need per-entity ranking, webhook deduplication, or state-machine verification without collapsing row granularity, I reach for window functions inside a CTE. For at-least-once Kafka or webhook streams, I partition by `idempotency_key` and order by `received_at ASC, event_id ASC` with `ROW_NUMBER() = 1`—always including a monotonic tie-breaker so ties are 100% deterministic. For order lifecycle QA, `LAG(status)` lets me assert state-transition invariants in a single pass without quadratic self-joins. And on running balances or `LAST_VALUE`, I explicitly declare `ROWS BETWEEN ...` rather than relying on SQL's default `RANGE` frame so tied timestamps never lump together."*

### 📚 Verified Primary Sources
- [PostgreSQL 17 Official Docs — Window Functions Tutorial](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL 17 Official Docs — Window Function Calls & Frame Clauses (`ROWS` vs `RANGE`)](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS)
- [SQLite Official Documentation — Window Functions & Frame Specifications](https://www.sqlite.org/windowfunctions.html)
