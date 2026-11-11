---
slug: api-07-grpc-protobuf-framing-and-deadlines
course_id: 04-api-and-api-automation
track: core-cs
volume: "04. Zero to Mastery: API & API Automation"
module_number: 3
module_title: "Module 3: Multi-Protocol (GraphQL, gRPC) & Async Sagas"
chapter_number: 7
level_tag: "Beginner → Staff"
title: "gRPC Internals: Protobuf Wire Framing, Schema Evolution & Deadline Propagation"
summary: "Protocol Buffers Tag-Length-Value varint bit-packing, backward/forward-compatible reserved field evolution, HTTP/2 5-byte length-prefixed gRPC frames and grpc-status trailers, unary vs bidirectional streaming verification, and mandatory deadline propagation."
reading_time_minutes: 23
visualizer_id: api-graphql-grpc-saga
lab_path: core-cs/computer-networks/01-tcp-tls-and-proxy-inspector
tags: ["api-automation", "grpc", "protobuf", "varint", "http2-trailers", "deadlines", "schema-evolution"]
---

# gRPC Internals: Protobuf Wire Framing, Schema Evolution & Deadline Propagation

```json continuity
{
  "previously": "In Chapter 06, we upgraded AeroClient v0.6 to validate GraphQL partial-error envelopes, AST depth/alias limits, and DataLoader O(1) SQL span budgets.",
  "painPoint": "Behind AeroCart's GraphQL gateway, our internal Pricing, Inventory, and Payment microservices communicate over binary gRPC (HTTP/2 + Protocol Buffers). Yesterday, a developer reused a deleted Protobuf field number (#5) and forgot to set a gRPC call deadline—corrupting live binary prices and hanging all 64 worker threads when PaymentLedger slowed down!",
  "unlock": "We will upgrade AeroClient to v0.7 with a binary Protobuf wire-frame inspector, a CI schema-evolution gate that catches reused field numbers, and mandatory per-call gRPC deadline propagation."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "1. Binary Numbered Tags",
    "caption": "Why is gRPC 5x faster than JSON? Because Protobuf never sends bulky field names like 'total_cents' over the network—it only sends tiny integer field numbers!",
    "code": "JSON (17B): {\"total_cents\":150}\nProtobuf (3B): [tag #1: 0x08] [varint: 0x96 0x01]"
  },
  {
    "time": "0:25",
    "badge": "2. First 5-Byte Frame",
    "caption": "In AeroClient v0.7, our starter code packs and unpacks the 5-byte gRPC HTTP/2 frame header (1 compression byte + 4-byte message length) and enforces an explicit RPC timeout.",
    "code": "frame = struct.pack(\">BI\", 0, len(proto_bytes)) + proto_bytes"
  },
  {
    "time": "0:50",
    "badge": "3. Field Reuse & Hang Traps",
    "caption": "If someone deletes field #5 and later reuses #5 for a new field, old pods silently read the new bytes into the old variable! And calling gRPC without a deadline hangs callers forever.",
    "code": "reserved 5; reserved \"legacy_points\";  // Never reuse field numbers!"
  },
  {
    "time": "1:15",
    "badge": "4. Deadlines & Round-Robin",
    "caption": "At Staff scale, AeroClient v0.7 propagates remaining grpc-timeout budgets across microservice hops and configures client-side round_robin load balancing so HTTP/2 doesn't pin one pod.",
    "code": "ManagedChannelBuilder.forTarget(\"dns:///orders:9090\").defaultLoadBalancingPolicy(\"round_robin\")"
  }
]
```

```json pretraining
[
  {
    "term": "Protobuf Wire Tag",
    "formula": "tag_byte = (field_number << 3) | wire_type",
    "meaning": "Instead of sending field names like 'price_cents' in every message, Protobuf replaces the name with a tiny integer number (#1, #2) packed into a single byte along with the data type."
  },
  {
    "term": "gRPC 5-Byte Prefix",
    "formula": "[1B CompressedFlag] + [4B MessageLength] + Payload",
    "meaning": "Every gRPC message sent over HTTP/2 starts with 5 header bytes: 1 byte saying whether the message is compressed, and 4 bytes telling the receiver the exact byte length of the message."
  },
  {
    "term": "Reserved Field Law",
    "formula": "reserved 4, 15; reserved \"legacy_ssn\";",
    "meaning": "A safety rule in .proto files that locks retired field numbers forever so no teammate accidentally reuses number #4 for a different field and corrupts older apps."
  },
  {
    "term": "Deadline Propagation",
    "formula": "grpc-timeout: 800m -> Child Budget = 800ms - Elapsed",
    "meaning": "Passing the remaining time budget down the chain of microservice calls so if the user's 800ms timeout runs out, every downstream database query stops working immediately instead of wasting CPU."
  }
]
```

## 🌱 Step 1: Plain-English Story — Paint-by-Numbers vs. Verbose Letters

Imagine mailing 10,000 furniture assembly instructions every second.
- **JSON (`REST` / `GraphQL`)** is like printing full English paragraphs on every single part: `{"part_identifier_code": 150, "is_fragile_glass": true}`. Every message repeats the long English labels `"part_identifier_code"` and `"is_fragile_glass"` over and over again.
- **Protocol Buffers (`gRPC`)** is like a **Paint-by-Numbers kit**. Both the sender and the receiver share a printed legend ahead of time (the `.proto` contract file) that says:
  - Box `#1` = Part Identifier Code
  - Box `#2` = Is Fragile Glass

When one microservice sends a message to another over the network, it **never sends the English words**. It simply sends `[#1: 150, #2: 1]` packed into a handful of binary bytes!

This makes gRPC blazingly fast, but it introduces three new rules for **`AeroClient v0.7`**:
1. **Never Reuse a Number**: If you erase Box `#2` (`Is Fragile Glass`) from the legend and next week assign Box `#2` to `Discount Dollars`, any warehouse worker still using last week's legend will read `Discount = 1` as `Is Fragile Glass = true`!
2. **Real Status Lives at the Very End (`Trailers`)**: Because gRPC can stream thousands of items over one `HTTP/2` pipe, it sends `HTTP 200 OK` as soon as the pipe opens. The real result (`grpc-status: 0 OK` or `4 DEADLINE_EXCEEDED`) arrives at the very end in an **HTTP/2 Trailer**.
3. **Every Call Needs a Stopwatch (`Deadline`)**: Without a deadline, a single slow downstream service will freeze every upstream service waiting on it.

```mermaid
flowchart LR
  Client["AeroClient v0.7 (Deadline: 800ms)"] -->|HTTP/2 + 5B Frame| Ord["Orders gRPC Service"]
  Ord -->|Remaining: 680ms| Pay["Payments gRPC Service"]
  Pay -->|HTTP/2 Trailer: grpc-status| Ord
  Ord -->|grpc-status: 0 OK| Client
```

---

## 🔨 Step 2: First Lines of Code — `AeroClient v0.7` Framing & Deadline Starter

Let's write our first minimal **`AeroClient v0.7`** helper in Python 3 and Java 17. In Python, we can inspect the exact `5-byte` gRPC wire header (`1` compression byte + `4-byte` big-endian length) and enforce a strict per-call `timeout` (deadline) on every RPC invocation.

```python
import struct

def frame_and_check_grpc(protobuf_payload: bytes, timeout_ms: int) -> bytes:
    """AeroClient v0.7 starter: packs 5-byte gRPC frame & verifies positive deadline."""
    if timeout_ms <= 0:
        raise ValueError("grpc.StatusCode.DEADLINE_EXCEEDED: timeout_ms must be > 0")
    # 1-byte compression flag (0 = raw) + 4-byte big-endian unsigned length
    header = struct.pack(">BI", 0, len(protobuf_payload))
    frame = header + protobuf_payload
    comp_flag, msg_len = struct.unpack(">BI", frame[:5])
    assert comp_flag == 0 and msg_len == len(protobuf_payload)
    return frame
```

### Java 17 Equivalent

```java
import java.nio.ByteBuffer;
import java.time.Duration;

public class AeroGrpcStarter {
    public static byte[] packGrpcFrame(byte[] protoBytes, Duration deadline) {
        if (deadline.isZero() || deadline.isNegative()) {
            throw new IllegalArgumentException("DEADLINE_EXCEEDED: deadline must be positive");
        }
        return ByteBuffer.allocate(5 + protoBytes.length)
            .put((byte) 0)                 // 0 = uncompressed
            .putInt(protoBytes.length)     // 4-byte big-endian message length
            .put(protoBytes)
            .array();
    }
}
```

---

## ⚡ Step 3: Where It Breaks in Real Life — Reused Field Tags, Sticky L4 Pods & Static Deadlines

When teams migrate from REST to gRPC without updating their testing playbook, three production outages happen almost immediately:

1. **Silent Binary Corruption from Reused `.proto` Field Numbers**: A developer deletes `int64 legacy_points = 5;` and next sprint adds `bool is_vip = 5;` without marking `reserved 5;`. Because both `int64` and `bool` use Protobuf `wire_type = 0` (`Varint`), zero framing errors occur—old and new pods silently misinterpret loyalty points as VIP flags!
2. **Kubernetes L4 `ClusterIP` Sticky-Pod Starvation**: Unlike HTTP/1.1, gRPC multiplexes all requests over **one persistent HTTP/2 TCP connection**. Standard Kubernetes `ClusterIP` load balances at Layer-4 (per TCP connection), pinning `100%` of your gRPC traffic onto a **single pod** while 9 other autoscaled pods sit at `0%` CPU!
3. ** HTTP/1.1 Proxies Stripping `grpc-status` Trailers**: If an misconfigured ingress downgrades HTTP/2 to HTTP/1.1 and drops trailing headers, clients see `HTTP 200` with a missing `grpc-status` and crash with `INTERNAL`.

```json contrast
{
  "title": "Naive Unbounded gRPC Stubs vs AeroClient v0.7 Deadlines, Wire-Compat & L7 Balancing",
  "naiveTitle": "Stub Without Deadline + K8s L4 VIP",
  "naiveMetric": "Thread Starvation · 1 Hot Pod @ 100% CPU",
  "naivePoints": [
    "Calls stub.createOrder(req) without withDeadlineAfter(), allowing hung downstream RPCs to pin caller threads forever",
    "Uses default Kubernetes ClusterIP (L4 TCP load balancing): 1 persistent HTTP/2 socket pins ALL 10,000 RPS onto a single pod!",
    "Deletes .proto fields without adding 'reserved <tag>;', causing silent binary type corruption during rolling deploys"
  ],
  "staffTitle": "AeroClient v0.7 Deadlines + Round-Robin + Wire Gate",
  "staffMetric": "Fast Context Cancel · Even Pod Spread",
  "staffPoints": [
    "Client interceptor rejects any outbound RPC lacking an explicit per-call Deadline and propagates remaining budget downstream",
    "Configures headless DNS / xDS client-side 'round_robin' load balancing across HTTP/2 subchannels so scaling pods works",
    "Enforces static Protobuf wire-compatibility checks ensuring deleted tags are reserved and wire types never mutate"
  ]
}
```

```json poe
{
  "question": "A microservice runs behind a Legacy Layer-7 HTTP/1.1 Reverse Proxy that downgrades HTTP/2 to HTTP/1.1 and strips HTTP Trailers. Unary gRPC calls appear to transmit request bytes, yet every gRPC client crashes with INTERNAL: HTTP status code 200 missing grpc-status. Why?",
  "options": [
    "Protobuf varints cannot traverse IPv4 NAT gateways",
    "gRPC sends HTTP 200 headers immediately when the stream opens and delivers the actual RPC outcome (grpc-status: 0 OK or 14 UNAVAILABLE) exclusively inside HTTP/2 Trailing HEADERS at the end of the stream—stripping trailers breaks the gRPC protocol contract",
    "gRPC requires TLS 1.2 RSA cipher suites",
    "HTTP/1.1 proxies uppercase binary Protobuf payload bytes"
  ],
  "answerIndex": 1,
  "explanation": "Because gRPC supports streaming responses, the server does not know if the RPC will succeed until the final message is generated; therefore grpc-status and grpc-message live in HTTP/2 Trailers."
}
```

---

## 🚀 Step 4: Staff Engineer Deep-Dive — Bit-Level Varint Math, Deadline Calculus & Production Blueprints

### 1. Protobuf Bit-Packing, ZigZag Encoding & Deadline Budget Calculus

On the binary wire, every Protobuf field begins with a **Tag Varint** combining the `field_number` ($f$) and the `wire_type` ($w \in \{0\text{=Varint}, 1\text{=64-bit}, 2\text{=Length-delimited}, 5\text{=32-bit}\}$):

$$\text{TagByte}(f, w) = (f \ll 3) \mid w$$

Because the first varint byte uses 1 MSB continuation bit, 3 bits for $w$, and 4 bits for $f$, field numbers **$1 \le f \le 15$ require exactly 1 tag byte**, whereas $16 \le f \le 2047$ require **2 tag bytes** (always reserve tags `1..15` for your hottest repeated/scalar fields!).

For signed negative integers, standard two's-complement `int32`/`int64` sets the sign bit to `1` in bit 63, forcing every negative number (even `-1`) to consume **10 bytes** on the wire. **`sint32`/`sint64` (ZigZag encoding)** interleaves positive and negative magnitudes so small negative values take 1 byte:

$$\text{ZigZag64}(n) = (n \ll 1) \oplus (n \gg 63) \implies \text{ZigZag}(0)=0,\; \text{ZigZag}(-1)=1,\; \text{ZigZag}(1)=2$$

Across a $K$-hop microservice call chain starting with edge deadline budget $B_0$, the remaining deadline budget propagated to hop $k$ via the `grpc-timeout` header is:

$$B_k = B_0 - \sum_{i=1}^{k-1} \left( T_{\text{compute}, i} + T_{\text{network}, i} \right) - \Delta_{\text{safety}} > 0$$

If $B_k \le 0$, the caller aborts immediately with `StatusCode.DEADLINE_EXCEEDED (4)` without transmitting bytes over the socket.

### 2. gRPC Status Code & Automation Verification Matrix

| `grpc-status` Code | Wire Meaning & Retry Safety | Equivalent HTTP | Mandatory `AeroClient v0.7` Test |
| :--- | :--- | :--- | :--- |
| **`0 OK`** | RPC completed cleanly | `200 OK` | Assert response Protobuf invariants + unknown-field preservation |
| **`3 INVALID_ARGUMENT`** | Deterministic domain/validation error (`google.rpc.BadRequest` detail) | `400 / 422` | Unpack `google.rpc.Status` rich `ErrorInfo`/`BadRequest` field violations |
| **`4 DEADLINE_EXCEEDED`** | Budget expired; server *may* or *may not* have committed state! | `504 Gateway Timeout` | Set `withDeadlineAfter(50ms)` against `150ms` stub; assert server cancels context |
| **`8 RESOURCE_EXHAUSTED`** | Rate limit quota exhausted OR `maxInboundMessageSize` (>4MB default) breached | `429 / 413` | Send `5MB` payload to default `4MB` server; assert clean `8` rejection, zero OOM |
| **`14 UNAVAILABLE`** | Transient transport/pod shutdown before processing (safe to retry idempotent calls) | `503 Service Unavailable` | Inject `GOAWAY` frame during rolling deploy; verify seamless subchannel failover |

### 3. Dual-Language Production Blueprints: `AeroClient v0.7` Codec & Deadline Interceptor

#### Python 3 Blueprint: Zero-Dependency Protobuf Varint/Frame Inspector + Deadline Guard

```python
from __future__ import annotations
from dataclasses import dataclass
import struct
import time
from typing import Dict, List, Tuple


def encode_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("Use encode_zigzag_varint for negative sint64 values")
    out = bytearray()
    while value > 0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)


def encode_zigzag_varint(signed_val: int) -> bytes:
    zigzag = (signed_val << 1) ^ (signed_val >> 63)
    return encode_varint(zigzag)


def pack_grpc_data_frame(protobuf_bytes: bytes, compressed: bool = False) -> bytes:
    """Wraps serialized Protobuf bytes in the 5-byte gRPC HTTP/2 DATA length-prefix envelope."""
    flag = 1 if compressed else 0
    return struct.pack(">BI", flag, len(protobuf_bytes)) + protobuf_bytes


def unpack_grpc_data_frame(frame: bytes) -> Tuple[bool, bytes]:
    if len(frame) < 5:
        raise ValueError("Truncated gRPC frame (< 5-byte header)")
    compressed_flag, msg_len = struct.unpack(">BI", frame[:5])
    if len(frame) - 5 != msg_len:
        raise ValueError(f"Frame length mismatch: header={msg_len}, actual={len(frame) - 5}")
    return bool(compressed_flag), frame[5:]


@dataclass(frozen=True)
class PropagatedDeadlineContext:
    deadline_monotonic: float
    trace_id: str

    def remaining_ms(self, now: float | None = None) -> int:
        ref = time.monotonic() if now is None else now
        rem = int((self.deadline_monotonic - ref) * 1000.0)
        if rem <= 0:
            raise TimeoutError("grpc.StatusCode.DEADLINE_EXCEEDED (code=4): budget exhausted before hop")
        return rem

    def to_grpc_metadata(self, safety_margin_ms: int = 5, now: float | None = None) -> Dict[str, str]:
        budget_ms = self.remaining_ms(now) - safety_margin_ms
        if budget_ms <= 0:
            raise TimeoutError("grpc.StatusCode.DEADLINE_EXCEEDED (code=4): insufficient hop margin")
        return {"grpc-timeout": f"{budget_ms}m", "x-trace-id": self.trace_id}


def verify_proto_wire_compatibility(
    v1_fields: Dict[int, str], v2_fields: Dict[int, str], v2_reserved_numbers: set[int]
) -> List[str]:
    """Static CI gate enforcing Protobuf binary wire-compatibility invariants between v1 and v2."""
    violations: List[str] = []
    for num, v1_type in v1_fields.items():
        if num not in v2_fields:
            if num not in v2_reserved_numbers:
                violations.append(f"Deleted field #{num} ({v1_type}) MUST be added to 'reserved {num};'")
        elif v2_fields[num] != v1_type:
            violations.append(f"Wire-breaking type mutation on field #{num}: {v1_type} -> {v2_fields[num]}")
    return violations
```

#### Java 17 Blueprint: Mandatory gRPC `ClientInterceptor` Enforcing Deadlines & Metadata

```java
package com.aerocart.api.grpc;

import io.grpc.CallOptions;
import io.grpc.Channel;
import io.grpc.ClientCall;
import io.grpc.ClientInterceptor;
import io.grpc.Deadline;
import io.grpc.ForwardingClientCall;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Metadata;
import io.grpc.MethodDescriptor;
import java.util.concurrent.TimeUnit;

public final class StaffGrpcChannelFactory {

    private static final Metadata.Key<String> AUTHORIZATION_KEY =
        Metadata.Key.of("authorization", Metadata.ASCII_STRING_MARSHALLER);
    private static final Metadata.Key<String> IDEMPOTENCY_KEY =
        Metadata.Key.of("x-idempotency-key", Metadata.ASCII_STRING_MARSHALLER);

    /**
     * Enforces mandatory per-RPC deadlines (preventing hung CI workers & production thread leaks)
     * and injects Bearer auth + idempotency metadata uniformly across unary and streaming stubs.
     */
    public static final class MandatoryDeadlineAndAuthInterceptor implements ClientInterceptor {
        private final long defaultTimeoutMillis;
        private final java.util.function.Supplier<String> bearerSupplier;

        public MandatoryDeadlineAndAuthInterceptor(
                long defaultTimeoutMillis, java.util.function.Supplier<String> bearerSupplier) {
            this.defaultTimeoutMillis = defaultTimeoutMillis;
            this.bearerSupplier = bearerSupplier;
        }

        @Override
        public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
                MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next) {
            CallOptions effectiveOptions = callOptions.getDeadline() != null
                ? callOptions
                : callOptions.withDeadline(Deadline.after(defaultTimeoutMillis, TimeUnit.MILLISECONDS));

            ClientCall<ReqT, RespT> delegate = next.newCall(method, effectiveOptions);
            return new ForwardingClientCall.SimpleForwardingClientCall<>(delegate) {
                @Override
                public void start(Listener<RespT> responseListener, Metadata headers) {
                    headers.put(AUTHORIZATION_KEY, "Bearer " + bearerSupplier.get());
                    if (!headers.containsKey(IDEMPOTENCY_KEY) && method.getType().clientSendsOneMessage()) {
                        headers.put(IDEMPOTENCY_KEY, java.util.UUID.randomUUID().toString());
                    }
                    super.start(responseListener, headers);
                }
            };
        }
    }

    public static ManagedChannel createRoundRobinChannel(
            String headlessTarget, long defaultDeadlineMs, java.util.function.Supplier<String> tokenFn) {
        return ManagedChannelBuilder.forTarget(headlessTarget) // e.g., "dns:///orders-headless.prod:9090"
            .defaultLoadBalancingPolicy("round_robin")          // Avoid L4 single-TCP-connection hot-spotting!
            .maxInboundMessageSize(4 * 1024 * 1024)             // Explicit 4 MiB cap
            .intercept(new MandatoryDeadlineAndAuthInterceptor(defaultDeadlineMs, tokenFn))
            .build();
    }
}
```

> [!WARNING] **Staff Interview Gotcha — Kubernetes L4 `ClusterIP` Breaks gRPC Load Balancing & `proto3` Default Zero-Value Ambiguity:** Two classic Staff traps in gRPC systems:
> 1. **L4 Sticky Socket Trap**: Because gRPC multiplexes all RPCs over a single persistent HTTP/2 TCP connection, pointing a gRPC `ManagedChannel` at a standard Kubernetes `ClusterIP` VIP routes **100% of RPCs to whichever single pod won the initial TCP handshake**, leaving newly autoscaled pods at `0%` CPU! Fix via **Headless Service (`clusterIP: None`) + `round_robin` client policy** or an L7 Envoy/Istio/xDS mesh.
> 2. **`proto3` Scalar Zero vs. Unset**: In `proto3`, an unadorned `int32 discount_pct = 3;` serializes `0` as **zero bytes on the wire**—meaning the server cannot distinguish `"client explicitly set discount_pct = 0"` from `"client omitted discount_pct"`! Always use the **`optional` keyword** (`optional int32 discount_pct = 3;`, restored in `proto3.15+` with explicit `hasDiscountPct()` field presence) whenever `0`, `""`, or `false` carries distinct business meaning from unset!

---

### Up Next in Chapter 08: Async `202 Accepted` Sagas & Webhook HMAC Verification

Synchronous REST, GraphQL, and gRPC calls work great when an operation finishes in `<200ms`. But what happens when AeroCart issues an international airline ticket that takes `4 seconds` across external partner banks and GDS clearinghouses? Holding a synchronous HTTP/gRPC connection open for 4 seconds exhausts every worker thread! In **Chapter 08**, we will upgrade `AeroClient` to `v0.8` to verify asynchronous **`HTTP 202 Accepted` Sagas**, compensating rollbacks, and cryptographically signed **Webhook (`HMAC-SHA256`)** callbacks!

```json quiz
[
  {
    "id": "api-07-q1",
    "question": "A developer deletes 'int64 legacy_loyalty_points = 5;' from Order.proto and in the next sprint adds 'bool is_gift_order = 5;' reusing field number 5 (since bool and int64 both use Protobuf wire_type 0 varint!). What happens during a rolling deployment?",
    "options": [
      "Protobuf rejects the message because the field name string does not match",
      "Silent data corruption: field names are absent on the binary wire, so un-upgraded v1 consumers decode 'is_gift_order = true' (varint 1) as 'legacy_loyalty_points = 1', and upgraded v2 consumers decode old loyalty points > 0 as 'is_gift_order = true'!",
      "gRPC returns UNIMPLEMENTED (code 12)",
      "HTTP/2 resets the stream with PROTOCOL_ERROR"
    ],
    "answerIndex": 1,
    "explanation": "Because int64 and bool share Wire Type 0 (Varint), reusing field tag #5 parses without any framing error while silently corrupting domain semantics across rolling versions. Deleted tags must ALWAYS be marked 'reserved 5;'."
  },
  {
    "id": "api-07-q2",
    "question": "In Java gRPC, an engineer builds ONE Deadline at application startup (CallOptions.DEFAULT.withDeadlineAfter(2, SECONDS)) and stores that CallOptions constant in a static final field reused across all RPCs. What breaks 2.001 seconds after the JVM boots?",
    "options": [
      "TLS certificates expire after 2 seconds",
      "Deadline.after(2, SECONDS) captures an ABSOLUTE wall-clock timestamp at construction time! Every single RPC invoked >2 seconds after JVM startup fails instantaneously on the client with DEADLINE_EXCEEDED without sending a packet—deadlines must be minted fresh per-call inside an interceptor or stub.withDeadlineAfter()",
      "ManagedChannel switches from HTTP/2 to HTTP/1.1",
      "Protobuf varints overflow 32 bits"
    ],
    "answerIndex": 1,
    "explanation": "io.grpc.Deadline represents a fixed point in monotonic time, not a relative duration template; caching a Deadline or pre-built stub.withDeadlineAfter() across time immediately expires all future RPCs."
  },
  {
    "id": "api-07-q3",
    "question": "Why does gRPC's built-in RetryPolicy (configured via ServiceConfig JSON) strongly recommend retrying StatusCode.UNAVAILABLE (14) while avoiding blind retries on StatusCode.DEADLINE_EXCEEDED (4) for state-mutating RPCs?",
    "options": [
      "DEADLINE_EXCEEDED closes the entire ManagedChannel",
      "UNAVAILABLE typically signals transport refusal or HTTP/2 GOAWAY before the server handler executed, whereas DEADLINE_EXCEEDED means the request WAS dispatched and the server may still commit the write milliseconds after the client gave up",
      "UNAVAILABLE uses UDP whereas DEADLINE_EXCEEDED uses TCP",
      "ServiceConfig JSON cannot parse code 4"
    ],
    "answerIndex": 1,
    "explanation": "DEADLINE_EXCEEDED is an ambiguous outcome on mutations unless paired with an explicit idempotency key and server-side context cancellation."
  }
]
```
