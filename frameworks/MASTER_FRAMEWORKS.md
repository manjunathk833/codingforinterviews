# 🚀 MAANG SDET Frameworks & System Design Master Sheet

Welcome to the **Automation Framework & SDET System Design Roadmap**, specifically curated for Senior SDET / QA Architect / SWE-Infra interviews at top-tier tech companies.

---

## ✈️ Benchmark Application Under Test (AUT)

All frameworks test the built-in **AeroCart Airline Booking & Merchant Platform** ([`apps/aerocart/server.py`](../apps/aerocart/server.py)):
- **Single Page App (UI):** Flight search, seat selection grid, JWT login modal, dynamic checkout.
- **Microservice REST API:** Flights, orders saga (asynchronous state transitions), chaos latency (504 timeout), rate limiting (429).
- **AI Concierge Endpoint:** RAG policy assistant with grounded, hallucinated, and irrelevant evaluation modes.
- **Run Standalone:** `python3 apps/aerocart/server.py 8000`

---

## 🏗️ Framework Modules & Architectures

| Module | Stack | Architecture Patterns | Target System | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1. REST Assured API Suite** | Java 17, REST Assured, TestNG, Jackson | Builder Pattern, Request/Response Specs, Custom Filters, POJOs | AeroCart REST APIs | `Ready` |
| **2. Pytest API Automation** | Python 3.9+, Requests, Pytest, Pydantic | Session pooling, Custom Pytest Fixtures, Schema Contract validation | AeroCart REST APIs | `Ready` |
| **3. Playwright UI Suite (Python)** | Python, Playwright, Pytest | Page Object Model (POM), Auto-waiting, Network intercepting | AeroCart UI SPA | `Ready` |
| **4. Playwright UI Suite (Java)** | Java 17, Playwright Java, TestNG | Thread-safe Playwright thread, Fluent Page Objects | AeroCart UI SPA | `Ready` |
| **5. Selenium Enterprise Suite** | Java 17, Selenium 4, TestNG | `ThreadLocal<WebDriver>`, Explicit Wait Decorators, Factory Pattern | Cross-browser grid | `Ready` |
| **6. SDET System Design Katas** | Python 3.9+ & Java 17 | Dynamic Tenant Key Partitioning, Kafka Asynchronous Poller | Distributed Microservices | `In Progress` |

---

## 🎯 SDET System Design & Architecture Katas

| Kata # | Problem Title | Architecture Core | Challenge Link | Status |
| :-: | :--- | :--- | :--- | :---: |
| **KATA-01** | [Distributed Concurrency & Tenant Isolation](./sdet-system-design/01-distributed-concurrency-isolation/) | 32 parallel threads, race condition mitigation, dynamic tenant UUID keys | [README](./sdet-system-design/01-distributed-concurrency-isolation/README.md) | `In Progress` |

---

## 🎯 Top-Tier MAANG SDET Live Coding Challenges

All 5 core framework coding challenges are fully implemented in both **Java and Python** with native test harnesses:

| Challenge # | Problem Title | Concepts Tested | Status | Command |
| :-: | :--- | :--- | :---: | :--- |
| **CH-01** | [Custom Retry Analyzer with Exponential Backoff](./design-challenges/01-custom-retry-analyzer/) | TestNG `IRetryAnalyzer`, Concurrency, State Tracking | `Passed` | `./run.sh test 01-custom-retry-analyzer` |
| **CH-02** | [Deep JSON Payload Diff Engine](./design-challenges/02-json-payload-diff-engine/) | Tree recursion, unordered JSON array matching, fuzzy tolerance | `Passed` | `./run.sh test 02-json-payload-diff-engine` |
| **CH-03** | [Thread-Safe Rate-Limited API Client](./design-challenges/03-rate-limited-test-client/) | Token Bucket algorithm, Mutex/Locks, HTTP throttling | `Passed` | `./run.sh test 03-rate-limited-test-client` |
| **CH-04** | [Dynamic Test Data Factory & Builder](./design-challenges/04-test-data-builder/) | Fluent Builder pattern, reflection, immutability, deep clone | `Passed` | `./run.sh test 04-test-data-builder` |
| **CH-05** | [Microservice Mock Server with Fault Injection](./design-challenges/05-microservice-mocking/) | Mocking latency, fault injection, dynamic stubs, verification | `Passed` | `./run.sh test 05-microservice-mocking` |

---

## 🛠️ Running Framework Suites

### API Automation (Python)
```bash
python3 frameworks/api-automation/pytest-requests-python/test_api.py
```

### UI Automation (Python Playwright)
```bash
python3 frameworks/ui-automation/playwright-python/test_e2e_journey.py
```

### Framework Coding Challenges (Dual Java & Python)
```bash
./run.sh test 01-custom-retry-analyzer
./run.sh test 02-json-payload-diff-engine
./run.sh test 03-rate-limited-test-client
./run.sh test 04-test-data-builder
./run.sh test 05-microservice-mocking
```
