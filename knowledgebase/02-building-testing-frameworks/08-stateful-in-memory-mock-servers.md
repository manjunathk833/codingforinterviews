---
slug: fw-08-stateful-in-memory-mock-servers
course_id: 02-building-testing-frameworks
track: system-design
volume: "02. Zero to Mastery: Building Testing Frameworks"
module_number: 3
module_title: "Module 3: Concurrency, Resilience & Stateful Doubles (MiniTest v0.6 → v0.8)"
chapter_number: 8
level_tag: "🌱 Foundations → Staff Architecture"
title: "Build MiniTest v0.8: Stateful In-Memory Mock Servers (`FakeStripeServer`)"
summary: "How do you test that your Smart Retry from Ch 07 actually survives two `503` crashes followed by `200 OK`? Real Stripe won't crash on command! Build a Stateful In-Memory Mock Server with fault queues and request journals!"
reading_time_minutes: 15
video_url: ""
visualizer_id: fw-retry-mock-sdk
lab_path: frameworks/design-challenges/05-microservice-mocking
tags: ["testing-frameworks", "mock-servers", "wiremock", "stateful-fakes", "fault-injection", "request-journal", "minitest"]
---

# Build MiniTest v0.8: Stateful In-Memory Mock Servers (`FakeStripeServer`)

```json continuity
{
  "previously": "In Ch 07, we built a Smart Retry + Token-Bucket client in `MiniTest v0.7` that retries `503/429` errors and fails fast on `AssertionError`.",
  "painPoint": "Now how do we TEST that our Smart Retry actually works when Stripe returns two `503`s followed by a `200 OK`? We can't call real Stripe on the internet and ask Stripe to crash twice on command—and mocking internal Python methods skips real HTTP headers and JSON serialization!",
  "unlock": "Build a Stateful In-Memory Mock Server (`FakeStripeServer`) for `MiniTest v0.8` that replays programmed fault sequences (`[503, 503, 200]`), tracks state (`PENDING -> PAID`), and records every request in a Journal!"
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Slide 1 / 4 · Why Real Sandboxes Can't Test Chaos",
    "caption": "Suppose you want to verify that AeroCart survives when Stripe returns `503`, `503`, and then `200 OK`. You can't call `api.stripe.com` and say 'Hey Stripe, please crash twice for my test!'",
    "code": "# How do we force this exact sequence on demand in 5ms?\n# Attempt 1 -> 503 Busy\n# Attempt 2 -> 503 Busy\n# Attempt 3 -> 200 OK {'status': 'PAID'}",
    "nodes": ["Test Needs [503, 503, 200]", "Real Stripe Won't Crash on Command", "Need Local Fake Server!"]
  },
  {
    "time": "0:25",
    "badge": "Slide 2 / 4 · Programmable Fault Queue (`[503, 503, 200]`)",
    "caption": "Our `FakeStripeServer` holds a simple queue of responses! Call #1 pops `503`, Call #2 pops `503`, and Call #3 pops `200 OK`—letting us test our Ch 07 Smart Retry deterministically in 1 millisecond!",
    "code": "fake_stripe.enqueue_responses([503, 503, 200])\nres = resilient_client.charge(36000)   # Pops 503 -> 503 -> 200!\nassert res == 200",
    "nodes": ["Queue: [503, 503, 200]", "Retry #1 & #2 Pop 503", "Attempt #3 Pops 200 OK!"]
  },
  {
    "time": "0:50",
    "badge": "Slide 3 / 4 · Stateful Memory (`POST /charge` -> `GET /charge/1`)",
    "caption": "Unlike a dumb stub that always returns the same hardcoded JSON, a Stateful Fake remembers what you created (`POST /charges` saves `ch_1`, so `GET /charges/ch_1` actually finds `ch_1`)!",
    "code": "fake_stripe.post_charge('ch_1', amount=36000)  # Saves to in-memory dict!\nassert fake_stripe.get_charge('ch_1')['status'] == 'PAID'",
    "nodes": ["POST /charges (Saves ch_1)", "In-Memory State Map", "GET /charges/ch_1 (Returns ch_1)"]
  },
  {
    "time": "1:15",
    "badge": "Slide 4 / 4 · The Request Journal (Security Camera Log)",
    "caption": "How do we prove our client actually sent the same `Idempotency-Key` header on all 3 retry attempts? Check `fake_stripe.journal`—which records every incoming request!",
    "code": "assert len(fake_stripe.journal) == 3\nassert fake_stripe.journal[0]['headers']['Idempotency-Key'] == 'key-99'",
    "nodes": ["3 Retry Attempts", "Request Journal Log", "Assert Headers & Count == 3!"]
  }
]
```

```json pretraining
[
  {
    "term": "Programmable Fault Queue",
    "formula": "Queue `[503, 503, 200]` -> Pops 1 status per call",
    "meaning": "A list of scripted responses loaded into a mock server before a test so Call #1 fails, Call #2 fails, and Call #3 succeeds on command."
  },
  {
    "term": "Stateful Fake vs. Dumb Stub",
    "formula": "Dumb Stub: Always returns X | Stateful Fake: Remembers `POST` -> `GET`",
    "meaning": "A Stateful Fake stores data in memory during a test (like a mini dictionary database) so creating an order actually makes that order show up when you fetch it next."
  },
  {
    "term": "Request Journal (Call Spy)",
    "formula": "`server.journal` -> List of every recorded request",
    "meaning": "A security-camera log inside the mock server that records the exact method, URL, headers, and JSON body of every call your app made."
  },
  {
    "term": "Loopback Wire Mock vs. `unittest.mock.patch`",
    "formula": "Real HTTP to `127.0.0.1` >> Patching internal functions",
    "meaning": "Talking to a local mock server tests your real HTTP client, JSON serializer, and headers—whereas patching a Python function skips the network layer completely."
  }
]
```

```json poe
{
  "question": "To test AeroCart's Stripe payment client, a developer uses `unittest.mock.patch('aerocart.stripe_client.post', return_value={'status': 'paid'})`. The test passes! The next day in production, every payment fails with `TypeError: Object of type Decimal is not JSON serializable`. Why did the test miss this?",
  "options": [
    "Because `Decimal` only breaks on Fridays",
    "Because `mock.patch` replaced the entire `post()` method in Python memory—so the test completely skipped converting the payload to JSON and sending HTTP headers! A local Mock Server forces the real HTTP client and JSON serializer to run",
    "Because Stripe does not accept JSON",
    "Because `mock.patch` is too slow"
  ],
  "answerIndex": 1,
  "explanation": "Monkey-patching an internal method (`mock.patch`) bypasses your real JSON serialization, auth headers, URL formatting, and timeout configuration! Sending real HTTP requests to a local in-memory mock server exercises 100% of your client code."
}
```

## 🌱 Step 1: Plain-English Story — Why Movie Stunt Doubles Beat Real Explosions!

In **Chapter 07**, we built a really cool **Smart Retry Client** for `MiniTest v0.7` that retries `HTTP 503` errors up to 3 times and attaches an `Idempotency-Key` header.
Now comes the million-dollar question: **How do we test our Smart Retry Client?**

Think about what we need to happen during the test:
1. On **Attempt #1**, the payment server must return **`503 Service Unavailable`**.
2. On **Attempt #2**, the payment server must return **`503 Service Unavailable`** again.
3. On **Attempt #3**, the payment server must return **`200 OK`**, and we need to verify that **all 3 attempts carried the exact same `Idempotency-Key` header**!

Can we run that test against the **real Stripe sandbox on the internet**?
No way! Real Stripe won't return two `503`s and a `200` on command whenever your test asks for it!
And what if we just replace our Python function with `mock.patch`? Then our HTTP client never even runs!

```mermaid
flowchart LR
  Client["AeroCart Resilient Client"] -->|"Attempt 1: POST /charge"| Fake["FakeStripeServer (Queue: [503, 503, 200])"]
  Fake -->|"1st & 2nd Call: Pop 503"| Client
  Fake -->|"3rd Call: Pop 200 + Record in Journal"| Verify["Test Asserts: journal.length == 3!"]
```

**The solution: Build a `FakeStripeServer` (a Movie Stunt Double!) right inside `MiniTest v0.8`!**
Our `FakeStripeServer` has **three superpowers**:
1. **A Fault Queue (`[503, 503, 200]`)**: You load a script of responses before the test, and it pops one response per call.
2. **A Memory Notebook (`state`)**: When you `POST` a charge, it remembers it so a follow-up `GET` can read it back.
3. **A Security Camera (`journal`)**: Every request that hits the server is saved in `server.journal`, so your test can assert `len(server.journal) == 3` and inspect every header!

## 🔨 Step 2: First Lines of Code — Build `FakeStripeServer` in 19 Lines!

Look how satisfying this is: in **19 lines of pure Python**, we build `FakeStripeServer` with a **Fault Queue (`responses`)**, **Stateful Storage (`charges`)**, and a **Request Journal (`journal`)**—and use it to test a `[503, 503, 200]` retry sequence!

```python
class FakeStripeServer:
    def __init__(self, scripted_statuses: list = None):
        self.queue = list(scripted_statuses or [])  # 1. Programmable Fault Queue
        self.charges = {}                           # 2. Stateful In-Memory DB
        self.journal = []                           # 3. Request Journal (Spy Log)

    def post_charge(self, charge_id: str, amount: int, headers: dict) -> tuple:
        self.journal.append({"id": charge_id, "amount": amount, "headers": headers})
        status = self.queue.pop(0) if self.queue else 200
        if status == 200:
            self.charges[charge_id] = {"status": "PAID", "amount": amount}
        return status, self.charges.get(charge_id, {"error": "Service Busy"})


# --- Test a [503, 503, 200] retry loop against our FakeStripeServer! ---
fake = FakeStripeServer(scripted_statuses=[503, 503, 200])
for _ in range(3):
    code, body = fake.post_charge("ch_99", 36000, {"Idempotency-Key": "ik-1"})
    if code == 200:
        break

assert code == 200 and fake.charges["ch_99"]["status"] == "PAID"
assert len(fake.journal) == 3 and fake.journal[0]["headers"]["Idempotency-Key"] == "ik-1"
```

### Java 17 Equivalent (`FakeStripeServer.java` — Mirrors WireMock Scenarios & Request Journal)

```java
import java.util.*;

public class FakeStripeServer {
    public record RecordedRequest(String id, int amount, Map<String, String> headers) {}

    private final Deque<Integer> statusQueue = new ArrayDeque<>();
    public final Map<String, String> charges = new HashMap<>();
    public final List<RecordedRequest> journal = new ArrayList<>();

    public FakeStripeServer(List<Integer> scriptedStatuses) {
        statusQueue.addAll(scriptedStatuses);
    }

    public int postCharge(String id, int amount, Map<String, String> headers) {
        journal.add(new RecordedRequest(id, amount, headers));
        int status = statusQueue.isEmpty() ? 200 : statusQueue.pollFirst();
        if (status == 200) charges.put(id, "PAID:" + amount);
        return status;
    }

    public static void main(String[] args) {
        FakeStripeServer fake = new FakeStripeServer(List.of(503, 503, 200));
        int status = 503;
        while (status != 200) {
            status = fake.postCharge("ch_99", 36000, Map.of("Idempotency-Key", "ik-1"));
        }
        assert fake.journal.size() == 3;
        assert fake.charges.get("ch_99").equals("PAID:36000");
    }
}
```

**Look how much power you just unlocked in 19 lines!** Without needing Wi-Fi or waiting on an external sandbox, your test proved that:
1. Two `503`s were retried,
2. The third call succeeded (`200`), and
3. `len(fake.journal) == 3` with `"Idempotency-Key": "ik-1"` on every single call!

## ⚡ Step 3: Where It Breaks in Real Life — Async Polling (`PENDING -> PROCESSING -> COMPLETED`) & Contract Drift

As soon as you use Mock Servers on real microservice teams, two deeper challenges appear:

1. **Challenge 1: Testing Polling Workflows (`PENDING -> COMPLETED`)**
   Many modern APIs (like generating an airline ticket PDF or running an AI job) don't finish in one call! Your app calls `POST /tickets`, and then polls `GET /tickets/1` three times:
   - Poll #1 returns `{"state": "PENDING"}`
   - Poll #2 returns `{"state": "PROCESSING"}`
   - Poll #3 returns `{"state": "COMPLETED", "pdf_url": "..."}`
   A static mock that only returns one canned JSON can't test polling! Our **Stateful Mock Server** solves this by advancing a **State Machine** on each call (just like **WireMock Scenarios**)!
2. **Challenge 2: "Mock Drift" (When the Fake Server Lies!)**
   What if Stripe renames `"amount"` to `"amount_cents"` in their real API, but your `FakeStripeServer` still accepts `"amount"`? Your tests stay 100% green while production breaks! Staff teams prevent Mock Drift by **validating every incoming request in `FakeStripeServer` against the shared OpenAPI / JSON Schema contract**!

```json contrast
{
  "title": "Monkey-Patched Stubs vs. Stateful Schema-Validated Wire Mock Server",
  "naiveTitle": "`unittest.mock.patch` + Static Canned JSON",
  "naiveMetric": "Skips Real HTTP/JSON · Cannot Test Retries or Polling",
  "naivePoints": [
    "Replaces internal Python/Java functions in memory, skipping JSON serialization, HTTP headers, and timeouts",
    "Returns the exact same static response on every call—unable to test `[503, 503, 200]` retries or `PENDING -> COMPLETED` polling",
    "Accepts any invalid payload dictionary without checking required schema fields ('Mock Drift')"
  ],
  "staffTitle": "Stateful Mock Server + Fault Queues + Request Journal + Schema Check",
  "staffMetric": "100% Wire Fidelity · Deterministic Chaos in 2ms",
  "staffPoints": [
    "Runs at the HTTP/transport boundary so real serialization, headers (`Idempotency-Key`), and retry loops execute",
    "Supports programmable fault queues (`[503, 503, 200]`) and stateful scenario transitions (`PENDING -> COMPLETED`)",
    "Records every request in `journal` for exact count/header assertions and validates request schemas against OpenAPI"
  ]
}
```

Step through the **Stateful Mock Server & Fault Sequence Simulator** below to watch fault queues, state transitions, and request journals in action!

## 🚀 Step 4: Staff Engineer Deep-Dive — State Automaton Model & WireMock / MockServer Mapping

Formally, a **Stateful Mock Server** is a deterministic finite-state transducer (Mealy Machine) over state space $S$, incoming request $r \in \mathcal{R}$, and outgoing response $y \in \mathcal{Y}$:

$$\bigl(s_{k+1},\; y_k\bigr) = \delta\bigl(s_k,\; r_k\bigr), \qquad \text{Journal}_{k+1} = \text{Journal}_k \cup \bigl\{(t_k, r_k, y_k)\bigr\}$$

When testing an idempotent payment endpoint with retry multiplicity $M$:
- Let $k_{\text{idemp}} = r.\text{headers}[\texttt{"Idempotency-Key"}]$.
- If $k_{\text{idemp}}$ has already committed a `200 OK` result $y^*$ in state $s_k$, then for any duplicate retry $r_{k+1}$ carrying the same $k_{\text{idemp}}$, the transition function returns the **exact cached response** $(s_k, y^*)$ without double-charging!

| Feature | Our `MiniTest v0.8` `StatefulMockServer` | Python (`responses` / `respx` / `pytest-httpserver`) | Java 17 (`WireMock` / `MockWebServer`) |
| :--- | :--- | :--- | :--- |
| **Fault Sequence (`[503, 503, 200]`)** | `enqueue_faults(route, [503, 503, 200])` | `respx.route(...).mock(side_effect=[...])` | WireMock `Scenario` (`STARTED -> RETRY_1 -> OK`) or OkHttp `MockWebServer.enqueue()` |
| **Request Journal Spy** | `server.journal_for("/v1/charges")` | `respx.calls` / `responses.calls` | `wireMock.verify(3, postRequestedFor(...))` |
| **Parallel Worker Isolation** | Per-test instance or `X-Test-Tenant` | Ephemeral port `pytest-httpserver` | `new WireMockServer(wireMockConfig().dynamicPort())` |

### Production Blueprint: Stateful Idempotent Mock Server With Polling Scenarios & Journal Verification

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class RecordedCall:
    method: str
    path: str
    headers: Dict[str, str]
    body: Dict[str, Any]
    response_status: int


@dataclass
class StatefulMockServer:
    """
    Production-grade in-memory service double supporting:
    1. Programmable Fault Queues ([503, 503, 200])
    2. Idempotency-Key deduplication (catches double-charge bugs if key is missing!)
    3. Stateful async job polling (PENDING -> PROCESSING -> COMPLETED)
    4. Full Request Journal inspection
    """
    fault_queues: Dict[str, List[int]] = field(default_factory=dict)
    idempotency_store: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    job_states: Dict[str, List[str]] = field(default_factory=dict)
    total_charged_cents: int = 0
    journal: List[RecordedCall] = field(default_factory=list)

    def enqueue_statuses(self, path: str, statuses: List[int]) -> None:
        self.fault_queues[path] = list(statuses)

    def seed_polling_job(self, job_id: str, states: List[str]) -> None:
        self.job_states[job_id] = list(states)

    def handle_request(
        self, method: str, path: str, headers: Dict[str, str], body: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any]]:
        queue = self.fault_queues.get(path, [])
        status = queue.pop(0) if queue else 200

        if status >= 500 or status == 429:
            self.journal.append(RecordedCall(method, path, dict(headers), dict(body), status))
            return status, {"error": f"Simulated HTTP {status}"}

        if method == "POST" and path == "/v1/charges":
            if "amount_cents" not in body or not isinstance(body["amount_cents"], int):
                self.journal.append(RecordedCall(method, path, dict(headers), dict(body), 400))
                return 400, {"error": "Schema violation: integer amount_cents required"}

            idem_key = headers.get("Idempotency-Key")
            if idem_key and idem_key in self.idempotency_store:
                cached = self.idempotency_store[idem_key]
                self.journal.append(RecordedCall(method, path, dict(headers), dict(body), 200))
                return 200, cached

            self.total_charged_cents += body["amount_cents"]
            resp = {"charge_id": f"ch_{len(self.journal) + 1}", "charged_cents": body["amount_cents"]}
            if idem_key:
                self.idempotency_store[idem_key] = resp
            self.journal.append(RecordedCall(method, path, dict(headers), dict(body), 200))
            return 200, resp

        if method == "GET" and path.startswith("/v1/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            states = self.job_states.get(job_id, ["COMPLETED"])
            current_state = states.pop(0) if len(states) > 1 else states[0]
            self.journal.append(RecordedCall(method, path, dict(headers), dict(body), 200))
            return 200, {"job_id": job_id, "state": current_state}

        self.journal.append(RecordedCall(method, path, dict(headers), dict(body), 404))
        return 404, {"error": "Route not found"}
```

### Java 17 Equivalent (Stateful Mock Server With Idempotency & Polling State Machine)

```java
import java.util.*;

public class StatefulWireMockDouble {
    public record CallEntry(String method, String path, Map<String, String> headers, int status) {}

    private final Map<String, Deque<Integer>> faultQueues = new HashMap<>();
    private final Map<String, String> idempotencyStore = new HashMap<>();
    public final List<CallEntry> journal = new ArrayList<>();
    public int totalChargedCents = 0;

    public void enqueueStatuses(String path, List<Integer> statuses) {
        faultQueues.put(path, new ArrayDeque<>(statuses));
    }

    public int handlePostCharge(int amountCents, Map<String, String> headers) {
        Deque<Integer> q = faultQueues.getOrDefault("/v1/charges", new ArrayDeque<>());
        int status = q.isEmpty() ? 200 : q.pollFirst();
        journal.add(new CallEntry("POST", "/v1/charges", Map.copyOf(headers), status));
        if (status != 200) return status;

        String idemKey = headers.get("Idempotency-Key");
        if (idemKey != null && idempotencyStore.containsKey(idemKey)) {
            return 200; // Idempotent replay: do NOT add to totalChargedCents again!
        }
        totalChargedCents += amountCents;
        if (idemKey != null) idempotencyStore.put(idemKey, "PAID");
        return 200;
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Shared Mock Server State Bleed Across Parallel Tests!**
> If 8 parallel workers (`gw0..gw7`) share a single global `WireMock` server and Worker `gw0` calls `wireMock.resetAll()` in `@AfterEach` (or enqueues `[503, 503]` onto `/v1/charges`), **`gw0` will accidentally inject `503` faults into `gw1`'s test!**
> **Two Staff Solutions**: Either spin up an isolated mock server per worker on an ephemeral port (`dynamicPort()`), OR scope every stub rule and journal query to a per-test header (`withHeader("X-Test-Correlation-ID", equalTo(testId))`)!

**Module 3 Complete — Up Next in Module 4 (Chapter 09)**: Our `MiniTest v0.8` framework is now fast, parallel, resilient, and backed by stateful mock servers! But when a test fails on CI at 2 AM, all `MiniTest` prints is a plain `print("✗ FAIL")` line in the console! How do real frameworks generate rich **Allure / JUnit XML Reports, failure-only trace attachments, copy-paste `cURL` reproducers, and OpenTelemetry spans**? Let's build `MiniTest v0.9` in Chapter 09!

```json quiz
[
  {
    "id": "fw-08-q1",
    "question": "Why is testing an HTTP client against a local Stateful Mock Server (`FakeStripeServer` / `WireMock`) much safer than using `unittest.mock.patch` to replace the Python method?",
    "options": [
      "Because `unittest.mock.patch` requires an internet connection",
      "Because `mock.patch` skips your real HTTP client, JSON serialization, auth headers, and timeout logic—whereas a local Mock Server forces the real client code to serialize payloads and send headers over the wire",
      "Because Mock Servers run inside the browser",
      "Because `mock.patch` cannot return dictionaries"
    ],
    "answerIndex": 1,
    "explanation": "Mocking at the network/HTTP boundary preserves high fidelity for serialization, headers, retries, and status code handling."
  },
  {
    "id": "fw-08-q2",
    "question": "After running a test where `ResilientTestClient` recovers from `[503, 503, 200]`, why should your test also assert `len(fake_stripe.journal) == 3`?",
    "options": [
      "To clear the mock server's memory",
      "To prove that the client actually made 3 attempts (2 retries + 1 success) and carried the expected headers (like `Idempotency-Key`) on every attempt, rather than succeeding on call #1 by mistake",
      "Because Python lists must always have length 3",
      "To slow down the test"
    ],
    "answerIndex": 1,
    "explanation": "Inspecting the Request Journal verifies the exact call multiplicity, retry behavior, and outbound headers."
  },
  {
    "id": "fw-08-q3",
    "question": "What happens if 8 parallel test threads share one `WireMock` server instance and each test calls `wireMock.resetAll()` in its teardown?",
    "options": [
      "It makes WireMock 8x faster",
      "Test A's `resetAll()` wipes out Test B's stub rules and request journal while Test B is still running! Either give each worker its own ephemeral-port server or scope stubs by a unique `X-Test-ID` header",
      "WireMock automatically ignores `resetAll()` in parallel mode",
      "The operating system blocks port 80"
    ],
    "answerIndex": 1,
    "explanation": "Global `resetAll()` on a shared mock server destroys active stubs and journals for concurrent tests; isolate per worker port or partition stubs by header."
  }
]
```
