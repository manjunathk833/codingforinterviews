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
    parts: List[str] = []
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

    # Consolidate into at most 4 predictable progressive steps
    if len(raw_sections) > 4:
        merged_tail = "\n\n".join(ch for _, ch in raw_sections[3:])
        raw_sections = raw_sections[:3] + [(raw_sections[3][0], merged_tail)]

    default_short = [
        "🌱 1. Plain-English Story",
        "🔨 2. First Lines of Code",
        "⚡ 3. Real-World & Sim",
        "🚀 4. Staff Deep-Dive",
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
        badge_prefix = ["🌱 1.", "🔨 2.", "⚡ 3.", "🚀 4."][min(idx, 3)]
        steps_out.append(
            {
                "stepNumber": idx + 1,
                "shortLabel": f"{badge_prefix} {clean_short}" if clean_short else default_short[min(idx, 3)],
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
                if key == "tags" and val.startswith("["):
                    try:
                        meta["tags"] = json.loads(val)
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
        row["slug"]: (row["sha256"], row["source_path"])
        for row in conn.execute("SELECT slug, sha256, source_path FROM kb_chapters").fetchall()
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
        if existing_rows.get(slug, ("", ""))[0] == sha:
            continue

        rebuild_fts = True
        rel_source = str(path.relative_to(REPO_ROOT))
        lab_path = parsed.get("lab_path") or (str(path.parent.relative_to(REPO_ROOT)) if path.name == "README.md" else "")
        conn.execute(
            """
            INSERT OR REPLACE INTO kb_chapters (
                slug, course_id, track, volume, module_number, module_title,
                chapter_number, level_tag, title, summary,
                reading_time_minutes, video_url, visualizer_id, lab_path, tags_json,
                continuity_json, walkthrough_json, pretraining_json, prediction_prompt_json,
                markdown_body, quizzes_json, source_path, sha256, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    conn.commit()


def get_kb_courses(db_path: pathlib.Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Return all 8 Prioritized Textbook Courses with hierarchical Modules -> Chapters and mastery progress."""
    ensure_initialized(db_path)
    conn = _get_connection(db_path)
    try:
        course_rows = conn.execute("SELECT * FROM kb_courses ORDER BY priority_rank ASC").fetchall()
        chapter_rows = conn.execute(
            """
            SELECT c.slug, c.course_id, c.track, c.volume, c.module_number, c.module_title,
                   c.chapter_number, c.level_tag, c.title, c.summary, c.reading_time_minutes,
                   c.visualizer_id, c.lab_path, c.quizzes_json,
                   COALESCE(a.mastered, 0) AS mastered
            FROM kb_chapters c
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
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

        # Group the 8 Textbook Courses across the 3 textbook pillar cards while exposing all 8 courses directly
        pillar_course_groups = {
            "system-design": ["01-zero-to-staff-sdet", "02-building-testing-frameworks", "07-distributed-system-design"],
            "ai-engineering": ["05-ai-engineering", "06-ai-engineering-qa-focused"],
            "core-cs": ["03-ui-automation-playwright", "04-api-and-api-automation", "08-core-cs-internals"],
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
                   COALESCE(a.mastered, 0) AS mastered,
                   a.score AS quiz_score,
                   a.total AS quiz_total
            FROM kb_chapters c
            LEFT JOIN kb_courses k ON k.course_id = c.course_id
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
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
                   COALESCE(a.mastered, 0) AS mastered,
                   a.score AS quiz_score,
                   a.total AS quiz_total
            FROM kb_chapters c
            LEFT JOIN kb_courses k ON k.course_id = c.course_id
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
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
            SELECT c.*, COALESCE(a.mastered, 0) AS mastered
            FROM kb_chapters c
            LEFT JOIN kb_quiz_attempts a ON a.slug = c.slug
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
        items = []
        for wb in WORKBENCH_CATALOG:
            entry = dict(wb)
            entry["lastRun"] = runs.get(wb["id"])
            items.append(entry)
        return {
            "executionModel": "100% Local Deterministic Verification (Strictly Zero AI Dependency)",
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
            SELECT session_id, title, target_role, status, overall_score,
                   folder_path, related_chapters_json, updated_at
            FROM mock_interview_sessions
            ORDER BY session_id ASC
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
            "SELECT * FROM mock_interview_sessions WHERE session_id = ?",
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
