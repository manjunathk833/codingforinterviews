# Course 11 Lab: `AeroPulse` Open-Loop Load, Coordinated Omission Corrector & Toxiproxy Chaos Gate

Deterministic local verification harness for **Course 11 (`11-performance-chaos-and-sre`)**.

## Invariants Verified
1. **Little's Law ($L = \lambda W$) & Core-Matched Pool Sizing**: Verifies steady-state concurrency math and PostgreSQL/HikariCP pool sizing ($C = (2 \times \text{cores}) + \text{spindles}$).
2. **Coordinated Omission Correction (`HdrHistogram` / Open-Loop Schedule)**: Proves how closed-loop VU stalls hide freeze queuing delays and computes true arrival-schedule latency percentiles.
3. **Toxiproxy Chaos Fault Injection & Circuit Breaker State Machine**: Verifies `CLOSED -> OPEN -> HALF_OPEN -> CLOSED` transitions with graceful degradation fallbacks.
4. **Google SRE Multi-Window Multi-Burn-Rate SLO Alerting**: Verifies `14.4x` (`1h + 5m`) and `6.0x` (`6h + 30m`) burn-rate alerting and rapid reset after recovery.

## Run Locally
```bash
python3 frameworks/performance-sre/01-load-coordinated-omission-and-chaos/reference_solution.py
```
