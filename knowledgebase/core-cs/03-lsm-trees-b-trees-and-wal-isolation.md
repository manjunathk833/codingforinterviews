---
slug: cs-03-lsm-trees-b-trees-and-wal-isolation
course_id: 08-core-cs-internals
track: core-cs
volume: "08. Core CS: OS, Networking & Storage"
module_number: 2
module_title: "Module 2: Storage Engines, WAL Isolation & Container Primitives"
chapter_number: 3
level_tag: "Senior → Staff Storage Internals"
title: "Database Storage Engines: B+Trees vs. LSM-Tree Internals, WAL & MVCC Isolation"
summary: "Inside relational and NoSQL storage engines: how Write-Ahead Logs (WAL), B+Tree page splits, LSM-Tree MemTables/SSTables, Bloom filters, and MVCC Snapshot Isolation anomalies (Write Skew) work."
reading_time_minutes: 23
visualizer_id: "cs-lsm-wal-bloom"
lab_path: "core-cs/databases/01-wal-and-isolation-anomalies"
tags: ["core-cs", "databases", "b-tree", "lsm-tree", "wal", "mvcc", "write-skew", "sqlite", "postgres", "rocksdb"]
---

# Database Storage Engines: B+Trees vs. LSM-Tree Internals, WAL & MVCC Isolation

```json pretraining
[
  {
    "term": "Write-Ahead Log (WAL + fsync)",
    "formula": "Append WAL Frame → fsync() → Mutate RAM Page",
    "meaning": "Guarantees ACID Durability without flushing random 8KB B+Tree pages on every commit; crash recovery simply replays sequential WAL records."
  },
  {
    "term": "LSM-Tree Write Path",
    "formula": "WAL Append + SkipList MemTable → Immutable SSTables",
    "meaning": "Converts random key writes into sequential disk I/O with background Leveled/Tiered Compaction reclaiming overwritten rows and delete Tombstones."
  },
  {
    "term": "SSTable Bloom Filter",
    "formula": "0% False Negatives (~10 bits/key ⇒ <1% FP)",
    "meaning": "Bit-array filter in RAM letting an LSM-Tree skip 99% of unnecessary disk SSTable lookups on absent keys."
  },
  {
    "term": "MVCC Snapshot Write Skew",
    "formula": "T1 reads A, writes B  ∥  T2 reads B, writes A",
    "meaning": "Subtle concurrency bug allowed under Snapshot Isolation (`REPEATABLE READ` in Postgres) when two transactions read overlapping invariants but mutate disjoint rows!"
  }
]
```

```json poe
{
  "question": "A hospital scheduling table requires at least 1 doctor on call. Currently Alice and Bob are BOTH `on_call = true`. Under PostgreSQL `REPEATABLE READ` (MVCC Snapshot Isolation), Tx1 checks `COUNT(*) WHERE on_call = true` (sees 2) and updates `Alice -> false`. Concurrently, Tx2 checks `COUNT(*) WHERE on_call = true` (sees 2) and updates `Bob -> false`. Both transactions `COMMIT`! What is the final database state?",
  "options": [
    "PostgreSQL automatically rolls back Tx2 with a Lost Update error",
    "BOTH commits succeed and ZERO doctors remain on call! Snapshot Isolation only blocks write-write conflicts on the SAME row; because Tx1 mutated Alice and Tx2 mutated Bob (disjoint rows!), this classic 'Write Skew' anomaly slips right through unless guarded by `SERIALIZABLE` (`SSI`) or `SELECT ... FOR UPDATE`!",
    "The B+Tree leaf page deadlocks and restarts Postgres",
    "WAL mode converts `REPEATABLE READ` into single-threaded execution"
  ],
  "answerIndex": 1,
  "explanation": "Write Skew (DDIA Ch. 7) is the #1 Staff database interview trap: MVCC Snapshot Isolation prevents Dirty Reads, Non-Repeatable Reads, and Lost Updates on the *same* row, but allows invariant-breaking disjoint writes unless promoted to Serializable Snapshot Isolation (`SSI`) or explicit row-level `FOR UPDATE` locks."
}
```

## Part I — B+Trees vs. LSM-Tree Storage Engines

Every database storage engine on Earth navigates a fundamental hardware trade-off between **Read-Optimized In-Place Page Trees (`B+Trees`)** and **Write-Optimized Append-Only Log Structures (`LSM-Tree`)**:

```mermaid
flowchart LR
  Write["Write(key, val)"] -->|1. Sequential fsync| WAL["Append-Only Disk WAL (Crash Durability)"]
  Write -->|2. O(log M) RAM| Mem["Sorted MemTable (SkipList / RB-Tree)"]
  Mem -->|3. Flush at 64MB| L0["Immutable SSTable L0 + RAM Bloom Filter"]
  L0 -->|4. Leveled Compaction| LK["Merged SSTables L1..LK (Purges Tombstones)"]
```

```json contrast
{
  "title": "Storage Engine Architecture & Concurrency Control",
  "naiveTitle": "SQLite Rollback Journal + Unindexed Scans",
  "naiveMetric": "Writers Block All Readers · Write Skew Bugs",
  "naivePoints": [
    "Default SQLite DELETE journal mode acquires an exclusive file lock on write, blocking all concurrent readers with SQLITE_BUSY",
    "Random UUID primary keys on B+Trees scatter inserts across cold 16KB pages, causing 50% page-split fragmentation and buffer-pool thrashing",
    "Mass deleting 10M rows in an LSM-Tree (`Cassandra`) immediately followed by `SELECT` scans 10M Tombstones and times out!",
    "Assumes MVCC `REPEATABLE READ` prevents multi-row business-rule race conditions (Write Skew)"
  ],
  "staffTitle": "WAL MVCC + UUIDv7 Locality + SSI / Locking",
  "staffMetric": "Zero Reader-Writer Blocking · Predictable P99 I/O",
  "staffPoints": [
    "Enables `PRAGMA journal_mode=WAL` so writers append frames to `-wal` while concurrent readers view consistent MVCC snapshots",
    "Uses time-ordered `UUIDv7` / Snowflake keys on B+Trees so inserts append sequentially to the rightmost leaf page",
    "Attaches 10-bit/key Bloom Filters to LSM-Tree SSTables + avoids wide tombstone range scans",
    "Prevents Write Skew via `SERIALIZABLE` (SSI) or materializing lockable conflict rows (`SELECT ... FOR UPDATE`)"
  ]
}
```

---

## Part II — Storage Engine & Isolation Level Trade-Off Matrices

### 1. B+Tree vs. LSM-Tree Amplification Trade-Offs

| Dimension | **B+Tree Engines** *(PostgreSQL, MySQL InnoDB, SQLite)* | **LSM-Tree Engines** *(RocksDB, Cassandra, ScyllaDB, Pebble)* |
| :--- | :--- | :--- |
| **Disk Layout** | Fixed-size mutable $4\text{KB}–16\text{KB}$ pages in a shallow $3–4$ level balanced tree | Append-only **WAL** + RAM **MemTable** flushed to immutable sorted **SSTables** |
| **Write Amplification** | Higher on random keys (WAL write + dirty $16\text{KB}$ page flush + InnoDB doublewrite) | Low on ingest ($\mathcal{O}(1)$ sequential append); paid asynchronously during background **Compaction** |
| **Read Amplification** | **Lowest**: deterministic $3–4$ page hops (inner nodes pinned in RAM) | Higher on range scans; point reads mitigated by per-SSTable **Bloom Filters** ($0\%$ false negatives) |
| **Space Amplification** | Moderate ($\sim 25\%–35\%$ internal page fragmentation) | **Lowest under Leveled Compaction** ($\sim 10\%$ dead space after merging SSTable levels) |

### 2. Concurrency Anomalies Across Isolation Levels

| Isolation Level | Dirty Read | Non-Repeatable Read | Lost Update *(Same Row)* | Write Skew / Phantom |
| :--- | :--- | :--- | :--- | :--- |
| **`READ COMMITTED`** *(Postgres Default!)* | Prevented | **Possible!** | **Possible!** (`x = x + 1` in app code loses increments!) | **Possible!** |
| **`REPEATABLE READ` / Snapshot (`MVCC`)** | Prevented | Prevented | Prevented in Postgres (`ERROR: could not serialize`); **Possible in MySQL InnoDB** without `FOR UPDATE`! | **Possible (`Write Skew`)!** |
| **`SERIALIZABLE` (`SSI` / `2PL`)** | Prevented | Prevented | Prevented | **100% Prevented** (Retry on `40001` serialization conflict) |

---

## Part III — Production Implementation Blueprints (Python 3 & Java 17)

### Python 3 Blueprint: Mini LSM-Tree (`WAL + MemTable + Tombstone Compaction + Bloom Filter`)
```python
import bisect


class MiniLSMStore:
    def __init__(self, flush_threshold: int = 4):
        self.flush_threshold = flush_threshold
        self.memtable: dict[str, str | None] = {}
        self.sstables: list[tuple[set[str], list[tuple[str, str | None]]]] = []

    def put(self, key: str, value: str) -> None:
        self.memtable[key] = value
        if len(self.memtable) >= self.flush_threshold:
            self.flush()

    def delete(self, key: str) -> None:
        # Deletions in an LSM-Tree append a Tombstone marker (None)!
        self.memtable[key] = None
        if len(self.memtable) >= self.flush_threshold:
            self.flush()

    def flush(self) -> None:
        if not self.memtable:
            return
        sorted_pairs = sorted(self.memtable.items(), key=lambda kv: kv[0])
        bloom_filter = {k for k, _ in sorted_pairs}
        self.sstables.append((bloom_filter, sorted_pairs))
        self.memtable.clear()

    def get(self, key: str) -> str | None:
        if key in self.memtable:
            return self.memtable[key]
        # Search SSTables from newest to oldest so newer values/tombstones shadow older levels
        for bloom, pairs in reversed(self.sstables):
            if key not in bloom:
                continue  # Bloom filter skipped SSTable disk read!
            keys = [p[0] for p in pairs]
            idx = bisect.bisect_left(keys, key)
            if idx < len(pairs) and pairs[idx][0] == key:
                return pairs[idx][1]
        return None

    def compact_all_major(self) -> int:
        """Major compaction merges SSTables oldest->newest and physically purges Tombstones!"""
        merged: dict[str, str | None] = {}
        for _, pairs in self.sstables:
            for k, v in pairs:
                merged[k] = v
        live_pairs = sorted((k, v) for k, v in merged.items() if v is not None)
        purged_tombstones = sum(1 for v in merged.values() if v is None)
        self.sstables = [({k for k, _ in live_pairs}, live_pairs)] if live_pairs else []
        return purged_tombstones
```

### Java 17 Blueprint: K-Hash BitSet Bloom Filter & Tombstone-Aware SSTable Resolver
```java
import java.util.BitSet;
import java.util.Optional;

public final class SstableStoragePrimitives {
    public record SstableEntry(String key, String value, boolean tombstone) {
        public Optional<String> resolve() {
            return tombstone ? Optional.empty() : Optional.ofNullable(value);
        }
    }

    /** Compact k-hash Kirsch-Mitzenmacher Bloom Filter guaranteeing 0% False Negatives. */
    public static final class SstableBloomFilter {
        private final BitSet bits;
        private final int bitCount;
        private final int numHashes;

        public SstableBloomFilter(int expectedKeys, int bitsPerKey) {
            this.bitCount = Math.max(64, expectedKeys * bitsPerKey);
            this.bits = new BitSet(this.bitCount);
            this.numHashes = Math.max(1, (int) Math.round(bitsPerKey * Math.log(2.0)));
        }

        public void add(String key) {
            long h1 = key.hashCode() & 0xFFFFFFFFL;
            long h2 = Long.rotateLeft(h1 * 0x9E3779B97F4A7C15L, 17) | 1L;
            for (int i = 0; i < numHashes; i++) {
                int bitIdx = (int) (Long.remainderUnsigned(h1 + i * h2, bitCount));
                bits.set(bitIdx);
            }
        }

        public boolean mightContain(String key) {
            long h1 = key.hashCode() & 0xFFFFFFFFL;
            long h2 = Long.rotateLeft(h1 * 0x9E3779B97F4A7C15L, 17) | 1L;
            for (int i = 0; i < numHashes; i++) {
                int bitIdx = (int) (Long.remainderUnsigned(h1 + i * h2, bitCount));
                if (!bits.get(bitIdx)) {
                    return false; // 100% guaranteed NOT in SSTable!
                }
            }
            return true;
        }
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Why Random `UUIDv4` Primary Keys Destroy B+Tree Write Throughput by $5\times–10\times$**:
> In MySQL InnoDB (where the Primary Key **is** the clustered B+Tree leaf order) and PostgreSQL B+Tree indexes, sequential/time-ordered `UUIDv7` keys always append cleanly to the single hot rightmost `16KB` leaf page in RAM. Random `UUIDv4` keys scatter every single `INSERT` into a random cold `16KB` leaf page across a `500 GB` table—forcing constant buffer-pool evictions, random disk reads, and $50\%$-empty page splits! Always use **`UUIDv7` (RFC 9562)** for distributed B+Tree primary keys.

---

## Part IV — End-of-Chapter Mastery Check

```json quiz
[
  {
    "id": "cs-03-q1",
    "question": "How does an LSM-Tree delete a key whose value is already stored inside an immutable SSTable on disk?",
    "options": [
      "It seeks into the middle of the SSTable file and zeros out the bytes in-place",
      "It appends a special 'Tombstone' marker for that key into the WAL and MemTable; the old value is physically reclaimed later during background SSTable compaction",
      "It drops the entire SSTable file",
      "It blocks all reads until the file is rewritten"
    ],
    "answerIndex": 1,
    "explanation": "Because SSTables are strictly immutable, deletes are append-only Tombstone records that shadow older versions until compaction merges the levels."
  },
  {
    "id": "cs-03-q2",
    "question": "In SQLite WAL (Write-Ahead Logging) mode, why can multiple readers execute concurrently alongside an active writer without blocking?",
    "options": [
      "Because SQLite disables ACID transactions in WAL mode",
      "Because the writer appends new page versions to the -wal file while readers read consistent historical snapshots up to their transaction's end-mark (MVCC Snapshot Isolation)",
      "Because SQLite loads the entire database into CPU L2 cache",
      "Because readers ignore committed rows"
    ],
    "answerIndex": 1,
    "explanation": "In WAL mode, changes are appended to the WAL file rather than overwriting the main database pages in-place, allowing readers to view a consistent snapshot while a writer appends new frames."
  },
  {
    "id": "cs-03-q3",
    "question": "What can a Bloom Filter tell an LSM-Tree storage engine during a point lookup?",
    "options": [
      "The exact byte offset of the key inside the SSTable",
      "Either 'the key is DEFINITELY NOT in this SSTable' (0% false negatives) or 'the key MIGHT be in this SSTable' (small false-positive rate)",
      "The sorted order of all keys in the database",
      "Whether the transaction is serializable"
    ],
    "answerIndex": 1,
    "explanation": "Bloom filters never produce false negatives, allowing the engine to skip reading SSTables that do not contain the target key."
  }
]
```
