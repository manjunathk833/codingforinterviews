---
slug: api-08-async-saga-and-webhook-verification
course_id: 04-api-and-api-automation
track: core-cs
volume: "04. Zero to Mastery: API & API Automation"
module_number: 3
module_title: "Module 3: Multi-Protocol (GraphQL, gRPC) & Async Sagas"
chapter_number: 8
level_tag: "Senior → Staff"
title: "Asynchronous Saga Polling (202 Accepted) & HMAC-SHA256 Webhook Verification"
summary: "Testing distributed eventual consistency without Thread.sleep(): 202 Accepted + Location status state machines, bounded deadline polling with terminal-state short-circuiting on AeroCart PENDING -> CONFIRMED | COMPENSATED sagas, and constant-time HMAC-SHA256 webhook signature & replay verification."
reading_time_minutes: 22
visualizer_id: api-graphql-grpc-saga
lab_path: frameworks/api-automation/pytest-requests-python
tags: ["api-automation", "async-saga", "202-accepted", "webhooks", "hmac-sha256", "awaitility", "eventual-consistency"]
---

# Asynchronous Saga Polling (202 Accepted) & HMAC-SHA256 Webhook Verification

```json pretraining
[
  {
    "term": "202 Accepted Contract",
    "formula": "POST /v1/checkout -> 202 + Location: /v1/operations/{op_id}",
    "meaning": "Decouples durable command ingestion from multi-step downstream Saga execution (Inventory -> Payment -> Fulfillment)."
  },
  {
    "term": "Terminal Short-Circuit",
    "formula": "Stop Poll Immediately on status ∈ {CONFIRMED, FAILED_COMPENSATED}",
    "meaning": "Never wait out a 15s polling timeout when a saga deterministically enters a terminal compensated failure state at t=80ms!"
  },
  {
    "term": "HMAC Replay Binding",
    "formula": "sig = HMAC_SHA256(secret, timestamp + \".\" + raw_utf8_bytes)",
    "meaning": "Signing timestamp + exact unparsed wire bytes prevents both payload tampering and captured-packet replay (>300s skew rejected)."
  },
  {
    "term": "Constant-Time Compare",
    "formula": "hmac.compare_digest(expected_mac, actual_mac)  // O(L) Fixed",
    "meaning": "Eliminates byte-by-byte early-exit timing side channels that otherwise let attackers forge HMACs in 256 * 32 probes."
  }
]
```

```json poe
{
  "question": "A webhook receiver parses the incoming JSON body into a Python dict / Java Map, re-serializes it via json.dumps(body), and computes HMAC-SHA256(secret, timestamp + '.' + json_str) using standard '==' string equality. Why does this break legitimate Stripe/AeroCart webhooks in production AND introduce a cryptographic vulnerability?",
  "options": [
    "SHA-256 cannot hash UTF-8 emojis",
    "1) JSON round-tripping alters whitespace and key ordering, invalidating the sender's cryptographic MAC over raw wire bytes; 2) standard '==' short-circuits on the first mismatched byte, leaking a timing side channel instead of constant-time hmac.compare_digest / MessageDigest.isEqual",
    "Webhooks require RSA-4096 instead of symmetric HMAC",
    "HTTP/2 compresses webhook signatures before application delivery"
  ],
  "answerIndex": 1,
  "explanation": "Webhook MACs are computed over the exact raw HTTP request byte array before JSON parsing; re-serializing parsed objects changes key order or float formatting, while '==' leaks byte-prefix timing."
}
```

## 1. Event-Driven Sagas (`202 Accepted`) & Why `sleep(5)` Ruins CI Suites

Modern commerce architectures (`AeroCart` Checkout) avoid distributed two-phase commits (`2PC`) across microservices. Instead, `POST /v1/checkouts` writes an Outbox command, returns **`202 Accepted`** in `9ms` with `Location: /v1/checkouts/chk-88/status` and `Retry-After: 1`, and progresses asynchronously through a **Choreographed or Orchestrated Saga**:

`PENDING` $\to$ `INVENTORY_RESERVED` $\to$ `PAYMENT_CAPTURED` $\to$ **`CONFIRMED`** *(or on payment decline: `PAYMENT_FAILED` $\to$ **`COMPENSATED`** releasing the reserved inventory!)*

Testing async sagas with `time.sleep(5.0)` creates the classic dual failure: if the runner finishes in `90ms`, you waste `4.91s` on every single test (`500 tests = 41 minutes` of pure idle CPU); if Kafka consumer rebalance takes `5.2s` once a week, the test flakes! Staff engineers use **bounded monotonic deadline polling with terminal-state short-circuiting** AND **ephemeral local callback listeners** for webhook push verification.

```mermaid
sequenceDiagram
  participant Test as Saga & Webhook Harness
  participant API as AeroCart Checkout API
  participant Saga as Outbox + Kafka Orchestrator
  participant Hook as Ephemeral Local Webhook Sink

  Test->>API: POST /v1/checkouts (Idempotency-Key: k-9)
  API-->>Test: 202 Accepted + Location: /v1/operations/op-42
  Saga->>Saga: Reserve Stock -> Capture Card -> Emit Event
  Saga->>Hook: POST /webhooks (X-Signature: t=1731...,v1=8a4f...)
  Test->>API: Poll Location (50ms->100ms->200ms) Until Terminal
  API-->>Test: 200 OK {status: "CONFIRMED", orderId: "ord-77"}
  Test->>Hook: Assert Constant-Time HMAC + Replay Protection + Event ID
```

---

## 2. Polling Anti-Patterns vs. Bounded Saga Harnesses & Webhook Security

```json contrast
{
  "title": "Fixed sleep(5) & Naive Webhook Receivers vs Terminal Saga Pollers & HMAC Guards",
  "naiveTitle": "time.sleep(5) + '==' Parsed JSON MAC",
  "naiveMetric": "41m Wasted CI · Flaky Rebalances · Replay Bug",
  "naivePoints": [
    "Hardcodes sleep(5) before GET /orders: wastes 98% wall-clock time on healthy runs and flakes under GC/Kafka jitter",
    "Keeps polling until timeout even when saga already transitioned to terminal FAILED_COMPENSATED at 60ms",
    "Verifies webhook HMAC without signing the Unix timestamp, allowing attackers to replay a valid $50 refund webhook 100 times!"
  ],
  "staffTitle": "Terminal-Aware Poller + Timestamped Raw HMAC",
  "staffMetric": "95ms Median Poll · 0 Replay / Timing Leaks",
  "staffPoints": [
    "Polls with capped backoff (50ms -> 400ms), exits the instant CONFIRMED arrives, and fails-fast on COMPENSATED",
    "Verifies compensating transaction invariant: payment failure MUST restore reserved SKU inventory back to pre-saga count",
    "Signs 't.<raw_bytes>', enforces |now - t| <= 300s clock window, deduplicates event_id, and uses compare_digest()"
  ]
}
```

| Verification Dimension | `202` Status Resource Polling | Outbound Webhook Delivery | Mandatory Failure-Mode Test |
| :--- | :--- | :--- | :--- |
| **Transport Contract** | `202 Accepted` + `Location` + `Retry-After` | `POST` to consumer URL within `5s` timeout | Webhook consumer returns `500` $\to$ verify sender retries with exponential backoff |
| **Deduplication** | `op_id` is immutable & idempotent to `GET` | Consumer deduplicates by unique `event_id` (`evt_...`) | Deliver identical `event_id` twice $\to$ assert consumer applies side effect **once** |
| **Security & Integrity** | Tenant-scoped `Location` (`BOLA` protected) | `HMAC-SHA256(secret, f"{ts}.{raw_body}")` + dual-key rotation (`v1=...`) | Send timestamp `t = now - 600s` with valid HMAC $\to$ assert `401` replay rejection |
| **Saga Compensation** | Terminal state exposes `failureReason` + `compensated: true` | Emits `checkout.compensated` event | Trigger `card_declined` fixture $\to$ assert stock count returns to initial baseline |

---

## 3. Dual-Language Production Blueprints: Terminal Saga Poller & Webhook Verifier

### Python 3 Blueprint: Terminal-State Saga Poller + Constant-Time Webhook HMAC Verifier
```python
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
import time
from typing import Callable, Mapping, Set, TypeVar

T = TypeVar("T")


class SagaCompensationError(AssertionError):
    """Raised immediately (zero wasted polling) when an async saga hits a terminal failure state."""


def poll_saga_until_terminal(
    fetch_fn: Callable[[], T],
    extract_status: Callable[[T], str],
    success_states: Set[str],
    terminal_failure_states: Set[str],
    deadline_sec: float = 8.0,
    initial_interval_sec: float = 0.05,
    max_interval_sec: float = 0.50,
    clock: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
) -> T:
    """
    Deterministic bounded poller for 202 Accepted sagas:
    - Returns immediately upon observing any state in `success_states`.
    - Aborts immediately (no wasted timeout wait!) upon any state in `terminal_failure_states`.
    """
    start = clock()
    deadline = start + deadline_sec
    interval = initial_interval_sec
    last_snapshot: T | None = None
    attempts = 0

    while True:
        attempts += 1
        last_snapshot = fetch_fn()
        state = extract_status(last_snapshot)
        if state in success_states:
            return last_snapshot
        if state in terminal_failure_states:
            raise SagaCompensationError(
                f"Saga aborted in terminal failure state '{state}' on poll #{attempts}: {last_snapshot!r}"
            )
        now = clock()
        if now >= deadline:
            raise TimeoutError(
                f"Saga stayed non-terminal ('{state}') after {deadline_sec:.2f}s ({attempts} polls): {last_snapshot!r}"
            )
        sleep_for = min(interval, max(0.001, deadline - now))
        sleeper(sleep_for)
        interval = min(max_interval_sec, interval * 1.6)


@dataclass(frozen=True)
class WebhookVerificationResult:
    valid: bool
    reason: str


class WebhookSecurityVerifier:
    """Stripe / AeroCart style timestamped raw-body HMAC-SHA256 + replay deduplicator."""

    def __init__(self, active_secrets: list[str], tolerance_sec: int = 300) -> None:
        self._secrets = [s.encode("utf-8") for s in active_secrets]
        self._tolerance = tolerance_sec
        self._processed_event_ids: set[str] = set()

    @staticmethod
    def sign_payload(secret: str, timestamp_sec: int, raw_body: bytes) -> str:
        signed_bytes = f"{timestamp_sec}.".encode("ascii") + raw_body
        digest = hmac.new(secret.encode("utf-8"), signed_bytes, hashlib.sha256).hexdigest()
        return f"t={timestamp_sec},v1={digest}"

    def verify_and_deduplicate(
        self, signature_header: str, raw_body: bytes, event_id: str, now_epoch: int
    ) -> WebhookVerificationResult:
        parts: Mapping[str, list[str]] = {}
        for item in signature_header.split(","):
            if "=" in item:
                k, v = item.strip().split("=", 1)
                parts.setdefault(k, []).append(v)

        if "t" not in parts or "v1" not in parts:
            return WebhookVerificationResult(False, "MALFORMED_SIGNATURE_HEADER")

        ts = int(parts["t"][0])
        if abs(now_epoch - ts) > self._tolerance:
            return WebhookVerificationResult(False, "TIMESTAMP_OUTSIDE_REPLAY_WINDOW")

        signed_payload = f"{ts}.".encode("ascii") + raw_body
        matched = False
        for secret_bytes in self._secrets:
            expected = hmac.new(secret_bytes, signed_payload, hashlib.sha256).hexdigest()
            for candidate in parts["v1"]:
                if hmac.compare_digest(expected, candidate):
                    matched = True
        if not matched:
            return WebhookVerificationResult(False, "HMAC_MISMATCH")

        if event_id in self._processed_event_ids:
            return WebhookVerificationResult(True, "DUPLICATE_EVENT_NOOP")
        self._processed_event_ids.add(event_id)
        return WebhookVerificationResult(True, "ACCEPTED")
```

### Java 17 Blueprint: Terminal-Aware Saga Poller & Constant-Time `MessageDigest.isEqual` HMAC
```java
package com.aerocart.api.saga;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.HexFormat;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;
import java.util.function.Supplier;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class AsyncSagaAndWebhookHarness {

    public static <T> T awaitSagaTerminal(
            Supplier<T> poller,
            Function<T, String> statusExtractor,
            Set<String> successStates,
            Set<String> terminalFailureStates,
            Duration timeout) throws InterruptedException {
        long deadlineNs = System.nanoTime() + timeout.toNanos();
        long sleepMs = 50L;
        int polls = 0;

        while (true) {
            polls++;
            T snapshot = poller.get();
            String state = statusExtractor.apply(snapshot);
            if (successStates.contains(state)) {
                return snapshot;
            }
            if (terminalFailureStates.contains(state)) {
                throw new AssertionError("Saga failed terminally in state=" + state + " on poll #" + polls);
            }
            long remainingMs = (deadlineNs - System.nanoTime()) / 1_000_000L;
            if (remainingMs <= 0) {
                throw new AssertionError("Saga timed out in non-terminal state=" + state + " after " + polls + " polls");
            }
            Thread.sleep(Math.min(sleepMs, Math.max(1L, remainingMs)));
            sleepMs = Math.min(500L, (long) (sleepMs * 1.6));
        }
    }

    private final byte[] webhookSecret;
    private final long maxSkewSeconds;
    private final Set<String> seenEventIds = ConcurrentHashMap.newKeySet();

    public AsyncSagaAndWebhookHarness(String secret, long maxSkewSeconds) {
        this.webhookSecret = secret.getBytes(StandardCharsets.UTF_8);
        this.maxSkewSeconds = maxSkewSeconds;
    }

    public boolean verifyWebhookConstantTime(
            long headerTimestampSec, String hexSignature, byte[] rawWireBytes, String eventId, long nowEpochSec)
            throws Exception {
        if (Math.abs(nowEpochSec - headerTimestampSec) > maxSkewSeconds) {
            return false; // Reject replay outside 300s window
        }
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(webhookSecret, "HmacSHA256"));
        mac.update((headerTimestampSec + ".").getBytes(StandardCharsets.US_ASCII));
        byte[] expectedDigest = mac.doFinal(rawWireBytes);
        byte[] providedDigest = HexFormat.of().parseHex(hexSignature);

        // Strictly constant-time comparison preventing byte-prefix timing attacks
        if (!MessageDigest.isEqual(expectedDigest, providedDigest)) {
            return false;
        }
        return seenEventIds.add(eventId); // True on first delivery, false on duplicate retry
    }
}
```

> [!WARNING] **Staff Interview Gotcha — Zero-Downtime Webhook Secret Rotation (`v1=sigA,v1=sigB`) & At-Least-Once Delivery:** In production, rotating a leaked or expiring webhook signing secret without dropping live customer webhooks requires **dual-signature overlapping windows**: the webhook sender emits **two `v1=` signatures** in the same header (`t=1731200000,v1=<old_key_hmac>,v1=<new_key_hmac>`) for 24 hours while consumers accept a request if **any** active key matches in constant time. Furthermore, webhook delivery is strictly **At-Least-Once**—if your receiver takes `5.1s` and the sender times out at `5.0s`, the sender **will** redeliver the exact same `event_id`. Consumers must commit `(event_id)` in a unique database constraint inside the same transaction as business side effects!

---

## 4. Scenario Retrieval-Practice Mastery Gate

```json quiz
[
  {
    "id": "api-08-q1",
    "question": "In Java Awaitility or a custom Python saga poller, what happens if you write await().atMost(15, SECONDS).until(() -> getOrder(id).status().equals(\"CONFIRMED\")) WITHOUT checking for terminal failure states like \"FAILED_COMPENSATED\"?",
    "options": [
      "Awaitility automatically detects enum names containing FAILED",
      "Every negative checkout test (or broken payment bug that compensates in 40ms) pointlessly hammers the API for the full 15.0 seconds before throwing a misleading ConditionTimeoutException instead of immediately reporting the terminal compensation reason",
      "HTTP 202 automatically converts to 404 after 2 polls",
      "The JVM garbage-collects the HTTP socket mid-poll"
    ],
    "answerIndex": 1,
    "explanation": "Polling predicates must distinguish transient in-progress states (PENDING, RESERVING) from terminal failure states (FAILED_COMPENSATED) to fail fast with clear diagnostics."
  },
  {
    "id": "api-08-q2",
    "question": "Why is signing ONLY the raw JSON body (HMAC_SHA256(secret, raw_body)) without prepending the Unix timestamp ('t.<raw_body>') a serious webhook security flaw even when the payload includes an 'event_id'?",
    "options": [
      "SHA-256 requires an integer prefix to initialize its Merkle-Damgard IV",
      "If the consumer's event_id deduplication cache uses a bounded Redis TTL (e.g., 24 hours), an attacker who captures a signed payload can replay the exact valid signature 25 hours later once the Redis TTL expires—bounding |now - t| <= 300s closes the replay window permanently",
      "JSON bodies shorter than 64 bytes cannot be hashed",
      "TLS 1.3 strips headers lacking Unix timestamps"
    ],
    "answerIndex": 1,
    "explanation": "Cryptographically binding the timestamp inside the HMAC input lets the receiver statelessly reject any packet older than 5 minutes, allowing the Redis event_id deduplication TTL to remain tiny (e.g., 10 minutes) with zero replay risk."
  },
  {
    "id": "api-08-q3",
    "question": "During an AeroCart checkout saga test, Inventory reserves 2 units of SKU-99 (stock drops 10 -> 8), and then the mocked Payment service returns 'card_declined'. What TWO assertions are required to prove Saga correctness?",
    "options": [
      "Assert HTTP 202 on checkout and HTTP 200 on health check",
      "1) The checkout operation reaches terminal state COMPENSATED (not stuck in INVENTORY_RESERVED), AND 2) querying Inventory proves compensating action restored SKU-99 available stock back from 8 to 10",
      "Assert PostgreSQL rolled back via XA two-phase commit",
      "Assert Kafka deleted the topic partition"
    ],
    "answerIndex": 1,
    "explanation": "A Saga's defining correctness invariant is backward recovery via compensating transactions—leaking permanently locked inventory on declined cards is a classic production P1 bug."
  }
]
```
