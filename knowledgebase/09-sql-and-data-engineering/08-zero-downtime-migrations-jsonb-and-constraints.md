---
slug: "sql-08-zero-downtime-migrations-jsonb-and-constraints"
course_id: "09-sql-and-data-engineering"
track: "system-design"
volume: "09. SQL, PostgreSQL & Data Validation Engineering"
module_number: 2
module_title: "Module 2: Storage Internals, Query Plans, MVCC Concurrency & Zero-Downtime Evolution"
chapter_number: 8
level_tag: "Absolute Zero → Senior/Staff"
title: "Zero-Downtime Schema Migrations, Lock Queues, JSONB GIN Indexes & NOT VALID"
summary: "Prevent catastrophic production outages caused by PostgreSQL `ACCESS EXCLUSIVE` lock queues: master Expand-Contract migrations, `lock_timeout` guards, `CREATE INDEX CONCURRENTLY`, `NOT VALID` + `VALIDATE CONSTRAINT`, and semi-structured `JSONB` indexing."
reading_time_minutes: 16
visualizer_id: "sql-btree-explain-planner"
lab_path: "frameworks/data-validation/01-sql-reconciliation-and-isolation"
tags: ["sql", "schema-migrations", "zero-downtime", "expand-contract", "jsonb", "gin-index", "locks"]
prerequisites: ["sql-05-btree-composite-indexes-and-sargability", "sql-07-acid-mvcc-isolation-and-seat-double-booking"]
primary_sources: ["https://www.postgresql.org/docs/current/explicit-locking.html", "https://www.postgresql.org/docs/current/sql-altertable.html", "https://www.postgresql.org/docs/current/datatype-json.html"]
---

# Zero-Downtime Schema Migrations, Lock Queues, JSONB GIN Indexes & NOT VALID

```json continuity
{
  "previously": "In Chapter 07 (`AeroLedger v0.7`), we protected seat inventory with MVCC row locks (`FOR UPDATE SKIP LOCKED`) and expiring leases.",
  "painPoint": "On Tuesday at 2 PM, an engineer ran `ALTER TABLE bookings ADD CONSTRAINT chk_fare CHECK (fare_cents > 0);` on our 80-million-row production table. Because a 45-second analytics report was reading `bookings`, the `ALTER TABLE` waited for an `ACCESS EXCLUSIVE` lock—and queued EVERY incoming checkout `SELECT` and `INSERT` behind it, causing a total 100% site outage in 4 seconds!",
  "unlock": "Upgrade to AeroLedger v0.8: prevent DDL lock-queue pileups with `lock_timeout`, roll out constraints via `NOT VALID` + `VALIDATE CONSTRAINT`, build indexes with `CREATE INDEX CONCURRENTLY`, and index dynamic partner payloads using `JSONB` + `GIN`."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "The Outage Physics",
    "title": "Why a '10ms' `ALTER TABLE` Takes Down Production: The FIFO Lock Queue Trap!",
    "caption": "`ALTER TABLE` requests an `ACCESS EXCLUSIVE` lock. If a 30s analytical `SELECT` is currently running, `ALTER TABLE` waits in line—and every new `SELECT` or `INSERT` queues BEHIND the waiting `ALTER TABLE`!",
    "nodes": ["30s Report ( Holds Read Lock)", "ALTER TABLE (Waits for Exclusive)", "2,000 Checkout Queries (Blocked Behind ALTER!)", "Site Outage!"],
    "activeIndex": 2,
    "code": "-- Mandatory safety belt before ANY production DDL in PostgreSQL:\nSET lock_timeout = '2s';\nSET statement_timeout = '15s';"
  },
  {
    "time": "0:25",
    "badge": "Two-Phase Constraints",
    "title": "Decouple Enforcement from Full-Table Scanning via `NOT VALID` + `VALIDATE CONSTRAINT`",
    "caption": "Adding a CHECK or FOREIGN KEY with `NOT VALID` enforces the rule on all NEW writes immediately without scanning existing rows! Then `VALIDATE CONSTRAINT` scans historical rows under a non-blocking `SHARE UPDATE EXCLUSIVE` lock.",
    "nodes": ["1. ADD ... NOT VALID (<5ms)", "New Writes Protected!", "2. Backfill Legacy Rows", "3. VALIDATE CONSTRAINT (Non-Blocking!)"],
    "activeIndex": 3,
    "code": "ALTER TABLE bookings ADD CONSTRAINT fk_flight\n  FOREIGN KEY (flight_id) REFERENCES flights(flight_id) NOT VALID;\n-- In a separate post-deploy step (does NOT block reads or writes!):\nALTER TABLE bookings VALIDATE CONSTRAINT fk_flight;"
  },
  {
    "time": "0:50",
    "badge": "Concurrent Indexes",
    "title": "`CREATE INDEX` Blocks Writes; `CREATE INDEX CONCURRENTLY` Keeps Writes Live!",
    "caption": "Standard `CREATE INDEX` takes a `SHARE` lock that blocks all `INSERT`/`UPDATE`/`DELETE` calls. `CREATE INDEX CONCURRENTLY` scans the table in two passes without blocking writes—just watch out for `INVALID` failed builds!",
    "nodes": ["CREATE INDEX (Blocks Writes!)", "CONCURRENTLY Pass 1", "CONCURRENTLY Pass 2", "Verify indisvalid=true"],
    "activeIndex": 2,
    "code": "-- Must run OUTSIDE a BEGIN...COMMIT transaction block:\nCREATE INDEX CONCURRENTLY idx_bookings_pax ON bookings (passenger_id);"
  },
  {
    "time": "1:15",
    "badge": "JSONB + GIN",
    "title": "Store Partner Metadata in `JSONB` (Binary Tree) & Index Containment (`@>`) with `GIN`",
    "caption": "Different airlines send custom loyalty/meal fields. Instead of 50 sparse nullable columns, store them in binary `JSONB` (never text `JSON`!) and index `@>` lookups via `USING gin (metadata jsonb_path_ops)`.",
    "nodes": ["Partner JSON Payload", "JSONB Binary Storage", "GIN jsonb_path_ops Index", "0.3ms `@>` Query"],
    "activeIndex": 2,
    "code": "CREATE INDEX CONCURRENTLY idx_meta_gin ON bookings USING gin (meta jsonb_path_ops);\nSELECT booking_id FROM bookings WHERE meta @> '{\"meal\": \"VEGAN\"}';"
  }
]
```

```json pretraining
[
  {
    "term": "Lock Queue Convoy (`ACCESS EXCLUSIVE`)",
    "formula": "Long Reader -> Waiting DDL -> All Subsequent Readers/Writers Blocked",
    "meaning": "Even if an `ALTER TABLE` takes 1ms on its own, waiting behind an active query for an `ACCESS EXCLUSIVE` lock blocks every new `SELECT` and `INSERT` arriving after it."
  },
  {
    "term": "Expand-Contract Pattern (Parallel Change)",
    "formula": "1. Expand (Additive) -> 2. Dual-Write/Backfill -> 3. Switch Reads -> 4. Contract",
    "meaning": "Rolling out schema changes across multiple safe steps so old and new application pods can run side-by-side during a rolling Kubernetes deploy without errors."
  },
  {
    "term": "`NOT VALID` + `VALIDATE CONSTRAINT`",
    "formula": "Instant Metadata Gate + Non-Blocking Historical Scan",
    "meaning": "PostgreSQL's two-phase constraint mechanism that enforces `CHECK`/`FOREIGN KEY` rules on new writes immediately while validating old rows without blocking traffic."
  },
  {
    "term": "`JSONB` vs. `JSON` + `GIN` Index",
    "formula": "Parsed Binary Key/Value Tree + Generalized Inverted Index (`@>`)",
    "meaning": "`JSON` stores raw unparsed text; `JSONB` parses keys into binary form on write so PostgreSQL can index nested keys using a `GIN` inverted index."
  }
]
```

## 🌱 Step 1: Plain-English Mental Model — Renovating an Airport Runway Without Closing the Airport

Why did a 5-millisecond `ALTER TABLE` take down all of `AeroCart`? Imagine a single-lane security checkpoint:
1. A slow tour bus (**30-second analytics `SELECT`**) is currently passing through.
2. A maintenance crew (**`ALTER TABLE` needing `ACCESS EXCLUSIVE`**) arrives and waits for the bus to finish.
3. Behind the maintenance crew, **2,000 regular passengers (`SELECT` and `INSERT` checkouts)** line up—blocked not by the 5ms maintenance work itself, but by the **waiting maintenance crew blocking the lane**!

```mermaid
flowchart LR
    Slow["Slow 30s SELECT"] -->|"Blocks"| Alter["Waiting ALTER TABLE (ACCESS EXCLUSIVE)"]
    Alter -->|"Blocks ALL"| Traffic["2,000 Live Checkout Queries -> Timeout!"]
```

To evolve a live 24/7 database with **zero downtime**, Staff engineers follow two ironclad laws:
1. **Always set `SET lock_timeout = '2s'`** so if `ALTER TABLE` cannot grab its lock within 2 seconds, it aborts harmlessly and retries instead of piling up a checkout queue.
2. **Use Expand-Contract**: never rename or drop a column while old application pods still read it!

---

## 🔨 Step 2: Zero-to-Running Starter & CLI — Migration Safety Linter & JSON Querying (`AeroLedger v0.8`)

Both `PostgreSQL 17` (`JSONB` / `jsonb_extract_path_text`) and `SQLite 3.38+` (`->>` JSON extraction + expression indexes) support querying and indexing semi-structured JSON payloads natively:

```bash
# Test native JSON `->>` extraction + indexed lookup in built-in SQLite 3.38+:
sqlite3 :memory: "CREATE TABLE b(id TEXT, meta TEXT); INSERT INTO b VALUES ('BK-1', '{\"tier\":\"GOLD\"}'); SELECT id FROM b WHERE meta ->> '$.tier' = 'GOLD';"
```

Let's build **`AeroLedger v0.8`** with an automated **DDL Migration Safety Linter** (catching blocking `CREATE INDEX` or unguarded `ADD CONSTRAINT` in CI) plus indexed JSON metadata extraction:

```python
from __future__ import annotations
import re
import sqlite3

# Subgoal 1: Lint raw migration SQL files in CI before they ever touch staging/prod
def lint_postgres_migration(sql: str) -> list[str]:
    errors: list[str] = []
    if "lock_timeout" not in sql.lower():
        errors.append("Missing `SET lock_timeout = '2s';` guard at start of migration")
    if re.search(r"\bCREATE\s+(?:UNIQUE\s+)?INDEX\b(?!\s+CONCURRENTLY)", sql, re.I):
        errors.append("Use `CREATE INDEX CONCURRENTLY` to avoid blocking table writes")
    if re.search(r"\bADD\s+CONSTRAINT\b.*?\b(?:FOREIGN\s+KEY|CHECK)\b(?![^;]*\bNOT\s+VALID\b)", sql, re.I | re.S):
        errors.append("Add FK/CHECK constraints with `NOT VALID`, then `VALIDATE CONSTRAINT`")
    return errors

# Subgoal 2: Index and query semi-structured partner metadata (`meta`) without full table scans
conn = sqlite3.connect(":memory:")
conn.executescript("""
    CREATE TABLE bookings (booking_id TEXT PRIMARY KEY, meta TEXT NOT NULL CHECK (json_valid(meta)));
    CREATE INDEX idx_bookings_loyalty_tier ON bookings (json_extract(meta, '$.loyalty_tier'));
    INSERT INTO bookings VALUES ('BK-101', '{"loyalty_tier": "PLATINUM", "meal": "VEGAN"}');
""")

# Subgoal 3: Verify unsafe DDL is blocked and JSON expression index serves the query
unsafe_ddl = "CREATE INDEX idx_a ON bookings(booking_id); ALTER TABLE bookings ADD CONSTRAINT c CHECK (1=1);"
assert len(lint_postgres_migration(unsafe_ddl)) == 3
plan = str(conn.execute("EXPLAIN QUERY PLAN SELECT booking_id FROM bookings WHERE json_extract(meta, '$.loyalty_tier') = 'PLATINUM'").fetchall())
assert "idx_bookings_loyalty_tier" in plan
print("AeroLedger v0.8 DDL linter & JSON index verified!")
```

### Java 17 Equivalent

```java
import java.sql.*;
import java.util.*;

public class AeroLedgerV08ZeroDowntimeMigration {
    // Subgoal 1: Safe PostgreSQL 17 two-step constraint rollout with lock_timeout guard
    public static final List<String> SAFE_CONSTRAINT_STEPS = List.of(
        "SET LOCAL lock_timeout = '2s'",
        "ALTER TABLE bookings ADD CONSTRAINT chk_fare_pos CHECK (fare_cents >= 0) NOT VALID"
    );

    // Subgoal 2: Query PostgreSQL JSONB containment (@>) using GIN jsonb_path_ops index
    public static List<String> findBookingsByJsonFilter(Connection conn, String jsonFilter) throws SQLException {
        String sql = "SELECT booking_id FROM bookings WHERE meta @> ?::jsonb ORDER BY booking_id";
        List<String> ids = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, jsonFilter);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    ids.add(rs.getString(1));
                }
            }
        }
        return ids;
    }

    public static void main(String[] args) {
        assert SAFE_CONSTRAINT_STEPS.get(1).endsWith("NOT VALID");
    }
}
```

**Starter Walkthrough:**
- In **Subgoal 1**, `lint_postgres_migration()` catches the 3 most common production outage triggers during PR review—before a migration script can ever merge!
- In **Subgoal 2**, `CHECK (json_valid(meta))` in SQLite (or native `JSONB` in Postgres) plus an expression/GIN index lets `AeroLedger` query partner-specific fields in sub-millisecond time.

---

## 🛠️ Step 3: Everyday Practitioner Workflows & Where Naive Code Breaks

### What Is Instant vs. What Rewrites the Whole Table in PostgreSQL 17?

| DDL Operation in PostgreSQL 11–17 | Table Rewrite? | Blocking Risk & Safe Pattern |
| :--- | :--- | :--- |
| **`ADD COLUMN col TEXT DEFAULT 'std' NOT NULL`** | **NO Rewrite!** (PG 11+ metadata-only!) | Fast metadata update—**still set `lock_timeout = '2s'`**! |
| **`ADD COLUMN col TEXT DEFAULT gen_random_uuid()`** | **YES! Full Rewrite** if volatile in older PG | Check volatility; backfill in batches if rewriting existing rows |
| **`ALTER COLUMN col TYPE BIGINT` (from `INT`)** | **YES! Full Table Rewrite (`ACCESS EXCLUSIVE`)!** | **NEVER on big tables!** Use Expand-Contract (`col_v2 BIGINT`) |
| **`ADD CONSTRAINT ... CHECK / FOREIGN KEY`** | **YES! Full Scan under heavy lock** | Use `ADD CONSTRAINT ... NOT VALID` + `VALIDATE CONSTRAINT` |
| **`SET NOT NULL` on existing column** | **Full Scan unless backed by `CHECK NOT VALID`!** | Add `CHECK (col IS NOT NULL) NOT VALID` $\to$ `VALIDATE` $\to$ `SET NOT NULL`! |

```json contrast
{
  "title": "Adding a NOT NULL Constraint & Index to an 80M-Row Table",
  "leftLabel": "❌ Naive Migration (Blocks Writes for 6 Minutes!)",
  "leftCode": "-- 1. Blocks all INSERT/UPDATE/DELETE during index build:\nCREATE INDEX idx_bk_user ON bookings (user_id);\n\n-- 2. Acquires ACCESS EXCLUSIVE & scans all 80M rows:\nALTER TABLE bookings ALTER COLUMN user_id SET NOT NULL;",
  "rightLabel": "✅ GitLab / Stripe Zero-Downtime Pattern",
  "rightCode": "-- 1. Non-blocking concurrent index build:\nCREATE INDEX CONCURRENTLY idx_bk_user ON bookings (user_id);\n\n-- 2. Non-blocking NOT VALID check -> VALIDATE -> instant SET NOT NULL:\nSET lock_timeout = '2s';\nALTER TABLE bookings ADD CONSTRAINT chk_user_nn CHECK (user_id IS NOT NULL) NOT VALID;\nALTER TABLE bookings VALIDATE CONSTRAINT chk_user_nn;\nALTER TABLE bookings ALTER COLUMN user_id SET NOT NULL;\nALTER TABLE bookings DROP CONSTRAINT chk_user_nn;"
}
```

```json poe
{
  "question": "A `CREATE INDEX CONCURRENTLY idx_orders_email ON orders (email)` job fails halfway through because a background worker hit a deadlock. What state is `idx_orders_email` left in inside PostgreSQL?",
  "options": [
    "PostgreSQL automatically rolls back and deletes the index",
    "The index remains on disk marked `INVALID` (`pg_index.indisvalid = false`): the query planner ignores it for `SELECT`s, YET every `INSERT`/`UPDATE` still pays the write overhead of updating it until you `DROP INDEX CONCURRENTLY`!",
    "The `orders` table becomes read-only",
    "PostgreSQL automatically retries in 60 seconds"
  ],
  "answerIndex": 1,
  "explanation": "Because `CREATE INDEX CONCURRENTLY` cannot run inside a transaction, a failed build leaves an `INVALID` index behind (`indisvalid = false`). It slows down writes without helping reads! Always check `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;` after migrations."
}
```

---

## 🏢 Step 4: How Big Tech Runs It at Scale, Staff Math & Production Blueprint

### 🏢 In the Wild: GitLab's 3-Release Expand-Contract & Batched Background Migrations

At **GitLab** and **Stripe**, Kubernetes rolling deployments run `v1` and `v2` application pods simultaneously for 10–30 minutes. If a migration renames `promo_code` to `discount_code` in place, all running `v1` pods crash immediately with `ERROR: column "promo_code" does not exist`!
Instead, GitLab enforces a **3-Step Expand-Contract Lifecycle**:
1. **Release 1 (Expand)**: Add nullable `discount_code TEXT`, install a lightweight database trigger (or app dual-write) copying `promo_code <-> discount_code`, and start a throttled **Batched Background Migration** (`UPDATE ... WHERE id BETWEEN $1 AND $2` in `5,000`-row chunks with `100ms` pause between batches so MVCC dead tuples don't overwhelm `autovacuum`!).
2. **Release 2 (Switch Reads & Validate)**: Switch application code to read/write `discount_code`, add `CHECK (discount_code IS NOT NULL) NOT VALID`, and run `VALIDATE CONSTRAINT`.
3. **Release 3 (Contract)**: Ignore the old column in ORM metadata first, then drop `promo_code` in a post-deployment migration.

### Batched Backfill MVCC Bloat & WAL Rate Math

Updating $N = 50,000,000$ rows in a single `UPDATE bookings SET ...` holds row locks for minutes, generates $50\text{M}$ dead MVCC tuples (`table bloat`), and spikes replication lag. Splitting into batches of size $B = 5,000$ with sleep interval $\Delta t$ bounds WAL throughput and allows `autovacuum` to recycle dead tuples continuously:

$$\text{Max Locked Rows} = B = 5,000 \ll N, \qquad \text{Write Rate} \le \frac{B}{T_{\text{batch}} + \Delta t} \text{ rows/sec}$$

| `JSONB` Indexing Strategy | Index Size | Operators Supported | Best Use Case |
| :--- | :--- | :--- | :--- |
| **`USING gin (meta)` (`jsonb_ops` default)** | Larger | `@>`, `?`, `?&`, `?|` (key existence + path containment) | Dynamic queries checking if arbitrary top-level/nested keys exist |
| **`USING gin (meta jsonb_path_ops)`** | **30–50% Smaller & Faster** | `@>` containment (`meta @> '{"meal":"VEGAN"}'`) | High-volume structured attribute filtering |
| **B+Tree Expression Index `((meta->>'tier'))`** | **Smallest (1 field)** | `=`, `<`, `>`, `ORDER BY` on 1 hot key | When 95% of queries filter a single known JSON key |

### Production Blueprint: Zero-Bloat Keyset Batched Backfill Runner

```python
from __future__ import annotations
import sqlite3


def run_keyset_batched_backfill(conn: sqlite3.Connection, batch_size: int = 2) -> int:
    """Backfill legacy NULL rows in small PK-ordered chunks (zero OFFSET scan, bounded lock duration)."""
    last_id = ""
    total_updated = 0
    while True:
        batch_ids = [
            r[0]
            for r in conn.execute(
                """
                SELECT booking_id FROM bookings
                WHERE booking_id > ? AND schema_v2_ready = 0
                ORDER BY booking_id ASC
                LIMIT ?
                """,
                (last_id, batch_size),
            ).fetchall()
        ]
        if not batch_ids:
            break
        placeholders = ",".join("?" for _ in batch_ids)
        cur = conn.execute(
            f"UPDATE bookings SET schema_v2_ready = 1 WHERE booking_id IN ({placeholders})",
            batch_ids,
        )
        conn.commit()
        total_updated += cur.rowcount
        last_id = batch_ids[-1]
    return total_updated


if __name__ == "__main__":
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE bookings (booking_id TEXT PRIMARY KEY, schema_v2_ready INT NOT NULL DEFAULT 0)")
    db.executemany("INSERT INTO bookings VALUES (?, 0)", [("BK-1",), ("BK-2",), ("BK-3",), ("BK-4",), ("BK-5",)])
    db.commit()
    updated = run_keyset_batched_backfill(db, batch_size=2)
    assert updated == 5
    remaining = db.execute("SELECT COUNT(*) FROM bookings WHERE schema_v2_ready = 0").fetchone()[0]
    assert remaining == 0
```

### Java 17 Equivalent

```java
import java.sql.*;
import java.util.*;

public final class PostgresInvalidIndexChecker {
    // Post-migration health gate: verify zero failed CREATE INDEX CONCURRENTLY artifacts remain
    public static List<String> findInvalidIndexes(Connection conn) throws SQLException {
        String sql = """
            SELECT c.relname AS index_name
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            WHERE i.indisvalid = false
            ORDER BY c.relname
            """;
        List<String> invalid = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                invalid.add(rs.getString(1));
            }
        }
        return invalid;
    }
}
```

> [!WARNING]
> **Hiring Bar-Raiser Gotcha — `JSON` vs. `JSONB` and Why `JSONB` Updates Amplify Write I/O!**
> In PostgreSQL, **always choose `JSONB` over `JSON`** (`JSON` is just unparsed text that re-parses on every read and cannot use `GIN` indexes). **However**, know where `JSONB` hurts: PostgreSQL cannot update a single 10-byte field inside a `50 KB` `JSONB` document in place—every `UPDATE` rewrites the **entire `50 KB` TOASTed `JSONB` value**! Never store rapidly incrementing counters or append-heavy arrays inside a `JSONB` column; keep high-churn fields as first-class relational columns.

*Up Next in Chapter 09*: How do we run **32 parallel CI test workers** against `AeroLedger` without tests trampling each other's rows, violating deep Foreign Key graphs, or exhausting PostgreSQL's `max_connections`? Welcome to **Module 3: Synthetic Test Data Seeding & Parallel DB Isolation**.

```json quiz
[
  {
    "id": "sql08-q1",
    "question": "Why can `ALTER TABLE bookings ADD COLUMN notes TEXT;` cause a 100% production outage even though adding a nullable column takes `< 2ms` in PostgreSQL?",
    "options": [
      "Nullable `TEXT` columns rewrite all existing pages",
      "`ALTER TABLE` requires an `ACCESS EXCLUSIVE` lock; if it waits behind a long-running `SELECT`, every new `SELECT` and `INSERT` queues behind the waiting `ALTER TABLE`!",
      "PostgreSQL restarts the server on every `ALTER TABLE`",
      "`TEXT` columns disable connection pooling"
    ],
    "answerIndex": 1,
    "explanation": "PostgreSQL's FIFO lock queue prevents starvation of waiting `ACCESS EXCLUSIVE` requests by blocking all newly arriving readers and writers behind them. Always guard DDL with `SET lock_timeout = '2s';`."
  },
  {
    "id": "sql08-q2",
    "question": "What is the zero-downtime PostgreSQL pattern for adding a `FOREIGN KEY` constraint to a live 100M-row table?",
    "options": [
      "Run `ALTER TABLE child ADD FOREIGN KEY ...` during peak traffic",
      "Run `ALTER TABLE child ADD CONSTRAINT fk_name FOREIGN KEY (...) REFERENCES parent(...) NOT VALID;` (instant), then `ALTER TABLE child VALIDATE CONSTRAINT fk_name;` (non-blocking `SHARE UPDATE EXCLUSIVE` lock)",
      "Disable all foreign keys permanently",
      "Export the table to CSV and re-import"
    ],
    "answerIndex": 1,
    "explanation": "`NOT VALID` enforces the FK on new writes immediately without scanning old rows; `VALIDATE CONSTRAINT` then verifies existing rows under a `SHARE UPDATE EXCLUSIVE` lock that allows concurrent reads and writes."
  },
  {
    "id": "sql08-q3",
    "question": "Why should rapidly changing counters (`login_count`, `seat_remaining`) NOT be stored inside a large `JSONB` document in PostgreSQL?",
    "options": [
      "`JSONB` cannot store numbers",
      "Under MVCC, updating a single key inside a `JSONB` column rewrites the entire row and full `JSONB` document (causing severe write amplification and TOAST bloat)",
      "`JSONB` columns are read-only after `INSERT`",
      "`GIN` indexes forbid integer values"
    ],
    "answerIndex": 1,
    "explanation": "PostgreSQL MVCC copies the full tuple (and full `JSONB` document if modified) on every `UPDATE`. Keep frequently mutated attributes as dedicated scalar columns."
  }
]
```

---

## 📋 Step 5: Master Cheat-Sheet, 60-Second Interview Pitch & Verified Sources

| Migration Task | Unsafe Naive DDL | Zero-Downtime Production DDL (PostgreSQL 17) |
| :--- | :--- | :--- |
| **Guard Lock Queue** | *(No timeout)* | `SET lock_timeout = '2s'; SET statement_timeout = '15s';` |
| **Add B+Tree / GIN Index** | `CREATE INDEX idx ON t(c);` | `CREATE INDEX CONCURRENTLY idx ON t(c);` (outside tx block) |
| **Add FK / CHECK** | `ALTER TABLE t ADD CHECK (...);` | `ADD CONSTRAINT c CHECK (...) NOT VALID;` $\to$ `VALIDATE CONSTRAINT c;` |
| **Rename / Change Column Type** | `ALTER TABLE t RENAME c1 TO c2;` | Expand (`ADD c2`) $\to$ Dual-Write & Backfill $\to$ Switch Reads $\to$ Contract |
| **Verify Concurrent Indexes** | *(None)* | `SELECT relname FROM pg_index JOIN pg_class ON oid=indexrelid WHERE NOT indisvalid;` |

### 🎙️ 60-Second Interview Soundbite

> *"To run zero-downtime PostgreSQL migrations on high-traffic tables, I design around lock-queue physics. Even a 2ms `ALTER TABLE` requests an `ACCESS EXCLUSIVE` lock; if it waits behind a slow analytical `SELECT`, every incoming application read and write piles up behind it. Therefore, every migration starts with `SET lock_timeout = '2s'`. Second, indexes are built outside transaction blocks via `CREATE INDEX CONCURRENTLY`, followed by a health check on `pg_index.indisvalid` to catch failed builds. Third, `FOREIGN KEY`, `CHECK`, and `NOT NULL` constraints use the two-phase `NOT VALID` + `VALIDATE CONSTRAINT` pattern so historical scans only take a non-blocking `SHARE UPDATE EXCLUSIVE` lock. And for breaking changes like column renames or type widenings, I enforce a 3-release Expand-Contract rollout with keyset-batched backfills."*

### 📚 Verified Primary Sources
- [PostgreSQL 17 Official Docs — Explicit Locking & Lock Conflict Matrix (`ACCESS EXCLUSIVE` vs `SHARE UPDATE EXCLUSIVE`)](https://www.postgresql.org/docs/current/explicit-locking.html)
- [PostgreSQL 17 Official Docs — `ALTER TABLE` (`NOT VALID` and `VALIDATE CONSTRAINT`)](https://www.postgresql.org/docs/current/sql-altertable.html)
- [PostgreSQL 17 Official Docs — `JSONB` Types & `GIN` Indexing (`jsonb_ops` vs `jsonb_path_ops`)](https://www.postgresql.org/docs/current/datatype-json.html)
