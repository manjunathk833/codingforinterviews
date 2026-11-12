#!/usr/bin/env python3
from __future__ import annotations
"""
The Hub of Learning — SQLite WAL + FTS5 Hybrid Storage Engine (`hub/storage.py`).

Implements the Local-First Hybrid Storage Architecture:
- Git-tracked Markdown & code files on disk are the human-readable Source of Truth.
- SQLite (`hub/hub.db`) in WAL mode with FTS5 (`kb_fts`) powers the 8 Prioritized Textbook Courses,
  the 6 Banked Scientific Visual-Aid Learning Blocks, Engineering Pulse Newsfeed, Local Workbench, and Mock Interviews.
"""
import hashlib
import json
import math
import pathlib
import re
import sqlite3
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from hub import newsfeed_engine, state_manager

HUB_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HUB_DIR.parent
DEFAULT_DB_PATH = HUB_DIR / "hub.db"

_DB_LOCK = threading.RLock()
_INITIALIZED_DBS: Dict[str, str] = {}

# ==============================================================================
# THE 8 PRIORITIZED "TEXTBOOK COURSES" MASTER CATALOG (EXACT PRIORITY ORDER)
# ==============================================================================
TEXTBOOK_COURSES_CATALOG: List[Dict[str, Any]] = [
    {
        "courseId": "01-zero-to-staff-sdet",
        "priorityRank": 1,
        "title": "01. Zero to Staff SDET",
        "shortTitle": "Zero to Staff SDET",
        "levelSpan": "Zero → Senior → Staff SDET",
        "plannedModules": 4,
        "plannedChapters": 12,
        "accentColor": "#C85A32",
        "pillBg": "#FCEEE8",
        "tagline": "First-principles determinism, flakiness combinatorics (p^N), seam economics, 32-worker tenant isolation, CI sharding, OpenTelemetry RCA & Staff RFCs.",
    },
    {
        "courseId": "02-building-testing-frameworks",
        "priorityRank": 2,
        "title": "02. Zero to Mastery: Building Testing Frameworks",
        "shortTitle": "Building Testing Frameworks",
        "levelSpan": "Zero → Framework Architect",
        "plannedModules": 4,
        "plannedChapters": 10,
        "accentColor": "#2B6CB0",
        "pillBg": "#EBF8FF",
        "tagline": "Runner lifecycles, DI fixtures, POM vs Screenplay vs App Actions, fluent immutable data builders, AST JSON diffing, smart retries & SDK packaging.",
    },
    {
        "courseId": "03-ui-automation-playwright",
        "priorityRank": 3,
        "title": "03. Zero to Mastery: UI Automation (Playwright-Focused)",
        "shortTitle": "UI Automation (Playwright)",
        "levelSpan": "Zero → Browser & CDP Internals",
        "plannedModules": 4,
        "plannedChapters": 10,
        "accentColor": "#1E6F5C",
        "pillBg": "#E6F4F0",
        "tagline": "CDP & WebDriver BiDi pipes, BrowserContext memory math, Accessibility getByRole locators, 5 actionability gates, HAR routing, storageState & sharded traces.",
    },
    {
        "courseId": "04-api-and-api-automation",
        "priorityRank": 4,
        "title": "04. Zero to Mastery: API & API Automation",
        "shortTitle": "API & API Automation",
        "levelSpan": "HTTP/REST → gRPC, GraphQL & Pact",
        "plannedModules": 4,
        "plannedChapters": 10,
        "accentColor": "#0F766E",
        "pillBg": "#E6FFFA",
        "tagline": "TCP/TLS 1.3, HTTP/2 pooling, JWT/OAuth2/mTLS, Pytest + Pydantic & Java 17 REST Assured pipelines, 429 Token Buckets, GraphQL, gRPC & Pact contracts.",
    },
    {
        "courseId": "05-ai-engineering",
        "priorityRank": 5,
        "title": "05. Zero to Mastery: AI Engineering",
        "shortTitle": "AI Engineering (ML → LLMs)",
        "levelSpan": "Classical ML → Transformers, RAG & Agents",
        "plannedModules": 5,
        "plannedChapters": 12,
        "accentColor": "#5B3FD9",
        "pillBg": "#F0EBFF",
        "tagline": "Loss functions, embeddings, Scaled Dot-Product Attention, RoPE, KV-Cache, Quantization, Hybrid BM25+HNSW+RRF RAG, LoRA/DPO & Autonomous MCP Agents.",
    },
    {
        "courseId": "06-ai-engineering-qa-focused",
        "priorityRank": 6,
        "title": "06. Zero to Mastery: AI Engineering — QA Focused",
        "shortTitle": "AI Engineering — QA Focused",
        "levelSpan": "Deterministic Evals → Judge Calibration & Red-Teaming",
        "plannedModules": 4,
        "plannedChapters": 10,
        "accentColor": "#7C3AED",
        "pillBg": "#F5F3FF",
        "tagline": "Golden datasets, RAG Triad claim entailment, negation traps, LLM-as-a-Judge debiasing & Rogan-Gladen calibration, prompt-injection red-teaming & AST self-healing.",
    },
    {
        "courseId": "07-distributed-system-design",
        "priorityRank": 7,
        "title": "07. Distributed System Design",
        "shortTitle": "Distributed System Design",
        "levelSpan": "Foundations → Staff Systems Resilience",
        "plannedModules": 2,
        "plannedChapters": 5,
        "accentColor": "#B45309",
        "pillBg": "#FEF3C7",
        "tagline": "Bounded ring-buffer backpressure, AWS Full Jitter, consistent hashing with virtual nodes, transactional outbox CDC, singleflight caching & quorum consensus.",
    },
    {
        "courseId": "08-core-cs-internals",
        "priorityRank": 8,
        "title": "08. Core CS: OS, Networking & Storage",
        "shortTitle": "Core CS: OS, Networks & Storage",
        "levelSpan": "Kernel, TCP/TLS 1.3 & Storage Engines",
        "plannedModules": 2,
        "plannedChapters": 5,
        "accentColor": "#374151",
        "pillBg": "#F3F4F6",
        "tagline": "Linux virtual memory, post-GC RSS leak slopes, TCP SYN backlogs, TLS 1.3/HTTP2, B+Trees vs LSM-Trees, SQLite WAL isolation, CAS atomics & epoll/cgroups.",
    },
    {
        "courseId": "09-sql-and-data-engineering",
        "priorityRank": 9,
        "title": "09. SQL, PostgreSQL & Data Validation Engineering",
        "shortTitle": "SQL, Postgres & Data QA",
        "levelSpan": "Absolute Zero → Staff Data & Ledger QA",
        "plannedModules": 3,
        "plannedChapters": 10,
        "accentColor": "#0F766E",
        "pillBg": "#CCFBF1",
        "tagline": "AeroLedger (v0.1→v1.0): 3VL NULL safety, 1:N join fan-out, window dedup/LAG, B+Tree sargability, EXPLAIN (ANALYZE, BUFFERS), MVCC FOR UPDATE SKIP LOCKED, zero-downtime migrations & Stripe double-entry ledgers.",
    },
    {
        "courseId": "10-docker-cicd-and-cloud-infra",
        "priorityRank": 10,
        "title": "10. Docker, Kubernetes, CI/CD & Quality Infrastructure",
        "shortTitle": "Docker, K8s & CI/CD Infra",
        "levelSpan": "Absolute Zero → Staff Quality Platform",
        "plannedModules": 3,
        "plannedChapters": 10,
        "accentColor": "#0369A1",
        "pillBg": "#E0F2FE",
        "tagline": "AeroPipe (v0.1→v1.0): Linux namespaces/cgroups, BuildKit multi-stage Dockerfiles, Compose healthcheck DAGs, Testcontainers + Ryuk, K8s probes & Exit 137 RCA, LPT CI sharding & ephemeral PR namespaces.",
    },
    {
        "courseId": "11-performance-chaos-and-sre",
        "priorityRank": 11,
        "title": "11. Performance, Load, Chaos & Reliability Engineering",
        "shortTitle": "Performance, Chaos & SRE",
        "levelSpan": "Absolute Zero → Staff Performance & SRE",
        "plannedModules": 3,
        "plannedChapters": 10,
        "accentColor": "#B91C1C",
        "pillBg": "#FEE2E2",
        "tagline": "AeroPulse (v0.1→v1.0): Little's Law, Coordinated Omission & HdrHistogram, k6/Locust open-loop arrival schedules, HikariCP/JVM/GIL flamegraphs, Toxiproxy chaos injection & Google SRE multi-window burn-rate SLOs.",
    },
    {
        "courseId": "12-app-api-and-ai-security",
        "priorityRank": 12,
        "title": "12. Application, API & AI Security Testing",
        "shortTitle": "App, API & AI Security QA",
        "levelSpan": "Absolute Zero → Staff AppSec & AI Red-Team",
        "plannedModules": 3,
        "plannedChapters": 10,
        "accentColor": "#4338CA",
        "pillBg": "#E0E7FF",
        "tagline": "AeroShield (v0.1→v1.0): Zero-Trust STRIDE, OWASP API Top 10 BOLA/IDOR, RFC 8725 JWT confusion, SQLi/XSS/CSP, Cloud IMDSv2 SSRF, Stripe HMAC webhooks, OWASP LLM Top 10 prompt-injection shields & SARIF CI gates.",
    },
]

COURSE_BY_ID: Dict[str, Dict[str, Any]] = {c["courseId"]: c for c in TEXTBOOK_COURSES_CATALOG}

FOLDER_TO_COURSE_ID: Dict[str, str] = {
    "01-zero-to-staff-sdet": "01-zero-to-staff-sdet",
    "02-building-testing-frameworks": "02-building-testing-frameworks",
    "03-ui-automation-playwright": "03-ui-automation-playwright",
    "04-api-and-api-automation": "04-api-and-api-automation",
    "05-ai-engineering": "05-ai-engineering",
    "06-ai-engineering-qa-focused": "06-ai-engineering-qa-focused",
    "ai-engineering": "06-ai-engineering-qa-focused",
    "07-distributed-system-design": "07-distributed-system-design",
    "system-design": "07-distributed-system-design",
    "08-core-cs-internals": "08-core-cs-internals",
    "core-cs": "08-core-cs-internals",
    "09-sql-and-data-engineering": "09-sql-and-data-engineering",
    "10-docker-cicd-and-cloud-infra": "10-docker-cicd-and-cloud-infra",
    "11-performance-chaos-and-sre": "11-performance-chaos-and-sre",
    "12-app-api-and-ai-security": "12-app-api-and-ai-security",
}

TRACK_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "id": "system-design",
        "title": "Distributed System Design & SDET Architecture",
        "archetype": "interactive-textbook",
        "archetypeLabel": "📖 Textbook Courses",
        "volume": "Textbook Courses (01, 02 & 07)",
        "tagline": "Zero to Staff SDET, Testing Frameworks, Backpressure, Consistent Hashing, Kafka Outbox & Sharding",
        "executionMode": "Course-Style Textbook Chapters + POE Simulators + Spatial SVGs + 1-Click Labs & Quizzes",
        "aiDependency": "Zero at runtime",
        "accentColor": "#C85A32",
    },
    {
        "id": "ai-engineering",
        "title": "AI Engineering & AI Quality Assurance",
        "archetype": "interactive-textbook",
        "archetypeLabel": "📖 Textbook Courses",
        "volume": "Textbook Courses (05 & 06)",
        "tagline": "Classical ML, Transformers, KV-Cache, Hybrid RAG, MCP Agents, RAG Triad Evals, Judge Calibration & AST Self-Healing",
        "executionMode": "Course-Style Textbook Chapters + POE Simulators + Spatial SVGs + 1-Click Labs & Quizzes",
        "aiDependency": "Zero at runtime (Deterministic Eval & ML Harnesses)",
        "accentColor": "#5B3FD9",
    },
    {
        "id": "core-cs",
        "title": "Playwright UI, API Contracts & Core CS Internals",
        "archetype": "interactive-textbook",
        "archetypeLabel": "📖 Textbook Courses",
        "volume": "Textbook Courses (03, 04 & 08)",
        "tagline": "Playwright CDP/BiDi, REST/gRPC/Pact Contracts, Linux Virtual Memory, TCP/TLS 1.3 & LSM-Tree Storage",
        "executionMode": "Course-Style Textbook Chapters + POE Simulators + Spatial SVGs + 1-Click Labs & Quizzes",
        "aiDependency": "Zero at runtime",
        "accentColor": "#1E6F5C",
    },
    {
        "id": "dsa",
        "title": "Algorithmic Foundations (DSA Studio)",
        "archetype": "in-browser-studio",
        "archetypeLabel": "💻 In-Browser 50/50 Split Studio (WS 1)",
        "volume": "15 Chapters · 128 Problems",
        "tagline": "3D Tactile Visualizers, 4-Tier Socratic Hints & Dual-Language Java 17 + Python 3 Studio",
        "executionMode": "In-Browser Code Editor synced atomically to dsa/<chapter>/<slug>/ with SHA-256 locking",
        "aiDependency": "Zero",
        "accentColor": "#B7791F",
    },
    {
        "id": "frameworks",
        "title": "SDET & Automation Frameworks Workbench",
        "archetype": "local-ide-workbench",
        "archetypeLabel": "🛠️ Local IDE Engineering Workbench (Zero AI)",
        "volume": "Local Multi-File Suites",
        "tagline": "Playwright, REST Assured, Pytest, Selenium, AeroCart AUT & 32-Worker Concurrency Katas",
        "executionMode": "Built in your Local IDE & verified 100% deterministically on your machine",
        "aiDependency": "Strictly Zero AI",
        "accentColor": "#2B6CB0",
    },
    {
        "id": "mock-interviews",
        "title": "Staff & Senior Mock Interview Simulator",
        "archetype": "mock-interview-simulator",
        "archetypeLabel": "🎙️ Interactive Mock Interview Studio",
        "volume": "100-Point Bar-Raiser Rubrics",
        "tagline": "Multi-Part Architectural Scenarios, 100-Point Bar-Raiser Rubrics & Textbook Course Deep-Links",
        "executionMode": "In-Browser Response Studio synced to mock-interviews/interview-N/",
        "aiDependency": "Hybrid (Deterministic Rubric Checklists + Optional Bar-Raiser Review)",
        "accentColor": "#9B2C2C",
    },
]

WORKBENCH_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "wb-concurrency-isolation",
        "title": "01. 32-Worker Distributed Concurrency & Tenant Isolation",
        "category": "SDET System Design",
        "stack": "Python 3 & Java 17 + AeroCart AUT",
        "folderPath": "frameworks/sdet-system-design/01-distributed-concurrency-isolation",
        "verifyCmd": [sys.executable, "frameworks/sdet-system-design/01-distributed-concurrency-isolation/reference_solution.py"],
        "cliDisplay": "python3 frameworks/sdet-system-design/01-distributed-concurrency-isolation/reference_solution.py",
        "invariant": "Namespace every worker payload with tenant_id + Idempotency-Key so 32 parallel threads achieve 32/32 (100%) isolated 201 Created responses.",
        "relatedChapter": "sdet-05-parallel-tenant-isolation",
    },
    {
        "id": "wb-custom-retry-analyzer",
        "title": "02. Custom Retry Analyzer & Flaky Quarantine Engine",
        "category": "Design Challenge",
        "stack": "Python 3 & Java 17",
        "folderPath": "frameworks/design-challenges/01-custom-retry-analyzer",
        "verifyCmd": [sys.executable, "frameworks/design-challenges/01-custom-retry-analyzer/solution.py"],
        "cliDisplay": "python3 frameworks/design-challenges/01-custom-retry-analyzer/solution.py",
        "invariant": "Classify transient network faults vs deterministic assertion failures and enforce bounded exponential backoff with jitter.",
        "relatedChapter": "sdet-01-determinism-and-flakiness-math",
    },
    {
        "id": "wb-json-payload-diff-engine",
        "title": "03. Recursive JSON Payload & Schema Diff Engine",
        "category": "Design Challenge",
        "stack": "Python 3 & Java 17",
        "folderPath": "frameworks/design-challenges/02-json-payload-diff-engine",
        "verifyCmd": [sys.executable, "frameworks/design-challenges/02-json-payload-diff-engine/solution.py"],
        "cliDisplay": "python3 frameworks/design-challenges/02-json-payload-diff-engine/solution.py",
        "invariant": "Recursively compare deeply nested API payloads while ignoring dynamic fields (UUIDs, timestamps) and reporting exact JSONPath mismatches.",
        "relatedChapter": "fw-05-recursive-payload-and-ast-diff-engines",
    },
    {
        "id": "wb-rate-limiter-backpressure",
        "title": "04. Token Bucket Rate-Limited Test Client & Backpressure",
        "category": "Design Challenge",
        "stack": "Python 3 & Java 17",
        "folderPath": "frameworks/design-challenges/03-rate-limited-test-client",
        "verifyCmd": [sys.executable, "frameworks/design-challenges/03-rate-limited-test-client/solution.py"],
        "cliDisplay": "python3 frameworks/design-challenges/03-rate-limited-test-client/solution.py",
        "invariant": "Enforce thread-safe Token Bucket refill rates and honor Retry-After headers without exceeding API quotas.",
        "relatedChapter": "fw-07-smart-retries-and-rate-limited-clients",
    },
    {
        "id": "wb-test-data-builder",
        "title": "05. Fluent Immutable Test Data Builder & Tenant Factory",
        "category": "Design Challenge",
        "stack": "Python 3 & Java 17",
        "folderPath": "frameworks/design-challenges/04-test-data-builder",
        "verifyCmd": [sys.executable, "frameworks/design-challenges/04-test-data-builder/solution.py"],
        "cliDisplay": "python3 frameworks/design-challenges/04-test-data-builder/solution.py",
        "invariant": "Construct thread-safe, immutable domain fixtures with deterministic defaults and zero shared mutable state across workers.",
        "relatedChapter": "fw-04-fluent-immutable-data-builders",
    },
    {
        "id": "wb-microservice-mocking",
        "title": "06. Stateful Microservice Stub & Contract Verifier",
        "category": "Design Challenge",
        "stack": "Python 3 & Java 17",
        "folderPath": "frameworks/design-challenges/05-microservice-mocking",
        "verifyCmd": [sys.executable, "frameworks/design-challenges/05-microservice-mocking/solution.py"],
        "cliDisplay": "python3 frameworks/design-challenges/05-microservice-mocking/solution.py",
        "invariant": "Simulate downstream latency, fault injection (503/429), and stateful request verification deterministically in local tests.",
        "relatedChapter": "sdet-03-test-pyramid-and-seam-economics",
    },
    {
        "id": "wb-playwright-ui-framework",
        "title": "07. Playwright UI Automation Architecture (Python & Java)",
        "category": "UI Automation Suite",
        "stack": "Playwright + CDP WebSockets + AeroCart AUT",
        "folderPath": "frameworks/ui-automation/playwright-python",
        "verifyCmd": [
            sys.executable,
            "-c",
            "import sys, unittest; sys.path.insert(0, 'frameworks/ui-automation/playwright-python'); "
            "suite = unittest.defaultTestLoader.discover('frameworks/ui-automation/playwright-python', pattern='test_*.py'); "
            "res = unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(0 if res.wasSuccessful() else 1)",
        ],
        "cliDisplay": "PYTHONPATH=frameworks/ui-automation/playwright-python python3 -m unittest discover -s frameworks/ui-automation/playwright-python -p 'test_*.py'",
        "invariant": "Role-based accessibility locators, network route interception, and zero-shared-state browser contexts per worker.",
        "relatedChapter": "pw-01-webdriver-http-vs-cdp-and-bidi-pipes",
    },
    {
        "id": "wb-api-automation-suite",
        "title": "08. API Automation Architecture (Pytest & REST Assured)",
        "category": "API Automation Suite",
        "stack": "Pytest + Requests / Java 17 REST Assured",
        "folderPath": "frameworks/api-automation/pytest-requests-python",
        "verifyCmd": [
            sys.executable,
            "-c",
            "import sys, unittest; sys.path.insert(0, 'frameworks/api-automation/pytest-requests-python'); "
            "suite = unittest.defaultTestLoader.discover('frameworks/api-automation/pytest-requests-python', pattern='test_*.py'); "
            "res = unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(0 if res.wasSuccessful() else 1)",
        ],
        "cliDisplay": "PYTHONPATH=frameworks/api-automation/pytest-requests-python python3 -m unittest discover -s frameworks/api-automation/pytest-requests-python -p 'test_*.py'",
        "invariant": "Typed request builders, token-bucket rate-limit resilience, and causal saga polling against AeroCart.",
        "relatedChapter": "api-04-production-api-clients-pydantic-and-rest-assured",
    },
    {
        "id": "wb-ci-shard-bin-packer-tia",
        "title": "09. LPT CI Shard Bin-Packer & AST Test Impact Analysis",
        "category": "SDET System Design",
        "stack": "Python 3 & Java 17",
        "folderPath": "frameworks/sdet-system-design/02-ci-shard-bin-packer-and-tia",
        "verifyCmd": [sys.executable, "frameworks/sdet-system-design/02-ci-shard-bin-packer-and-tia/solution.py"],
        "cliDisplay": "python3 frameworks/sdet-system-design/02-ci-shard-bin-packer-and-tia/solution.py",
        "invariant": "Balance K parallel CI shards in O(N log K) via LPT min-heap bin packing and compute safe reverse-AST test impact closures.",
        "relatedChapter": "sdet-07-ci-sharding-and-bin-packing",
    },
    {
        "id": "wb-sql-data-reconciliation",
        "title": "10. AeroLedger SQL Grain, Seat-12A Locking & Double-Entry Reconciliation",
        "category": "SQL & Data Validation",
        "stack": "Python 3 sqlite3 WAL & Java 17 JDBC",
        "folderPath": "frameworks/data-validation/01-sql-reconciliation-and-isolation",
        "verifyCmd": [sys.executable, "frameworks/data-validation/01-sql-reconciliation-and-isolation/reference_solution.py"],
        "cliDisplay": "python3 frameworks/data-validation/01-sql-reconciliation-and-isolation/reference_solution.py",
        "invariant": "Prevent 1:N join fan-out, deduplicate webhooks with ROW_NUMBER(), enforce covering B-Tree plans, serialize 16-thread Seat-12A claims, and assert SUM(debits) == SUM(credits).",
        "relatedChapter": "sql-10-event-to-warehouse-reconciliation-and-data-qa",
    },
    {
        "id": "wb-cicd-container-sharding",
        "title": "11. AeroPipe Dockerfile Layer Auditor, K8s cgroup Guard & LPT CI Shard Orchestrator",
        "category": "Docker, K8s & CI/CD Infra",
        "stack": "Python 3 & Java 17 + Docker/K8s Specs",
        "folderPath": "frameworks/cicd-infra/01-container-and-sharding-orchestrator",
        "verifyCmd": [sys.executable, "frameworks/cicd-infra/01-container-and-sharding-orchestrator/reference_solution.py"],
        "cliDisplay": "python3 frameworks/cicd-infra/01-container-and-sharding-orchestrator/reference_solution.py",
        "invariant": "Enforce lockfile-first multi-stage Docker caching, prevent K8s Exit 137 via JVM MaxRAMPercentage <= 75% pod limit, and balance K parallel CI shards via LPT bin packing.",
        "relatedChapter": "infra-07-dynamic-ci-matrix-sharding-and-bin-packing",
    },
    {
        "id": "wb-perf-chaos-sre-harness",
        "title": "12. AeroPulse Open-Loop Load, Coordinated Omission Corrector & Toxiproxy Chaos Gate",
        "category": "Performance, Chaos & SRE",
        "stack": "Python 3 & Java 17 + HdrHistogram/SLO Math",
        "folderPath": "frameworks/performance-sre/01-load-coordinated-omission-and-chaos",
        "verifyCmd": [sys.executable, "frameworks/performance-sre/01-load-coordinated-omission-and-chaos/reference_solution.py"],
        "cliDisplay": "python3 frameworks/performance-sre/01-load-coordinated-omission-and-chaos/reference_solution.py",
        "invariant": "Correct closed-loop Coordinated Omission latency distortion, size HikariCP pools via Little's Law, trip/recover Circuit Breakers under chaos faults, and evaluate 14.4x/6x multi-window SLO burn rates.",
        "relatedChapter": "perf-02-coordinated-omission-and-open-vs-closed-loops",
    },
    {
        "id": "wb-security-bola-jwt-llm",
        "title": "13. AeroShield BOLA/IDOR, JWT RFC 8725, SSRF Socket Guard & LLM Prompt-Injection Gate",
        "category": "App, API & AI Security",
        "stack": "Python 3 & Java 17 + OWASP API/LLM Top 10",
        "folderPath": "frameworks/security-testing/01-bola-jwt-and-prompt-shield",
        "verifyCmd": [sys.executable, "frameworks/security-testing/01-bola-jwt-and-prompt-shield/reference_solution.py"],
        "cliDisplay": "python3 frameworks/security-testing/01-bola-jwt-and-prompt-shield/reference_solution.py",
        "invariant": "Enforce composite (resource_id, tenant_id) BOLA guards, block JWT alg:none/HS256 confusion, reject RFC1918/IMDSv2 SSRF IPs pre-connect, verify HMAC replay windows, and block indirect prompt injection.",
        "relatedChapter": "sec-02-owasp-api-top10-bola-bfla-and-mass-assignment",
    },
]


def _get_connection(db_path: pathlib.Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def sanitize_fts5_query(raw_query: str) -> str:
    """
    Normalize a raw user search query into a safe SQLite FTS5 expression.
    Splits on non-alphanumeric boundaries so hyphenated/slash terms like
    `LSM-Tree`, `HTTP/2`, or `CI/CD` never trigger FTS5 boolean/column syntax errors,
    and appends `*` for fast prefix matching.
    """
    tokens = re.findall(r"[A-Za-z0-9]+", (raw_query or "").lower())
    if not tokens:
        return ""
    return " ".join(f'"{tok}"*' for tok in tokens[:8])


def _compute_kb_signature() -> str:
    """Fast filesystem mtime+size signature so live server picks up newly authored chapters automatically."""
    kb_root = REPO_ROOT / "knowledgebase"
    seed_file = HUB_DIR / "seed_newsfeed.json"
    parts: List[str] = ["v4-roadmap-interleaved-60sessions"]
    if kb_root.exists():
        for md in sorted(kb_root.rglob("*.md")):
            st = md.stat()
            parts.append(f"{md.relative_to(REPO_ROOT)}:{st.st_size}:{st.st_mtime_ns}")
    if seed_file.exists():
        st = seed_file.stat()
        parts.append(f"seed:{st.st_size}:{st.st_mtime_ns}")
    return hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()


def split_markdown_into_steps(markdown_body: str) -> List[Dict[str, Any]]:
    """
    Split chapter markdown into up to 4 bite-sized Udemy-style micro-lesson steps
    along `## ` H2 boundaries so learners are never hit with a 10,000px wall of text.
    """
    body = (markdown_body or "").strip()
    if not body:
        return []

    # Strip optional leading `# Title` line so Step 1 starts cleanly
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        body = "\n".join(lines[1:]).lstrip()

    pattern = re.compile(r"^##\s+(.+)$", flags=re.MULTILINE)
    matches = list(pattern.finditer(body))
    if not matches:
        words = len(body.split())
        return [
            {
                "stepNumber": 1,
                "shortLabel": "1. Guided Lesson",
                "title": "Guided Lesson",
                "markdown": body,
                "estMinutes": max(2, round(words / 170) + 1),
            }
        ]

    raw_sections: List[Tuple[str, str]] = []
    leading = body[: matches[0].start()].strip()
    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        chunk = body[start:end].strip()
        if idx == 0 and leading:
            chunk = leading + "\n\n" + chunk
        raw_sections.append((m.group(1).strip(), chunk))

    # Consolidate into at most 5 predictable progressive steps (4-step v1 or 5-step Hiring-Grade v2)
    if len(raw_sections) > 5:
        merged_tail = "\n\n".join(ch for _, ch in raw_sections[4:])
        raw_sections = raw_sections[:4] + [(raw_sections[4][0], merged_tail)]

    default_short = [
        "🌱 1. Plain-English Story",
        "🔨 2. Starter & CLI",
        "🛠️ 3. Practitioner & Sim",
        "🏢 4. Big Tech & Blueprint",
        "📋 5. Cheat-Sheet & Pitch",
    ]
    steps_out: List[Dict[str, Any]] = []
    for idx, (heading, chunk) in enumerate(raw_sections):
        words = len(chunk.split())
        clean_short = heading
        if ":" in heading:
            clean_short = heading.split(":", 1)[1].strip()
        clean_short = re.sub(r"^(?:Part\s+[IVXLC]+|\d+\.)\s*[—:-]?\s*", "", clean_short).strip()
        if len(clean_short) > 26:
            clean_short = clean_short[:24].rstrip() + "…"
        badge_prefix = ["🌱 1.", "🔨 2.", "🛠️ 3.", "🏢 4.", "📋 5."][min(idx, 4)]
        steps_out.append(
            {
                "stepNumber": idx + 1,
                "shortLabel": f"{badge_prefix} {clean_short}" if clean_short else default_short[min(idx, 4)],
                "title": heading,
                "markdown": chunk,
                "estMinutes": max(2, min(6, round(words / 165) + 1)),
            }
        )
    return steps_out


def _synthesize_walkthrough_frames(
    title: str,
    summary: str,
    body: str,
    pretraining: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Synthesize a clean 4-slide 90s Visual Storyboard when explicit ```json walkthrough``` is omitted."""
    code_match = re.search(r"```(?:python|java|javascript|typescript|bash)\n(.*?)```", body, flags=re.DOTALL)
    sample_code = "# Step through this chapter to build the pattern!\nassert True"
    if code_match:
        snippet_lines = [ln for ln in code_match.group(1).strip().splitlines() if ln.strip()][:7]
        sample_code = "\n".join(snippet_lines)

    contrast_match = re.search(r"```(?:json\s+)?contrast\s*\n(.*?)```", body, flags=re.DOTALL)
    naive_vs_pro = "# Naive approach -> fragile under scale\n# Staff pattern  -> deterministic & fast"
    contrast_caption = "Watch where beginners hit a wall in real projects—and the clean engineering fix that eliminates it."
    if contrast_match:
        try:
            c_obj = json.loads(contrast_match.group(1).strip())
            n_title = c_obj.get("naiveTitle", "Naive Pattern")
            s_title = c_obj.get("staffTitle", "Staff Architecture")
            n_pt = (c_obj.get("naivePoints") or [""])[0]
            s_pt = (c_obj.get("staffPoints") or [""])[0]
            contrast_caption = f"Common trap ({n_title}): {n_pt} — Upgraded to {s_title}: {s_pt}"
            naive_vs_pro = f"❌ {n_title}\n   {c_obj.get('naiveMetric', '')}\n\n✓ {s_title}\n   {c_obj.get('staffMetric', '')}"
        except Exception:
            pass

    first_term = pretraining[0] if pretraining else {"term": "Core Mental Model", "meaning": summary, "formula": ""}
    return [
        {
            "time": "0:00",
            "badge": "Slide 1 / 4 · Why Care?",
            "caption": summary or f"Let's unpack {title} from plain English before writing a single line of complex code.",
            "code": f"// 🎯 Goal: {title[:56]}\n// Start simple -> build intuition -> scale up",
        },
        {
            "time": "0:22",
            "badge": "Slide 2 / 4 · Core Idea in Code",
            "caption": f"Key building block — {first_term.get('term', 'Concept')}: {first_term.get('meaning', '')}",
            "code": sample_code,
        },
        {
            "time": "0:48",
            "badge": "Slide 3 / 4 · Trap vs. Pro Fix",
            "caption": contrast_caption[:240],
            "code": naive_vs_pro.strip(),
        },
        {
            "time": "1:12",
            "badge": "Slide 4 / 4 · Ready to Build!",
            "caption": "Now step through the 4 bite-sized lessons below at your own pace—starting with the plain-English story in Step 1!",
            "code": "# Bite 1: Plain-English Story (2m)\n# Bite 2: First Lines of Code (3m)\n# Bite 3: Interactive Sim (4m)\n# Bite 4: Staff Deep-Dive & Lab (5m)",
        },
    ]


def parse_markdown_frontmatter_and_quizzes(
    raw_md: str, fallback_slug: str, fallback_track: str, fallback_num: int
) -> Dict[str, Any]:
    """
    Parse YAML-style frontmatter (`--- ... ---`) plus structured cognitive learning blocks:
    - ```json continuity ... ```  -> Udemy-style Story Continuity Bridge (Where we were -> Problem -> Goal)
    - ```json walkthrough ... ``` -> 90-Second Narrated Visual Storyboard Slides
    - ```json pretraining ... ``` -> Just-in-Time Vocabulary & Primitives
    - ```json poe ... ```         -> Predict-Observe-Explain Simulator Prompt (Bjork)
    - ```json quiz ... ```        -> Scenario Retrieval-Practice Mastery Gate
    (Note: ```json contrast ... ``` and ```mermaid ... ``` stay in markdown_body for inline spatial rendering.)
    """
    default_course = FOLDER_TO_COURSE_ID.get(fallback_track, "07-distributed-system-design")
    course_meta = COURSE_BY_ID.get(default_course, TEXTBOOK_COURSES_CATALOG[0])

    meta: Dict[str, Any] = {
        "slug": fallback_slug,
        "course_id": default_course,
        "track": fallback_track,
        "volume": course_meta["title"],
        "module_number": 1,
        "module_title": "Module 1: First-Principles Foundations & Architecture",
        "chapter_number": fallback_num,
        "level_tag": course_meta["levelSpan"],
        "title": fallback_slug,
        "summary": "",
        "reading_time_minutes": 14,
        "video_url": "",
        "visualizer_id": "arch-endpoint-cloud-sync",
        "lab_path": "",
        "tags": [fallback_track],
        "prerequisites": [],
        "primary_sources": [],
    }

    body = raw_md
    if raw_md.startswith("---\n"):
        end_idx = raw_md.find("\n---\n", 4)
        if end_idx != -1:
            fm_block = raw_md[4:end_idx]
            body = raw_md[end_idx + 5 :].lstrip()
            for line in fm_block.splitlines():
                if ":" not in line:
                    continue
                k, v = line.split(":", 1)
                key = k.strip()
                val = v.strip()
                if key in ("tags", "prerequisites", "primary_sources") and val.startswith("["):
                    try:
                        meta[key] = json.loads(val)
                    except Exception:
                        pass
                elif key in ("chapter_number", "reading_time_minutes", "module_number"):
                    try:
                        meta[key] = int(val.strip('"').strip("'"))
                    except Exception:
                        pass
                else:
                    meta[key] = val.strip('"').strip("'")

    # Ensure course_id maps cleanly even if frontmatter only had legacy `track:`
    if meta.get("course_id") not in COURSE_BY_ID:
        meta["course_id"] = FOLDER_TO_COURSE_ID.get(meta.get("track", fallback_track), default_course)

    # Extract first H1 heading if title wasn't set in frontmatter
    if meta["title"] == fallback_slug:
        for line in body.splitlines():
            if line.startswith("# "):
                meta["title"] = line.lstrip("# ").strip()
                break

    # Extract structured cognitive blocks (`continuity`, `walkthrough`, `pretraining`, `poe`, `quiz`)
    def _extract_fenced_json(text: str, block_tag: str, default_val: Any) -> Tuple[str, Any]:
        pattern = rf"```json\s+{re.escape(block_tag)}\s*\n(.*?)```"
        m = re.search(pattern, text, flags=re.DOTALL)
        if not m:
            return text, default_val
        parsed_val = default_val
        try:
            parsed_val = json.loads(m.group(1).strip())
        except Exception:
            parsed_val = default_val
        cleaned = (text[: m.start()].rstrip() + "\n\n" + text[m.end() :].lstrip()).strip()
        return cleaned, parsed_val

    body, continuity = _extract_fenced_json(body, "continuity", {})
    if not continuity:
        body, continuity = _extract_fenced_json(body, "journey", {})
    body, walkthrough = _extract_fenced_json(body, "walkthrough", [])
    body, pretraining = _extract_fenced_json(body, "pretraining", [])
    body, prediction_prompt = _extract_fenced_json(body, "poe", {})
    body, quizzes = _extract_fenced_json(body, "quiz", [])

    # Provide sensible synthesized Pre-Training & POE defaults for supplementary README labs or legacy chapters
    if not pretraining:
        pretraining = [
            {
                "term": t.replace("-", " ").title(),
                "formula": f"#{idx + 1} Key Term",
                "meaning": f"Core building block unlocked in {meta['title']}.",
            }
            for idx, t in enumerate((meta.get("tags") or ["architecture"])[:3])
        ]
    if not prediction_prompt:
        if quizzes and isinstance(quizzes, list) and len(quizzes) > 0:
            q0 = quizzes[0]
            prediction_prompt = {
                "question": q0.get("question", f"What is the primary invariant enforced in {meta['title']}?"),
                "options": (q0.get("options") or [])[:4],
                "answerIndex": int(q0.get("answerIndex", 0)),
                "explanation": q0.get("explanation", ""),
            }

    if not meta["summary"]:
        clean_lines = [
            ln.strip()
            for ln in body.splitlines()
            if ln.strip() and not ln.strip().startswith(("#", "```", "|", ">", "-"))
        ]
        meta["summary"] = (clean_lines[0] if clean_lines else meta["title"])[:260]

    if not walkthrough:
        walkthrough = _synthesize_walkthrough_frames(meta["title"], meta["summary"], body, pretraining)

    meta["continuity"] = continuity
    meta["walkthrough"] = walkthrough
    meta["pretraining"] = pretraining
    meta["prediction_prompt"] = prediction_prompt
    meta["markdown_body"] = body
    meta["quizzes"] = quizzes
    return meta


def ensure_initialized(db_path: pathlib.Path = DEFAULT_DB_PATH) -> None:
    db_key = str(db_path.resolve())
    kb_sig = _compute_kb_signature()
    with _DB_LOCK:
        if _INITIALIZED_DBS.get(db_key) == kb_sig and db_path.exists():
            return
        conn = _get_connection(db_path)
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS kb_courses (
                    course_id TEXT PRIMARY KEY,
                    priority_rank INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    short_title TEXT NOT NULL,
                    level_span TEXT NOT NULL,
                    planned_modules INTEGER NOT NULL,
                    planned_chapters INTEGER NOT NULL,
                    accent_color TEXT NOT NULL,
                    pill_bg TEXT NOT NULL,
                    tagline TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS kb_chapters (
                    slug TEXT PRIMARY KEY,
                    course_id TEXT NOT NULL DEFAULT '07-distributed-system-design',
                    track TEXT NOT NULL,
                    volume TEXT NOT NULL,
                    module_number INTEGER NOT NULL DEFAULT 1,
                    module_title TEXT NOT NULL DEFAULT 'Module 1: Core Architecture',
                    chapter_number INTEGER NOT NULL,
                    level_tag TEXT NOT NULL DEFAULT 'Foundations → Staff',
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    reading_time_minutes INTEGER NOT NULL DEFAULT 15,
                    video_url TEXT NOT NULL DEFAULT '',
                    visualizer_id TEXT,
                    lab_path TEXT,
                    tags_json TEXT NOT NULL,
                    prerequisites_json TEXT NOT NULL DEFAULT '[]',
                    primary_sources_json TEXT NOT NULL DEFAULT '[]',
                    continuity_json TEXT NOT NULL DEFAULT '{}',
                    walkthrough_json TEXT NOT NULL DEFAULT '[]',
                    pretraining_json TEXT NOT NULL DEFAULT '[]',
                    prediction_prompt_json TEXT NOT NULL DEFAULT '{}',
                    markdown_body TEXT NOT NULL,
                    quizzes_json TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS kb_fts USING fts5(
                    slug UNINDEXED,
                    track,
                    title,
                    summary,
                    tags,
                    markdown_body,
                    tokenize = "unicode61"
                );

                CREATE TABLE IF NOT EXISTS kb_quiz_attempts (
                    slug TEXT PRIMARY KEY,
                    score INTEGER NOT NULL,
                    total INTEGER NOT NULL,
                    mastered INTEGER NOT NULL DEFAULT 0,
                    answers_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS news_sources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    feed_url TEXT NOT NULL,
                    homepage TEXT NOT NULL,
                    etag TEXT,
                    last_checked_at REAL
                );

                CREATE TABLE IF NOT EXISTS news_articles (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    reading_minutes INTEGER NOT NULL DEFAULT 8,
                    summary TEXT NOT NULL,
                    why_it_matters TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    related_chapters_json TEXT NOT NULL,
                    bookmarked INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS workbench_runs (
                    item_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    exit_code INTEGER NOT NULL,
                    duration_ms REAL NOT NULL,
                    output TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS mock_interview_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    target_role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    overall_score TEXT NOT NULL,
                    folder_path TEXT NOT NULL,
                    questions_md TEXT NOT NULL,
                    evaluation_md TEXT NOT NULL,
                    mastery_guide_md TEXT NOT NULL,
                    candidate_responses_json TEXT NOT NULL,
                    related_chapters_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS roadmap_items (
                    item_id TEXT PRIMARY KEY,
                    track TEXT NOT NULL,
                    title TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    phase_number INTEGER NOT NULL,
                    order_index INTEGER NOT NULL,
                    estimated_minutes INTEGER NOT NULL DEFAULT 15,
                    xp_reward INTEGER NOT NULL DEFAULT 100,
                    meta_json TEXT NOT NULL DEFAULT '{}',
                    prerequisites_json TEXT NOT NULL DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS roadmap_completions (
                    item_id TEXT PRIMARY KEY,
                    completed INTEGER NOT NULL DEFAULT 0,
                    completed_at REAL,
                    source TEXT NOT NULL DEFAULT 'manual',
                    notes TEXT
                );
                """
            )

            # Safe online schema migration for pre-existing hub/hub.db files
            existing_cols = {
                r["name"] for r in conn.execute("PRAGMA table_info(kb_chapters)").fetchall()
            }
            new_col_defs = [
                ("course_id", "TEXT NOT NULL DEFAULT '07-distributed-system-design'"),
                ("module_number", "INTEGER NOT NULL DEFAULT 1"),
                ("module_title", "TEXT NOT NULL DEFAULT 'Module 1: Core Architecture'"),
                ("level_tag", "TEXT NOT NULL DEFAULT 'Foundations → Staff'"),
                ("video_url", "TEXT NOT NULL DEFAULT ''"),
                ("continuity_json", "TEXT NOT NULL DEFAULT '{}'"),
                ("walkthrough_json", "TEXT NOT NULL DEFAULT '[]'"),
                ("pretraining_json", "TEXT NOT NULL DEFAULT '[]'"),
                ("prediction_prompt_json", "TEXT NOT NULL DEFAULT '{}'"),
                ("prerequisites_json", "TEXT NOT NULL DEFAULT '[]'"),
                ("primary_sources_json", "TEXT NOT NULL DEFAULT '[]'"),
            ]
            migrated = False
            for col_name, col_sql in new_col_defs:
                if col_name not in existing_cols:
                    conn.execute(f"ALTER TABLE kb_chapters ADD COLUMN {col_name} {col_sql}")
                    migrated = True
            if migrated:
                # Force one-time re-parse of existing chapters so course_id, pretraining_json, and poe populate
                conn.execute("UPDATE kb_chapters SET sha256 = ''")

            conn.commit()
            _sync_filesystem_locked(conn)
            _INITIALIZED_DBS[db_key] = kb_sig
        finally:
            conn.close()


def _sync_filesystem_locked(conn: sqlite3.Connection) -> None:
    """Incrementally sync the 8 Textbook Courses, supplementary labs, newsfeed seeds, and mock interviews into SQLite + FTS5."""
    # 0. Sync Master 8-Course Catalog
    for c in TEXTBOOK_COURSES_CATALOG:
        conn.execute(
            """
            INSERT OR REPLACE INTO kb_courses (
                course_id, priority_rank, title, short_title, level_span,
                planned_modules, planned_chapters, accent_color, pill_bg, tagline
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                c["courseId"],
                c["priorityRank"],
                c["title"],
                c["shortTitle"],
                c["levelSpan"],
                c["plannedModules"],
                c["plannedChapters"],
                c["accentColor"],
                c["pillBg"],
                c["tagline"],
            ),
        )

    existing_rows = {
        row["slug"]: (row["sha256"], row["source_path"], row["course_id"])
        for row in conn.execute("SELECT slug, sha256, source_path, course_id FROM kb_chapters").fetchall()
    }

    candidate_docs: List[Tuple[str, str, int, pathlib.Path]] = []

    # 1. Primary Textbook Course chapters in knowledgebase/<course_or_track>/*.md
    kb_root = REPO_ROOT / "knowledgebase"
    if kb_root.exists():
        for track_dir in sorted(kb_root.iterdir()):
            if not track_dir.is_dir() or track_dir.name.startswith("."):
                continue
            for idx, md_file in enumerate(sorted(track_dir.glob("*.md")), start=1):
                candidate_docs.append((md_file.stem, track_dir.name, idx, md_file))

    # 2. Supplementary Design Challenges & System Design Labs (for deep FTS5 discoverability)
    supplementary_dirs = [
        ("system-design", REPO_ROOT / "frameworks/design-challenges", 50),
        ("system-design", REPO_ROOT / "frameworks/sdet-system-design", 60),
    ]
    for track_id, parent_dir, base_num in supplementary_dirs:
        if parent_dir.exists():
            for offset, readme in enumerate(sorted(parent_dir.glob("*/README.md")), start=1):
                slug = f"lab-{readme.parent.name}"
                candidate_docs.append((slug, track_id, base_num + offset, readme))

    seen_slugs: set[str] = set()
    rebuild_fts = False

    for fallback_slug, track_id, fallback_num, path in candidate_docs:
        raw_md = path.read_text(encoding="utf-8")
        sha = hashlib.sha256(raw_md.encode("utf-8")).hexdigest()
        parsed = parse_markdown_frontmatter_and_quizzes(raw_md, fallback_slug, track_id, fallback_num)
        slug = parsed["slug"]
        seen_slugs.add(slug)
        rel_source = str(path.relative_to(REPO_ROOT))
        if existing_rows.get(slug, ("", "", "")) == (sha, rel_source, parsed["course_id"]):
            continue

        rebuild_fts = True
        lab_path = parsed.get("lab_path") or (str(path.parent.relative_to(REPO_ROOT)) if path.name == "README.md" else "")
        conn.execute(
            """
            INSERT OR REPLACE INTO kb_chapters (
                slug, course_id, track, volume, module_number, module_title,
                chapter_number, level_tag, title, summary,
                reading_time_minutes, video_url, visualizer_id, lab_path, tags_json,
                prerequisites_json, primary_sources_json,
                continuity_json, walkthrough_json, pretraining_json, prediction_prompt_json,
                markdown_body, quizzes_json, source_path, sha256, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slug,
                parsed["course_id"],
                parsed["track"],
                parsed["volume"],
                parsed["module_number"],
                parsed["module_title"],
                parsed["chapter_number"],
                parsed["level_tag"],
                parsed["title"],
                parsed["summary"],
                parsed["reading_time_minutes"],
                parsed.get("video_url", ""),
                parsed["visualizer_id"],
                lab_path,
                json.dumps(parsed["tags"]),
                json.dumps(parsed.get("prerequisites", [])),
                json.dumps(parsed.get("primary_sources", [])),
                json.dumps(parsed["continuity"]),
                json.dumps(parsed["walkthrough"]),
                json.dumps(parsed["pretraining"]),
                json.dumps(parsed["prediction_prompt"]),
                parsed["markdown_body"],
                json.dumps(parsed["quizzes"]),
                rel_source,
                sha,
                time.time(),
            ),
        )

    # Prune deleted markdown chapters if any were moved/renamed
    stale_slugs = set(existing_rows.keys()) - seen_slugs
    if stale_slugs:
        rebuild_fts = True
        for st_slug in stale_slugs:
            conn.execute("DELETE FROM kb_chapters WHERE slug = ?", (st_slug,))

    if rebuild_fts:
        conn.execute("DELETE FROM kb_fts;")
        rows = conn.execute(
            "SELECT slug, track, course_id, module_title, title, summary, tags_json, continuity_json, walkthrough_json, markdown_body FROM kb_chapters"
        ).fetchall()
        for r in rows:
            tags_str = " ".join(json.loads(r["tags_json"])) + f" {r['course_id']} {r['module_title']}"
            wt_captions = " ".join(
                f.get("caption", "") for f in json.loads(r["walkthrough_json"] or "[]") if isinstance(f, dict)
            )
            cont_text = " ".join(
                str(v) for v in json.loads(r["continuity_json"] or "{}").values()
            )
            fts_body = f"{r['markdown_body']}\n{cont_text}\n{wt_captions}"
            conn.execute(
                "INSERT INTO kb_fts (slug, track, title, summary, tags, markdown_body) VALUES (?, ?, ?, ?, ?, ?)",
                (r["slug"], r["track"], r["title"], r["summary"], tags_str, fts_body),
            )

    # 3. Seed Engineering Pulse Newsfeed sources & articles (bookmark-preserving upsert)
    seed_data = newsfeed_engine.load_seed_data()
    for src in seed_data.get("sources", []):
        conn.execute(
            """
            INSERT INTO news_sources (id, name, category, feed_url, homepage)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                feed_url = excluded.feed_url,
                homepage = excluded.homepage
            """,
            (src["id"], src["name"], src["category"], src["feedUrl"], src["homepage"]),
        )

    for art in seed_data.get("articles", []):
        conn.execute(
            """
            INSERT INTO news_articles (
                id, source_id, source_name, category, title, url,
                published_at, reading_minutes, summary, why_it_matters,
                tags_json, related_chapters_json, bookmarked
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(id) DO UPDATE SET
                source_id = excluded.source_id,
                source_name = excluded.source_name,
                category = excluded.category,
                title = excluded.title,
                url = excluded.url,
                published_at = excluded.published_at,
                reading_minutes = excluded.reading_minutes,
                summary = excluded.summary,
                why_it_matters = excluded.why_it_matters,
                tags_json = excluded.tags_json,
                related_chapters_json = excluded.related_chapters_json
            """,
            (
                art["id"],
                art["sourceId"],
                art["sourceName"],
                art["category"],
                art["title"],
                art["url"],
                art["publishedAt"],
                art.get("readingMinutes", 8),
                art["summary"],
                art.get("whyItMatters", ""),
                json.dumps(art.get("tags", [])),
                json.dumps(art.get("relatedChapters", [])),
            ),
        )

    # 4. Sync Mock Interview Sessions from mock-interviews/interview-*/
    mi_root = REPO_ROOT / "mock-interviews"
    if mi_root.exists():
        for mi_dir in sorted(mi_root.glob("interview-*")):
            if not mi_dir.is_dir():
                continue
            sid = mi_dir.name
            q_file = mi_dir / "interviewquestions.md"
            e_file = mi_dir / "evaluation-and-feedback.md"
            m_file = mi_dir / "conceptual-mastery-guide.md"
            q_md = q_file.read_text(encoding="utf-8") if q_file.exists() else ""
            e_md = e_file.read_text(encoding="utf-8") if e_file.exists() else ""
            m_md = m_file.read_text(encoding="utf-8") if m_file.exists() else ""
            existing_mi = conn.execute(
                "SELECT candidate_responses_json FROM mock_interview_sessions WHERE session_id = ?",
                (sid,),
            ).fetchone()
            responses_json = existing_mi["candidate_responses_json"] if existing_mi else "{}"
            related_chapters = [
                "sdet-01-determinism-and-flakiness-math",
                "sd-01-continuous-sync-and-backpressure",
                "sd-02-consistent-hashing-and-sharding",
                "ai-01-rag-triad-and-claim-verification",
                "cs-01-os-virtual-memory-gc-and-fd-leaks",
                "cs-02-tcp-tls-http2-and-websocket-framing",
            ]
            conn.execute(
                """
                INSERT OR REPLACE INTO mock_interview_sessions (
                    session_id, title, target_role, status, overall_score,
                    folder_path, questions_md, evaluation_md, mastery_guide_md,
                    candidate_responses_json, related_chapters_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sid,
                    f"Mock Interview #{sid.split('-')[-1]}: Staff Distributed Systems, AI RAG & Concurrency",
                    "Staff / Senior SDET & Systems Architect",
                    "Evaluated" if e_md else "In Progress",
                    "82 / 100 (Strong Senior / Staff)" if e_md else "Pending",
                    str(mi_dir.relative_to(REPO_ROOT)),
                    q_md,
                    e_md,
                    m_md,
                    responses_json,
                    json.dumps(related_chapters),
                    time.time(),
                ),
            )

    _sync_roadmap_locked(conn)
    conn.commit()


def get_kb_courses(db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Return all 12 Prioritized Textbook Courses with hierarchical Modules -> Chapters and mastery progress."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        course_rows = conn.execute("SELECT * FROM kb_courses ORDER BY priority_rank ASC").fetchall()
        chapter_rows = conn.execute(
            """
            SELECT c.slug, c.course_id, c.track, c.volume, c.module_number, c.module_title,
                   c.chapter_number, c.level_tag, c.title, c.summary, c.reading_time_minutes,
                   c.visualizer_id, c.lab_path, c.quizzes_json,
                   COALESCE(rc.completed, a.mastered, 0) AS mastered
            FROM kb_chapters c
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
            LEFT JOIN roadmap_completions rc ON rc.item_id = c.slug
            WHERE c.slug NOT LIKE 'lab-%'
            ORDER BY c.module_number ASC, c.chapter_number ASC, c.slug ASC
            """
        ).fetchall()

        by_course: Dict[str, List[sqlite3.Row]] = {}
        for r in chapter_rows:
            by_course.setdefault(r["course_id"], []).append(r)

        courses_out = []
        total_published = 0
        total_planned = 0
        total_mastered = 0

        for cr in course_rows:
            cid = cr["course_id"]
            ch_list = by_course.get(cid, [])
            modules_map: Dict[int, Dict[str, Any]] = {}
            mastered_cnt = 0
            for ch in ch_list:
                if ch["mastered"]:
                    mastered_cnt += 1
                mnum = int(ch["module_number"] or 1)
                if mnum not in modules_map:
                    modules_map[mnum] = {
                        "moduleNumber": mnum,
                        "moduleTitle": ch["module_title"],
                        "chapters": [],
                    }
                modules_map[mnum]["chapters"].append({
                    "slug": ch["slug"],
                    "courseId": cid,
                    "track": ch["track"],
                    "moduleNumber": mnum,
                    "moduleTitle": ch["module_title"],
                    "chapterNumber": ch["chapter_number"],
                    "levelTag": ch["level_tag"],
                    "title": ch["title"],
                    "summary": ch["summary"],
                    "readingTimeMinutes": ch["reading_time_minutes"],
                    "visualizerId": ch["visualizer_id"],
                    "labPath": ch["lab_path"],
                    "quizCount": len(json.loads(ch["quizzes_json"])),
                    "mastered": bool(ch["mastered"]),
                })

            total_published += len(ch_list)
            total_planned += int(cr["planned_chapters"])
            total_mastered += mastered_cnt

            courses_out.append({
                "courseId": cid,
                "priorityRank": cr["priority_rank"],
                "title": cr["title"],
                "shortTitle": cr["short_title"],
                "levelSpan": cr["level_span"],
                "plannedModules": cr["planned_modules"],
                "plannedChapters": cr["planned_chapters"],
                "publishedChapters": len(ch_list),
                "masteredChapters": mastered_cnt,
                "accentColor": cr["accent_color"],
                "pillBg": cr["pill_bg"],
                "tagline": cr["tagline"],
                "firstChapterSlug": ch_list[0]["slug"] if ch_list else "",
                "modules": [modules_map[k] for k in sorted(modules_map.keys())],
            })

        return {
            "sectionTitle": "Textbook Courses",
            "totalCourses": len(courses_out),
            "totalPublishedChapters": total_published,
            "totalPlannedChapters": total_planned,
            "totalMasteredChapters": total_mastered,
            "courses": courses_out,
        }
    finally:
        conn.close()


def get_tracks_catalog(db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Return all 6 core archetype tracks + the 8 Prioritized Textbook Courses catalog."""
    ensure_initialized(db_path)
    courses_payload = get_kb_courses(db_path)
    courses_by_id = {c["courseId"]: c for c in courses_payload["courses"]}

    conn = _get_connection(db_path)
    try:
        wb_passed = conn.execute("SELECT COUNT(*) AS cnt FROM workbench_runs WHERE status = 'PASS'").fetchone()["cnt"]
        mi_total = conn.execute("SELECT COUNT(*) AS cnt FROM mock_interview_sessions").fetchone()["cnt"]
        dsa_overview = state_manager.get_dsa_overview()

        # Group the 12 Textbook Courses across the 3 textbook pillar cards while exposing all 12 courses directly
        pillar_course_groups = {
            "system-design": [
                "01-zero-to-staff-sdet",
                "02-building-testing-frameworks",
                "07-distributed-system-design",
                "10-docker-cicd-and-cloud-infra",
                "11-performance-chaos-and-sre",
            ],
            "ai-engineering": [
                "05-ai-engineering",
                "06-ai-engineering-qa-focused",
                "12-app-api-and-ai-security",
            ],
            "core-cs": [
                "03-ui-automation-playwright",
                "04-api-and-api-automation",
                "08-core-cs-internals",
                "09-sql-and-data-engineering",
            ],
        }

        tracks_out = []
        for t in TRACK_DEFINITIONS:
            tid = t["id"]
            item = dict(t)
            if tid in pillar_course_groups:
                cids = pillar_course_groups[tid]
                item["totalItems"] = sum(courses_by_id[c]["publishedChapters"] for c in cids if c in courses_by_id)
                item["completedItems"] = sum(courses_by_id[c]["masteredChapters"] for c in cids if c in courses_by_id)
                item["unitLabel"] = "Course Chapters"
            elif tid == "dsa":
                item["totalItems"] = dsa_overview["total"]
                item["completedItems"] = dsa_overview["bothDone"]
                item["unitLabel"] = "Algorithmic Problems"
            elif tid == "frameworks":
                item["totalItems"] = len(WORKBENCH_CATALOG)
                item["completedItems"] = wb_passed
                item["unitLabel"] = "Local IDE Suites & Katas"
            elif tid == "mock-interviews":
                item["totalItems"] = mi_total
                item["completedItems"] = mi_total
                item["unitLabel"] = "Interview Simulations"
            tracks_out.append(item)

        return {
            "platformTitle": "The Hub of Learning",
            "tracks": tracks_out,
            "textbookCourses": courses_payload["courses"],
            "totalTextbookChapters": courses_payload["totalPublishedChapters"],
        }
    finally:
        conn.close()


def list_kb_chapters(
    track: Optional[str] = None,
    course: Optional[str] = None,
    include_labs: bool = False,
    db_path: pathlib.Path = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        clauses = []
        params: List[Any] = []
        if course and course != "all":
            clauses.append("c.course_id = ?")
            params.append(course)
        elif track and track != "all":
            clauses.append("(c.track = ? OR c.course_id = ?)")
            params.extend([track, track])
        if not include_labs:
            clauses.append("c.slug NOT LIKE 'lab-%'")
        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = conn.execute(
            f"""
            SELECT c.slug, c.course_id, c.track, c.volume, c.module_number, c.module_title,
                   c.chapter_number, c.level_tag, c.title, c.summary,
                   c.reading_time_minutes, c.visualizer_id, c.lab_path, c.tags_json,
                   c.quizzes_json, c.source_path,
                   COALESCE(k.priority_rank, 99) AS priority_rank,
                   COALESCE(k.title, c.volume) AS course_title,
                   COALESCE(rc.completed, a.mastered, 0) AS mastered,
                   a.score AS quiz_score,
                   a.total AS quiz_total
            FROM kb_chapters c
            LEFT JOIN kb_courses k ON k.course_id = c.course_id
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
            LEFT JOIN roadmap_completions rc ON rc.item_id = c.slug
            {where_sql}
            ORDER BY priority_rank ASC, c.module_number ASC, c.chapter_number ASC, c.slug ASC
            """,
            params,
        ).fetchall()
        out = []
        for r in rows:
            quizzes = json.loads(r["quizzes_json"])
            out.append({
                "slug": r["slug"],
                "courseId": r["course_id"],
                "courseTitle": r["course_title"],
                "priorityRank": r["priority_rank"],
                "track": r["track"],
                "volume": r["volume"],
                "moduleNumber": r["module_number"],
                "moduleTitle": r["module_title"],
                "chapterNumber": r["chapter_number"],
                "levelTag": r["level_tag"],
                "title": r["title"],
                "summary": r["summary"],
                "readingTimeMinutes": r["reading_time_minutes"],
                "visualizerId": r["visualizer_id"],
                "labPath": r["lab_path"],
                "tags": json.loads(r["tags_json"]),
                "quizCount": len(quizzes),
                "mastered": bool(r["mastered"]),
                "quizScore": r["quiz_score"],
                "quizTotal": r["quiz_total"],
                "sourcePath": r["source_path"],
            })
        return out
    finally:
        conn.close()


def get_kb_chapter(slug: str, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Tuple[int, Dict[str, Any]]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT c.*,
                   COALESCE(k.title, c.volume) AS course_title,
                   COALESCE(k.priority_rank, 99) AS priority_rank,
                   COALESCE(k.accent_color, '#C85A32') AS course_accent,
                   COALESCE(rc.completed, a.mastered, 0) AS mastered,
                   a.score AS quiz_score,
                   a.total AS quiz_total
            FROM kb_chapters c
            LEFT JOIN kb_courses k ON k.course_id = c.course_id
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
            LEFT JOIN roadmap_completions rc ON rc.item_id = c.slug
            WHERE c.slug = ?
            """,
            (slug,),
        ).fetchone()
        if row is None:
            return 404, {"error": f"Chapter '{slug}' not found"}

        # Compute Prev / Next chapter navigation within the same Textbook Course
        siblings = conn.execute(
            """
            SELECT slug, chapter_number, title
            FROM kb_chapters
            WHERE course_id = ? AND slug NOT LIKE 'lab-%'
            ORDER BY module_number ASC, chapter_number ASC, slug ASC
            """,
            (row["course_id"],),
        ).fetchall()
        prev_ch = None
        next_ch = None
        for idx, sib in enumerate(siblings):
            if sib["slug"] == slug:
                if idx > 0:
                    prev_ch = {"slug": siblings[idx - 1]["slug"], "title": siblings[idx - 1]["title"], "chapterNumber": siblings[idx - 1]["chapter_number"]}
                if idx + 1 < len(siblings):
                    next_ch = {"slug": siblings[idx + 1]["slug"], "title": siblings[idx + 1]["title"], "chapterNumber": siblings[idx + 1]["chapter_number"]}
                break

        # Find cross-linked Engineering Pulse Newsfeed articles
        all_news = conn.execute("SELECT * FROM news_articles ORDER BY published_at DESC").fetchall()
        chapter_tags = set(json.loads(row["tags_json"]))
        related_news = []
        for art in all_news:
            rel_slugs = set(json.loads(art["related_chapters_json"]))
            art_tags = set(json.loads(art["tags_json"]))
            if slug in rel_slugs or len(chapter_tags & art_tags) >= 2:
                related_news.append({
                    "id": art["id"],
                    "sourceName": art["source_name"],
                    "title": art["title"],
                    "url": art["url"],
                    "publishedAt": art["published_at"],
                    "summary": art["summary"],
                    "whyItMatters": art["why_it_matters"],
                    "tags": json.loads(art["tags_json"]),
                })

        raw_continuity = json.loads(row["continuity_json"] or "{}")
        continuity_out = {
            "previously": raw_continuity.get("previously")
            or (
                f"Ch {prev_ch['chapterNumber']:02d}: {prev_ch['title']}"
                if prev_ch
                else f"Course Start — Welcome to {row['course_title']}! Zero prior context assumed."
            ),
            "painPoint": raw_continuity.get("painPoint")
            or f"As systems grow, ad-hoc solutions hit a bottleneck inside {row['module_title']}.",
            "unlock": raw_continuity.get("unlock") or row["summary"],
            "upNext": raw_continuity.get("upNext")
            or (
                f"Ch {next_ch['chapterNumber']:02d}: {next_ch['title']}"
                if next_ch
                else "Course Capstone Mastered!"
            ),
        }

        from hub import tts_walkthrough_engine

        raw_wt = json.loads(row["walkthrough_json"] or "[]")
        if not raw_wt:
            raw_wt = _synthesize_walkthrough_frames(
                row["title"],
                row["summary"],
                row["markdown_body"],
                json.loads(row["pretraining_json"] or "[]"),
            )
        walkthrough_synced = tts_walkthrough_engine.normalize_section_durations(raw_wt, audio_dur=0.0)

        return 200, {
            "slug": row["slug"],
            "courseId": row["course_id"],
            "courseTitle": row["course_title"],
            "priorityRank": row["priority_rank"],
            "courseAccent": row["course_accent"],
            "track": row["track"],
            "volume": row["volume"],
            "moduleNumber": row["module_number"],
            "moduleTitle": row["module_title"],
            "chapterNumber": row["chapter_number"],
            "levelTag": row["level_tag"],
            "title": row["title"],
            "summary": row["summary"],
            "readingTimeMinutes": row["reading_time_minutes"],
            "videoUrl": row["video_url"] or "",
            "visualizerId": row["visualizer_id"],
            "labPath": row["lab_path"],
            "tags": json.loads(row["tags_json"]),
            "prerequisites": json.loads(row["prerequisites_json"] or "[]"),
            "primarySources": json.loads(row["primary_sources_json"] or "[]"),
            "continuity": continuity_out,
            "walkthrough": walkthrough_synced,
            "steps": split_markdown_into_steps(row["markdown_body"]),
            "pretraining": json.loads(row["pretraining_json"] or "[]"),
            "predictionPrompt": json.loads(row["prediction_prompt_json"] or "{}"),
            "markdownBody": row["markdown_body"],
            "quizzes": json.loads(row["quizzes_json"]),
            "mastered": bool(row["mastered"]),
            "quizScore": row["quiz_score"],
            "quizTotal": row["quiz_total"],
            "sourcePath": row["source_path"],
            "prevChapter": prev_ch,
            "nextChapter": next_ch,
            "relatedNews": related_news[:4],
        }
    finally:
        conn.close()


def get_kb_course_compendium(
    course_id: str, db_path: pathlib.Path = DEFAULT_DB_PATH
) -> Tuple[int, Dict[str, Any]]:
    """
    Compile an entire Textbook Course (`Ch 01 -> Ch N`) into a single-page, unabridged
    Master Revision Compendium in one SQLite pass (`~2-5ms`).

    Retains 100% of deep technical text, mental models, Mermaid diagrams, Naive-vs-Staff
    contrast matrices, dual-language code blueprints, Staff equations, trade-off tables,
    Staff gotchas, vocabulary, and Self-Check Q&A explanations while stripping out
    video/audio walkthrough players, simulator widgets, and quiz submission forms.
    """
    t0 = time.perf_counter()
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        target_course = (course_id or "01-zero-to-staff-sdet").strip()
        course_row = conn.execute(
            "SELECT * FROM kb_courses WHERE course_id = ?", (target_course,)
        ).fetchone()
        if course_row is None:
            return 404, {"error": f"Course '{target_course}' not found"}

        rows = conn.execute(
            """
            SELECT c.*, COALESCE(rc.completed, a.mastered, 0) AS mastered
            FROM kb_chapters c
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
            LEFT JOIN roadmap_completions rc ON rc.item_id = c.slug
            WHERE c.course_id = ? AND c.slug NOT LIKE 'lab-%'
            ORDER BY c.module_number ASC, c.chapter_number ASC, c.slug ASC
            """,
            (target_course,),
        ).fetchall()

        chapters_compiled: List[Dict[str, Any]] = []
        red_thread_map: List[Dict[str, Any]] = []
        master_glossary: List[Dict[str, Any]] = []
        seen_terms: set[str] = set()

        total_words = 0
        total_reading_mins = 0
        total_code_blocks = 0
        total_mermaid = 0
        total_math = 0
        total_qa = 0

        for idx, row in enumerate(rows):
            md = row["markdown_body"]
            words = len(md.split())
            code_blocks = len(re.findall(r"```(?:python|java)\b", md, flags=re.IGNORECASE))
            mermaids = len(re.findall(r"```mermaid\b", md, flags=re.IGNORECASE))
            maths = len(re.findall(r"\$\$[\s\S]*?\$\$", md))

            total_words += words
            total_reading_mins += int(row["reading_time_minutes"] or 15)
            total_code_blocks += code_blocks
            total_mermaid += mermaids
            total_math += maths

            raw_cont = json.loads(row["continuity_json"] or "{}")
            continuity_out = {
                "previously": raw_cont.get("previously")
                or (
                    f"Ch {rows[idx - 1]['chapter_number']:02d}: {rows[idx - 1]['title']}"
                    if idx > 0
                    else f"Course Start — {course_row['title']}"
                ),
                "painPoint": raw_cont.get("painPoint") or row["summary"],
                "unlock": raw_cont.get("unlock") or row["summary"],
            }

            pretraining = json.loads(row["pretraining_json"] or "[]")
            for pt in pretraining:
                tk = str(pt.get("term", "")).strip().lower()
                if tk and tk not in seen_terms:
                    seen_terms.add(tk)
                    master_glossary.append(
                        {
                            "term": pt.get("term", ""),
                            "formula": pt.get("formula", ""),
                            "meaning": pt.get("meaning", ""),
                            "chapterNumber": row["chapter_number"],
                            "chapterSlug": row["slug"],
                        }
                    )

            qa_key: List[Dict[str, Any]] = []
            poe = json.loads(row["prediction_prompt_json"] or "{}")
            if poe.get("question") and poe.get("options"):
                opts = poe.get("options") or []
                aidx = int(poe.get("answerIndex", 0))
                qa_key.append(
                    {
                        "id": f"{row['slug']}-poe",
                        "kind": "Architecture Prediction",
                        "question": poe["question"],
                        "correctAnswer": opts[aidx] if 0 <= aidx < len(opts) else "",
                        "options": opts,
                        "answerIndex": aidx,
                        "explanation": poe.get("explanation", ""),
                    }
                )
            for q in json.loads(row["quizzes_json"] or "[]"):
                opts = q.get("options") or []
                aidx = int(q.get("answerIndex", 0))
                qa_key.append(
                    {
                        "id": q.get("id", ""),
                        "kind": "Staff Scenario Check",
                        "question": q.get("question", ""),
                        "correctAnswer": opts[aidx] if 0 <= aidx < len(opts) else "",
                        "options": opts,
                        "answerIndex": aidx,
                        "explanation": q.get("explanation", ""),
                    }
                )
            total_qa += len(qa_key)

            red_thread_map.append(
                {
                    "chapterNumber": row["chapter_number"],
                    "moduleNumber": row["module_number"],
                    "moduleTitle": row["module_title"],
                    "slug": row["slug"],
                    "title": row["title"],
                    "painPoint": continuity_out["painPoint"],
                    "unlock": continuity_out["unlock"],
                    "readingTimeMinutes": row["reading_time_minutes"],
                }
            )

            chapters_compiled.append(
                {
                    "slug": row["slug"],
                    "chapterNumber": row["chapter_number"],
                    "moduleNumber": row["module_number"],
                    "moduleTitle": row["module_title"],
                    "levelTag": row["level_tag"],
                    "title": row["title"],
                    "summary": row["summary"],
                    "readingTimeMinutes": row["reading_time_minutes"],
                    "wordCount": words,
                    "labPath": row["lab_path"] or "",
                    "tags": json.loads(row["tags_json"] or "[]"),
                    "prerequisites": json.loads(row["prerequisites_json"] or "[]"),
                    "primarySources": json.loads(row["primary_sources_json"] or "[]"),
                    "mastered": bool(row["mastered"]),
                    "continuity": continuity_out,
                    "pretraining": pretraining,
                    "steps": split_markdown_into_steps(md),
                    "markdownBody": md,
                    "selfCheckKey": qa_key,
                }
            )

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return 200, {
            "course": {
                "courseId": course_row["course_id"],
                "priorityRank": course_row["priority_rank"],
                "title": course_row["title"],
                "shortTitle": course_row["short_title"],
                "levelSpan": course_row["level_span"],
                "plannedModules": course_row["planned_modules"],
                "plannedChapters": course_row["planned_chapters"],
                "publishedChapters": len(chapters_compiled),
                "accentColor": course_row["accent_color"],
                "pillBg": course_row["pill_bg"],
                "tagline": course_row["tagline"],
            },
            "latencyMs": latency_ms,
            "stats": {
                "chapterCount": len(chapters_compiled),
                "totalWords": total_words,
                "totalReadingMinutes": total_reading_mins,
                "reviseEstimatedMinutes": max(15, round(total_reading_mins * 0.55)),
                "totalCodeBlocks": total_code_blocks,
                "totalMermaidDiagrams": total_mermaid,
                "totalDisplayEquations": total_math,
                "totalGlossaryTerms": len(master_glossary),
                "totalSelfCheckQuestions": total_qa,
            },
            "redThreadMap": red_thread_map,
            "masterGlossary": master_glossary,
            "chapters": chapters_compiled,
        }
    finally:
        conn.close()


def search_knowledgebase(
    raw_query: str,
    track: Optional[str] = None,
    course: Optional[str] = None,
    db_path: pathlib.Path = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    """Execute sub-millisecond SQLite FTS5 BM25 full-text search across Textbook Courses & design challenges."""
    ensure_initialized(db_path)
    safe_q = sanitize_fts5_query(raw_query)
    if not safe_q:
        return {"query": raw_query, "safeQuery": "", "results": []}

    t0 = time.perf_counter()
    conn = _get_connection(db_path)
    try:
        sql = """
            SELECT f.slug, f.track, c.course_id, f.title, f.summary, f.tags,
                   snippet(kb_fts, 5, '<mark>', '</mark>', ' … ', 20) AS snippet,
                   bm25(kb_fts, 0.0, 2.0, 6.0, 3.0, 4.0, 1.0) AS rank
            FROM kb_fts f
            LEFT JOIN kb_chapters c ON c.slug = f.slug
            WHERE kb_fts MATCH ?
        """
        params: List[Any] = [safe_q]
        if course and course != "all":
            sql += " AND c.course_id = ?"
            params.append(course)
        elif track and track != "all":
            sql += " AND (f.track = ? OR c.course_id = ?)"
            params.extend([track, track])
        sql += " ORDER BY rank LIMIT 18"

        rows = conn.execute(sql, params).fetchall()
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        results = [
            {
                "slug": r["slug"],
                "courseId": r["course_id"] or FOLDER_TO_COURSE_ID.get(r["track"], "07-distributed-system-design"),
                "track": r["track"],
                "title": r["title"],
                "summary": r["summary"],
                "tags": r["tags"].split(),
                "snippet": r["snippet"],
                "rank": round(float(r["rank"]), 4),
            }
            for r in rows
        ]
        return {
            "query": raw_query,
            "safeQuery": safe_q,
            "latencyMs": latency_ms,
            "count": len(results),
            "results": results,
        }
    finally:
        conn.close()


def submit_kb_quiz(slug: str, submitted_answers: Dict[str, int], db_path: pathlib.Path = DEFAULT_DB_PATH) -> Tuple[int, Dict[str, Any]]:
    """Deterministically grade an end-of-chapter quiz submission and persist mastery in SQLite."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        row = conn.execute("SELECT quizzes_json FROM kb_chapters WHERE slug = ?", (slug,)).fetchone()
        if row is None:
            return 404, {"error": f"Chapter '{slug}' not found"}

        quizzes = json.loads(row["quizzes_json"])
        if not quizzes:
            return 400, {"error": f"Chapter '{slug}' has no quiz questions"}

        correct = 0
        feedback = []
        for idx, q in enumerate(quizzes):
            qid = q.get("id") or f"q{idx + 1}"
            chosen = submitted_answers.get(qid, submitted_answers.get(str(idx)))
            expected = int(q["answerIndex"])
            is_correct = chosen is not None and int(chosen) == expected
            if is_correct:
                correct += 1
            feedback.append({
                "id": qid,
                "chosenIndex": chosen,
                "answerIndex": expected,
                "correct": is_correct,
                "explanation": q.get("explanation", ""),
            })

        total = len(quizzes)
        mastered = 1 if correct == total else 0
        conn.execute(
            """
            INSERT OR REPLACE INTO kb_quiz_attempts (slug, score, total, mastered, answers_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (slug, correct, total, mastered, json.dumps(submitted_answers), time.time()),
        )
        conn.commit()
        return 200, {
            "slug": slug,
            "score": correct,
            "total": total,
            "mastered": bool(mastered),
            "feedback": feedback,
        }
    finally:
        conn.close()


def get_newsfeed(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    bookmarked_only: bool = False,
    db_path: pathlib.Path = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        clauses = []
        params: List[Any] = []
        if category and category != "all":
            clauses.append("category = ?")
            params.append(category)
        if bookmarked_only:
            clauses.append("bookmarked = 1")
        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = conn.execute(
            f"SELECT * FROM news_articles {where_sql} ORDER BY published_at DESC, id ASC",
            params,
        ).fetchall()

        articles = []
        for r in rows:
            tags_list = json.loads(r["tags_json"])
            if tag and tag.lower() not in [t.lower() for t in tags_list]:
                continue
            articles.append({
                "id": r["id"],
                "sourceId": r["source_id"],
                "sourceName": r["source_name"],
                "category": r["category"],
                "title": r["title"],
                "url": r["url"],
                "publishedAt": r["published_at"],
                "readingMinutes": r["reading_minutes"],
                "summary": r["summary"],
                "whyItMatters": r["why_it_matters"],
                "tags": tags_list,
                "relatedChapters": json.loads(r["related_chapters_json"]),
                "bookmarked": bool(r["bookmarked"]),
            })

        sources = [
            {
                "id": s["id"],
                "name": s["name"],
                "category": s["category"],
                "feedUrl": s["feed_url"],
                "homepage": s["homepage"],
            }
            for s in conn.execute("SELECT * FROM news_sources ORDER BY name ASC").fetchall()
        ]
        return {
            "count": len(articles),
            "sources": sources,
            "articles": articles,
        }
    finally:
        conn.close()


def toggle_news_bookmark(article_id: str, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Tuple[int, Dict[str, Any]]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        row = conn.execute("SELECT bookmarked FROM news_articles WHERE id = ?", (article_id,)).fetchone()
        if row is None:
            return 404, {"error": f"Article '{article_id}' not found"}
        new_val = 0 if row["bookmarked"] else 1
        conn.execute("UPDATE news_articles SET bookmarked = ? WHERE id = ?", (new_val, article_id))
        conn.commit()
        return 200, {"id": article_id, "bookmarked": bool(new_val)}
    finally:
        conn.close()


def refresh_newsfeed(fetch_remote: bool = False, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Refresh newsfeed from seed + optional live RSS/Atom poll with offline fallback."""
    ensure_initialized(db_path)
    chapters = list_kb_chapters(db_path=db_path)
    conn = _get_connection(db_path)
    inserted_live = 0
    try:
        if fetch_remote:
            sources = conn.execute("SELECT * FROM news_sources").fetchall()
            for src in sources:
                xml_text = newsfeed_engine.fetch_live_feed(src["feed_url"])
                if not xml_text:
                    continue
                parsed_items = newsfeed_engine.parse_feed_xml(
                    xml_text, src["id"], src["name"], src["category"], chapters
                )
                for art in parsed_items:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO news_articles (
                            id, source_id, source_name, category, title, url,
                            published_at, reading_minutes, summary, why_it_matters,
                            tags_json, related_chapters_json, bookmarked
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """,
                        (
                            art["id"],
                            art["sourceId"],
                            art["sourceName"],
                            art["category"],
                            art["title"],
                            art["url"],
                            art["publishedAt"],
                            art["readingMinutes"],
                            art["summary"],
                            art["whyItMatters"],
                            json.dumps(art["tags"]),
                            json.dumps(art["relatedChapters"]),
                        ),
                    )
                    inserted_live += 1
            conn.commit()
    finally:
        conn.close()
    feed = get_newsfeed(db_path=db_path)
    feed["liveFetchedCount"] = inserted_live
    return feed


def get_workbench_catalog(db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Return all Local IDE Framework Workbench projects (100% deterministic, zero AI) with last run status."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        runs = {
            r["item_id"]: {
                "status": r["status"],
                "exitCode": r["exit_code"],
                "durationMs": r["duration_ms"],
                "output": r["output"],
                "updatedAt": r["updated_at"],
            }
            for r in conn.execute("SELECT * FROM workbench_runs").fetchall()
        }
        manual_comp = {
            r["item_id"]: int(r["completed"])
            for r in conn.execute("SELECT item_id, completed FROM roadmap_completions").fetchall()
        }
        items = []
        completed_count = 0
        for wb in WORKBENCH_CATALOG:
            entry = dict(wb)
            last_run = runs.get(wb["id"])
            entry["lastRun"] = last_run
            if wb["id"] in manual_comp:
                is_done = bool(manual_comp[wb["id"]])
            else:
                is_done = bool(last_run and last_run.get("status") == "PASS")
            entry["completed"] = is_done
            if is_done:
                completed_count += 1
            items.append(entry)
        return {
            "executionModel": "100% Local Deterministic Verification (Strictly Zero AI Dependency)",
            "total": len(items),
            "completed": completed_count,
            "items": items,
        }
    finally:
        conn.close()


def run_workbench_verification(item_id: str, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Tuple[int, Dict[str, Any]]:
    """Execute a local deterministic framework or concurrency challenge verification script."""
    ensure_initialized(db_path)
    target = next((wb for wb in WORKBENCH_CATALOG if wb["id"] == item_id), None)
    if target is None:
        return 404, {"error": f"Workbench item '{item_id}' not found"}

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            target["verifyCmd"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        status = "PASS" if proc.returncode == 0 else "FAIL"
        output = ((proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")).strip()
        if not output and status == "PASS":
            output = f"✓ Deterministic verification passed for {target['title']} ({duration_ms}ms)."
        exit_code = proc.returncode
    except Exception as exc:
        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        status = "ERROR"
        output = str(exc)
        exit_code = 1

    conn = _get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO workbench_runs (item_id, status, exit_code, duration_ms, output, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_id, status, exit_code, duration_ms, output, time.time()),
        )
        conn.commit()
    finally:
        conn.close()

    return 200, {
        "itemId": item_id,
        "title": target["title"],
        "status": status,
        "exitCode": exit_code,
        "durationMs": duration_ms,
        "output": output,
    }


def get_interviews_catalog(db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT m.session_id, m.title, m.target_role, m.status, m.overall_score,
                   m.folder_path, m.related_chapters_json, m.updated_at,
                   COALESCE(rc.completed, 0) AS completed
            FROM mock_interview_sessions m
            LEFT JOIN roadmap_completions rc ON rc.item_id = m.session_id
            ORDER BY m.session_id ASC
            """
        ).fetchall()
        sessions = [
            {
                "sessionId": r["session_id"],
                "title": r["title"],
                "targetRole": r["target_role"],
                "status": r["status"],
                "overallScore": r["overall_score"],
                "folderPath": r["folder_path"],
                "relatedChapters": json.loads(r["related_chapters_json"]),
                "completed": bool(r["completed"]),
            }
            for r in rows
        ]
        return {"sessions": sessions}
    finally:
        conn.close()


def get_interview_session(session_id: str, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Tuple[int, Dict[str, Any]]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT m.*, COALESCE(rc.completed, 0) AS completed
            FROM mock_interview_sessions m
            LEFT JOIN roadmap_completions rc ON rc.item_id = m.session_id
            WHERE m.session_id = ?
            """,
            (session_id,),
        ).fetchone()
        if row is None:
            return 404, {"error": f"Mock interview session '{session_id}' not found"}
        return 200, {
            "sessionId": row["session_id"],
            "title": row["title"],
            "targetRole": row["target_role"],
            "status": row["status"],
            "overallScore": row["overall_score"],
            "folderPath": row["folder_path"],
            "questionsMarkdown": row["questions_md"],
            "evaluationMarkdown": row["evaluation_md"],
            "masteryGuideMarkdown": row["mastery_guide_md"],
            "candidateResponses": json.loads(row["candidate_responses_json"]),
            "relatedChapters": json.loads(row["related_chapters_json"]),
            "completed": bool(row["completed"]),
        }
    finally:
        conn.close()


def save_interview_response(
    session_id: str, question_id: str, response_text: str, db_path: pathlib.Path = DEFAULT_DB_PATH
) -> Tuple[int, Dict[str, Any]]:
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT candidate_responses_json FROM mock_interview_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return 404, {"error": f"Mock interview session '{session_id}' not found"}
        responses = json.loads(row["candidate_responses_json"])
        responses[str(question_id)] = response_text
        conn.execute(
            "UPDATE mock_interview_sessions SET candidate_responses_json = ?, updated_at = ? WHERE session_id = ?",
            (json.dumps(responses), time.time(), session_id),
        )
        conn.commit()
        return 200, {
            "sessionId": session_id,
            "questionId": question_id,
            "saved": True,
            "candidateResponses": responses,
        }
    finally:
        conn.close()


# ==============================================================================
# STAFF SDET ROADMAP, 5-PHASE CURRICULUM ORDER & GAMIFIED HABIT ENGINE
# ==============================================================================
ROADMAP_PHASES_SPEC: List[Dict[str, Any]] = [
    {
        "phaseNumber": 1,
        "title": "Phase 1: SDET Foundations & Core Algorithms",
        "shortTitle": "Foundations & DSA Core",
        "objective": "Master flaky test combinatorics (p^N), boundary value analysis, seam economics, AST framework lifecycles, and O(1) hash/pointer invariants.",
        "exitGate": "Complete Courses 01–02 + Core Design Katas + Arrays & Two Pointers",
        "courses": ["01-zero-to-staff-sdet", "02-building-testing-frameworks"],
        "workbenchIds": [
            "wb-custom-retry-analyzer",
            "wb-json-payload-diff-engine",
            "wb-rate-limiter-backpressure",
            "wb-test-data-builder",
            "wb-microservice-mocking",
        ],
        "dsaChapterNumbers": ["01", "02"],
        "mockIds": [],
        "soundbiteTitle": "🎙️ Phase 1 Bar-Raiser Soundbite — Flakiness & Framework Economics",
        "soundbiteQuote": (
            "At scale, suite reliability is P(pass) = p^N: a 99% reliable test across 100 tests yields only 36.6% green builds. "
            "I eliminate flakiness structurally via Hermetic Contract Seams, LIFO DI teardown, and deterministic AST payload diffing rather than blind @Retry loops."
        ),
    },
    {
        "phaseNumber": 2,
        "title": "Phase 2: Microservices, Concurrency & Contracts",
        "shortTitle": "Concurrency, UI & API Contracts",
        "objective": "Architect zero-collision 32-worker parallel execution, CDP/BiDi browser pipes, HTTP/2 connection pools, Token Bucket backpressure, and Pact consumer-driven contracts.",
        "exitGate": "Complete Courses 03–04 + 32-Worker Concurrency Lab + Sliding Window/Stack/Binary Search",
        "courses": ["03-ui-automation-playwright", "04-api-and-api-automation"],
        "workbenchIds": [
            "wb-concurrency-isolation",
            "wb-playwright-ui-framework",
            "wb-api-automation-suite",
            "wb-ci-shard-bin-packer-tia",
        ],
        "dsaChapterNumbers": ["03", "04", "05"],
        "mockIds": [],
        "soundbiteTitle": "🎙️ Phase 2 Bar-Raiser Soundbite — 32-Worker Tenant Isolation",
        "soundbiteQuote": (
            "Shared staging environments fail under parallel CI because workers collide on mutable rows. "
            "I enforce X-Tenant-ID header propagation, composite (tenant_id, resource_id) isolation, and RFC 8785 canonical Pact contracts so 32 parallel workers achieve 100% deterministic 201 Created throughput."
        ),
    },
    {
        "phaseNumber": 3,
        "title": "Phase 3: SQL Ledger, Cloud CI/CD & AI Engineering",
        "shortTitle": "SQL, Cloud CI/CD & AI QA",
        "objective": "Build double-entry SQL reconciliation harnesses, multi-stage Docker/K8s ephemeral test environments, LPT bin-packed CI shards, and calibrated LLM/RAG evaluation pipelines.",
        "exitGate": "Complete Courses 09, 10, 05, 06 + AeroLedger & AeroPipe Labs + Trees/Heaps",
        "courses": [
            "09-sql-and-data-engineering",
            "10-docker-cicd-and-cloud-infra",
            "05-ai-engineering",
            "06-ai-engineering-qa-focused",
        ],
        "workbenchIds": ["wb-sql-data-reconciliation", "wb-cicd-container-sharding"],
        "dsaChapterNumbers": ["06", "07", "08", "09"],
        "mockIds": [],
        "soundbiteTitle": "🎙️ Phase 3 Bar-Raiser Soundbite — SQL Ledgers, LPT Sharding & RAG Calibration",
        "soundbiteQuote": (
            "To prevent 1:N join fan-out from corrupting financial totals, I pre-aggregate child grains via CTEs before joining, "
            "serialize high-contention seat claims with SELECT FOR UPDATE SKIP LOCKED, bin-pack CI shards via O(N log K) LPT min-heaps, and debias LLM judges with Rogan-Gladen prevalence calibration."
        ),
    },
    {
        "phaseNumber": 4,
        "title": "Phase 4: Performance, Chaos SRE & App/AI Security",
        "shortTitle": "Perf, Chaos SRE & App/AI Security",
        "objective": "Eliminate Coordinated Omission in open-loop load tests, size HikariCP pools via Little's Law, inject deterministic Toxiproxy faults, and enforce BOLA/JWT/SSRF/Prompt-Injection gates.",
        "exitGate": "Complete Courses 11–12 + AeroPulse & AeroShield Labs + Graphs & DP",
        "courses": ["11-performance-chaos-and-sre", "12-app-api-and-ai-security"],
        "workbenchIds": ["wb-perf-chaos-sre-harness", "wb-security-bola-jwt-llm"],
        "dsaChapterNumbers": ["10", "11", "12", "13"],
        "mockIds": [],
        "soundbiteTitle": "🎙️ Phase 4 Bar-Raiser Soundbite — Coordinated Omission & Zero-Trust AppSec",
        "soundbiteQuote": (
            "Closed-loop load generators hide tail-latency stalls by waiting for slow responses before sending the next request. "
            "I use open-loop Poisson arrival schedules with HdrHistogram correction, multi-window 14.4x/6x SLO burn-rate gates, and automated BOLA + RFC 8725 JWT + IMDSv2 SSRF regression shields."
        ),
    },
    {
        "phaseNumber": 5,
        "title": "Phase 5: Staff Bar-Raiser & System Design Mastery",
        "shortTitle": "Staff System Design & Mock Sim",
        "objective": "Synthesize distributed backpressure, consistent hashing, Raft quorums, Linux kernel/storage internals, and clear the 100-Point Staff Bar-Raiser Mock Interview Simulator.",
        "exitGate": "Complete Courses 07–08 + Advanced DSA + Score ≥ 85/100 on Staff Mock Simulator",
        "courses": ["07-distributed-system-design", "08-core-cs-internals"],
        "workbenchIds": [],
        "dsaChapterNumbers": ["14", "15"],
        "mockIds": ["interview-1"],
        "soundbiteTitle": "🎙️ Phase 5 Bar-Raiser Soundbite — Principal Quality Architect Pitch",
        "soundbiteQuote": (
            "As a Staff SDET, my product is engineering velocity with mathematical confidence: bounding tail latency via Little's Law and Full Jitter backpressure, "
            "proving data durability across WAL/LSM storage engines, and embedding deterministic quality gates across every microservice and AI pipeline."
        ),
    },
]


ROADMAP_PHASE_SESSION_BUDGETS: Dict[int, int] = {
    1: 10,  # Sessions 1–10   (Weeks 1–2)
    2: 10,  # Sessions 11–20  (Weeks 3–4)
    3: 20,  # Sessions 21–40  (Weeks 5–8)
    4: 15,  # Sessions 41–55  (Weeks 9–11)
    5: 5,   # Sessions 56–60  (Week 12)
}


def _milestone_session_map(items: List[Dict[str, Any]], total_sessions: int) -> Dict[int, List[Dict[str, Any]]]:
    """Place Workbench Labs and Staff Mock Interviews on evenly spaced milestone sessions within a phase."""
    by_s: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(total_sessions)}
    n = len(items)
    if n == 0 or total_sessions <= 0:
        return by_s
    for idx, it in enumerate(items):
        target_s = min(total_sessions - 1, max(0, ((idx + 1) * total_sessions) // n - 1))
        by_s[target_s].append(it)
    return by_s


def _sync_roadmap_locked(conn: sqlite3.Connection) -> None:
    """Seed user_preferences and build the interleaved 60-Session (and 120-Light-Session) 5-Phase Staff SDET curriculum."""
    now = time.time()
    default_prefs = [
        ("staff_sdet_roadmap_enabled", "1"),
        ("active_roadmap_profile", "staff-sdet"),
        ("roadmap_pace", "60d"),
        ("current_streak_days", "14"),
        ("base_xp", "1200"),
    ]
    for k, v in default_prefs:
        conn.execute(
            "INSERT OR IGNORE INTO user_preferences (key, value, updated_at) VALUES (?, ?, ?)",
            (k, v, now),
        )

    chapter_rows = conn.execute(
        """
        SELECT c.slug, c.course_id, c.chapter_number, c.title, c.reading_time_minutes,
               COALESCE(k.priority_rank, 99) AS priority_rank,
               COALESCE(k.short_title, c.volume) AS course_short_title
        FROM kb_chapters c
        LEFT JOIN kb_courses k ON k.course_id = c.course_id
        WHERE c.slug NOT LIKE 'lab-%'
        ORDER BY priority_rank ASC, c.chapter_number ASC, c.module_number ASC, c.slug ASC
        """
    ).fetchall()
    chapters_by_course: Dict[str, List[sqlite3.Row]] = {}
    for r in chapter_rows:
        chapters_by_course.setdefault(r["course_id"], []).append(r)

    wb_by_id = {w["id"]: w for w in WORKBENCH_CATALOG}
    mi_rows = {
        r["session_id"]: r
        for r in conn.execute("SELECT session_id, title FROM mock_interview_sessions ORDER BY session_id ASC").fetchall()
    }
    dsa_dash = state_manager.get_dashboard_payload().get("dsa", {})
    dsa_by_ch: Dict[str, List[Dict[str, Any]]] = {}
    for p in dsa_dash.get("problems", []):
        ch_num = str(p.get("chapterNumber") or "01").zfill(2)
        dsa_by_ch.setdefault(ch_num, []).append(p)

    order_idx = 0
    session_60_cursor = 0
    session_120_cursor = 0
    prev_item_id: Optional[str] = None
    conn.execute("DELETE FROM roadmap_items;")

    for phase in ROADMAP_PHASES_SPEC:
        pnum = int(phase["phaseNumber"])
        s_count = ROADMAP_PHASE_SESSION_BUDGETS.get(pnum, 10)
        course_xp = 100 if pnum <= 2 else (125 if pnum == 3 else 150)

        # 1. Build ordered per-track lists for this phase
        phase_courses: List[Dict[str, Any]] = []
        for cid in phase["courses"]:
            for ch in chapters_by_course.get(cid, []):
                c_rank = int(ch["priority_rank"] or 1)
                ch_num = int(ch["chapter_number"] or 1)
                alias_id = f"c{c_rank:02d}-ch{ch_num:02d}"
                short_title_raw = str(ch["title"]).split(":")[0].strip()
                if len(short_title_raw) > 22:
                    short_title_raw = short_title_raw[:20].rstrip() + "…"
                phase_courses.append({
                    "item_id": ch["slug"],
                    "track": "courses",
                    "title": f"Course {c_rank:02d} · Ch {ch_num:02d}: {ch['title']}",
                    "slug": ch["slug"],
                    "estimated_minutes": int(ch["reading_time_minutes"] or 15),
                    "xp_reward": course_xp,
                    "meta": {
                        "courseId": cid,
                        "courseShortTitle": ch["course_short_title"],
                        "chapterNumber": ch_num,
                        "aliasId": alias_id,
                        "shortChipLabel": f"C{c_rank:02d}·Ch{ch_num:02d}: {short_title_raw}",
                        "actionType": "course-chapter",
                    },
                })

        phase_dsa: List[Dict[str, Any]] = []
        for ch_num in phase["dsaChapterNumbers"]:
            for prob in dsa_by_ch.get(ch_num, []):
                prob_id_num = int(prob["id"])
                dsa_item_id = f"dsa-{prob_id_num:03d}"
                f_slug = prob.get("folderSlug") or f"{prob_id_num:03d}-{prob['slug']}"
                p_short = str(prob["title"])
                if len(p_short) > 20:
                    p_short = p_short[:18].rstrip() + "…"
                phase_dsa.append({
                    "item_id": dsa_item_id,
                    "track": "dsa",
                    "title": f"DSA #{prob_id_num:03d}: {prob['title']} ({prob.get('pattern', '')})",
                    "slug": f_slug,
                    "estimated_minutes": 20,
                    "xp_reward": 120,
                    "meta": {
                        "problemId": prob_id_num,
                        "folderSlug": f_slug,
                        "aliasId": f_slug,
                        "chapterNumber": ch_num,
                        "pattern": prob.get("pattern", ""),
                        "difficulty": prob.get("difficulty", "Medium"),
                        "hasLocalFiles": bool(prob.get("hasLocalFiles")),
                        "shortChipLabel": f"DSA #{prob_id_num:03d}: {p_short}",
                        "actionType": "dsa-problem",
                    },
                })

        phase_wb: List[Dict[str, Any]] = []
        for wbid in phase["workbenchIds"]:
            wb = wb_by_id.get(wbid)
            if not wb:
                continue
            wb_short = re.sub(r"^\d+\.\s*", "", str(wb["title"]))
            if len(wb_short) > 20:
                wb_short = wb_short[:18].rstrip() + "…"
            phase_wb.append({
                "item_id": wbid,
                "track": "workbench",
                "title": f"Workbench Lab: {wb['title']}",
                "slug": wbid,
                "estimated_minutes": 25,
                "xp_reward": 300,
                "meta": {
                    "category": wb["category"],
                    "folderPath": wb["folderPath"],
                    "relatedChapter": wb.get("relatedChapter", ""),
                    "shortChipLabel": f"Lab: {wb_short}",
                    "actionType": "workbench-lab",
                },
            })

        phase_mock: List[Dict[str, Any]] = []
        for mid in phase["mockIds"]:
            mrow = mi_rows.get(mid)
            title = mrow["title"] if mrow else f"Staff Mock Interview ({mid})"
            phase_mock.append({
                "item_id": mid,
                "track": "mock",
                "title": title,
                "slug": mid,
                "estimated_minutes": 45,
                "xp_reward": 500,
                "meta": {
                    "sessionId": mid,
                    "shortChipLabel": "Mock Sim #1 (100-Pt)",
                    "actionType": "mock-interview",
                },
            })

        wb_by_s = _milestone_session_map(phase_wb, s_count)
        mock_by_s = _milestone_session_map(phase_mock, s_count)

        # 2. Partition into `s_count` daily sessions with Course + DSA micro-interleaving
        n_courses = len(phase_courses)
        n_dsa = len(phase_dsa)
        for s_idx in range(s_count):
            session_60_cursor += 1
            c_slice = phase_courses[(s_idx * n_courses) // s_count : ((s_idx + 1) * n_courses) // s_count]
            d_slice = phase_dsa[math.ceil(s_idx * n_dsa / s_count) : math.ceil((s_idx + 1) * n_dsa / s_count)]

            paired: List[Dict[str, Any]] = []
            max_pair_len = max(len(c_slice), len(d_slice))
            for k in range(max_pair_len):
                if k < len(c_slice):
                    paired.append(c_slice[k])
                if k < len(d_slice):
                    paired.append(d_slice[k])
            paired.extend(wb_by_s[s_idx])
            paired.extend(mock_by_s[s_idx])

            mid_split = max(1, len(paired) // 2) if len(paired) > 1 else len(paired)
            s120_a = session_120_cursor + 1
            s120_b = session_120_cursor + 2
            session_120_cursor += 2

            for idx_in_s, entry in enumerate(paired):
                order_idx += 1
                meta_obj = dict(entry["meta"])
                meta_obj["session60"] = session_60_cursor
                meta_obj["session120"] = s120_a if idx_in_s < mid_split else s120_b
                prereqs = [prev_item_id] if prev_item_id else []
                conn.execute(
                    """
                    INSERT OR REPLACE INTO roadmap_items (
                        item_id, track, title, slug, phase_number, order_index,
                        estimated_minutes, xp_reward, meta_json, prerequisites_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry["item_id"],
                        entry["track"],
                        entry["title"],
                        entry["slug"],
                        pnum,
                        order_idx,
                        entry["estimated_minutes"],
                        entry["xp_reward"],
                        json.dumps(meta_obj),
                        json.dumps(prereqs),
                    ),
                )
                prev_item_id = entry["item_id"]


def _resolve_roadmap_item_id(conn: sqlite3.Connection, raw_item_id: str) -> Optional[str]:
    """Resolve canonical item_id or shorthand alias (e.g. 'c01-ch01', 'dsa-001', or '001-two-sum')."""
    candidate = (raw_item_id or "").strip()
    if not candidate:
        return None
    direct = conn.execute("SELECT item_id FROM roadmap_items WHERE item_id = ? OR slug = ?", (candidate, candidate)).fetchone()
    if direct:
        return direct["item_id"]
    m_dsa = re.match(r"^dsa-(\d+)$", candidate.lower())
    if m_dsa:
        prefix = f"{int(m_dsa.group(1)):03d}-%"
        row = conn.execute(
            "SELECT item_id FROM roadmap_items WHERE track = 'dsa' AND item_id LIKE ? LIMIT 1",
            (prefix,),
        ).fetchone()
        if row:
            return row["item_id"]
    m = re.match(r"^c(\d+)-ch(\d+)$", candidate.lower())
    if m:
        c_rank = int(m.group(1))
        ch_num = int(m.group(2))
        row = conn.execute(
            """
            SELECT c.slug FROM kb_chapters c
            JOIN kb_courses k ON k.course_id = c.course_id
            WHERE k.priority_rank = ? AND c.chapter_number = ? AND c.slug NOT LIKE 'lab-%'
            LIMIT 1
            """,
            (c_rank, ch_num),
        ).fetchone()
        if row:
            return row["slug"]
    return None


def get_roadmap_status(db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Compute unified Staff SDET Roadmap status, 4-track counters, 5-phase progression, Rank/XP/Streak, and Up Next item."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        prefs = {
            r["key"]: r["value"]
            for r in conn.execute("SELECT key, value FROM user_preferences").fetchall()
        }
        roadmap_enabled = prefs.get("staff_sdet_roadmap_enabled", "1") in ("1", "true", "True", "yes")
        raw_pace = str(prefs.get("roadmap_pace", "60d") or "60d").strip().lower()
        pace = "120d" if "120" in raw_pace or raw_pace == "light" else "60d"
        total_sessions = 120 if pace == "120d" else 60
        streak_days = int(prefs.get("current_streak_days", "14") or 14)
        base_xp = int(prefs.get("base_xp", "1200") or 1200)

        manual_rows = {
            r["item_id"]: (int(r["completed"]), r["source"], r["completed_at"])
            for r in conn.execute("SELECT item_id, completed, source, completed_at FROM roadmap_completions").fetchall()
        }
        quiz_mastered = {
            r["slug"]
            for r in conn.execute("SELECT slug FROM kb_quiz_attempts WHERE mastered = 1").fetchall()
        }
        wb_passed = {
            r["item_id"]
            for r in conn.execute("SELECT item_id FROM workbench_runs WHERE status = 'PASS'").fetchall()
        }
        dsa_dash = state_manager.get_dashboard_payload().get("dsa", {})
        dsa_done = set()
        for p in dsa_dash.get("problems", []):
            if p.get("bothDone"):
                dsa_done.add(f"dsa-{int(p['id']):03d}")
                if p.get("folderSlug"):
                    dsa_done.add(p["folderSlug"])

        item_rows = conn.execute(
            "SELECT * FROM roadmap_items ORDER BY order_index ASC"
        ).fetchall()

        tracks_acc: Dict[str, Dict[str, Any]] = {
            "courses": {
                "track": "courses",
                "title": "📖 Textbook Courses (01–12)",
                "shortTitle": "Courses",
                "unitLabel": "Chapters",
                "total": 0,
                "completed": 0,
                "done": 0,
                "remaining": 0,
                "percentage": 0,
                "pct": 0,
                "nextItem": None,
            },
            "dsa": {
                "track": "dsa",
                "title": "🧩 DSA 50/50 Coding Studio",
                "shortTitle": "Coding / DSA",
                "unitLabel": "Problems",
                "total": 0,
                "completed": 0,
                "done": 0,
                "remaining": 0,
                "percentage": 0,
                "pct": 0,
                "nextItem": None,
            },
            "workbench": {
                "track": "workbench",
                "title": "🛠️ Local Zero-AI Workbench",
                "shortTitle": "Workbench",
                "unitLabel": "Labs & Suites",
                "total": 0,
                "completed": 0,
                "done": 0,
                "remaining": 0,
                "percentage": 0,
                "pct": 0,
                "nextItem": None,
            },
            "mock": {
                "track": "mock",
                "title": "🎙️ Staff Mock Simulator",
                "shortTitle": "Mock Sim",
                "unitLabel": "Scenarios",
                "total": 0,
                "completed": 0,
                "done": 0,
                "remaining": 0,
                "percentage": 0,
                "pct": 0,
                "nextItem": None,
            },
        }

        track_type_map = {
            "courses": "course",
            "dsa": "dsa",
            "workbench": "workbench",
            "mock": "interview",
        }

        items_by_phase: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: [], 4: [], 5: []}
        completions_map: Dict[str, bool] = {}
        up_next_item: Optional[Dict[str, Any]] = None
        total_items = 0
        completed_items = 0
        earned_xp = base_xp

        for row in item_rows:
            iid = row["item_id"]
            trk = row["track"]
            pnum = int(row["phase_number"])
            order_idx = int(row["order_index"])
            est_mins = int(row["estimated_minutes"])
            meta = json.loads(row["meta_json"] or "{}")

            if iid in manual_rows:
                is_done = manual_rows[iid][0] == 1
                comp_source = manual_rows[iid][1]
            else:
                if trk == "courses":
                    is_done = iid in quiz_mastered
                    comp_source = "quiz_100" if is_done else "pending"
                elif trk == "dsa":
                    is_done = iid in dsa_done
                    comp_source = "dsa_passed" if is_done else "pending"
                elif trk == "workbench":
                    is_done = iid in wb_passed
                    comp_source = "lab_verified" if is_done else "pending"
                else:
                    is_done = False
                    comp_source = "pending"

            completions_map[iid] = is_done
            if meta.get("aliasId"):
                completions_map[meta["aliasId"]] = is_done
            if trk == "dsa" and meta.get("problemId") is not None:
                completions_map[f"dsa-{int(meta['problemId']):03d}"] = is_done

            parent_group = (
                meta.get("courseShortTitle")
                or (f"Ch {meta.get('chapterNumber')}: {meta.get('pattern')}" if trk == "dsa" else "")
                or meta.get("category")
                or "Staff Bar-Raiser"
            )
            s60 = int(meta.get("session60") or 1)
            s120 = int(meta.get("session120") or (s60 * 2 - 1))
            active_s_num = s120 if pace == "120d" else s60
            short_chip = str(meta.get("shortChipLabel") or row["title"][:28])
            why_now = (
                f"Session {active_s_num} of {total_sessions} (Phase {pnum} · {parent_group}) — interleaved daily slot keeping Course architecture + DSA reps synchronized."
            )

            item_obj = {
                "itemId": iid,
                "aliasId": meta.get("aliasId", iid),
                "track": trk,
                "trackType": track_type_map.get(trk, "course"),
                "title": row["title"],
                "shortChipLabel": short_chip,
                "slug": row["slug"],
                "phaseNumber": pnum,
                "session60": s60,
                "session120": s120,
                "sessionNumber": active_s_num,
                "orderIndex": order_idx,
                "globalOrder": order_idx,
                "estimatedMinutes": est_mins,
                "estMinutes": est_mins,
                "xpReward": int(row["xp_reward"]),
                "completed": is_done,
                "source": comp_source,
                "parentGroup": parent_group,
                "whyNow": why_now,
                "meta": meta,
            }

            total_items += 1
            if is_done:
                completed_items += 1
                earned_xp += int(row["xp_reward"])
            elif up_next_item is None:
                up_next_item = item_obj

            if trk in tracks_acc:
                tracks_acc[trk]["total"] += 1
                if is_done:
                    tracks_acc[trk]["completed"] += 1
                    tracks_acc[trk]["done"] += 1
                elif tracks_acc[trk]["nextItem"] is None:
                    tracks_acc[trk]["nextItem"] = item_obj

            items_by_phase.setdefault(pnum, []).append(item_obj)

        for t_obj in tracks_acc.values():
            t_tot = t_obj["total"]
            t_comp = t_obj["completed"]
            t_obj["remaining"] = max(0, t_tot - t_comp)
            pct_val = round((t_comp / t_tot) * 100, 1) if t_tot > 0 else 0.0
            t_obj["percentage"] = pct_val
            t_obj["pct"] = pct_val

        overall_pct = round((completed_items / total_items) * 100, 1) if total_items > 0 else 0.0
        if overall_pct >= 90:
            rank_icon = "👑"
            rank_short = "Staff Bar-Raiser"
            rank_title = "👑 Staff Bar-Raiser (Principal Systems Architect)"
            next_rank = "🏆 Principal Quality Fellow (Max Rank)"
            next_rank_pct = 100
        elif overall_pct >= 60:
            rank_icon = "⚡"
            rank_short = "Staff SDET Candidate"
            rank_title = "⚡ Staff SDET Candidate (SRE, Data & Security)"
            next_rank = "👑 Staff Bar-Raiser (Principal Systems Architect)"
            next_rank_pct = 90
        elif overall_pct >= 30:
            rank_icon = "🛠️"
            rank_short = "Lead SDET"
            rank_title = "🛠️ Lead SDET (Frameworks & Concurrency)"
            next_rank = "⚡ Staff SDET Candidate (SRE, Data & Security)"
            next_rank_pct = 60
        else:
            rank_icon = "🌱"
            rank_short = "Senior SDET"
            rank_title = "🌱 Senior SDET (Foundations & Scale)"
            next_rank = "🛠️ Lead SDET (Frameworks & Concurrency)"
            next_rank_pct = 30

        phase_weeks_map = {
            1: "Weeks 1–2",
            2: "Weeks 3–4",
            3: "Weeks 5–8",
            4: "Weeks 9–11",
            5: "Week 12",
        }
        phases_out = []
        active_phase_found = False
        unlocked_soundbites = 0
        all_items_flat: List[Dict[str, Any]] = []
        for p_spec in ROADMAP_PHASES_SPEC:
            pnum = int(p_spec["phaseNumber"])
            p_items = items_by_phase.get(pnum, [])
            all_items_flat.extend(p_items)
            p_tot = len(p_items)
            p_comp = sum(1 for x in p_items if x["completed"])
            p_rem = max(0, p_tot - p_comp)
            p_pct = round((p_comp / p_tot) * 100, 1) if p_tot > 0 else 0.0
            if p_tot > 0 and p_comp == p_tot:
                p_status = "completed"
            elif not active_phase_found:
                p_status = "active"
                active_phase_found = True
            else:
                p_status = "locked"

            sb_unlocked = p_comp > 0 or pnum == 1
            if sb_unlocked:
                unlocked_soundbites += 1

            if p_items:
                s_min = min(x["sessionNumber"] for x in p_items)
                s_max = max(x["sessionNumber"] for x in p_items)
                session_range = f"S{s_min}–S{s_max}"
            else:
                session_range = f"Phase {pnum}"

            p_next = next((x for x in p_items if not x["completed"]), None)
            phases_out.append({
                "phaseNumber": pnum,
                "title": p_spec["title"],
                "shortTitle": p_spec["shortTitle"],
                "subtitle": p_spec["objective"],
                "objective": p_spec["objective"],
                "weeks": phase_weeks_map.get(pnum, f"Phase {pnum}"),
                "sessionRange": session_range,
                "exitGate": p_spec["exitGate"],
                "status": p_status,
                "total": p_tot,
                "totalItems": p_tot,
                "completed": p_comp,
                "completedItems": p_comp,
                "remaining": p_rem,
                "percentage": p_pct,
                "pct": p_pct,
                "soundbite": p_spec["soundbiteQuote"],
                "soundbiteTitle": p_spec["soundbiteTitle"],
                "soundbiteQuote": p_spec["soundbiteQuote"],
                "soundbiteUnlocked": sb_unlocked,
                "nextItem": p_next,
                "items": p_items,
            })

        # Compute Today's Active Rigid Session summary & item chips
        active_session_num = up_next_item["sessionNumber"] if up_next_item else total_sessions
        today_items = [x for x in all_items_flat if x["sessionNumber"] == active_session_num]
        if not today_items and all_items_flat:
            today_items = [all_items_flat[0]]
        td_phase = today_items[0]["phaseNumber"] if today_items else 1
        td_comp = sum(1 for x in today_items if x["completed"])
        td_tot = len(today_items)
        td_rem_mins = sum(x["estMinutes"] for x in today_items if not x["completed"])
        c_tot = sum(1 for x in today_items if x["track"] == "courses")
        c_done = sum(1 for x in today_items if x["track"] == "courses" and x["completed"])
        d_tot = sum(1 for x in today_items if x["track"] == "dsa")
        d_done = sum(1 for x in today_items if x["track"] == "dsa" and x["completed"])
        w_tot = sum(1 for x in today_items if x["track"] == "workbench")
        w_done = sum(1 for x in today_items if x["track"] == "workbench" and x["completed"])
        m_tot = sum(1 for x in today_items if x["track"] == "mock")
        m_done = sum(1 for x in today_items if x["track"] == "mock" and x["completed"])

        quota_parts: List[str] = []
        if c_tot:
            quota_parts.append(f"📚 {c_done}/{c_tot} Ch")
        if d_tot:
            quota_parts.append(f"💻 {d_done}/{d_tot} DSA")
        if w_tot:
            quota_parts.append(f"🛠️ {w_done}/{w_tot} Lab")
        if m_tot:
            quota_parts.append(f"🎙️ {m_done}/{m_tot} Mock")
        quota_parts.append(f"{td_comp}/{td_tot} Done (~{td_rem_mins}m left)")

        today_session = {
            "sessionNumber": active_session_num,
            "totalSessions": total_sessions,
            "pace": pace,
            "phaseNumber": td_phase,
            "completedCount": td_comp,
            "totalCount": td_tot,
            "remainingMinutes": td_rem_mins,
            "quotaSummary": " · ".join(quota_parts),
            "items": [
                {
                    "itemId": x["itemId"],
                    "globalOrder": x["globalOrder"],
                    "track": x["track"],
                    "trackType": x["trackType"],
                    "title": x["title"],
                    "shortChipLabel": x["shortChipLabel"],
                    "estMinutes": x["estMinutes"],
                    "completed": x["completed"],
                    "isUpNext": bool(up_next_item and x["itemId"] == up_next_item["itemId"]),
                }
                for x in today_items
            ],
        }

        pages_alias = {
            "courses": tracks_acc["courses"],
            "dsa": tracks_acc["dsa"],
            "workbench": tracks_acc["workbench"],
            "interviews": tracks_acc["mock"],
            "mock": tracks_acc["mock"],
        }

        return {
            "roadmapEnabled": roadmap_enabled,
            "profile": prefs.get("active_roadmap_profile", "staff-sdet"),
            "pace": pace,
            "totalSessions": total_sessions,
            "todaySession": today_session,
            "macro": {
                "totalItems": total_items,
                "completedItems": completed_items,
                "remainingItems": max(0, total_items - completed_items),
                "pct": overall_pct,
            },
            "gamification": {
                "rankIcon": rank_icon,
                "rankTitle": rank_short,
                "fullRankTitle": rank_title,
                "nextRank": next_rank,
                "nextRankAtPct": next_rank_pct,
                "xp": earned_xp,
                "streakDays": streak_days,
                "freezeAvailable": True,
                "unlockedSoundbitesCount": unlocked_soundbites,
            },
            "overall": {
                "total": total_items,
                "completed": completed_items,
                "remaining": max(0, total_items - completed_items),
                "percentage": overall_pct,
                "rank": rank_title,
                "nextRank": next_rank,
                "nextRankAtPct": next_rank_pct,
                "xp": earned_xp,
                "streakDays": streak_days,
                "unlockedSoundbitesCount": unlocked_soundbites,
            },
            "upNext": up_next_item,
            "pages": pages_alias,
            "tracks": tracks_acc,
            "phases": phases_out,
            "completedMap": completions_map,
            "completionsMap": completions_map,
        }
    finally:
        conn.close()


def set_roadmap_pace(pace: str, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Configure daily session pace ('60d' Standard ~80m/day vs '120d' Light ~40m/day)."""
    ensure_initialized(db_path)
    norm_pace = "120d" if "120" in str(pace or "").lower() or str(pace or "").lower() == "light" else "60d"
    conn = _get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES ('roadmap_pace', ?, ?)
            """,
            (norm_pace, time.time()),
        )
        conn.commit()
    finally:
        conn.close()
    return get_roadmap_status(db_path)


def set_roadmap_toggle(enabled: bool, db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Enable or disable the configurable Staff SDET Roadmap tracker on the Home page & across views."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES ('staff_sdet_roadmap_enabled', ?, ?)
            """,
            ("1" if enabled else "0", time.time()),
        )
        conn.commit()
    finally:
        conn.close()
    return get_roadmap_status(db_path)


def set_roadmap_item_done(
    item_id: str,
    completed: Optional[bool] = None,
    source: str = "manual",
    db_path: pathlib.Path = DEFAULT_DB_PATH,
) -> Tuple[int, Dict[str, Any]]:
    """Mark any Course chapter, DSA problem, Workbench lab, or Mock Interview scenario as done/undone (toggles if completed is None)."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        resolved_id = _resolve_roadmap_item_id(conn, item_id)
        if not resolved_id:
            return 404, {"error": f"Roadmap item '{item_id}' not found"}
        if completed is None:
            cur_status = get_roadmap_status(db_path)
            cur_val = bool(cur_status.get("completedMap", {}).get(resolved_id))
            next_completed = not cur_val
        else:
            next_completed = bool(completed)
        conn.execute(
            """
            INSERT OR REPLACE INTO roadmap_completions (item_id, completed, completed_at, source, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                resolved_id,
                1 if next_completed else 0,
                time.time() if next_completed else None,
                source or "manual",
                "",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    status = get_roadmap_status(db_path)
    status["itemId"] = resolved_id
    status["requestedId"] = item_id
    status["completed"] = bool(next_completed)
    status["updatedItem"] = {
        "itemId": resolved_id,
        "requestedId": item_id,
        "completed": bool(next_completed),
        "source": source or "manual",
    }
    return 200, status

