#!/usr/bin/env python3
"""
State Manager & Curriculum Feed Engine for the Antigravity Learning Hub.
Synchronizes progress across:
- dsa/MASTER_SHEET.md
- PRACTICE_CYCLE.md
- frameworks/MASTER_FRAMEWORKS.md
- mock-interviews/README.md
- hub/db.json (XP, streaks, completed concept cards, quiz history, SRS queue)
"""

import json
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DSA_ROOT = REPO_ROOT / "dsa"
MASTER_SHEET = DSA_ROOT / "MASTER_SHEET.md"
PRACTICE_CYCLE = REPO_ROOT / "PRACTICE_CYCLE.md"
MOCK_README = REPO_ROOT / "mock-interviews" / "README.md"
HUB_DIR = REPO_ROOT / "hub"
DB_PATH = HUB_DIR / "db.json"

# ------------------------------------------------------------------------------
# High-Yield Concept Feed Cards (Casual "Social Media Style" Micro-Learning)
# ------------------------------------------------------------------------------
CONCEPT_FEED_CARDS: List[Dict[str, Any]] = [
    {
        "id": "card-dsa-group-anagrams",
        "category": "DSA Invariants",
        "title": "Why Counting Beats Sorting in Group Anagrams",
        "readTime": "60 sec",
        "difficulty": "Medium",
        "tags": ["Hash Table", "String", "O(M*N)"],
        "mentalModel": (
            "Imagine sorting 10,000 bags of Scrabble tiles alphabetically just to see which bags "
            "have the same tiles—that costs O(N log N) per bag. Instead, weigh how many 'a's, 'b's, "
            "and 'z's are in each bag in a single pass O(N) and print a 26-number barcode on the bag!"
        ),
        "mechanics": (
            "1. Allocate a fixed 26-slot array `count = [0] * 26`.\n"
            "2. Map each character via ASCII offset: `ord(c) - ord('a')`.\n"
            "3. In Python, convert the mutable list to an immutable `tuple(count)` to serve as a dict key.\n"
            "4. In Java, serialize with a delimiter (`#1#0#2...`) because `int[]` uses reference equality."
        ),
        "diagram": (
            'Word: "eat" -> [1, 0, 0, 0, 1, ..., 1, ...] -> Key: (1,0,0,0,1..1..)\n'
            'Word: "tea" -> [1, 0, 0, 0, 1, ..., 1, ...] -> Key: (1,0,0,0,1..1..)  [SAME BUCKET!]'
        ),
        "gotcha": (
            "In Java, if you concatenate counts without a delimiter (`1` then `11` vs `11` then `1`), "
            "both produce `\"111\"` and collide! Always prefix each count with `'#'`."
        ),
        "visualizerId": "dsa-group-anagrams",
        "quiz": {
            "question": "Why can't we use a Python list `[1, 0, ...]` directly as a dictionary key?",
            "options": [
                "Lists are too large in memory for hash tables",
                "Lists are mutable and therefore unhashable in Python",
                "Python dictionaries only accept string keys",
                "Tuples sort elements automatically whereas lists do not"
            ],
            "correctIndex": 1,
            "explanation": "Dictionary keys must have a stable hash value over their lifetime. Since lists can be mutated in-place, Python forbids hashing them (`TypeError: unhashable type: 'list'`)."
        }
    },
    {
        "id": "card-os-memory-and-leaks",
        "category": "OS Internals",
        "title": "Desktop Daemons: Memory Leaks, Handle Leaks & Kernel Hooks",
        "readTime": "90 sec",
        "difficulty": "Staff SDET",
        "tags": ["Operating Systems", "macOS", "Windows", "Profiling"],
        "mentalModel": (
            "A background endpoint agent (like Netskope or CrowdStrike) runs 24/7. If a short-lived script "
            "leaks 1MB per minute, nobody notices. If a background daemon leaks 1MB or 5 file descriptors "
            "per minute, the user's Mac or Windows PC crashes with Out-Of-Memory or 'Too Many Open Files' within hours."
        ),
        "mechanics": (
            "• Virtual Memory vs. RSS (Resident Set Size): RSS is actual physical RAM occupied.\n"
            "• File Descriptor / Handle Leaks: Every open file, socket, or pipe consumes an OS kernel handle (`lsof -p <pid>` on macOS/Linux; `PerfMon` / `Process Explorer` on Windows).\n"
            "• USB & Filesystem Monitoring: Modern macOS uses the `EndpointSecurity` (ES) framework & `FSEvents` in user-space (replacing deprecated kernel extensions `kexts`), while Windows uses File System Minifilter drivers in kernel-space."
        ),
        "diagram": (
            "[User Space]   Endpoint Agent Daemon (RSS Memory, Thread Pool, SQLite Queue)\n"
            "                     ▲  │ (System Calls / IPC / Mach Ports)\n"
            "[Kernel Space] VFS / EndpointSecurity (macOS) | Minifilter Driver (Windows) ◄── USB / Disk I/O"
        ),
        "gotcha": (
            "When testing memory leaks in C#/Java/Python clients, a rising memory graph isn't always a leak—it "
            "could be uncollected garbage. Always trigger a full GC and measure the post-GC baseline floor across a 24h soak test!"
        ),
        "visualizerId": "arch-endpoint-cloud-sync",
        "quiz": {
            "question": "During a 48-hour soak test of a macOS desktop client, RAM stays flat at 80MB, but the app crashes when opening network sockets. What is the most likely root cause?",
            "options": [
                "CPU thermal throttling",
                "File descriptor (socket/file handle) leak exhausting the OS ulimit",
                "Swap space fragmentation",
                "DNS cache poisoning"
            ],
            "correctIndex": 1,
            "explanation": "Each unclosed file or socket consumes an OS file descriptor without using much RAM. Once the process hits `ulimit -n` (e.g. 1024 or 4096), all new `socket()` or `open()` syscalls fail with `EMFILE (Too many open files)`."
        }
    },
    {
        "id": "card-net-cdp-vs-w3c",
        "category": "Computer Networks",
        "title": "Playwright CDP WebSockets vs. Selenium W3C HTTP Protocol",
        "readTime": "75 sec",
        "difficulty": "Senior SDET",
        "tags": ["WebSockets", "HTTP", "Playwright", "Selenium"],
        "mentalModel": (
            "Selenium is like mailing paper letters via a postmaster (`chromedriver`) for every single click—each "
            "command waits for an HTTP roundtrip. Playwright opens a direct, persistent fiber-optic phone line "
            "(full-duplex WebSocket) directly into the browser engine."
        ),
        "mechanics": (
            "• Selenium (W3C WebDriver): Stateless HTTP Request/Response. 50 DOM checks = 50 HTTP roundtrips through the driver binary.\n"
            "• Playwright (CDP over WebSocket): Single persistent TCP connection upgraded via HTTP `101 Switching Protocols`. Bidirectional JSON-RPC frames stream events (`domcontentloaded`, `networkidle`) in <1ms.\n"
            "• Memory Isolation: 1 `Browser` process spawns 32 isolated `BrowserContext` incognito profiles (~20MB RAM each vs. ~500MB per Selenium browser process)."
        ),
        "diagram": (
            "Selenium:   [Test] ──HTTP POST──► [ChromeDriver] ──HTTP──► [Browser] (New roundtrip every call)\n"
            "Playwright: [Test] ◄══Persistent Full-Duplex WebSocket══► [Browser -> Context 1..32]"
        ),
        "gotcha": (
            "Even with Playwright's auto-waiting, SSR apps (Next.js/React) can flake due to the 'Hydration Gap': "
            "the HTML button is visible and enabled before React finishes attaching the JS `onClick` listener!"
        ),
        "visualizerId": "arch-playwright-vs-selenium",
        "quiz": {
            "question": "How does Playwright isolate 32 parallel test threads without consuming 16GB+ of RAM?",
            "options": [
                "It runs all tests inside the same browser tab sequentially",
                "It shares a single OS Browser process and creates lightweight isolated BrowserContexts per thread",
                "It compresses the DOM tree into binary protobufs",
                "It disables JavaScript execution in parallel workers"
            ],
            "correctIndex": 1,
            "explanation": "A `BrowserContext` acts like an isolated incognito profile (separate cookies, localStorage, and cache) inside a single shared Browser process, taking ~15ms and ~20MB RAM."
        }
    },
    {
        "id": "card-sd-endpoint-cloud-sync",
        "category": "System Design",
        "title": "Endpoint-to-Cloud Continuous Sync & Preventing Thundering Herds",
        "readTime": "90 sec",
        "difficulty": "Staff SDET",
        "tags": ["Distributed Systems", "Backpressure", "Resilience"],
        "mentalModel": (
            "Imagine 100,000 desktop agents lose connection during a 2-minute cloud blip. If all 100,000 agents "
            "reconnect at the exact same millisecond and dump their buffered logs, they will DDoS your own cloud "
            "backend—a classic 'Thundering Herd'."
        ),
        "mechanics": (
            "1. Local Ring-Buffer / SQLite WAL Queue: When offline, the endpoint writes events to a bounded local disk queue with FIFO eviction.\n"
            "2. Exponential Backoff + Full Jitter: On failure, wait `random(0, min(max_cap, base * 2^attempt))` before reconnecting.\n"
            "3. Idempotency Keys: Every event carries a deterministic UUID so retries never create duplicate records in the cloud DB."
        ),
        "diagram": (
            "[100k Endpoints] ──(Local SQLite Buffer)──► [Jittered Backoff] ──► [API Gateway] ──► [Kafka] ──► [DB]"
        ),
        "gotcha": (
            "Exponential backoff WITHOUT jitter still causes synchronized spikes! If 10,000 clients fail at t=0, "
            "pure exponential backoff makes all 10,000 retry together at t=2s, t=4s, and t=8s. Random jitter spreads the load."
        ),
        "visualizerId": "arch-endpoint-cloud-sync",
        "quiz": {
            "question": "Why is 'Exponential Backoff' alone insufficient when 50,000 endpoints recover from a network outage simultaneously?",
            "options": [
                "TCP sockets do not support timers longer than 30 seconds",
                "Without random jitter, all 50,000 clients still retry in synchronized waves at 2s, 4s, 8s",
                "Exponential backoff corrupts TLS session tickets",
                "Kafka partitions reject delayed messages"
            ],
            "correctIndex": 1,
            "explanation": "Deterministic backoff shifts the spike in time without spreading it out. Adding random jitter decorrelates client retries into a smooth, flat ingestion rate."
        }
    },
    {
        "id": "card-sd-concurrency-isolation",
        "category": "System Design",
        "title": "Distributed Test Data Isolation Across 32 Parallel CI Workers",
        "readTime": "60 sec",
        "difficulty": "Senior SDET",
        "tags": ["Concurrency", "Microservices", "Test Data"],
        "mentalModel": (
            "If 32 parallel tests all try to book 'Seat 1A' on 'Flight AI-202' in a shared database, 1 test "
            "succeeds and 31 crash with HTTP 409 Conflict. And truncating the DB before each test wipes out "
            "other workers' in-flight data!"
        ),
        "mechanics": (
            "• Never mutate shared static IDs in parallel CI.\n"
            "• Generate an ephemeral cryptographic Tenant Key per test worker: `X-Test-Tenant-ID: tenant_<uuid>`.\n"
            "• Downstream microservices partition state by tenant key (or test-scoped flight IDs), giving every parallel thread its own isolated sandbox."
        ),
        "diagram": (
            "Worker 1 ──(X-Test-Tenant-ID: tenant_a1)──► [Order Svc] ──► [Partition a1: Seat 1A -> 201 OK]\n"
            "Worker 2 ──(X-Test-Tenant-ID: tenant_b2)──► [Order Svc] ──► [Partition b2: Seat 1A -> 201 OK]"
        ),
        "gotcha": (
            "Storing test data in a local Java/Python `ThreadLocal` only isolates variables inside your test runner's RAM—it "
            "does NOT isolate the remote PostgreSQL database unless you propagate the unique tenant/entity key over the network!"
        ),
        "visualizerId": "arch-concurrency-isolation",
        "quiz": {
            "question": "Why doesn't `ThreadLocal` in your test runner prevent `409 Conflict` errors in a shared staging microservice?",
            "options": [
                "ThreadLocal only works in Python, not Java",
                "ThreadLocal isolates memory inside the test runner process, not the remote microservice database",
                "ThreadLocal is garbage-collected before the HTTP request completes",
                "HTTP headers cannot be sent from ThreadLocal threads"
            ],
            "correctIndex": 1,
            "explanation": "Microservices maintain state in remote databases/caches. You must pass a unique tenant header or dynamic entity key in the API request so the backend isolates the state."
        }
    },
    {
        "id": "card-ai-rag-triad",
        "category": "AI & RAG",
        "title": "The RAG Evaluation Triad: Catching LLM Hallucinations in CI",
        "readTime": "75 sec",
        "difficulty": "Staff SDET",
        "tags": ["RAG", "LLM-as-a-Judge", "Ragas", "AI QE"],
        "mentalModel": (
            "Testing a RAG bot is like grading an open-book exam. You must grade two separate things: "
            "1) Did the student open the right page in the textbook (Retrieval)? "
            "2) Did the student only state facts from that page without making things up (Faithfulness)?"
        ),
        "mechanics": (
            "• Context Recall (Retrieval): Fraction of ground-truth facts present in the retrieved vector chunks.\n"
            "• Faithfulness / Groundedness (Generation): Break the LLM's answer into atomic claims $C$; verify what % of $C$ are strictly entailed by the retrieved chunks.\n"
            "• Answer Relevance (Generation): Cosine similarity between the user's question and synthetic questions reverse-generated from the answer."
        ),
        "diagram": (
            "Query ──► [Vector DB] ──► Context Chunks (Recall) ──► [LLM] ──► Answer (Faithfulness & Relevance)"
        ),
        "gotcha": (
            "If your test asserts `cosine_similarity(answer, ground_truth) > 0.85`, an LLM answer that says "
            "'You CANNOT get a refund within 24 hours' will have 96% embedding similarity to 'You CAN get a refund within 24 hours' and pass! Always test claim entailment (Faithfulness)."
        ),
        "visualizerId": "dsa-valid-anagram",
        "quiz": {
            "question": "If a RAG bot retrieves the correct refund policy chunk, but invents a fake $50 bonus credit in its response, which metric drops?",
            "options": [
                "Context Recall",
                "Context Precision",
                "Faithfulness (Groundedness)",
                "Vector Index Latency"
            ],
            "correctIndex": 2,
            "explanation": "Faithfulness measures the ratio of claims in the generated answer that are supported by the retrieved context. Invented claims directly lower Faithfulness."
        }
    }
]


def load_db() -> Dict[str, Any]:
    """Load or initialize the persistent Hub state JSON."""
    default_db = {
        "xp": 250,
        "streakDays": 3,
        "lastActiveDate": str(date.today()),
        "completedCards": [],
        "bookmarkedCards": [],
        "quizHistory": {},
        "srsQueue": ["001-two-sum", "002-valid-anagram", "card-sd-concurrency-isolation"],
        "telegramInbox": []
    }
    if not DB_PATH.exists():
        save_db(default_db)
        return default_db
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        for k, v in default_db.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default_db


def save_db(data: Dict[str, Any]) -> None:
    """Persist Hub state to hub/db.json."""
    HUB_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def discover_local_dsa_folders() -> Dict[str, str]:
    """Map problem slug to relative directory path for problems that exist on disk."""
    mapping = {}
    if not DSA_ROOT.exists():
        return mapping
    for root, _, files in os.walk(DSA_ROOT):
        if "utils" in root or "/." in root:
            continue
        if "Solution.java" in files or "solution.py" in files:
            p = Path(root)
            rel = str(p.relative_to(REPO_ROOT))
            # Extract slug without numeric prefix, e.g. '001-two-sum' -> 'two-sum'
            slug = re.sub(r"^\d+-", "", p.name.lower())
            mapping[slug] = rel
            mapping[p.name.lower()] = rel
    return mapping


def get_dsa_overview() -> Dict[str, Any]:
    """Parse dsa/MASTER_SHEET.md and enrich with local runnable status."""
    local_folders = discover_local_dsa_folders()
    problems = []

    if MASTER_SHEET.exists():
        content = MASTER_SHEET.read_text(encoding="utf-8")
        row_pattern = re.compile(
            r"^\|\s*(\d+)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*\[([ xX])\]\s*\|\s*\[([ xX])\]\s*\|\s*([^|]+)\|\s*([^|]+)\|"
        )
        for line in content.splitlines():
            m = row_pattern.match(line)
            if m:
                prob_id = int(m.group(1))
                title = m.group(2).strip()
                url = m.group(3).strip()
                pattern = m.group(4).strip()
                difficulty = m.group(5).strip()
                java_done = m.group(6).lower() == "x"
                py_done = m.group(7).lower() == "x"
                score = m.group(8).strip()
                status = m.group(9).strip()

                slug = url.strip("/").split("/")[-1].lower()
                local_path = local_folders.get(slug)
                folder_slug = Path(local_path).name if local_path else None

                visualizer_map = {
                    "two-sum": "dsa-two-sum",
                    "valid-anagram": "dsa-valid-anagram",
                    "group-anagrams": "dsa-group-anagrams"
                }

                problems.append({
                    "id": prob_id,
                    "title": title,
                    "slug": slug,
                    "folderSlug": folder_slug,
                    "localPath": local_path,
                    "hasLocalFiles": bool(local_path),
                    "visualizerId": visualizer_map.get(slug),
                    "url": url,
                    "pattern": pattern,
                    "difficulty": difficulty,
                    "javaDone": java_done,
                    "pyDone": py_done,
                    "bothDone": java_done and py_done,
                    "score": score,
                    "status": status
                })

    total = len(problems) or 1
    both_done = sum(1 for p in problems if p["bothDone"])
    local_scaffolded = sum(1 for p in problems if p["hasLocalFiles"])

    by_pattern: Dict[str, Dict[str, int]] = {}
    for p in problems:
        pat = p["pattern"]
        if pat not in by_pattern:
            by_pattern[pat] = {"total": 0, "done": 0, "scaffolded": 0}
        by_pattern[pat]["total"] += 1
        if p["bothDone"]:
            by_pattern[pat]["done"] += 1
        if p["hasLocalFiles"]:
            by_pattern[pat]["scaffolded"] += 1

    return {
        "total": len(problems),
        "bothDone": both_done,
        "localScaffolded": local_scaffolded,
        "completionPct": round((both_done / total) * 100, 1),
        "byPattern": by_pattern,
        "problems": problems
    }


def get_practice_cycle() -> Dict[str, Any]:
    """Parse PRACTICE_CYCLE.md for the active 4-stage loop."""
    stages = []
    cycle_name = "Cycle #1: Distributed Concurrency, Data Isolation & Hash Invariants"
    if PRACTICE_CYCLE.exists():
        content = PRACTICE_CYCLE.read_text(encoding="utf-8")
        m_title = re.search(r"\*\*Current Cycle:\*\*\s*`([^`]+)`", content)
        if m_title:
            cycle_name = m_title.group(1)

        row_pattern = re.compile(
            r"^\|\s*\*\*(\d+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|"
        )
        for line in content.splitlines():
            m = row_pattern.match(line.strip())
            if m:
                stages.append({
                    "stage": int(m.group(1)),
                    "focus": m.group(2).strip().strip("*` "),
                    "target": m.group(3).strip().strip("` "),
                    "command": m.group(4).strip().strip("` "),
                    "status": m.group(5).strip().strip("` ")
                })
    return {
        "cycleName": cycle_name,
        "stages": stages
    }


def get_dashboard_payload() -> Dict[str, Any]:
    """Return full unified dashboard payload for the Web UI."""
    db = load_db()
    dsa_data = get_dsa_overview()
    cycle_data = get_practice_cycle()

    # Calculate dynamic Readiness Score out of 1000
    base_score = 605
    card_bonus = len(db.get("completedCards", [])) * 15
    dsa_bonus = dsa_data["bothDone"] * 10
    readiness_score = min(1000, base_score + card_bonus + dsa_bonus)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "readinessScore": readiness_score,
        "userStats": {
            "xp": db["xp"],
            "streakDays": db["streakDays"],
            "completedCardsCount": len(db["completedCards"]),
            "totalCardsCount": len(CONCEPT_FEED_CARDS),
            "srsQueue": db["srsQueue"]
        },
        "practiceCycle": cycle_data,
        "dsa": dsa_data
    }


def get_feed_payload() -> Dict[str, Any]:
    """Return all concept feed cards enriched with user state."""
    db = load_db()
    completed = set(db.get("completedCards", []))
    bookmarked = set(db.get("bookmarkedCards", []))
    quiz_history = db.get("quizHistory", {})

    cards = []
    for c in CONCEPT_FEED_CARDS:
        card_copy = dict(c)
        card_copy["completed"] = c["id"] in completed
        card_copy["bookmarked"] = c["id"] in bookmarked
        card_copy["quizAnswered"] = quiz_history.get(c["id"])
        cards.append(card_copy)

    return {
        "cards": cards,
        "categories": ["All", "DSA Invariants", "OS Internals", "Computer Networks", "System Design", "AI & RAG"]
    }


def record_feed_interaction(card_id: str, action: str, selected_option: int = None) -> Dict[str, Any]:
    """Update user progress when completing a concept card or answering a quiz."""
    db = load_db()
    if action == "quiz" and selected_option is not None:
        card = next((c for c in CONCEPT_FEED_CARDS if c["id"] == card_id), None)
        is_correct = False
        if card:
            is_correct = (selected_option == card["quiz"]["correctIndex"])
        db["quizHistory"][card_id] = {
            "selected": selected_option,
            "isCorrect": is_correct,
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }
        if is_correct and card_id not in db["completedCards"]:
            db["completedCards"].append(card_id)
            db["xp"] += 50
    elif action == "toggle_bookmark":
        if card_id in db["bookmarkedCards"]:
            db["bookmarkedCards"].remove(card_id)
        else:
            db["bookmarkedCards"].append(card_id)
    elif action == "complete":
        if card_id not in db["completedCards"]:
            db["completedCards"].append(card_id)
            db["xp"] += 25

    save_db(db)
    return {
        "status": "ok",
        "xp": db["xp"],
        "completedCards": db["completedCards"],
        "bookmarkedCards": db["bookmarkedCards"],
        "quizHistory": db["quizHistory"]
    }
