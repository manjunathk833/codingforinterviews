# 🎙️ Mock Technical Interview Session #5: Performance, Chaos SRE & App/AI Security — Little's Law, SLOs & Zero-Trust (Phase 4 Exit Gate)

**Target Role:** Staff Performance, Chaos & Security QE Architect  
**Roadmap Milestone:** Phase 4 Exit Gate  
**Session Guidelines:** Draft structured Staff-level architectural responses for all 5 questions in the **Candidate Architectural Response Studio** (`Q1`–`Q5`) and click **`▶ Evaluate Session (100-Pt Rubric)`** for instant deterministic Bar-Raiser scoring across *Mechanisms (30)*, *Math & SLAs (20)*, *Trade-Offs & Failure Modes (25)*, *Operability (15)*, and *Clarity (10)*.

---

### Question 1: Little's Law (`L = λW`), Connection Pool Sizing & Coordinated Omission
**Scenario:**  
A closed-loop 50-VU load test reports `p99 = 45ms`, yet production users hit `4.2s` freezes during 1.5-second JVM/DB pauses at `500 RPS`.

**Your Task as Staff Architect:**
1. Explain **Coordinated Omission** in closed-loop VUs vs open-loop constant-arrival-rate schedules (`k6` / `HdrHistogram`).
2. Apply Little's Law (`L = λ * W`) at `λ = 500 RPS` during a `W = 400ms` downstream slowdown to size thread & HikariCP DB pools without thrashing.
3. Design load-shedding / queue-timeout bounds before pool starvation cascades.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 2: Scientific Chaos Engineering (`Toxiproxy`), Circuit Breakers & Soak Leak Detection
**Scenario:**  
Injecting a Redis timeout in staging brings down Flight Search completely instead of falling back cleanly.

**Your Task as Staff Architect:**
1. Structure a scientific Chaos Experiment (Steady-State Hypothesis, Blast-Radius Abort Condition, Toxiproxy toxic injection).
2. Verify 3-state Circuit Breaker transitions (`CLOSED -> OPEN -> HALF_OPEN -> CLOSED`) and Bulkhead isolation.
3. Detect slow off-heap memory / file-descriptor (`FD`) leaks in a 6-hour soak test using linear regression slope gates.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 3: Multi-Window Multi-Burn-Rate SLO Gates (`14.4x` / `6x`) & Canary Rollbacks
**Scenario:**  
Static `> 1% error rate for 5m` alerts page engineers on harmless blips yet miss slow 3-day error-budget exhaustion.

**Your Task as Staff Architect:**
1. Calculate the monthly 30-day Error Budget for a `99.9%` availability SLO (`43.2 minutes` / `0.1%` bad requests).
2. Explain Google SRE Multi-Window Multi-Burn-Rate alerts (`1h/5m` at `14.4x` fast burn vs `6h/30m` at `6x` burn).
3. Automate Canary deployment rollback gates comparing canary vs baseline pods statistically (Mann-Whitney / error ratio).

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 4: Automated OWASP API Security — BOLA (`IDOR`), Mass Assignment & RFC 8725 JWT
**Scenario:**  
A user swaps `/api/v1/orders/ORD-99` with Tenant A's valid JWT and reads Tenant B's passport details (`200 OK`).

**Your Task as Staff Architect:**
1. Build an automated Cross-Tenant BOLA/BFLA matrix test harness running on every OpenAPI endpoint.
2. Test RFC 8725 JWT attacks (`alg: none`, RS256->HS256 public-key confusion, unverified `kid` injection, missing `aud`/`exp`).
3. Catch Mass Assignment (`role: 'admin'`, `price_cents: 0`) via strict DTO allowlisting tests.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 5: Cloud Metadata SSRF (`169.254.169.254` / IMDSv2), Webhook HMAC Replay & Race-Condition Double-Spend
**Scenario:**  
An invoice-logo URL previewer fetches user-supplied URLs, and a Stripe refund webhook lacks timestamp replay protection.

**Your Task as Staff Architect:**
1. Prevent SSRF against cloud metadata (`169.254.169.254`, IPv6/octal bypasses, DNS rebinding) + enforce AWS IMDSv2 hop-limit.
2. Verify Webhook authenticity (`HMAC-SHA256` constant-time `hmac.compare_digest` + `5-minute` timestamp replay window).
3. Write a parallel Race-Condition Double-Spend security test (`20` simultaneous coupon/wallet redemptions).

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---
