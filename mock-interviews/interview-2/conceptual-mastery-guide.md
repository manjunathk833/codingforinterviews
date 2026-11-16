## 🧠 Conceptual Mastery Guide — Session #2: Frontend & Browser Architecture

**Milestone:** `Phase 1 Exit Gate` · **Target Bar:** `>= 85 / 100` across all 5 Staff dimensions.

## Core Architectural Mental Models & Benchmark Blueprints

### Q1: Flakiness Combinatorics (p^N) & Hermetic UI Seam Economics
- **Problem Core:** A checkout SPA suite has 250 browser tests each passing 99.2% of runs independently, yet PR builds fail over 85% of the time.
- **Staff Benchmark Synthesis:** `0.992^250 = 0.134` (86.6% build failure!). Reaching `0.95` across 250 tests requires `p = 0.95^(1/250) = 0.99979`. Keep 10–15 true E2E smoke journeys unmocked while shifting 235 UI state permutations onto OpenAPI/Pact-verified `page.route` seams rather than masking races with blind `@Retry`.
- ** Trap / Anti-Patterns to Reject:** `thread.sleep`, `retry everything 5 times`

### Q2: Browser Process vs BrowserContext Memory Sizing on K8s Runners
- **Problem Core:** Your Playwright runner pods (`4 vCPU, 8 GiB RAM`, `/dev/shm` default `64 MiB`) crash with `Target closed` and Exit Code `137` at 16 workers.
- **Staff Benchmark Synthesis:** 1 Browser (~350MB) + 16 BrowserContexts (16 * 25MB = 400MB) fits comfortably under 1.5 GiB vs 8+ GiB for 16 full browsers. Mount tmpfs `/dev/shm` >= 1–2 GiB (or `--disable-dev-shm-usage`) to prevent Exit 137 SIGKILL, and mint per-worker API `storageState` JSONs in setup so workers skip UI login with zero cart collisions.
- ** Trap / Anti-Patterns to Reject:** `login via ui before every test`, `share one mutable user across workers`

### Q3: Next.js SSR Hydration Races, Shadow DOM & Five Actionability Gates
- **Problem Core:** Tests click a visible server-rendered `Book Seat` button in Next.js, Playwright reports `click()` succeeded, yet no `/api/orders` POST fires.
- **Staff Benchmark Synthesis:** Playwright verifies Attached, Visible, Stable, Receives Events, and Enabled—but SSR paints enabled HTML before React attaches JS `onClick` handlers. Emit deterministic hydration readiness (`data-hydrated='true'`) or assert post-hydration interactive state, use CSS/getByRole auto-piercing on open Shadow roots, and isolate Stripe iframes via `page.frameLocator()`.
- ** Trap / Anti-Patterns to Reject:** `page.wait_for_timeout`, `time.sleep`, `xpath //div[3]/button`

### Q4: Deterministic Clock Virtualization, WebSocket Mocking & Network Faults
- **Problem Core:** AeroCart's seat-hold countdown expires after 10 minutes over a live WebSocket ticker and shows a degraded banner on HTTP 429/503.
- **Staff Benchmark Synthesis:** Install `page.clock.install()` before navigation and call `clock.fastForward('10:01')` to trigger expiry in <50ms. Use `page.routeWebSocket()` to inject synthetic `SEAT_LOCKED` frames deterministically, and `page.route('**/api/v1/orders')` returning `429` with `Retry-After: 2` to assert accessible `role='alert'` degradation banners.
- ** Trap / Anti-Patterns to Reject:** `sleep(600)`, `wait 10 minutes in ci`

### Q5: Visual Pixel-Diffing vs Accessibility (`axe-core`) Gates & Blob Sharding
- **Problem Core:** Font anti-aliasing differences between macOS laptops and Linux CI runners break `toHaveScreenshot()` on every PR.
- **Staff Benchmark Synthesis:** Generate and verify visual baselines exclusively inside pinned Linux Playwright Docker images, masking dynamic timestamps/avatars and disabling CSS animations. Pair `@axe-core/playwright` WCAG 2.1 AA checks (4.5:1 contrast, labels, focus traps) with keyboard tab-order tests, and aggregate `--shard=i/N` runs via `playwright merge-reports`.
- ** Trap / Anti-Patterns to Reject:** `disable visual tests completely`, `set threshold to 50%`

## Deep-Linked Textbook Chapters
- `sdet-01-determinism-and-flakiness-math`
- `pw-01-webdriver-http-vs-cdp-and-bidi-pipes`
- `pw-02-browser-processes-vs-browser-context-memory`
- `pw-03-dom-shadow-dom-iframes-and-hydration-races`
- `pw-06-zero-ui-auth-storage-state-and-personas`
- `pw-07-network-interception-route-and-har-replay`
