# 🗄️ Databases Lab 01: SQLite WAL Ring-Buffers & Optimistic Concurrency Control

**Domain:** Database Internals & Local Endpoint Storage  
**Target Role:** Senior / Staff SDET (Storage Engines, Transaction Isolation, Offline Resilience)  
**Interactive Visualizer:** `arch-endpoint-cloud-sync` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

1. **Write-Ahead Logging (`WAL`) vs. Rollback Journal**:
   - In default SQLite (`DELETE` journal mode), readers block writers and writers block readers.
   - Enabling `PRAGMA journal_mode=WAL;` appends changes sequentially to a `-wal` file, allowing **concurrent reads and writes** with high sequential disk I/O throughput—essential for local endpoint telemetry agents.
2. **Bounded Disk Ring-Buffer (FIFO Eviction)**:
   - When an endpoint goes offline for hours, buffering telemetry in RAM causes an Out-Of-Memory crash. Writing to an unbounded disk table fills the user's SSD.
   - A **Bounded WAL Ring-Buffer** caps capacity at $K$ records (or $M$ megabytes), automatically evicting the oldest committed entries (`FIFO`) when full while preserving strict ordering.
3. **ACID Isolation & Preventing "Lost Updates" via Optimistic Concurrency Control (`CAS`)**:
   - Under `Read Committed`, if Worker A and Worker B both read row version `v=1` (`balance=100`) and both write an update, the second write silently overwrites the first (**Lost Update Anomaly**).
   - **Optimistic Concurrency Control (Compare-And-Swap)**: Every update specifies `WHERE id = ? AND version = expected_version`. If the row's current version no longer matches `expected_version`, the database rejects the write (`0 rows updated` $\to$ conflict), preventing silent data corruption without holding long pessimistic locks!

---

## 🧪 2. Running Verification

```bash
./run.sh test 01-wal-and-isolation-anomalies
```

