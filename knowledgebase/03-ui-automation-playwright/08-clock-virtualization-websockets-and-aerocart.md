---
slug: pw-08-clock-virtualization-websockets-and-aerocart
course_id: 03-ui-automation-playwright
track: core-cs
volume: "03. Zero to Mastery: UI Automation (Playwright-Focused)"
module_number: 3
module_title: "Module 3: Network Control, State & Hybrid API+UI Flows"
chapter_number: 8
level_tag: "Senior → Staff"
title: "Clock Virtualization, WebSocket Routing & AeroCart Saga Verification"
summary: "Testing 15-minute JWT/seat-hold expirations in 20 milliseconds via `page.clock`, intercepting real-time WebSocket frames with `route_web_socket`, and verifying AeroCart async sagas."
reading_time_minutes: 21
visualizer_id: pw-network-auth-sharding
lab_path: frameworks/ui-automation/playwright-python
tags: ["clock-api", "time-virtualization", "websockets", "route-websocket", "aerocart", "async-saga", "event-driven-ui"]
---

# Clock Virtualization, WebSocket Routing & AeroCart Saga Verification

```json pretraining
[
  {
    "term": "Synthetic Browser Clock (`page.clock`)",
    "formula": "Overrides Date.now, performance.now, setTimeout, setInterval, rAF",
    "meaning": "Installing `page.clock` before navigation lets tests fast-forward a 15-minute seat-hold countdown or idle-logout modal in <20ms of wall-clock time!"
  },
  {
    "term": "`fast_forward` vs `run_for` Semantics",
    "formula": "fast_forward('15:00') [Fires Due Timers Once] vs run_for('15:00') [Every Tick]",
    "meaning": "`fast_forward` jumps virtual time without firing 900 intermediate 1-second `setInterval` UI ticks, keeping CPU cost $O(1)$ instead of $O(T)$."
  },
  {
    "term": "Bidirectional `route_web_socket`",
    "formula": "Client <-> ws_route <-> Server (or Pure Synthetic Push Frames)",
    "meaning": "Playwright intercepts `ws://` / `wss://` frames in-browser to inspect, drop, delay, or inject real-time `SEAT_LOCKED` / `ORDER_CONFIRMED` events on demand."
  },
  {
    "term": "End-to-End Saga Causal Verification",
    "formula": "API Seed -> UI Seat Hold -> Clock Jump / WS Push -> Assert UI + Backend State",
    "meaning": "Combining `APIRequestContext`, `page.clock`, and `route_web_socket` verifies complex distributed sagas (`PENDING -> CONFIRMED`) deterministically."
  }
]
```

```json poe
{
  "question": "AeroCart holds a selected flight seat for **10 minutes (`600,000ms`)** using `setTimeout` + `Date.now()` before displaying a `'Seat Hold Expired'` modal. Previously, QA marked this test `@manual_only` because nobody wanted a 10-minute `sleep(600)` in CI! An engineer writes:\n`page.goto('/flights/FL-100/seats')`\n`page.clock.install(time='2026-06-01T12:00:00Z')`\n`page.clock.fast_forward('10:01')`\nWhy did the timer fail to fire correctly when `page.clock.install()` was called **after** `page.goto()`?",
  "options": [
    "`fast_forward` only accepts integer milliseconds, never `'MM:SS'` strings",
    "Application bundles often cache references to native `window.setTimeout` and `Date.now` at module initialization during `page.goto()`! Calling `page.clock.install()` **before** `page.goto()` ensures the virtualized globals are injected via init script *before* any app code boots and schedules timers",
    "Chromium disables `setTimeout` when `headless=True`",
    "10 minutes exceeds JavaScript's 32-bit timer integer limit"
  ],
  "answerIndex": 1,
  "explanation": "Libraries like React schedulers, RxJS, and auth SDKs frequently capture `const _setTimeout = globalThis.setTimeout` at bundle load time. Installing `page.clock.install(...)` *prior* to `page.goto()` guarantees every timer and timestamp read binds to Playwright's virtual clock."
}
```

## Part I — First-Principles Mental Model: Virtualizing Time & Streaming Frames

Two categories of UI features historically forced teams into slow, brittle manual QA checklists:
1. **Long-Horizon Temporal Logic**: 15-minute idle session warning modals, 10-minute concert/flight seat-hold countdowns, JWT silent-refresh schedules (`exp - 60s`), and "Flash Sale starts at Midnight UTC" banners. Waiting real wall-clock minutes in CI is untenable.
2. **Asynchronous WebSocket / Push Sagas (`AeroCart` Checkout)**: When a buyer submits an AeroCart seat booking, `OrdersService` returns `202 Accepted` (`status: "PENDING"`), publishes a Kafka event to `Inventory` and `Payment` workers, and pushes `{"type": "BOOKING_CONFIRMED", "pnr": "AC9921"}` over a **WebSocket (`wss://`)** 400ms later—or pushes `{"type": "SEAT_SNIPED_BY_OTHER_BUYER"}` on conflict!

Playwright makes both 100% deterministic in milliseconds:
- **`page.clock` Virtualization**: Replaces `Date`, `performance.now`, `setTimeout`, `setInterval`, and `requestAnimationFrame` across all frames in the context. Calling `page.clock.fast_forward("10:05")` advances the virtual epoch by 605 seconds and triggers expired callbacks in **~15ms**!
- **`page.route_web_socket()` Frame Interception**: Sits as an in-memory man-in-the-middle (or pure synthetic server) on WebSocket connections:
  - **Pure Synthetic Mode** (don't call `ws.connect_to_server()`): Instantly push `ws.send('{"type":"SEAT_SNIPED","seat":"14A"}')` to prove the UI disables seat `14A` in real time!
  - **Proxy / Spy Mode** (`server = ws.connect_to_server()`): Forward live frames between AeroCart's backend and UI while asserting frame schemas or dropping/reordering specific messages!

```mermaid
flowchart LR
  Clock["1. page.clock.install() BEFORE goto()"] -->|Open Seat Map| WS["2. page.route_web_socket('/ws/seats')"]
  WS -->|Inject Frame: SEAT_LOCKED 12A| UI["3. AeroCart UI Disables 12A"]
  UI -->|fast_forward('10:01') in 15ms| Modal["4. Assert 'Hold Expired' Dialog"]
```

```json contrast
{
  "title": "Wall-Clock `sleep(600)` & Untested WebSocket Races vs `page.clock` & `route_web_socket`",
  "naiveTitle": "Real `sleep()` + Uncontrolled Live WS",
  "naiveMetric": "10m Test Runtime · Untested Race Edges",
  "naivePoints": [
    "Skips testing 15-minute session-expiry and 10-minute seat-hold timers in CI because wall-clock waits are too slow",
    "Cannot deterministically simulate another user sniping Seat `4F` via WebSocket 50ms before checkout click",
    "Polls backend DB with `time.sleep(2)` loops instead of synchronizing on pushed UI state transitions"
  ],
  "staffTitle": "`page.clock.fast_forward` + `route_web_socket`",
  "staffMetric": "18ms Virtual Jump · Deterministic WS Frames",
  "staffPoints": [
    "Installs `page.clock` prior to navigation and jumps 15 minutes via `fast_forward('15:00')` in <20ms",
    "Intercepts `wss://.../ws/orders` via `route_web_socket` to inject out-of-order, duplicate, or conflict events",
    "Verifies full AeroCart `PENDING -> CONFIRMED` saga across API seed, WebSocket push, and Web-First DOM assertions"
  ]
}
```

---

## Part II — `page.clock` & `route_web_socket` Control Primitives

Step through the **`pw-network-auth-sharding`** interactive simulator to watch virtual clock jumps and WebSocket frame injections drive AeroCart's booking state machine.

| Primitive | Exact Runtime Behavior | Ideal Test Scenario | Critical Nuance |
| :--- | :--- | :--- | :--- |
| `clock.install(time=...)` | Hooks `Date`, `setTimeout`, `setInterval`, `rAF` at fixed start epoch | Pinning `"Midnight New Year Promo"` or deterministic billing dates | **Must** be called *before* `page.goto()`! |
| `clock.fast_forward("10:00")` | Advances clock once & fires due timers **at most once** | Jumping past 10m seat-hold or 15m JWT idle timeout in $O(1)$ | Does not execute 600 intermediate `1s` `setInterval` ticks. |
| `clock.pause_at(t)` + `run_for(dt)` | Steps deterministically firing **every** intermediate interval tick | Testing a visual second-by-second countdown (`09:59` $\to$ `09:58`) | Slightly heavier CPU if ticking thousands of 10ms intervals. |
| `page.route_web_socket(url, fn)` | Intercepts browser WebSocket handshake & bidirectional frames | Pushing instant `SEAT_SNIPED`, `ORDER_CONFIRMED`, or disconnect chaos | Call `ws.connect_to_server()` only when proxying to a real WS backend. |

---

## Part III — Production Implementation Blueprints (Python 3 & Java 17)

### Python 3 Blueprint: AeroCart 10-Minute Seat Hold Expiry (`clock`) + Real-Time WebSocket Saga (`route_web_socket`)
```python
from __future__ import annotations
import json
from playwright.sync_api import Page, WebSocketRoute, expect


def test_aerocart_ten_minute_seat_hold_expires_in_milliseconds(page: Page) -> None:
    """Verifies a 10-minute seat-hold countdown expires cleanly in ~15ms of wall-clock time."""
    # CRITICAL: Install virtualized clock BEFORE navigating so app timers bind to fake setTimeout!
    page.clock.install(time="2026-09-15T09:00:00Z")
    page.goto("/aerocart/flights/AC-808/seats")

    page.get_by_role("button", name="Seat 4A", exact=True).click()
    expect(page.get_by_test_id("hold-timer")).to_have_text("10:00")

    # Jump 10 minutes and 1 second instantaneously without sleeping!
    page.clock.fast_forward("10:01")

    expired_dialog = page.get_by_role("alertdialog", name="Seat Hold Expired")
    expect(expired_dialog).to_be_visible()


def test_aerocart_websocket_saga_pending_to_confirmed_and_snipe(page: Page) -> None:
    """Deterministically drives AeroCart's WebSocket booking state machine without backend race sleeps."""
    pushed_channels: list[WebSocketRoute] = []

    def _ws_handler(ws: WebSocketRoute) -> None:
        pushed_channels.append(ws)
        ws.on_message(lambda msg: None)  # Observe outbound client subscription frames

    page.route_web_socket("**/ws/bookings/*", _ws_handler)
    page.goto("/aerocart/checkout/BOOK-7741")

    # Initial SSR/REST state shows async saga in progress
    status_badge = page.get_by_test_id("saga-status-badge")
    expect(status_badge).to_have_text("PENDING")
    assert len(pushed_channels) == 1

    # Push duplicate + final confirmation frames over the intercepted WebSocket (tests UI idempotency too!)
    event_frame = json.dumps({"event": "BOOKING_CONFIRMED", "bookingId": "BOOK-7741", "pnr": "XK92LM"})
    pushed_channels[0].send(event_frame)
    pushed_channels[0].send(event_frame)

    expect(status_badge).to_have_text("CONFIRMED")
    expect(page.get_by_test_id("issued-pnr")).to_have_text("XK92LM")
```

### Java 17 Blueprint: `Page.clock()` JWT Expiry Test & `routeWebSocket` Live Inventory Push
```java
package com.aerocart.qa.realtime;

import com.microsoft.playwright.*;
import com.microsoft.playwright.options.AriaRole;
import java.util.concurrent.atomic.AtomicReference;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public final class AeroCartRealtimeSagaSpec {

    public void verifyIdleSessionWarningAndWebSocketPush(Page page) {
        // 1. Install deterministic virtual clock prior to bundle boot
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

        // 2. Inject real-time concurrent buyer lock frame over WebSocket
        activeSocket.get().send("{\"type\":\"SEAT_LOCKED\",\"seat\":\"12F\",\"by\":\"other_tenant\"}");
        assertThat(seat12F).isDisabled();

        // 3. Fast-forward 14m 30s to trigger the 30s pre-expiry session warning banner in <20ms!
        page.clock().fastForward("14:30");
        assertThat(page.getByRole(AriaRole.ALERT)).containsText("Your session expires in 30 seconds");
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Virtualizing Browser `page.clock` Does NOT Advance the Backend Server's Clock!**:
> Remember the process boundary: `page.clock.fast_forward("15:00")` advances time **inside the browser's JavaScript V8/WebKit engine only**! If the browser then sends a real `GET /api/orders` to a live backend container with a JWT whose `exp` claim is `now + 15m`, the **backend server's OS clock** has only advanced `20ms`—so the backend still considers the JWT valid (or vice-versa if you minted an already-expired JWT)! When testing **frontend** expiry modals/refresh triggers, `page.clock` is sufficient; when testing **backend** JWT expiration rejection, mint a short-TTL test token (`exp = now + 1s`) via your test auth helper rather than expecting `page.clock` to warp Postgres/Go server clocks!

---

## Part IV — Scenario Retrieval-Practice Mastery Gate

```json quiz
[
  {
    "id": "pw-08-q1",
    "question": "What is the critical behavioral difference between `page.clock.fast_forward('10:00')` and `page.clock.run_for('10:00')` when the page runs a `setInterval(renderTick, 100)` progress animation?",
    "options": [
      "They are aliases for the exact same function",
      "`run_for('10:00')` simulates every single `100ms` tick (`6,000` callback invocations + DOM renders!), whereas `fast_forward('10:00')` jumps clock time directly by 10 minutes and fires due timers at most once—making `fast_forward` orders of magnitude faster when testing end-of-window expiration",
      "`fast_forward` only advances `Date.now()` without ever firing `setTimeout`",
      "`run_for` requires root `sudo` permissions in Docker"
    ],
    "answerIndex": 1,
    "explanation": "Use `fast_forward` whenever you care about the state *after* a long timeout expires (idle logout, seat hold expiry), and reserve `pause_at` + `run_for` for stepping smoothly through intermediate animation/countdown ticks."
  },
  {
    "id": "pw-08-q2",
    "question": "Inside a `page.route_web_socket('**/ws/chat', handler)` callback, what determines whether the browser's WebSocket connects to the real backend server versus operating as a 100% hermetic in-memory mock?",
    "options": [
      "Whether `headless=True` is set",
      "By default, `route_web_socket` does **NOT** connect to the real server (100% hermetic mock mode); it only opens an upstream connection to the real backend if `handler` explicitly invokes `server = ws.connect_to_server()`!",
      "Playwright always forwards WebSocket frames to the real server automatically",
      "You must edit `/etc/hosts` to block real WebSockets"
    ],
    "answerIndex": 1,
    "explanation": "Not calling `ws.connect_to_server()` keeps the WebSocket completely isolated in memory so `ws.send(...)` drives the UI deterministically; calling `ws.connect_to_server()` switches into bidirectional proxy/interceptor mode."
  },
  {
    "id": "pw-08-q3",
    "question": "An engineer uses `page.clock.fast_forward('60:00')` and asserts that clicking `'Fetch Account Balance'` causes the live Go backend API to return `401 Token Expired`. Instead, the Go API returns `200 OK`! Why?",
    "options": [
      "Go ignores JWT `exp` claims by default",
      "`page.clock` virtualizes time **only inside the browser's JS runtime** (`Date.now`, `setTimeout`); the separate Go backend container's OS clock only elapsed ~15ms, so the 1-hour JWT was still valid on the server! Server-side `401` handling in UI tests should be triggered either via a short-lived test JWT (`TTL=1s`) or `page.route` returning `401`",
      "`fast_forward` resets cookies",
      "JWTs use UTC whereas `page.clock` uses local time"
    ],
    "answerIndex": 1,
    "explanation": "Understanding seam boundaries prevents false assumptions: `page.clock` controls client-side JS timers and client-side `Date.now()` checks, never remote microservice system clocks."
  }
]
```
