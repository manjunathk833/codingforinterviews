---
slug: sd-03-kafka-outbox-and-eventual-consistency
course_id: 07-distributed-system-design
track: system-design
volume: "07. Distributed System Design"
module_number: 1
module_title: "Module 1: Flow Control, Sharding & Event-Driven Pipelines"
chapter_number: 3
level_tag: "Senior → Staff Distributed Systems"
title: "Kafka Eventual Consistency, Transactional Outbox, CDC & Idempotent Consumers"
summary: "Eliminating dual-write bugs between ACID databases and Kafka streams using the Transactional Outbox pattern, Debezium WAL CDC, idempotent consumer ledgers, and causal offset watermarks."
reading_time_minutes: 22
visualizer_id: "arch-kafka-cdc-pipeline"
lab_path: "system-design/03-kafka-cdc-and-eventual-consistency"
tags: ["system-design", "kafka", "transactional-outbox", "cdc", "eventual-consistency", "idempotency", "sagas"]
---

# Kafka Eventual Consistency, Transactional Outbox, CDC & Idempotent Consumers

```json pretraining
[
  {
    "term": "The Dual-Write Anti-Pattern",
    "formula": "DB.commit() + Kafka.send() ≠ Atomic",
    "meaning": "Writing to two independent storage systems without a shared transaction log guarantees silent divergence on process crash or network timeout."
  },
  {
    "term": "Transactional Outbox + WAL CDC",
    "formula": "BEGIN; INSERT row; INSERT outbox; COMMIT",
    "meaning": "Piggybacking event persistence onto local RDBMS ACID atomicity, then streaming committed WAL frames into Kafka asynchronously via Debezium."
  },
  {
    "term": "Effectively-Once = At-Least-Once + Idempotence",
    "formula": "INSERT INTO seen_events ON CONFLICT DO NOTHING",
    "meaning": "Because network ACK drops force Outbox/Kafka retries, downstream consumers achieve exact business state by committing deduplication IDs atomically with side effects."
  },
  {
    "term": "Causal Offset Watermark",
    "formula": "Wait(ConsumerOffset ≥ MinExpectedLSN)",
    "meaning": "Replacing flaky sleep(5000) calls in E2E tests and read-your-writes APIs with deterministic monotonic log-sequence polling."
  }
]
```

```json poe
{
  "question": "To fix a Dual-Write bug, an engineer reverses the order: they call `kafkaProducer.send(event).get()` FIRST, and only if Kafka ACKs do they run `db.commit()`. Two weeks later, downstream Billing charged 14 customers for orders that do NOT exist in the Orders database! How did that happen?",
  "options": [
    "Kafka deleted the messages before Billing read them",
    "Reversing the order merely flips the Dual-Write failure direction: Kafka durably persisted and delivered the event to Billing, and 1ms later `db.commit()` failed due to a unique-constraint violation, deadlock rollback, or OOM kill—emitting a 'Phantom Event'!",
    "Postgres automatically rolls back Kafka partitions",
    "Setting acks=all in Kafka makes Postgres transactions atomic"
  ],
  "answerIndex": 1,
  "explanation": "`DB first, then Kafka` loses events on crash; `Kafka first, then DB` emits phantom events for rolled-back DB transactions! Only writing both to the same single ACID log (Transactional Outbox or Event Sourcing) achieves true atomicity."
}
```

## Part I — First-Principles Mental Model & Visual Cue

Why is **Dual Writing** (`db.commit()` followed by `kafka.produce()`) one of the most notorious anti-patterns in distributed systems?

Because if the database commit succeeds and the process crashes (or a GC pause / network partition hits) **1 millisecond before** `kafka.produce()` completes, the database shows the order is paid, while downstream Inventory, Shipping, and Elasticsearch projections **never receive the event**—leaving the platform permanently inconsistent without slow, fragile cross-system Two-Phase Commit (`2PC` / XA).

### The Staff Architecture: Transactional Outbox + Log-Based CDC + Idempotent Ledger
1. **Single-Database Atomic Commit**: The service writes **both** the domain mutation (`INSERT INTO orders`) AND an immutable event record (`INSERT INTO outbox_events`) inside **the exact same local ACID database transaction**.
2. **WAL-Tailing CDC Relay (`Debezium`)**: Instead of hammering the primary DB with `SELECT ... WHERE published = false` polling queries, a Change-Data-Capture connector tails the Postgres **Write-Ahead Log (`WAL`)** / MySQL `binlog` in-order and publishes to Kafka (`acks=all`, `enable.idempotence=true`) keyed by `aggregate_id` (`order_id`) for strict per-entity partition ordering.
3. **Atomic Consumer Deduplication**: Downstream consumers insert `event_id` into a local `processed_events` table **in the same transaction** as their business state update (or pass `event_id` as an external `Idempotency-Key`), converting **At-Least-Once** transport into **Effectively-Once** business execution.

```mermaid
sequenceDiagram
  participant API as Order API
  participant DB as Postgres (ACID + WAL)
  participant CDC as Debezium WAL Relay
  participant K as Kafka (Key=order_id)
  participant C as Consumer + Seen Ledger

  API->>DB: BEGIN; INSERT orders; INSERT outbox; COMMIT (LSN 904)
  DB-->>CDC: Stream Committed WAL Frame (LSN 904)
  CDC->>K: Produce(key=order_id, event_id, acks=all)
  K->>C: Poll Batch (Partition 3, Offset 4021)
  C->>C: Atomic Tx: INSERT seen_ids + Apply Side Effect + Commit Offset
```

```json contrast
{
  "title": "Microservice State + Event Publication Reliability",
  "naiveTitle": "Application-Level Dual Write + sleep(5s) Tests",
  "naiveMetric": "Silent Data Drift · Flaky E2E Suites",
  "naivePoints": [
    "Executes db.commit() then kafka.send() in memory—loses events on pod eviction or broker blip",
    "Uses random UUIDs as Kafka partition keys, scrambling CREATED / CANCELLED event order across partitions",
    "Assumes Kafka 'Exactly-Once' magically makes non-transactional HTTP/Email side effects idempotent",
    "Uses hardcoded Thread.sleep(5000) in integration tests to wait for async consumers"
  ],
  "staffTitle": "Transactional Outbox + Partition Keying + Watermark Poll",
  "staffMetric": "Zero Lost/Phantom Events · Deterministic <50ms E2E",
  "staffPoints": [
    "Commits domain state + outbox_events row in a single local RDBMS ACID transaction",
    "Streams Postgres WAL via Debezium keyed by order_id so per-aggregate lifecycle order is 100% preserved",
    "Enforces consumer idempotency via UNIQUE(event_id) inside the target database transaction",
    "Verifies eventual consistency deterministically by polling consumer offset watermarks against tx LSN"
  ]
}
```

---

## Part II — Delivery Guarantees, Poison Pills & Deterministic Verification

What happens when a single malformed message (**Poison Pill**) lands at Offset `4022` on Partition `3`? If the consumer crashes and retries forever, Partition `3` consumer lag climbs to millions while blocking every healthy customer hashed to Partition `3`! Staff pipelines implement bounded retry tiers (`retry-5s` $\to$ `retry-1m`) followed by routing to a **Dead-Letter Queue (`DLQ`)** carrying original headers, stack trace, and offset metadata—alerting on-call immediately whenever `dlq_messages_total > 0`.

| Pattern | DB Load Impact | Latency (`P99`) | Ordering Guarantee | Operational Trade-Off |
| :--- | :--- | :--- | :--- | :--- |
| **Polling Outbox Relay** (`SELECT ... FOR UPDATE SKIP LOCKED`) | Medium (Periodic index scans + `DELETE`/`UPDATE`) | $100\text{ ms}–1\text{s}$ | Per-partition if ordered by monotonic sequence | Zero extra CDC infra; works on any SQL DB immediately |
| **WAL Log-Tailing CDC** (`Debezium` + Postgres Replication Slot) | **Near-Zero** (Reads sequential WAL stream) | **$10\text{ ms}–60\text{ ms}$** | Strict commit-LSN order | **Must monitor replication slot lag** so unconsumed WAL files don't fill primary disk! |
| **Distributed `2PC` / XA** | High (Row locks held across network RTTs) | High | Strict synchronous | Coordinator single point of failure; unsupported by modern cloud queues |

---

## Part III — Production Implementation Blueprints (Python 3 & Java 17)

### Python 3 Blueprint: Transactional Outbox, Idempotent Consumer & Causal Watermark Poller
```python
import time
from typing import Callable


class OutboxPipeline:
    def __init__(self):
        self.orders: dict[str, dict] = {}
        self.outbox: list[dict] = []
        self.kafka_partition_log: list[dict] = []
        self.processed_event_ids: set[str] = set()
        self.search_index: dict[str, int] = {}
        self.consumer_watermark: int = -1

    def create_order_atomic(self, order_id: str, tenant_id: str, amount_cents: int) -> dict:
        """Simulates single ACID transaction writing domain row + outbox event."""
        event_id = f"evt-{order_id}-v1"
        self.orders[order_id] = {"tenant": tenant_id, "amount": amount_cents}
        self.outbox.append({
            "event_id": event_id,
            "partition_key": order_id,
            "order_id": order_id,
            "amount": amount_cents,
            "relayed": False,
        })
        return {"orderId": order_id, "eventId": event_id}

    def relay_outbox_at_least_once(self, simulate_duplicate: bool = False) -> int:
        last_offset = len(self.kafka_partition_log) - 1
        for row in self.outbox:
            if not row["relayed"]:
                self.kafka_partition_log.append(dict(row))
                if simulate_duplicate:
                    # Simulate relay crash after Kafka ACK before checkpoint update!
                    self.kafka_partition_log.append(dict(row))
                row["relayed"] = True
                last_offset = len(self.kafka_partition_log) - 1
        return last_offset

    def consume_next_idempotent(self) -> bool:
        next_idx = self.consumer_watermark + 1
        if next_idx >= len(self.kafka_partition_log):
            return False
        event = self.kafka_partition_log[next_idx]
        eid = event["event_id"]
        if eid not in self.processed_event_ids:
            self.processed_event_ids.add(eid)
            self.search_index[event["order_id"]] = event["amount"]
        self.consumer_watermark = next_idx
        return True


def await_causal_watermark(
    poll_fn: Callable[[], int],
    min_expected_offset: int,
    timeout_sec: float = 2.0,
) -> bool:
    """Staff replacement for flaky time.sleep(): bounded deadline polling on causal offset."""
    deadline = time.monotonic() + timeout_sec
    delay = 0.005
    while time.monotonic() < deadline:
        if poll_fn() >= min_expected_offset:
            return True
        time.sleep(delay)
        delay = min(0.050, delay * 1.5)
    return poll_fn() >= min_expected_offset
```

### Java 17 Blueprint: Transactional Idempotent Consumer &Bounded Watermark Awaiter
```java
import java.time.Duration;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.LongSupplier;

public final class IdempotentEventConsumer {
    private final Set<String> seenEventIds = ConcurrentHashMap.newKeySet();

    /**
     * In production JDBC/JPA, INSERT INTO processed_events(event_id) executes inside
     * the exact same @Transactional boundary as the domain table mutation!
     */
    public boolean processOnce(String eventId, Runnable sideEffect) {
        if (!seenEventIds.add(eventId)) {
            return false; // Duplicate Kafka delivery safely skipped!
        }
        sideEffect.run();
        return true;
    }

    public static void awaitOffsetWatermark(
            LongSupplier currentConsumerOffset, long targetOffset, Duration timeout)
            throws InterruptedException {
        long deadlineNanos = System.nanoTime() + timeout.toNanos();
        long sleepMs = 5;
        while (System.nanoTime() < deadlineNanos) {
            if (currentConsumerOffset.getAsLong() >= targetOffset) {
                return;
            }
            Thread.sleep(sleepMs);
            sleepMs = Math.min(100, sleepMs * 2);
        }
        if (currentConsumerOffset.getAsLong() < targetOffset) {
            throw new AssertionError("Consumer watermark lagged past deadline; target=" + targetOffset);
        }
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Postgres Logical Replication Slot Disk-Full Outage**:
> When using Debezium CDC on PostgreSQL, if the Debezium connector or Kafka cluster goes down for 6 hours, Postgres **retains every single WAL segment on disk** waiting for the replication slot to advance—until the primary database runs out of disk space (`PANIC: could not write to file "pg_wal/..."`) and takes down production! Always configure `max_slot_wal_keep_size` in Postgres + P0 paging alerts on `pg_replication_slots` byte lag!

---

## Part IV — End-of-Chapter Mastery Check

```json quiz
[
  {
    "id": "sd-03-q1",
    "question": "Why does the Transactional Outbox pattern require downstream Kafka consumers to be idempotent?",
    "options": [
      "Because Kafka partitions sort messages alphabetically",
      "Because the Outbox/CDC relay guarantees At-Least-Once delivery—if the relay crashes after publishing to Kafka but before marking the outbox row relayed, it will republish the same event on restart",
      "Because SQLite does not support primary keys",
      "Because TLS 1.3 duplicates TCP packets"
    ],
    "answerIndex": 1,
    "explanation": "An outbox relay can crash between receiving Kafka's ACK and updating its own checkpoint, causing duplicate event publication. Consumers must deduplicate by event_id."
  },
  {
    "id": "sd-03-q2",
    "question": "In Kafka, how do you guarantee strict ordering of all state transitions (CREATED -> PAID -> SHIPPED) for a single Order ID?",
    "options": [
      "Use a random partition key on every message",
      "Use order_id as the Kafka message partition key so all events for that order hash to the exact same partition",
      "Set replication.factor=1",
      "Use UDP instead of TCP"
    ],
    "answerIndex": 1,
    "explanation": "Kafka guarantees strict total order only within a single partition. Keying messages by order_id routes all lifecycle events for that order to the same partition."
  },
  {
    "id": "sd-03-q3",
    "question": "What is the Staff-grade alternative to hardcoded sleep(5000) when testing asynchronous Kafka projections?",
    "options": [
      "Increase sleep to 30,000ms",
      "Bounded deadline polling with exponential backoff against causal offset watermarks or state predicates",
      "Disable Kafka acknowledgments (acks=0)",
      "Catch and ignore AssertionError"
    ],
    "answerIndex": 1,
    "explanation": "Polling against causal watermarks or state invariants with a deadline completes in milliseconds when the broker is fast while tolerating transient GC/rebalance pauses."
  }
]
```
