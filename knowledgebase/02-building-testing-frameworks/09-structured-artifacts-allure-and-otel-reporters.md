---
slug: fw-09-structured-artifacts-allure-and-otel-reporters
course_id: 02-building-testing-frameworks
track: system-design
volume: "02. Zero to Mastery: Building Testing Frameworks"
module_number: 4
module_title: "Module 4: Enterprise Observability, Config & SDK Packaging (MiniTest v0.9 → v1.0)"
chapter_number: 9
level_tag: "🌱 Foundations → Staff Architecture"
title: "Build MiniTest v0.9: Structured Reporters, Auto-Attached Forensics & OpenTelemetry"
summary: "Right now `MiniTest` only prints `PASS / FAIL` to the terminal—which is painful to read at 2 AM and invisible to CI dashboards! Add a pluggable `on_test_end` Reporter Hook that emits JSON/JUnit XML, attaches failure snapshots, and links OpenTelemetry traces!"
reading_time_minutes: 15
video_url: ""
visualizer_id: sdet-otel-chaos-rca
lab_path: frameworks/design-challenges/01-custom-retry-analyzer
tags: ["testing-frameworks", "observability", "opentelemetry", "traceparent", "allure-reporting", "junit-xml", "minitest"]
---

# Build MiniTest v0.9: Structured Reporters, Auto-Attached Forensics & OpenTelemetry

```json continuity
{
  "previously": "In Ch 08, we added `FakeStripeServer` to `MiniTest v0.8` so we can test retries, state transitions, and request journals locally in milliseconds.",
  "painPoint": "Right now `MiniTest` only prints `✓ PASS` or `✗ FAIL` to the terminal! When a test fails on GitHub Actions at 2 AM, scrolling through 10,000 lines of raw text is miserable, screenshots/logs from passing tests fill up the hard drive, and CI dashboards can't graph plain `print()` output!",
  "unlock": "Add a pluggable Reporter Hook (`on_test_end`) to `MiniTest v0.9` that writes structured JSON / JUnit XML reports, keeps failure-only forensic snapshots (DOM + redacted `cURL`), and links client-to-DB OpenTelemetry `traceparent` IDs!"
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Slide 1 / 4 · Why Plain `print()` Fails in CI",
    "caption": "Human eyes read `print('✓ PASS')`, but GitHub Actions, Jenkins, and Allure Dashboards cannot graph raw terminal text—they need structured data (`results.json` or `junit.xml`)!",
    "code": "# ❌ Terminal text disappears into 10,000-line scrollback:\nprint('✗ FAIL: test_vip_checkout -> 449.8 != 360.0')\n# ✓ Structured JSON / XML feeds CI dashboards & flake trackers!",
    "nodes": ["MiniTest Runner", "on_test_end() Hook", "results.json + junit.xml"]
  },
  {
    "time": "0:25",
    "badge": "Slide 2 / 4 · The 'Dashcam' Rule: Keep Snapshots ONLY on Failure!",
    "caption": "How does a car dashcam avoid filling up its SD card? It records in memory, throws away boring drives, and ONLY saves the video if a crash happens! Do the exact same thing for test screenshots, HARs, and logs!",
    "code": "if outcome == 'PASSED':\n    ring_buffer.clear()          # 0 bytes written to disk!\nelse:\n    save_artifact(ring_buffer)   # Save screenshot + cURL ONLY on FAIL!",
    "nodes": ["Record in RAM Buffer", "Test PASSED -> Discard (0 Disk!)", "Test FAILED -> Save Snapshot!"]
  },
  {
    "time": "0:50",
    "badge": "Slide 3 / 4 · Auto-Attach a Copy-Pasteable (Redacted!) `cURL`",
    "caption": "When an API test fails with `HTTP 500`, don't make backend engineers guess what your test sent! Have your reporter automatically attach a ready-to-run `curl` command (with `Authorization` masked as `***REDACTED***`)!",
    "code": "# Attached automatically to every failed API test report:\n# Reproduce locally:\n# curl -X POST http://127.0.0.1:8090/checkout -H 'Authorization: ***REDACTED***'",
    "nodes": ["API Test Fails (500)", "Mask Auth Secrets", "Attach Copy-Paste cURL!"]
  },
  {
    "time": "1:15",
    "badge": "Slide 4 / 4 · The Magic Bridge: W3C `traceparent` ID!",
    "caption": "How do you connect a failed browser/API test in CI directly to the exact SQL query that crashed on the backend server? Stamp every test request with a `traceparent` ID and print a 1-click link in the failure report!",
    "code": "trace_id = uuid.uuid4().hex  # 32-char OpenTelemetry Trace ID\nheaders['traceparent'] = f'00-{trace_id}-0123456789abcdef-01'",
    "nodes": ["Test Generates trace_id", "Sends traceparent Header", "1-Click Link to Backend SQL Log!"]
  }
]
```

```json pretraining
[
  {
    "term": "Reporter Hook (`on_test_end`)",
    "formula": "Test Finishes -> Notify [ConsoleReporter, JsonReporter, JUnitXmlReporter]",
    "meaning": "A plug-in slot in your test runner (like `pytest_runtest_makereport` in Pytest or `TestWatcher` in JUnit 5) that receives every test's result, duration, and error."
  },
  {
    "term": "Failure-Only Dashcam Retention",
    "formula": "PASS -> Discard RAM buffer | FAIL -> Flush Screenshot/HAR/Logs to disk",
    "meaning": "Capturing rich breadcrumbs in memory during every test, but only saving files to disk when a test actually fails—saving 95% of CI storage!"
  },
  {
    "term": "Sanitized `cURL` Reproducer",
    "formula": "Failed HTTP Request -> Copy-paste `curl` with `***REDACTED***` token",
    "meaning": "Automatically generating a terminal `curl` command when an API test fails so any developer can reproduce the failure in 3 seconds without leaking passwords."
  },
  {
    "term": "W3C `traceparent` (OpenTelemetry)",
    "formula": "`00-<32-hex-trace-id>-<16-hex-span-id>-01`",
    "meaning": "A universal tracking number header attached to every HTTP call in a test so you can look up all matching backend microservice and database logs in 1 click."
  }
]
```

```json poe
{
  "question": "A team enables full Playwright video, DOM trace zip, and network HAR recording on Disk for ALL 1,000 tests in their suite (where 995 tests pass and 5 fail). What happens to their CI pipeline?",
  "options": [
    "Nothing changes—videos take zero disk space",
    "99.5% of the gigabytes written to disk and uploaded to S3 are for PASSING tests that nobody ever opens! Uploading 8 GB of passing videos slows CI by 10 minutes and burns cloud storage budget. Instead, buffer in RAM and persist artifacts ONLY on `FAILED` or `ERROR`!",
    "Playwright deletes failing videos automatically",
    "CI runs 50% faster when writing gigabytes to disk"
  ],
  "answerIndex": 1,
  "explanation": "Saving heavy artifacts (videos, DOM snapshots, HAR files) for the 99% of tests that pass wastes massive I/O time and storage (`retain-on-failure` in Playwright / failure-only ring buffers in `MiniTest` cut storage by >95%)."
}
```

## 🌱 Step 1: Plain-English Story — The Car Dashcam & The Package Tracking Number

Look back at how `MiniTest` reported test results in Chapter 01:
`print(f"✗ FAIL: {fn.__name__} -> {err}")`

When you run 3 tests on your own laptop, `print()` is fine.
Now imagine you have **500 AeroCart tests** running at 2:00 AM on a remote CI server, and `test_vip_checkout` fails with `HTTP 500 Internal Server Error`.
With plain `print()`, three painful things happen:
1. **Dashboards Are Blind**: GitHub Actions, Jenkins, and Allure can't build pass/fail charts or track flaky tests from raw `print()` lines—they need a structured file (`results.json` or `junit.xml`).
2. **No Crime-Scene Photos (Or Too Many!)**: If you don't save the HTTP request/screenshot, you can't tell *why* it failed. If you save videos for all 500 passing tests, your CI disk fills up in a week!
3. **The Backend Black Box**: The test says `"HTTP 500"`, and the backend engineer says *"I have 50,000 log lines on the server—which one was your test?!"*

```mermaid
flowchart LR
  Run["Test Runs (With trace_id + RAM Dashcam)"] --> Check{"Did Test Pass?"}
  Check -->|"✓ PASSED"| Drop["Discard RAM Dashcam (0 Disk Used!)"]
  Check -->|"✗ FAILED"| Save["Write JSON/XML Report + Redacted cURL + trace_id Link!"]
```

**How do we upgrade `MiniTest v0.9` so debugging any 2 AM failure takes 30 seconds instead of 45 minutes?**
We borrow two ideas from everyday life:
1. **The Car Dashcam (`retain-on-failure`)**: While a test runs, record every step (clicks, API calls, headers) into a temporary list in memory. If the test **passes**, throw the list in the trash (`0` disk space used!). If the test **fails**, attach that list + a ready-to-paste **`curl` command** (with secrets masked as `***REDACTED***`) to a structured **JSON / XML Report**!
2. **The FedEx Tracking Number (`traceparent`)**: Give every test its own unique **`trace_id`** and send it in the HTTP header (`traceparent`). When a test fails, the report prints that `trace_id` so you can find the exact crashing SQL query on the backend server in 1 second!

## 🔨 Step 2: First Lines of Code — Add a Pluggable Reporter & Dashcam to `MiniTest v0.9`!

Let's build a **Failure-Only Dashcam + Structured JSON Reporter** into `MiniTest v0.9` in **19 lines of Python**! Watch how a passing test saves `0` forensic attachments (keeping reports tiny), while a failing test automatically attaches the recorded steps and `trace_id`!

```python
import uuid


def run_with_reporter(test_fn) -> dict:
    trace_id = uuid.uuid4().hex[:16]
    dashcam_log = []  # In-memory buffer: only kept if the test FAILS!

    def record_step(step: str):
        dashcam_log.append(f"[trace={trace_id}] {step}")

    try:
        test_fn(record_step)
        # Test PASSED! Throw away dashcam_log so we waste ZERO disk/report space!
        return {"test": test_fn.__name__, "status": "PASSED", "trace_id": trace_id, "forensics": []}
    except AssertionError as err:
        # Test FAILED! Flush dashcam_log into the structured report!
        return {"test": test_fn.__name__, "status": "FAILED", "error": str(err), "trace_id": trace_id, "forensics": dashcam_log}


# --- Verify: Passing test discards dashcam; Failing test preserves dashcam! ---
pass_rep = run_with_reporter(lambda log: log("GET /flights -> 200 OK"))
fail_rep = run_with_reporter(lambda log: (log("POST /pay -> 449.80"), (_ for _ in ()).throw(AssertionError("Expected 360")))[1])
assert pass_rep["forensics"] == [] and len(fail_rep["forensics"]) == 1
```

### Java 17 Equivalent (`MiniStructuredReporter.java` — Mirrors JUnit 5 `TestWatcher`)

```java
import java.util.*;

public class MiniStructuredReporter {
    public record TestReport(String name, String status, String traceId, List<String> forensics) {}

    public static TestReport runWithDashcam(String name, java.util.function.Consumer<List<String>> testBody) {
        String traceId = UUID.randomUUID().toString().substring(0, 16);
        List<String> dashcam = new ArrayList<>();
        try {
            testBody.accept(dashcam);
            // PASSED: discard dashcam buffer (empty list)!
            return new TestReport(name, "PASSED", traceId, List.of());
        } catch (AssertionError err) {
            // FAILED: preserve full forensic trail + traceId!
            return new TestReport(name, "FAILED", traceId, List.copyOf(dashcam));
        }
    }

    public static void main(String[] args) {
        TestReport pass = runWithDashcam("testOk", log -> log.add("GET /health -> 200"));
        TestReport fail = runWithDashcam("testBug", log -> {
            log.add("POST /pay -> 449.80");
            throw new AssertionError("Expected 360.0");
        });
        assert pass.forensics().isEmpty() && fail.forensics().size() == 1;
    }
}
```

**Look at `pass_rep["forensics"] == []` vs. `fail_rep["forensics"]`**: when 499 tests pass and 1 test fails, your CI report isn't bloated with 499 useless logs—it contains the **exact forensic crime scene for the 1 test that failed**!

## ⚡ Step 3: Where It Breaks in Real Life — Leaking Bearer Tokens in Failure Reports!

Now watch the **#1 security disaster** that happens when teams build auto-attached `cURL` reproducers and failure HAR files:

Suppose `test_vip_checkout` fails with `HTTP 500`, and your helpful reporter automatically prints the failed HTTP request into `junit.xml` and Allure HTML so developers can copy-paste it:
`curl -X POST https://staging.aerocart.io/pay -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." -d '{"card_pan": "4111222233334444"}'`

Wait—who can view `junit.xml` and Allure HTML artifacts in GitHub Actions or Jenkins? **Every contractor, intern, and third-party plugin in the company (or the entire public internet on an open-source repo)!**
If your reporter writes raw `Authorization`, `Cookie`, `X-API-Key`, or credit card numbers to disk without **automatic secret redaction**, your test framework just caused a security breach!

```json contrast
{
  "title": "Raw Console Prints & Unredacted Dumps vs. Failure-Only Redacted OTel Forensics",
  "naiveTitle": "Always-On Disk Videos + Raw Unredacted Headers",
  "naiveMetric": "10 GB Wasted Storage · Leaked Auth Tokens in CI",
  "naivePoints": [
    "Saves videos, screenshots, and HAR files for all 1,000 passing tests, slowing CI uploads to a crawl",
    "Dumps raw `Authorization: Bearer ...` and `Cookie` headers directly into `junit.xml` and Allure HTML",
    "Prints `HTTP 500` with zero correlation ID, forcing engineers to grep 50,000 backend log lines manually"
  ],
  "staffTitle": "Failure-Only Ring Buffer + PII Redactor + W3C `traceparent` + JUnit/Allure Schema",
  "staffMetric": "95% Less Storage · Zero Leaked Secrets · 1-Click Backend Trace",
  "staffPoints": [
    "Buffers breadcrumbs in RAM and flushes DOM/HAR/`cURL` artifacts to disk ONLY when a test fails or errors",
    "Scrubs sensitive keys (`authorization`, `cookie`, `x-api-key`, `password`, `cvv`) to `***REDACTED***` before touching disk",
    "Injects W3C `traceparent` (`00-<trace_id>-<span_id>-01`) so every failure links directly to backend OpenTelemetry spans"
  ]
}
```

Explore the **OpenTelemetry & Failure Forensics Simulator** below to trace how a failed test in `MiniTest v0.9` links to backend spans and generates a sanitized `cURL` reproducer!

## 🚀 Step 4: Staff Engineer Deep-Dive — Storage Economics & W3C `traceparent` Specification

Let's calculate how much CI storage and upload time **Failure-Only Ring Retention** saves on a suite of $N = 2,000$ E2E tests running $R = 50$ times per day with failure rate $f = 0.02$ ($2\%$) and per-test artifact size $S = 5\text{ MB}$ (trace zip + video + HAR):

$$\text{Daily Storage}_{\text{always-on}} = N \times R \times S = 2,000 \times 50 \times 5\text{ MB} = 500,000\text{ MB} = \mathbf{500\text{ GB / day!}}$$

$$\text{Daily Storage}_{\text{failure-only}} = N \times R \times f \times S = 2,000 \times 50 \times 0.02 \times 5\text{ MB} = \mathbf{10\text{ GB / day (98\% reduction!)}}$$

And to link every test failure directly to backend logs in Grafana Tempo / Jaeger / Datadog, we format the **W3C Trace Context (`traceparent`)** header according to the official specification:

$$\texttt{traceparent} = \underbrace{\texttt{00}}_{\text{version}} - \underbrace{\texttt{4bf92f3577b34da6a3ce929d0e0e4736}}_{\text{128-bit (32-hex) trace\_id}} - \underbrace{\texttt{00f067aa0ba902b7}}_{\text{64-bit (16-hex) span\_id}} - \underbrace{\texttt{01}}_{\text{sampled flag}}$$

| Reporting Layer | Our `MiniTest v0.9` | `Pytest` Ecosystem (Python 3) | `JUnit 5` Ecosystem (Java 17) |
| :--- | :--- | :--- | :--- |
| **Hook Lifecycle** | `ReporterPlugin.on_test_end(report)` | `pytest_runtest_makereport` (`conftest.py` hookwrapper) | `TestWatcher` / `AfterTestExecutionCallback` |
| **CI XML / JSON Output** | `to_junit_xml()` + `to_allure_json()` | `pytest --junitxml=report.xml` / `allure-pytest` | Maven Surefire `TEST-*.xml` / `allure-junit5` |
| **Failure-Only Artifacts** | Flush RAM buffer on `FAILED`/`ERROR` | Playwright `--tracing retain-on-failure` | JUnit `ExtensionContext.getExecutionException().isPresent()` |
| **Distributed Trace Link** | `make_w3c_traceparent()` | `opentelemetry-instrumentation-requests` | `opentelemetry-javaagent` / `W3CTraceContextPropagator` |

### Production Blueprint: W3C `traceparent` Generator + Secret-Redacted `cURL` Builder + JUnit XML Emitter

```python
from dataclasses import dataclass, field
import html
from typing import Dict, List, Tuple
import uuid

SENSITIVE_KEYS = {"authorization", "cookie", "set-cookie", "x-api-key", "password", "secret", "token"}


def make_w3c_traceparent() -> Tuple[str, str]:
    """Returns (trace_id, w3c_traceparent_header) following W3C Trace Context spec."""
    trace_id = uuid.uuid4().hex              # 32 lowercase hex chars (128-bit)
    span_id = uuid.uuid4().hex[:16]          # 16 lowercase hex chars (64-bit)
    return trace_id, f"00-{trace_id}-{span_id}-01"


def build_redacted_curl(method: str, url: str, headers: Dict[str, str], body: str = "") -> str:
    """Builds a copy-pasteable cURL reproducer with all auth secrets scrubbed to ***REDACTED***."""
    parts = [f"curl -X {method} '{url}'"]
    for k, v in headers.items():
        safe_val = "***REDACTED***" if k.lower() in SENSITIVE_KEYS else v
        parts.append(f"-H '{k}: {safe_val}'")
    if body:
        parts.append(f"-d '{body}'")
    return " \\\n  ".join(parts)


@dataclass
class TestCaseReport:
    name: str
    classname: str
    duration_sec: float
    status: str  # "PASSED" | "FAILED" | "ERROR"
    trace_id: str
    failure_message: str = ""
    forensic_attachments: List[str] = field(default_factory=list)


def export_junit_xml(suite_name: str, reports: List[TestCaseReport]) -> str:
    """Emits standard JUnit XML consumable by GitHub Actions, GitLab CI, Jenkins, and Datadog CI."""
    failures = sum(1 for r in reports if r.status == "FAILED")
    errors = sum(1 for r in reports if r.status == "ERROR")
    lines = [f'<testsuite name="{html.escape(suite_name)}" tests="{len(reports)}" failures="{failures}" errors="{errors}">']
    for r in reports:
        lines.append(f'  <testcase classname="{html.escape(r.classname)}" name="{html.escape(r.name)}" time="{r.duration_sec:.3f}">')
        if r.status in ("FAILED", "ERROR"):
            tag = "failure" if r.status == "FAILED" else "error"
            body = f"trace_id={r.trace_id}\n" + "\n".join(r.forensic_attachments)
            lines.append(f'    <{tag} message="{html.escape(r.failure_message)}">{html.escape(body)}</{tag}>')
        lines.append("  </testcase>")
    lines.append("</testsuite>")
    return "\n".join(lines)
```

### Java 17 Equivalent (W3C `traceparent` + Redacted `cURL` + JUnit 5 `TestWatcher` Pattern)

```java
import java.util.*;

public class ForensicReporter {
    private static final Set<String> SECRET_HEADERS = Set.of("authorization", "cookie", "x-api-key");

    public static String makeTraceparent(String traceId32Hex, String spanId16Hex) {
        return "00-" + traceId32Hex + "-" + spanId16Hex + "-01";
    }

    public static String buildRedactedCurl(String method, String url, Map<String, String> headers) {
        StringBuilder sb = new StringBuilder("curl -X ").append(method).append(" '").append(url).append("'");
        headers.forEach((k, v) -> {
            String safeVal = SECRET_HEADERS.contains(k.toLowerCase(Locale.ROOT)) ? "***REDACTED***" : v;
            sb.append(" -H '").append(k).append(": ").append(safeVal).append("'");
        });
        return sb.toString();
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Why Pytest Local-Variable Tracebacks Can Leak Secrets Unless Redacted!**
> Remember in Chapter 01 how Pytest prints the values of local variables whenever an `assert` fails (`--showlocals` / default traceback)? If a test function has `api_key = os.environ["STRIPE_LIVE_KEY"]` in a local variable and the test fails 10 lines later, **Pytest will print `api_key = 'sk_live_998877...'` straight into `junit.xml` and the public CI console!**
> **Fix**: Never hold raw secret strings in test local variables—wrap secrets in an opaque **`SecretStr`** object whose `__repr__` always prints `'***REDACTED***'`! (We will build `SecretStr` right now in Chapter 10!)

**Up Next in Chapter 10 (Course 02 Finale!)**: Speaking of leaked `api_key` strings and hardcoded `http://localhost:8090` URLs—how do we add **Multi-Environment Typed Config (`local` / `staging` / `prod-canary`), `SecretStr` Zero-Leak Credentials, Production Safety Guardrails, and `pyproject.toml` / Maven SDK Packaging** to ship **`MiniTest v1.0`** to the entire engineering org? Let's finish `MiniTest v1.0` in Chapter 10!

```json quiz
[
  {
    "id": "fw-09-q1",
    "question": "Why do Staff test frameworks use 'Failure-Only Ring Retention' (recording steps/traces in memory, discarding them on `PASSED`, and saving to disk only on `FAILED`/`ERROR`)?",
    "options": [
      "Because passing tests never execute any code",
      "Because in a healthy suite where 98% of tests pass, saving heavy videos/HARs/DOM snapshots for passing tests wastes ~98% of CI disk I/O and cloud storage on files nobody ever looks at",
      "Because hard drives cannot store JSON files",
      "Because JUnit XML only lists failed tests"
    ],
    "answerIndex": 1,
    "explanation": "Buffering forensic breadcrumbs in RAM and flushing to disk strictly on `FAILED`/`ERROR` gives 100% failure visibility while cutting storage and upload time by >95%."
  },
  {
    "id": "fw-09-q2",
    "question": "What does injecting a W3C `traceparent` header (`00-<trace_id>-<span_id>-01`) into every test HTTP request unlock when a test fails with `HTTP 500`?",
    "options": [
      "It automatically fixes the SQL syntax error on the server",
      "It propagates the test's unique `trace_id` across every backend microservice and database query, allowing the failure report to print a 1-click link straight to the exact crashing backend span in Tempo/Jaeger/Datadog",
      "It bypasses authentication",
      "It compresses the JSON response"
    ],
    "answerIndex": 1,
    "explanation": "W3C `traceparent` bridges the gap between the test runner and backend distributed tracing, eliminating manual log grepping."
  },
  {
    "id": "fw-09-q3",
    "question": "Before a test reporter writes an auto-generated `cURL` command or HAR file to disk on failure, what mandatory security step must run first?",
    "options": [
      "Convert all URLs to uppercase",
      "Scrub sensitive headers and fields (`Authorization`, `Cookie`, `X-API-Key`, passwords, credit card PANs) to `***REDACTED***` so CI artifacts (`junit.xml`, Allure HTML) never leak live credentials",
      "Delete the test file",
      "Wait 60 seconds"
    ],
    "answerIndex": 1,
    "explanation": "CI test reports and artifact zips are broadly accessible; redaction must happen in memory before any forensic payload is written to disk."
  }
]
```
