---
slug: pw-08-clock-virtualization-websockets-and-aerocart
course_id: 03-ui-automation-playwright
track: core-cs
volume: "03. Zero to Mastery: UI Automation (Playwright-Focused)"
module_number: 3
module_title: "Module 3: Network Control, State & Hybrid API+UI Flows"
chapter_number: 8
level_tag: "Senior → Staff"
title: "AeroBot v0.8: Clock Virtualization, WebSocket Routing & AeroCart Saga Verification"
summary: "Why wait 10 real minutes in CI for a seat-hold countdown to expire? Upgrade AeroBot v0.8 to fast-forward browser time in 15ms with `page.clock` and intercept real-time WebSocket frames with `route_web_socket`."
reading_time_minutes: 15
visualizer_id: pw-network-auth-sharding
lab_path: frameworks/ui-automation/playwright-python
tags: ["clock-api", "time-virtualization", "websockets", "route-websocket", "aerocart", "async-saga", "event-driven-ui"]
---

# AeroBot v0.8: Clock Virtualization, WebSocket Routing & AeroCart Saga Verification

```json continuity
{
  "previously": "In Chapter 07, AeroBot v0.7 mastered HTTP network interception (`page.route`) and HAR replay so we can simulate slow or failing REST APIs on demand.",
  "painPoint": "Two features still force our team into manual testing: (1) AeroCart holds a selected seat for 10 minutes before showing a 'Seat Hold Expired' modal—nobody wants a 600-second sleep in CI!—and (2) live seat-sniping alerts arrive over a persistent WebSocket (`wss://`), which standard HTTP `page.route` cannot intercept.",
  "unlock": "Upgrade to AeroBot v0.8 using `page.clock` to fast-forward 10-minute timers in 15ms and `page.route_web_socket` to inject real-time WebSocket events deterministically!"
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Slide 1 / 4 · The 10-Minute Countdown Trap",
    "caption": "Suppose AeroCart locks Seat 4A for 10 minutes. Waiting 600 real seconds in CI makes your test suite crawl—so teams skip testing timer expirations altogether!",
    "code": "# ❌ Naive: Waits 10 real wall-clock minutes!\ntime.sleep(600)\nexpect(page.get_by_role('alertdialog')).to_be_visible()"
  },
  {
    "time": "0:24",
    "badge": "Slide 2 / 4 · Time-Travel in 15ms with `page.clock`",
    "caption": "By installing `page.clock` BEFORE navigating, AeroBot v0.8 takes over JavaScript's `Date.now` and `setTimeout`. Calling `fast_forward('10:01')` jumps 10 minutes ahead in 15 milliseconds!",
    "code": "page.clock.install(time='2026-09-15T09:00:00Z')\npage.goto('/aerocart/flights/AC-808/seats')\npage.clock.fast_forward('10:01')  # Runs in ~15ms!"
  },
  {
    "time": "0:50",
    "badge": "Slide 3 / 4 · Intercepting Live WebSockets",
    "caption": "What if another passenger snipes Seat 12F over a live WebSocket while we are looking at the seat map? `page.route_web_socket` lets AeroBot push synthetic WebSocket frames right into the browser!",
    "code": "page.route_web_socket('**/ws/seats', lambda ws: ws.send(\n    '{\"type\":\"SEAT_LOCKED\",\"seat\":\"12F\"}'\n))"
  },
  {
    "time": "1:15",
    "badge": "Slide 4 / 4 · Browser Clock vs. Backend Clock",
    "caption": "Remember the golden boundary: `page.clock` fast-forwards JavaScript inside the browser tab, not your remote Postgres or Go server clock!",
    "code": "# Browser UI countdowns -> use page.clock.fast_forward()\n# Backend JWT expiry    -> mint short-TTL token or mock 401"
  }
]
```

```json pretraining
[
  {
    "term": "Synthetic Browser Clock (`page.clock`)",
    "formula": "Overrides Date.now, performance.now, setTimeout, setInterval, rAF",
    "meaning": "A time-travel controller inside the browser tab that lets your test jump forward 15 minutes in a few milliseconds without waiting in real life."
  },
  {
    "term": "`fast_forward` vs `run_for`",
    "formula": "fast_forward('10:00') [1 Jump] vs run_for('10:00') [Every 1s Tick]",
    "meaning": "`fast_forward` jumps straight to the end of a timer in one step, whereas `run_for` fires every single intermediate second-by-second tick."
  },
  {
    "term": "WebSocket Route (`route_web_socket`)",
    "formula": "Browser <-> Playwright WS Interceptor <-> (Optional Server)",
    "meaning": "A switchboard that lets your test inspect, block, or push instant real-time WebSocket messages into the web page on command."
  },
  {
    "term": "Async Checkout Saga",
    "formula": "202 Accepted (PENDING) -> WebSocket Push -> CONFIRMED",
    "meaning": "A multi-step checkout flow where the server immediately says 'Working on it!' and pushes the final boarding pass over a WebSocket a moment later."
  }
]
```

```json poe
{
  "question": "AeroCart holds a selected flight seat for 10 minutes (`600,000ms`) using `setTimeout` + `Date.now()` before displaying a `'Seat Hold Expired'` modal. An engineer writes:\n`page.goto('/flights/FL-100/seats')`\n`page.clock.install(time='2026-06-01T12:00:00Z')`\n`page.clock.fast_forward('10:01')`\nWhy did the timer fail to fire when `page.clock.install()` was called **after** `page.goto()`?",
  "options": [
    "`fast_forward` only accepts integer milliseconds, never `'MM:SS'` strings",
    "Frontend frameworks often capture native `window.setTimeout` and `Date.now` references when the JavaScript bundle first boots during `page.goto()`! Calling `page.clock.install()` **before** `page.goto()` ensures the virtual clock is injected before any app code runs",
    "Chromium disables `setTimeout` when `headless=True`",
    "10 minutes exceeds JavaScript's 32-bit timer integer limit"
  ],
  "answerIndex": 1,
  "explanation": "Libraries like React schedulers and auth SDKs frequently save `const _setTimeout = globalThis.setTimeout` when the page loads. Installing `page.clock.install(...)` *prior* to `page.goto()` guarantees every timer binds to Playwright's virtual clock."
}
```

## 🌱 Step 1: Plain-English Story — The Time Machine & The Walkie-Talkie Switchboard

Imagine testing a digital parking meter that gives a driver **10 minutes** before flashing `"TIME EXPIRED"`.
- If you test that parking meter with a real stopwatch (`time.sleep(600)`), checking 6 edge cases takes **an entire hour**!
- Instead, what if you had a screwdriver that turned the meter's clock hands forward 10 minutes in **15 milliseconds**? That is **`page.clock`**!

Now imagine a second challenge on `AeroCart`'s live seat map: while you are staring at Seat `12F`, another shopper in London books Seat `12F`. How does your screen turn Seat `12F` gray right away without you refreshing the page?
- The browser keeps a live two-way walkie-talkie channel open called a **WebSocket (`wss://`)**.
- Standard HTTP mocks (`page.route`) only catch one-shot postcards (`GET`/`POST`). To test live seat-sniping or instant order confirmations, **`AeroBot v0.8`** plugs into **`page.route_web_socket()`**—acting as the walkie-talkie switchboard so we can push `"SEAT_LOCKED: 12F"` into the page on command!

```mermaid
flowchart LR
  Clock["1. page.clock.install() BEFORE goto()"] -->|Open Seat Map| WS["2. page.route_web_socket('/ws/seats')"]
  WS -->|Push Frame: SEAT_LOCKED 12F| UI["3. AeroCart Disables Seat 12F"]
  UI -->|fast_forward('10:01') in 15ms| Modal["4. Assert 'Hold Expired' Modal"]
```

## 🔨 Step 2: First Lines of Code — Fast-Forwarding 10 Minutes in 15ms (`AeroBot v0.8`)

Let's write our first **`AeroBot v0.8`** check: we install the virtual clock **before** opening `AeroCart`, click Seat `4A` (which starts a 10-minute countdown), and jump forward `10:01` in 15 milliseconds!

```python
from playwright.sync_api import Page, expect


def test_aerobot_v08_fast_forwards_ten_minute_seat_hold(page: Page) -> None:
    # 1. Install virtual clock BEFORE page.goto() so app timers bind to fake time!
    page.clock.install(time="2026-09-15T09:00:00Z")
    page.goto("http://127.0.0.1:8090/aerocart/seats")

    # 2. Select Seat 4A -> UI starts a 10:00 countdown timer
    page.get_by_role("button", name="Seat 4A", exact=True).click()
    expect(page.get_by_test_id("hold-timer")).to_have_text("10:00")

    # 3. Jump 10 minutes & 1 second ahead in ~15ms (ZERO real waiting!)
    page.clock.fast_forward("10:01")
    expect(page.get_by_role("alertdialog", name="Seat Hold Expired")).to_be_visible()
```

### Java 17 Equivalent

```java
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.AriaRole;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class AeroBotV08ClockStarter {
    public static void verifyTenMinuteSeatHoldExpiresInstantly(Page page) {
        // 1. Install virtual clock BEFORE navigate()
        page.clock().install(new Clock.InstallOptions().setTime("2026-09-15T09:00:00Z"));
        page.navigate("http://127.0.0.1:8090/aerocart/seats");

        // 2. Click Seat 4A and verify initial 10:00 countdown
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Seat 4A").setExact(true)).click();
        assertThat(page.getByTestId("hold-timer")).hasText("10:00");

        // 3. Fast-forward 10m 01s in ~15ms!
        page.clock().fastForward("10:01");
        assertThat(page.getByRole(AriaRole.ALERTDIALOG)).isVisible();
    }
}
```

## ⚡ Step 3: Where It Breaks in Real Life — `fast_forward` vs. `run_for` & Live WebSocket Races

What happens when teams try to test real-time UIs without `page.clock` and `route_web_socket`?
1. **Skipped Expiration Tests**: Nobody wants a 15-minute `sleep(900)` in CI, so session-timeout and seat-expiry dialogs go completely untested until they break in production.
2. **Untestable Seat-Sniping Races**: Trying to spin up a second real browser to buy Seat `12F` at the exact millisecond Buyer 1 views the map is a timing nightmare. With `page.route_web_socket()`, `AeroBot v0.8` injects the exact JSON frame `{"type": "SEAT_LOCKED", "seat": "12F"}` deterministically in 1ms!

```json contrast
{
  "title": "Wall-Clock `sleep(600)` & Live WS Races vs `page.clock` & `route_web_socket`",
  "naiveTitle": "Real `sleep()` + Uncontrolled Live WS",
  "naiveMetric": "10m Test Runtime · Untested Race Edges",
  "naivePoints": [
    "Skips testing 15-minute session-expiry and 10-minute seat-hold timers in CI because wall-clock waits are too slow",
    "Cannot deterministically simulate another user sniping Seat `12F` via WebSocket 50ms before checkout click",
    "Polls backend DB with `time.sleep(2)` loops instead of synchronizing on pushed UI state transitions"
  ],
  "staffTitle": "`page.clock.fast_forward` + `route_web_socket`",
  "staffMetric": "15ms Virtual Jump · Deterministic WS Frames",
  "staffPoints": [
    "Installs `page.clock` prior to navigation and jumps 10–15 minutes via `fast_forward()` in <20ms",
    "Intercepts `wss://.../ws/orders` via `route_web_socket` to inject out-of-order, duplicate, or conflict events",
    "Verifies full AeroCart `PENDING -> CONFIRMED` saga across API seed, WebSocket push, and Web-First DOM assertions"
  ]
}
```

Step through the **`pw-network-auth-sharding`** simulator below to watch virtual clock jumps and WebSocket frame injections drive `AeroCart`'s booking state machine.

## 🚀 Step 4: Staff Engineer Deep-Dive — Tick Complexity Math & Full Saga Blueprints

When choosing between `page.clock.fast_forward(ΔT)` and `page.clock.run_for(ΔT)` for an application that registers a periodic interval $\Delta t_{\text{interval}}$ (such as a `100ms` progress bar or `1000ms` countdown clock) over horizon $\Delta T$:

$$\text{Invocations}_{\text{run\_for}}(\Delta T) = \left\lfloor \frac{\Delta T}{\Delta t_{\text{interval}}} \right\rfloor = \mathcal{O}\left(\frac{\Delta T}{\Delta t_{\text{interval}}}\right), \qquad \text{Invocations}_{\text{fast\_forward}}(\Delta T) = \mathcal{O}(1)$$

For a 15-minute (`900,000ms`) idle-logout check on a page with a `100ms` UI ticker, `run_for("15:00")` executes **9,000 synchronous timer callbacks and DOM re-renders**, whereas `fast_forward("15:00")` advances the virtual epoch in **$\mathcal{O}(1)$ (`1` callback execution)**!

| Primitive | Exact Runtime Behavior | Ideal Test Scenario | Critical Nuance |
| :--- | :--- | :--- | :--- |
| `clock.install(time=...)` | Hooks `Date`, `setTimeout`, `setInterval`, `rAF` at fixed start epoch | Pinning `"Midnight Promo"` or deterministic billing dates | **Must** be called *before* `page.goto()`! |
| `clock.fast_forward("10:00")` | Advances clock once & fires due timers **at most once** ($\mathcal{O}(1)$) | Jumping past 10m seat-hold or 15m JWT idle timeout | Skips intermediate `1s` `setInterval` ticks for maximum speed. |
| `clock.pause_at(t)` + `run_for(dt)` | Steps deterministically firing **every** intermediate interval tick | Testing a visual second-by-second countdown (`09:59` $\to$ `09:58`) | Executes all $\lfloor \Delta T / \Delta t \rfloor$ ticks. |
| `page.route_web_socket(url, fn)` | Intercepts browser WebSocket handshake & bidirectional frames | Pushing instant `SEAT_SNIPED`, `BOOKING_CONFIRMED`, or duplicate frames | Call `ws.connect_to_server()` only when proxying to a real WS backend. |

### Production Blueprint: `AeroBot v0.8` WebSocket Saga + Idempotent Duplicate Frame Verification (Python 3)

```python
from __future__ import annotations
import json
from playwright.sync_api import Page, WebSocketRoute, expect


def test_aerocart_websocket_saga_pending_to_confirmed_and_duplicate_guard(page: Page) -> None:
    """Deterministically drives AeroCart's WebSocket booking state machine without backend race sleeps."""
    pushed_channels: list[WebSocketRoute] = []

    def _ws_handler(ws: WebSocketRoute) -> None:
        pushed_channels.append(ws)
        ws.on_message(lambda msg: None)  # Observe outbound client subscription frames

    page.route_web_socket("**/ws/bookings/*", _ws_handler)
    page.goto("/aerocart/checkout/BOOK-7741")

    status_badge = page.get_by_test_id("saga-status-badge")
    expect(status_badge).to_have_text("PENDING")
    assert len(pushed_channels) == 1

    # Push duplicate confirmation frames over the intercepted WebSocket to verify UI idempotency!
    event_frame = json.dumps({"event": "BOOKING_CONFIRMED", "bookingId": "BOOK-7741", "pnr": "XK92LM"})
    pushed_channels[0].send(event_frame)
    pushed_channels[0].send(event_frame)

    expect(status_badge).to_have_text("CONFIRMED")
    expect(page.get_by_test_id("issued-pnr")).to_have_text("XK92LM")
```

### Java 17 Equivalent

```java
package com.aerocart.qa.realtime;

import com.microsoft.playwright.*;
import com.microsoft.playwright.options.AriaRole;
import java.util.concurrent.atomic.AtomicReference;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public final class AeroCartRealtimeSagaSpec {

    public void verifyIdleSessionWarningAndWebSocketPush(Page page) {
        page.clock().install(new Clock.InstallOptions().setTime("2026-09-15T14:00:00Z"));

        AtomicReference<WebSocketRoute> activeSocket = new AtomicReference<>();
        page.routeWebSocket("**/ws/inventory", ws -> {
            activeSocket.set(ws);
            ws.onMessage(clientFrame -> { /* Inspect client subscribe payload */ });
        });

        page.navigate("/aerocart/flights/AC-808/seats");
        Locator seat12F = page.getByRole(AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName("Seat 12F").setExact(true));
        assertThat(seat12F).isEnabled();

        // Inject real-time concurrent buyer lock frame over WebSocket
        activeSocket.get().send("{\"type\":\"SEAT_LOCKED\",\"seat\":\"12F\",\"by\":\"other_tenant\"}");
        assertThat(seat12F).isDisabled();

        // Fast-forward 14m 30s to trigger the 30s pre-expiry session warning banner in <20ms!
        page.clock().fastForward("14:30");
        assertThat(page.getByRole(AriaRole.ALERT)).containsText("Your session expires in 30 seconds");
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Virtualizing Browser `page.clock` Does NOT Advance the Backend Server's Clock!**
> `page.clock.fast_forward("15:00")` advances time **inside the browser's JavaScript runtime only**! If the browser then sends a real `GET /api/orders` to a live backend container with a JWT whose `exp` claim is `now + 15m`, the **backend server's OS clock** has only advanced `15ms`—so the backend still considers the JWT valid! Use `page.clock` for **frontend** timers/modals, and use a short-TTL test token (`exp = now + 1s`) or `page.route` `401` mock when testing backend token expiration.

**Up Next in Chapter 09**: What happens when a test still fails on a remote CI runner at 3:00 AM, or a CSS change accidentally turns our `"Pay Now"` button white-on-white? In Chapter 09, we'll upgrade to **`AeroBot v0.9`** with **Time-Travel `trace.zip` Forensics, Automated WCAG 2.1 AA (`axe-core`) Audits, and Masked Visual Diffing**!

```json quiz
[
  {
    "id": "pw-08-q1",
    "question": "What is the critical behavioral difference between `page.clock.fast_forward('10:00')` and `page.clock.run_for('10:00')` when the page runs a `setInterval(renderTick, 100)` progress animation?",
    "options": [
      "They are aliases for the exact same function",
      "`run_for('10:00')` simulates every single `100ms` tick (`6,000` callback invocations + DOM renders!), whereas `fast_forward('10:00')` jumps clock time directly by 10 minutes and fires due timers at most once in O(1)",
      "`fast_forward` only advances `Date.now()` without ever firing `setTimeout`",
      "`run_for` requires root `sudo` permissions in Docker"
    ],
    "answerIndex": 1,
    "explanation": "Use `fast_forward` whenever you care about the state *after* a long timeout expires (idle logout, seat hold expiry), and reserve `pause_at` + `run_for` for stepping through intermediate animation/countdown ticks."
  },
  {
    "id": "pw-08-q2",
    "question": "Inside a `page.route_web_socket('**/ws/chat', handler)` callback, what determines whether the browser's WebSocket connects to the real backend server versus operating as a 100% hermetic in-memory mock?",
    "options": [
      "Whether `headless=True` is set",
      "By default, `route_web_socket` does NOT connect to the real server (100% hermetic mock mode); it only opens an upstream connection to the real backend if `handler` explicitly calls `server = ws.connect_to_server()`",
      "Playwright always forwards WebSocket frames to the real server automatically",
      "You must edit `/etc/hosts` to block real WebSockets"
    ],
    "answerIndex": 1,
    "explanation": "Not calling `ws.connect_to_server()` keeps the WebSocket completely isolated in memory so `ws.send(...)` drives the UI deterministically; calling `ws.connect_to_server()` switches into bidirectional proxy/spy mode."
  },
  {
    "id": "pw-08-q3",
    "question": "An engineer uses `page.clock.fast_forward('60:00')` and asserts that clicking `'Fetch Account Balance'` causes the live Go backend API to return `401 Token Expired`. Instead, the Go API returns `200 OK`! Why?",
    "options": [
      "Go ignores JWT `exp` claims by default",
      "`page.clock` virtualizes time only inside the browser's JS runtime (`Date.now`, `setTimeout`); the separate Go backend container's OS clock only elapsed ~15ms, so the 1-hour JWT was still valid on the server!",
      "`fast_forward` resets cookies",
      "JWTs use UTC whereas `page.clock` uses local time"
    ],
    "answerIndex": 1,
    "explanation": "`page.clock` controls client-side JS timers and client-side `Date.now()` checks, never remote microservice system clocks."
  }
]
```
