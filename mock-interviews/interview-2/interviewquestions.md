# 🎙️ Mock Technical Interview Session #2: Frontend & Browser Architecture — CDP Pipes, Context Memory & Hydration (Phase 1 Exit Gate)

**Target Role:** Senior / Staff Frontend Quality Architect  
**Roadmap Milestone:** Phase 1 Exit Gate  
**Session Guidelines:** Draft structured Staff-level architectural responses for all 5 questions in the **Candidate Architectural Response Studio** (`Q1`–`Q5`) and click **`▶ Evaluate Session (100-Pt Rubric)`** for instant deterministic Bar-Raiser scoring across *Mechanisms (30)*, *Math & SLAs (20)*, *Trade-Offs & Failure Modes (25)*, *Operability (15)*, and *Clarity (10)*.

---

### Question 1: Flakiness Combinatorics (p^N) & Hermetic UI Seam Economics
**Scenario:**  
A checkout SPA suite has 250 browser tests each passing 99.2% of runs independently, yet PR builds fail over 85% of the time.

**Your Task as Staff Architect:**
1. Prove mathematically why 99.2% per-test reliability collapses across 250 tests (`P = p^N`) and calculate the per-test reliability needed for 95% green CI runs.
2. Design a Hermetic UI Seam strategy deciding what runs against real backend pods vs deterministic network route mocks (`page.route` / HAR).
3. Explain why blind `@Retry(3)` hides concurrency bugs and inflates CI cost.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 2: Browser Process vs BrowserContext Memory Sizing on K8s Runners
**Scenario:**  
Your Playwright runner pods (`4 vCPU, 8 GiB RAM`, `/dev/shm` default `64 MiB`) crash with `Target closed` and Exit Code `137` at 16 workers.

**Your Task as Staff Architect:**
1. Calculate memory footprint comparing 16 OS Chromium processes vs 1 Browser + 16 isolated `BrowserContext` instances.
2. Diagnose why Docker's `64 MiB` `/dev/shm` crashes Chromium compositors and specify exact container flags/mounts.
3. Design zero-UI authentication state reuse (`storageState`) across 16 parallel worker personas without session token collisions.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 3: Next.js SSR Hydration Races, Shadow DOM & Five Actionability Gates
**Scenario:**  
Tests click a visible server-rendered `Book Seat` button in Next.js, Playwright reports `click()` succeeded, yet no `/api/orders` POST fires.

**Your Task as Staff Architect:**
1. List Playwright's 5 Actionability Gates and explain why SSR hydration still defeats them.
2. Architect a deterministic fix across app instrumentation (`data-hydrated` / readiness signals) and web-first assertions.
3. Explain how closed vs open Shadow DOM piercing and cross-origin payment `iframe` (`Stripe Elements`) locators work.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 4: Deterministic Clock Virtualization, WebSocket Mocking & Network Faults
**Scenario:**  
AeroCart's seat-hold countdown expires after 10 minutes over a live WebSocket ticker and shows a degraded banner on HTTP 429/503.

**Your Task as Staff Architect:**
1. Design a sub-second test verifying the 10-minute countdown expiry without waiting 600 real seconds (`page.clock`).
2. Architect deterministic WebSocket frame interception (`page.routeWebSocket`) for concurrent seat-snatch events.
3. Test UI retry/degradation banners under injected `429 Retry-After` and `503` upstream faults.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 5: Visual Pixel-Diffing vs Accessibility (`axe-core`) Gates & Blob Sharding
**Scenario:**  
Font anti-aliasing differences between macOS laptops and Linux CI runners break `toHaveScreenshot()` on every PR.

**Your Task as Staff Architect:**
1. Solve cross-OS font/GPU rendering drift so visual regression tests stay 100% reproducible.
2. Define WCAG 2.1 AA automated gates (`@axe-core/playwright`) and what human/screen-reader gaps remain.
3. Design sharded Playwright execution merging Blob reports (`--reporter=blob` -> `merge-reports`).

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---
