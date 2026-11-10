# System Design Lab 03: Transactional Outbox, Kafka CDC & Idempotent Eventual Consistency

This dual-language deterministic lab implements:
1. **Atomic Transactional Outbox (`orders` + `outbox_events`)** eliminating dual-write split-brain between SQLite/Postgres and Kafka.
2. **At-Least-Once Relay & Idempotent Consumer Deduplication** handling broker retries (`event_id` deduplication table) with strictly zero duplicate side effects.
3. **Bounded Eventual-Consistency Saga Poller** verifying `PENDING -> CONFIRMED` transitions without `sleep()` anti-patterns.

## Run Locally (Zero AI)
```bash
./run.sh test 03-kafka-cdc-and-eventual-consistency
```
