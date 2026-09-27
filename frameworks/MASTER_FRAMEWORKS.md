# 🚀 MAANG SDET Frameworks & System Design Master Sheet

Welcome to the **Automation Framework & SDET System Design Roadmap**, specifically curated for Senior SDET / QA Architect / SWE-Infra interviews at top-tier tech companies.

---

## 🏗️ Framework Modules & Architectures

| Module | Stack | Architecture Patterns | Core Capabilities | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1. REST Assured API Suite** | Java 17, REST Assured, TestNG, Jackson | Builder Pattern, Request/Response Specs, Custom Filters, POJOs | Bearer Auth, JSON Schema validation, centralized logging, Allure integration | `Scaffolded` |
| **2. Pytest API Automation** | Python 3.9+, Requests, Pytest, Pydantic | Session pooling, Custom Pytest Fixtures, Schema Contract validation | Dynamic payloads, auth caching, parallel execution with `pytest-xdist` | `Scaffolded` |
| **3. Playwright UI Suite (Python)** | Python, Playwright, Pytest | Page Object Model (POM), Auto-waiting, Network intercepting | Headless/Headed, multi-context browser isolation, visual snapshots | `Scaffolded` |
| **4. Playwright UI Suite (Java)** | Java 17, Playwright Java, TestNG | Thread-safe Playwright thread, Fluent Page Objects | Resilient locators, network request mocking, video & trace capturing | `Ready` |
| **5. Selenium Enterprise Suite** | Java 17, Selenium 4, TestNG | `ThreadLocal<WebDriver>`, Explicit Wait Decorators, Factory Pattern | Cross-browser grid, retry listeners, shadow-DOM / iframe handling | `Ready` |

---

## 🎯 Top-Tier MAANG SDET Live Coding Challenges

MAANG SDET interviews commonly feature 45-minute live coding rounds testing your ability to write **framework utilities, concurrency-safe drivers, and custom algorithms** from scratch without third-party helpers:

| Challenge # | Problem Title | Concepts Tested | Status |
| :-: | :--- | :--- | :---: |
| **CH-01** | [Custom Retry Analyzer with Exponential Backoff](./design-challenges/01-custom-retry-analyzer/) | TestNG `IRetryAnalyzer`, Concurrency, State Tracking | `Included` |
| **CH-02** | [Deep JSON Payload Diff Engine](./design-challenges/02-json-payload-diff-engine/) | Tree recursion, unordered JSON array matching, fuzzy tolerance | `Included` |
| **CH-03** | [Thread-Safe Rate-Limited API Client](./design-challenges/03-rate-limited-test-client/) | Token Bucket algorithm, Mutex/Locks, HTTP throttling | `Roadmap` |
| **CH-04** | [Dynamic Test Data Factory & Builder](./design-challenges/04-test-data-builder/) | Fluent Builder pattern, reflection, immutability | `Roadmap` |
| **CH-05** | [Microservice Mock Server with WireMock](./design-challenges/05-microservice-mocking/) | Mocking latency, fault injection, dynamic stubs | `Roadmap` |

---

## 🛠️ Running Framework Suites

### API Automation (Python)
```bash
cd frameworks/api-automation/pytest-requests-python
python3 -m unittest test_users_api.py
```

### UI Automation (Python Playwright)
```bash
cd frameworks/ui-automation/playwright-python
python3 -m unittest test_login.py
```

### Framework Coding Challenges
Every design challenge follows the standard dual-language runner:
```bash
./run.sh test frameworks/design-challenges/01-custom-retry-analyzer
```
