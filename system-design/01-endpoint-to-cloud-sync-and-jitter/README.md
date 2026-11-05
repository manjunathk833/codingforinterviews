# 🌩️ System Design Lab 01: Endpoint-to-Cloud Sync, Full Jitter & Idempotency

**Domain:** Distributed Resilience, Backpressure & SASE Telemetry Ingestion  
**Target Role:** Senior / Staff SDET & Distributed Systems Architect  
**Interactive Visualizer:** `arch-endpoint-cloud-sync` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

When 10,000 desktop security agents (e.g., Netskope Client) lose connectivity during a 60-second cloud gateway blip:
1. **Why Pure Exponential Backoff Fails (Synchronized Waves)**:
   If all 10,000 clients fail at $t = 0$ and compute `delay = base * (2 ** attempt)` ($2\text{s}, 4\text{s}, 8\text{s}$), all 10,000 clients still wake up at the **exact same second** ($t=2\text{s}$, then $t=4\text{s}$) and DDoS the API gateway again!
2. **AWS / Staff Pattern — Exponential Backoff with Full Jitter**:
   $$\text{sleep} = \text{random}\left(0, \min\left(\text{Cap}, \text{Base} \times 2^{\text{attempt}}\right)\right)$$
   Adding uniform randomness across the backoff window spreads the 10,000 reconnecting clients across all time buckets, reducing peak burst RPS by $>80\%$.
3. **Exactly-Once Ingestion via Idempotency Keys**:
   When a network ACK is lost, an endpoint retries sending the same telemetry batch. By attaching a deterministic `idempotency_key` (`UUID`) to each batch, the cloud gateway deduplicates retries in O(1) time.

---

## 🧪 2. Running Verification

```bash
./run.sh test 01-endpoint-to-cloud-sync-and-jitter
```

