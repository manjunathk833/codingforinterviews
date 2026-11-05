# 🏛️ Distributed System Design & SDET Platform Architecture (`system-design/`)

Welcome to the **System Design Pillar** of the Antigravity Learning Hub.
This pillar bridges classical distributed systems primitives (Backpressure, Jitter, Idempotency, Consistent Hashing, Kafka Sagas) with Staff/Principal SDET Platform Architecture.

---

## 📊 System Design Curriculum & Lab Tracker

| # | Domain | Lab / Module | Key Concepts Covered | Java | Python | Visualizer ID | Status |
| :-: | :--- | :--- | :--- | :-: | :-: | :--- | :---: |
| **1** | **Resilience & Scale** | [`01-endpoint-to-cloud-sync-and-jitter`](01-endpoint-to-cloud-sync-and-jitter/) | Thundering Herd Mitigation, Exponential Backoff + Full Jitter, Idempotency Key Deduplication | [x] | [x] | `arch-endpoint-cloud-sync` | `Completed` |
| **2** | **Distributed Sharding** | [`02-consistent-hashing-and-grid-sharding`](02-consistent-hashing-and-grid-sharding/) | Modulo `hash(k) % N` Resharding Storm vs. Consistent Hashing Ring with Virtual Nodes (`vnodes`) | [x] | [x] | `arch-concurrency-isolation` | `Completed` |

---

## 🚀 How to Run System Design Labs

```bash
# Test Endpoint-to-Cloud Sync, Full Jitter & Idempotency (Java 17 & Python 3)
./run.sh test 01-endpoint-to-cloud-sync-and-jitter

# Test Consistent Hashing Ring & Distributed Grid Sharding (Java 17 & Python 3)
./run.sh test 02-consistent-hashing-and-grid-sharding
```

