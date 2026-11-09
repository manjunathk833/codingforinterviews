---
slug: sd-03-kafka-outbox-and-eventual-consistency
track: system-design
volume: "Volume I: Distributed Systems & Resilience"
chapter_number: 3
title: "Kafka Eventual Consistency, Transactional Outbox & CDC Verification"
summary: "Eliminating dual-write bugs between relational databases and Kafka event streams using the Transactional Outbox pattern, idempotent consumers, and monotonic offset watermarks."
reading_time_minutes: 19
visualizer_id: "arch-kafka-cdc-pipeline"
lab_path: "system-design/03-kafka-cdc-and-eventual-consistency"
tags: ["system-design", "kafka", "transactional-outbox", "cdc", "eventual-consistency", "idempotency", "sagas"]
---

# Kafka Eventual Consistency, Transactional Outbox & CDC Verification

## Part I — First-Principles Mental Model & Visual Cue

Why is **Dual Writing** (`db.commit()` followed by `kafka.produce()`) one of the most notorious anti-patterns in distributed systems?

Because if the database commit succeeds and the process crashes (or the network drops) **1 millisecond before** `kafka.produce()` completes, the database shows the order is paid, but the downstream Inventory, Shipping, and Search Elastic indexes **never receive the event**—leaving the system permanently inconsistent without distributed 2-Phase Commit (`2PC`).

### The Solution: The Transactional Outbox + CDC Relay
Instead of calling Kafka directly from the web request thread:
1. The service writes **both** the business row (`INSERT INTO orders`) AND an event row (`INSERT INTO outbox_events`) inside **the same local ACID database transaction**.
2. A Change-Data-Capture (CDC) log tailer (e.g., Debezium reading Postgres WAL / MySQL Binlog) relays `outbox_events` to Kafka with **At-Least-Once** delivery.
3. Downstream consumers deduplicate events using an **Idempotency Ledger (`processed_event_ids`)** keyed by `event_id`.

```mermaid
sequenceDiagram
  participant API as Order Service
  participant DB as Postgres (ACID Tx + WAL)
  participant CDC as Debezium / Outbox Relay
  participant K as Kafka Partition
  participant C as Consumer + Idempotency Store

  API->>DB: BEGIN; INSERT orders; INSERT outbox_events; COMMIT
  DB-->>CDC: Tail WAL / Outbox Table
  CDC->>K: Produce Event (At-Least-Once)
  K->>C: Deliver Event (Offset 4021)
  C->>C: Check event_id in processed_ids (Deduplicate)
```

---

## Part II — Monotonic Watermarks & Deterministic Verification

When testing or verifying an eventually consistent pipeline, `time.sleep(5)` is an anti-pattern (either too slow or flaky under load).
Instead, deterministic verification tracks **Causal Offset Watermarks**:
- Every write returns a causal token (`min_expected_offset` or `tx_lsn`).
- The verifier polls with bounded exponential backoff until `consumer_watermark >= min_expected_offset` AND outbox lag reaches `0`.

---

## Part III — Production Implementation Blueprints (Java 17 & Python 3)

### Python 3 Blueprint: Transactional Outbox + Idempotent Consumer
```python
class OutboxPipeline:
    def __init__(self):
        self.orders = {}
        self.outbox = []
        self.processed_event_ids = set()
        self.search_index = {}

    def create_order_atomic(self, order_id: str, tenant_id: str, amount_cents: int) -> str:
        event_id = f"evt-{order_id}-v1"
        self.orders[order_id] = {"tenant": tenant_id, "amount": amount_cents}
        self.outbox.append({"event_id": event_id, "order_id": order_id, "amount": amount_cents})
        return event_id

    def consume_idempotent(self, event: dict) -> bool:
        eid = event["event_id"]
        if eid in self.processed_event_ids:
            return False  # Duplicate delivery safely ignored
        self.processed_event_ids.add(eid)
        self.search_index[event["order_id"]] = event["amount"]
        return True
```

### Java 17 Blueprint: Idempotent Consumer Guard
```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public final class IdempotentEventConsumer {
    private final Set<String> seenEventIds = ConcurrentHashMap.newKeySet();

    public boolean processOnce(String eventId, Runnable sideEffect) {
        if (!seenEventIds.add(eventId)) {
            return false; // Duplicate Kafka delivery skipped atomically
        }
        sideEffect.run();
        return true;
    }
}
```

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
