---
slug: api-04-production-api-clients-pydantic-and-rest-assured
course_id: 04-api-and-api-automation
track: core-cs
volume: "04. Zero to Mastery: API & API Automation"
module_number: 2
module_title: "Module 2: Security, Throttling & Production Client Pipelines"
chapter_number: 4
level_tag: "Beginner → Staff"
title: "Production Domain API Clients: Pydantic v2 Pipelines & Java 17 REST Assured"
summary: "Evolving AeroClient v0.3 into AeroClient v0.4: replacing scattered URL strings and raw dictionary lookups with typed Domain API Clients, strict Pydantic v2 and Java 17 record schemas, dual-mode result envelopes, W3C traceparent headers, and secret-redacted cURL failure artifacts."
reading_time_minutes: 15
visualizer_id: fw-abstraction-diff-builder
lab_path: frameworks/api-automation/pytest-requests-python
tags: ["api-automation", "pydantic-v2", "rest-assured", "domain-client", "java-17", "traceparent", "curl-filter"]
---

# Production Domain API Clients: Pydantic v2 Pipelines & Java 17 REST Assured

```json continuity
{
  "previously": "In Chapter 03, we upgraded AeroClient v0.3 with thread-safe OAuth2 token caching, mTLS certificates, and HMAC webhook verification.",
  "painPoint": "As our test suite grew to 400 tests, every test still hardcoded '/v1/orders' URL strings and raw dictionary lookups like resp.json()['price_cents']. When a backend developer renamed one field or returned a 422 validation error, 400 tests crashed with cryptic KeyErrors and leaked secret tokens into CI logs.",
  "unlock": "We will build AeroClient v0.4: a clean Domain API Client that wraps every HTTP call in strict data models (Pydantic v2 and Java 17 records), returns a safe result envelope for both 200 OK and 4xx errors, and prints a secret-redacted cURL command with a trace ID only when a test fails."
}
```

```json walkthrough
[
  {
    "slide": 1,
    "title": "The Restaurant Waiter Analogy",
    "time": "0:00 - 0:22",
    "badge": "PLAIN STORY",
    "caption": "Writing raw HTTP URLs and dictionary lookups inside every test is like letting 400 restaurant customers walk directly into the kitchen to shout orders. A Domain API Client acts like a polite waiter with a printed menu—if a recipe changes in the kitchen, you update the menu in one place instead of retraining 400 customers.",
    "focusSelector": "#step-1-story",
    "code": "# Scattered vs Waiter Seam\n# Bad:  requests.post(f'{URL}/v1/orders', json={'sku': 'A'})\n# Good: aero_client.create_order(OrderRequest(sku='A'))"
  },
  {
    "slide": 2,
    "title": "AeroClient v0.4: First Typed Client",
    "time": "0:22 - 0:45",
    "badge": "FIRST CODE",
    "caption": "In less than 15 lines of Python or Java, we replace loose dictionaries with a typed OrderRequest and OrderReceipt class inside AeroClient v0.4. Now your IDE autocompletes every field name before the test even runs.",
    "focusSelector": "#step-2-code",
    "code": "@dataclass(frozen=True)\nclass OrderReceipt:\n    order_id: str\n    price_cents: int"
  },
  {
    "slide": 3,
    "title": "Why Naive Clients Break on 4xx & Type Drift",
    "time": "0:45 - 1:10",
    "badge": "FAILURE MODE",
    "caption": "If your client throws an exception on HTTP 422, writing negative tests becomes a nightmare. Worse, if a backend bug changes price_cents from integer 2500 to string '2500', loose JSON parsers silently ignore it while mobile apps crash.",
    "focusSelector": "#step-3-breaks",
    "code": "# Loose parser passes string '2500' -> iOS app crashes!\n# Strict schema catches '2500' != 2500 immediately"
  },
  {
    "slide": 4,
    "title": "Staff Blueprint: Envelopes, Trace IDs & Redacted cURL",
    "time": "1:10 - 1:35",
    "badge": "STAFF BLUEPRINT",
    "caption": "Our Staff AeroClient v0.4 returns an ApiEnvelope holding either the validated data or a structured error, attaches a unique tracking ID header to link test failures to server logs, and builds a secret-scrubbed cURL command for instant debugging.",
    "focusSelector": "#step-4-staff",
    "code": "envelope = client.create_order(req, idem_key='k1')\norder = envelope.expect_ok(201) # Emits redacted curl on fail"
  }
]
```

```json pretraining
[
  {
    "term": "Domain API Client",
    "formula": "Test -> AeroClient.create_order(req) -> Typed Result",
    "meaning": "A helper class that hides raw URLs, headers, and JSON formatting behind simple business methods so tests read like plain English and only one file changes when an endpoint URL changes."
  },
  {
    "term": "Strict Schema Validation",
    "formula": "JSON Wire Bytes -> Exact Type Check (int != str)",
    "meaning": "Checking that every field returned by the server has the exact right data type—such as rejecting the text string '2500' when the contract promises the whole number 2500."
  },
  {
    "term": "Dual-Mode Envelope",
    "formula": "ApiEnvelope = (status_code, ok_data, error_detail)",
    "meaning": "A wrapper box returned by our client that safely holds either a successful order receipt OR a structured error message, so negative tests can inspect 400/422 errors cleanly without crashing."
  },
  {
    "term": "Redacted cURL & Trace Header",
    "formula": "Failure -> curl -H 'Authorization: <REDACTED>' + Trace ID",
    "meaning": "A copy-pasteable terminal command and unique tracking tag printed only when a test fails, letting developers reproduce the exact bug in seconds without leaking secret passwords into logs."
  }
]
```

## 🌱 Step 1: Plain-English Story — The Restaurant Waiter & The Printed Menu

Imagine running a busy restaurant where 400 customers skip the dining room, barge straight into the kitchen, and scribble their own ticket notes onto sticky pads. One customer writes `"qty": 2`, another writes `"quantity": 2`, and when the chef moves the burger grill to a new station, all 400 customers get lost.

That is exactly what happens when we scatter raw `session.post(f"{url}/v1/orders", json={"sku": "BAG"})` calls across 400 test files. If a backend engineer changes `/v1/orders` to `/v2/orders` or renames a JSON field, you are stuck editing 400 files by hand. Even worse, when a test fails in overnight automation, the raw dictionary lookup `resp.json()["order_id"]` crashes with an unhelpful `KeyError: 'order_id'`, hiding the real reason the kitchen rejected the order.

To fix this in **`AeroClient v0.4`**, we introduce a **Domain API Client**—our polite restaurant waiter—paired with a **Strict Schema** (the printed menu):

```mermaid
flowchart LR
  Test["Business Test"] -->|1. Typed OrderReq| Client["AeroClient v0.4"]
  Client -->|2. Add Auth & Trace ID| Server["AeroCart API"]
  Server -->|3. JSON Response| Envelope["Safe Result Envelope"]
  Envelope -->|4. Strict Type Check| Receipt["Typed OrderReceipt"]
```

Instead of touching raw URLs or JSON dictionaries, a test simply hands a typed request object to `AeroClient`. `AeroClient` handles the URL, attaches our Chapter 03 auth token and a tracking number, and checks that the kitchen's response matches the printed menu before handing back a clean receipt.

---

## 🔨 Step 2: First Lines of Code — Wrapping `AeroClient v0.4` in Typed Models

Let's evolve our `AeroClient` from Chapter 03 by wrapping `/v1/orders` inside a dedicated method that accepts a typed `OrderRequest` and returns a validated `OrderReceipt`.

```python
from dataclasses import asdict, dataclass
import requests

@dataclass(frozen=True)
class OrderRequest:
    sku: str
    quantity: int = 1

@dataclass(frozen=True)
class OrderReceipt:
    order_id: str
    price_cents: int

class AeroClientV04:
    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.session, self.base_url = session, base_url.rstrip("/")

    def create_order(self, req: OrderRequest) -> OrderReceipt:
        resp = self.session.post(f"{self.base_url}/v1/orders", json=asdict(req), timeout=5.0)
        body = resp.json()
        return OrderReceipt(order_id=body["order_id"], price_cents=body["price_cents"])
```

### Java 17 Equivalent

```java
package com.aerocart.client;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;

public class AeroClientV04 {
    public record OrderRequest(String sku, int quantity) {}
    public record OrderReceipt(String orderId, int priceCents) {}

    private final String baseUrl;
    public AeroClientV04(String baseUrl) { this.baseUrl = baseUrl; }

    public OrderReceipt createOrder(OrderRequest req) {
        return RestAssured.given().baseUri(baseUrl).contentType(ContentType.JSON)
            .body(req).when().post("/v1/orders").then().extract().as(OrderReceipt.class);
    }
}
```

With just 18 lines of code, our test files no longer contain `/v1/orders` or untyped string keys!

---

## ⚡ Step 3: Where It Breaks in Real Life — Silent Type Coercion, 4xx Crashes & Leaked Secrets

Our simple `AeroClientV04` feels clean until three real-world production incidents hit:

1. **Silent String-to-Integer Coercion**: A backend developer accidentally changes `price_cents` from integer `2500` to string `"2500"`. Many default JSON validators (including default Pydantic lax mode) quietly convert `"2500"` into `2500` so your Python test passes green—while the iOS Swift app crashes in production!
2. **Negative Tests Bypass the Client**: If `create_order` assumes every response is a `201 Created` `OrderReceipt`, it crashes whenever a test intentionally sends `quantity: -5` to verify a `422 Unprocessable Entity` error. Frustrated engineers go right back to writing raw `requests.post()` calls for negative tests.
3. **Leaked Bearer Tokens in CI Logs**: Turning on global request logging prints `Authorization: Bearer eyJ...` into shared build logs for all 1,000 passing tests.

```json contrast
{
  "title": "Naive Client Wrapper vs Staff AeroClient v0.4 Pipeline",
  "naiveTitle": "Naive Happy-Path Client",
  "naiveMetric": "400-File Edits · Missed Type Bugs",
  "naivePoints": [
    "Throws exceptions or crashes on 400/422 responses, forcing negative tests to bypass the client",
    "Permissive JSON parsing silently converts string '2500' to int 2500, missing mobile-crashing bugs",
    "Dumps raw Authorization JWTs into public CI stdout on every passing request"
  ],
  "staffTitle": "Staff AeroClient v0.4 Envelope + Trace Filter",
  "staffMetric": "1-File Updates · <5s Trace Triage",
  "staffPoints": [
    "Returns ApiEnvelope[OrderDto, ProblemDetail] so 201 positive and 422 negative tests use the exact same method",
    "Enforces strict wire types (rejects string '2500' and undocumented extra fields immediately)",
    "Attaches W3C traceparent header and prints a secret-redacted cURL command ONLY when an assertion fails"
  ]
}
```

```json poe
{
  "question": "If AeroClient.create_order() calls response.raise_for_status() internally and only returns an OrderReceipt, what happens when the team needs to write 45 negative validation tests (HTTP 400, 409, 422)?",
  "options": [
    "Pydantic v2 refuses to parse HTTP 422 JSON bodies",
    "Engineers either wrap every negative test in messy try/except blocks or bypass AeroClient with raw requests.post() calls—breaking the single-source-of-truth client",
    "HTTP/2 closes the TCP socket whenever raise_for_status() executes",
    "Pytest marks caught HTTPError exceptions as XFAIL automatically"
  ],
  "answerIndex": 1,
  "explanation": "A Staff Domain Client returns a dual-mode ApiEnvelope holding either the validated 2xx DTO or the 4xx/5xx ProblemDetail so positive and negative tests share identical plumbing."
}
```

---

## 🚀 Step 4: Staff Engineer Deep-Dive — Maintenance Math, W3C `traceparent` & Production Blueprints

To quantify why a Domain API Client is mandatory at scale, compare refactoring cost across $N_{\text{tests}}$ test cases touching $E$ endpoints when a contract changes. With inline requests, maintenance work scales with total test count; with a Domain Client seam, it scales strictly with endpoint count:

$$C_{\text{inline}} = \mathcal{O}(N_{\text{tests}}) \quad \gg \quad C_{\text{domain\_client}} = \mathcal{O}(E) \quad \text{where } E \ll N_{\text{tests}}$$

Furthermore, when a test fails, injecting a **W3C Trace Context** header (`traceparent: 00-<32-hex-trace-id>-<16-hex-span-id>-01`) reduces mean time to resolution ($\text{MTTR}$) from $\mathcal{O}(\log N_{\text{logs}})$ timestamp grepping to an $\mathcal{O}(1)$ trace lookup in Jaeger/Datadog.

| Architectural Layer | Python 3 Staff Stack | Java 17 Staff Stack | Core Guarantee Enforced |
| :--- | :--- | :--- | :--- |
| **Wire DTO Schema** | `pydantic.BaseModel` (`ConfigDict(strict=True, extra="forbid")`) or strict validator | Java 17 `record` + Jackson strict deserialization | Fails immediately if `"2500"` replaces `2500` or unknown fields leak |
| **Result Container** | `ApiEnvelope[T]` (`data: Optional[T]`, `problem: Optional[ProblemDetail]`) | `ApiResult<T>` `record` with RFC 9457 `ProblemDetailDto` | Unified pipeline for both `2xx` happy paths and `4xx/5xx` negative tests |
| **Observability & Security** | PreparedRequest scrubber + `traceparent` generator | Thread-safe `io.restassured.filter.Filter` (`ThreadLocal`) | Zero leaked tokens in CI logs; instant copy-paste redacted cURL on failure |

### Python 3 Production Blueprint: `AeroClient v0.4` with Strict Validation, `ApiEnvelope` & Redacted cURL

```python
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import json, secrets, shlex, time
from typing import Any, Callable, Dict, Generic, Optional, TypeVar
import requests

T = TypeVar("T")
SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}

@dataclass(frozen=True)
class ProblemDetail:
    """RFC 9457 standard error model."""
    type: str
    title: str
    status: int
    detail: str = ""
    trace_id: str = ""

@dataclass(frozen=True)
class CreateOrderRequest:
    tenant_id: str
    sku: str = "SKU-CARRY-ON"
    quantity: int = 1

    def with_quantity(self, qty: int) -> "CreateOrderRequest":
        return replace(self, quantity=qty)

@dataclass(frozen=True)
class OrderDto:
    order_id: str
    tenant_id: str
    sku: str
    quantity: int

    @classmethod
    def validate_strict(cls, raw: Dict[str, Any]) -> "OrderDto":
        extra = set(raw.keys()) - {"order_id", "tenant_id", "sku", "quantity"}
        if extra:
            raise AssertionError(f"Undocumented wire fields leaked: {sorted(extra)}")
        if type(raw.get("quantity")) is not int:
            raise AssertionError(f"Strict type mismatch on quantity: {raw.get('quantity')!r}")
        return cls(str(raw["order_id"]), str(raw["tenant_id"]), str(raw["sku"]), raw["quantity"])

@dataclass(frozen=True)
class ApiEnvelope(Generic[T]):
    status_code: int
    latency_ms: float
    traceparent: str
    redacted_curl: str
    data: Optional[T]
    problem: Optional[ProblemDetail]

    def expect_ok(self, expected_status: int = 201) -> T:
        if self.status_code != expected_status or self.data is None:
            raise AssertionError(
                f"Expected {expected_status}, got {self.status_code} ({self.latency_ms}ms)\n"
                f"traceparent: {self.traceparent}\nReproduce: {self.redacted_curl}"
            )
        return self.data

class AeroOrdersClient:
    def __init__(self, session: requests.Session, base_url: str, token_fn: Callable[[], str]) -> None:
        self._session, self._base, self._token_fn = session, base_url.rstrip("/"), token_fn

    @staticmethod
    def _redacted_curl(req: requests.PreparedRequest) -> str:
        parts = ["curl", "-i", "-X", req.method or "GET", shlex.quote(req.url or "")]
        for k, v in req.headers.items():
            val = "<REDACTED>" if k.lower() in SENSITIVE_HEADERS else v
            parts.extend(["-H", shlex.quote(f"{k}: {val}")])
        if req.body:
            body_s = req.body.decode() if isinstance(req.body, bytes) else str(req.body)
            parts.extend(["--data-raw", shlex.quote(body_s)])
        return " ".join(parts)

    def create_order(self, payload: CreateOrderRequest, idem_key: str) -> ApiEnvelope[OrderDto]:
        trace_id, span_id = secrets.token_hex(16), secrets.token_hex(8)
        traceparent = f"00-{trace_id}-{span_id}-01"
        t0 = time.perf_counter()
        resp = self._session.post(
            f"{self._base}/v1/orders",
            data=json.dumps(asdict(payload)),
            headers={
                "Authorization": f"Bearer {self._token_fn()}",
                "Content-Type": "application/json",
                "Idempotency-Key": idem_key,
                "traceparent": traceparent,
            },
            timeout=(2.0, 5.0),
        )
        ms = round((time.perf_counter() - t0) * 1000.0, 2)
        curl = self._redacted_curl(resp.request)
        if 200 <= resp.status_code < 300:
            return ApiEnvelope(resp.status_code, ms, traceparent, curl, OrderDto.validate_strict(resp.json()), None)
        err = resp.json() if "json" in resp.headers.get("Content-Type", "") else {}
        prob = ProblemDetail(err.get("type", "about:blank"), err.get("title", "Error"),
                             resp.status_code, err.get("detail", resp.text[:160]), trace_id)
        return ApiEnvelope(resp.status_code, ms, traceparent, curl, None, prob)
```

### Java 17 Production Blueprint: `record` DTOs, `RequestSpecBuilder` & Thread-Safe Trace Filter

```java
package com.aerocart.api.client;

import io.restassured.RestAssured;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.filter.Filter;
import io.restassured.filter.FilterContext;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.specification.FilterableRequestSpecification;
import io.restassured.specification.FilterableResponseSpecification;
import io.restassured.specification.RequestSpecification;
import java.util.HexFormat;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;

public final class AeroOrdersClient {
    public record CreateOrderDto(String tenantId, String sku, int quantity) {}
    public record OrderDto(String orderId, String tenantId, String sku, int quantity) {}
    public record ProblemDetailDto(String type, String title, int status, String detail, String traceId) {}
    public record ApiResult<T>(int status, long ms, String traceparent, String curl, T data, ProblemDetailDto problem) {}

    public static final class TraceAndRedactedCurlFilter implements Filter {
        private static final Set<String> SECRETS = Set.of("authorization", "cookie", "x-api-key");
        private final ThreadLocal<String> lastCurl = new ThreadLocal<>();
        private final ThreadLocal<String> lastTrace = new ThreadLocal<>();

        @Override
        public Response filter(FilterableRequestSpecification req, FilterableResponseSpecification res, FilterContext ctx) {
            byte[] t = new byte[16]; byte[] s = new byte[8];
            ThreadLocalRandom.current().nextBytes(t); ThreadLocalRandom.current().nextBytes(s);
            String tp = "00-" + HexFormat.of().formatHex(t) + "-" + HexFormat.of().formatHex(s) + "-01";
            req.header("traceparent", tp);
            lastTrace.set(tp);

            StringBuilder c = new StringBuilder("curl -i -X ").append(req.getMethod()).append(" '").append(req.getURI()).append("'");
            req.getHeaders().forEach(h -> {
                String v = SECRETS.contains(h.getName().toLowerCase()) ? "<REDACTED>" : h.getValue();
                c.append(" -H '").append(h.getName()).append(": ").append(v).append("'");
            });
            if (req.getBody() != null) c.append(" --data-raw '").append(req.getBody().toString()).append("'");
            lastCurl.set(c.toString());
            return ctx.next(req, res);
        }
        public String curl() { return lastCurl.get(); }
        public String trace() { return lastTrace.get(); }
    }

    private final RequestSpecification baseSpec;
    private final TraceAndRedactedCurlFilter filter = new TraceAndRedactedCurlFilter();

    public AeroOrdersClient(String baseUri) {
        this.baseSpec = new RequestSpecBuilder().setBaseUri(baseUri)
            .setContentType(ContentType.JSON).addFilter(filter).build();
    }

    public ApiResult<OrderDto> createOrder(CreateOrderDto dto, String token, UUID idemKey) {
        Response r = RestAssured.given().spec(baseSpec)
            .header("Authorization", "Bearer " + token)
            .header("Idempotency-Key", idemKey.toString())
            .body(dto).when().post("/v1/orders");
        int code = r.statusCode();
        if (code >= 200 && code < 300) {
            return new ApiResult<>(code, r.time(), filter.trace(), filter.curl(), r.as(OrderDto.class), null);
        }
        ProblemDetailDto prob = r.contentType().contains("json")
            ? r.as(ProblemDetailDto.class)
            : new ProblemDetailDto("about:blank", "Error", code, r.asString(), filter.trace());
        return new ApiResult<>(code, r.time(), filter.trace(), filter.curl(), null, prob);
    }
}
```

> [!WARNING] **Staff Interview Gotcha — Mutating Global `RestAssured.requestSpecification` or Lax Pydantic Coercion:** Never assign `RestAssured.requestSpecification` or `RestAssured.baseURI` inside `@BeforeEach` when running JUnit 5 tests in parallel—those are static JVM-wide globals that cause Tenant A's Bearer token to leak into Tenant B's request! Always build an instance-scoped `RequestSpecBuilder` and pass it via `given().spec(baseSpec)`. Similarly, in Python Pydantic v2, always set `model_config = ConfigDict(strict=True, extra="forbid")` on response models so string-to-int wire regressions (`"2500"` vs `2500`) fail immediately.

**Up Next in Chapter 05:** Now that `AeroClient v0.4` can fire clean, typed requests across 32 parallel workers, what happens when our fast test suite blasts the staging server with 500 requests per second and triggers a wave of `HTTP 429 Too Many Requests` and cascading retry storms? In Chapter 05, we will upgrade to **`AeroClient v0.5`** with Token Bucket rate limiting, `Retry-After` budget-aware backoff, and twin connect/read timeouts.

```json quiz
[
  {
    "id": "api-04-q1",
    "question": "A mobile iOS client crashes in production because a backend microservice began serializing 'unitPriceCents' as a JSON string (\"2500\") instead of a JSON integer (2500), yet all 300 Python Pydantic API contract tests passed green. Why?",
    "options": [
      "JSON RFC 8259 treats quoted integers and unquoted integers as identical tokens",
      "Pydantic's default lax validation mode coerces numeric strings (\"2500\") into Python ints (2500) unless strict=True (ConfigDict(strict=True)) is explicitly enabled on API response models",
      "HTTP/2 HPACK strips quotes from numeric JSON values",
      "requests.Response.json() converts all strings to integers automatically"
    ],
    "answerIndex": 1,
    "explanation": "Default Pydantic lax mode is convenient for form/query parsing, but fatal for wire contract verification; API response schemas must enable strict=True so string-to-int wire regressions fail immediately."
  },
  {
    "id": "api-04-q2",
    "question": "Why should a custom REST Assured Filter or Python Session hook buffer redacted cURL commands per request and attach them ONLY on test failure rather than enabling RequestLoggingFilter / ResponseLoggingFilter globally?",
    "options": [
      "REST Assured logging filters disable TLS 1.3",
      "Global request/response logging across 5,000 parallel tests floods GBs of CI console output, slows I/O, and leaks unredacted Authorization Bearer JWTs, cookies, and PII into build artifacts",
      "cURL cannot execute HTTP POST requests",
      "JUnit 5 truncates stdout after 100 lines"
    ],
    "answerIndex": 1,
    "explanation": "Attaching a secret-scrubbed cURL command + W3C traceparent strictly on failed assertions achieves high signal-to-noise ratio and zero credential leakage."
  },
  {
    "id": "api-04-q3",
    "question": "In JUnit 5 parallel execution (junit.jupiter.execution.parallel.enabled=true), tests randomly send Tenant A's Bearer header to Tenant B's endpoint. Inspection shows BeforeEach sets RestAssured.requestSpecification = new RequestSpecBuilder().addHeader('Authorization', token).build(). What is the fix?",
    "options": [
      "Add synchronized keywords to every JUnit @Test method",
      "Never mutate static RestAssured.* globals in parallel suites; pass an instance-scoped or ThreadLocal RequestSpecification explicitly into RestAssured.given().spec(tenantSpec)",
      "Switch from HTTP/2 to HTTP/1.0",
      "Disable Jackson record deserialization"
    ],
    "answerIndex": 1,
    "explanation": "RestAssured.requestSpecification is a static JVM-wide field; mutating it from concurrent worker threads creates immediate cross-test auth races."
  }
]
```
