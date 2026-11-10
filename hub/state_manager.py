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
        "labSlug": "003-group-anagrams",
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
        "visualizerId": "cs-os-leak-detector",
        "labSlug": "01-memory-and-handle-leak-detector",
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
        "labSlug": "01-endpoint-to-cloud-sync-and-jitter",
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
        "visualizerId": "ai-rag-triad-gate",
        "labSlug": "01-rag-triad-evaluator",
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
    },
    {
        "id": "card-cs-tcp-tls-backlog",
        "category": "Computer Networks",
        "title": "TCP 3-Way Handshake, TLS 1.3 & The Linux listen(5) SYN Backlog Trap",
        "readTime": "75 sec",
        "difficulty": "Staff SDET",
        "tags": ["TCP/IP", "TLS 1.3", "Linux Kernel", "HTTP/2"],
        "mentalModel": (
            "Think of a server's TCP `listen(backlog)` queue as a restaurant waiting room. If the waiting room only holds "
            "5 people (`request_queue_size = 5`) and a tour bus of 32 parallel CI workers arrives at the exact same millisecond, "
            "the bouncer (Linux kernel) slams the door in the face of 27 workers with `ConnectionResetError (TCP RST)`!"
        ),
        "mechanics": (
            "• Cold TLS 1.2 Connection: 1 RTT (TCP SYN/SYN-ACK/ACK) + 2 RTTs (TLS 1.2) + 1 RTT (HTTP) = 4 RTTs.\n"
            "• Cold TLS 1.3 Connection: Embeds key share in ClientHello -> 1 RTT TCP + 1 RTT TLS 1.3 = 2 RTTs before HTTP.\n"
            "• HTTP/2 Keep-Alive Multiplexing: Pays handshake once and multiplexes concurrent streams over a single TCP socket.\n"
            "• Linux SYN/Accept Backlog: Increasing `request_queue_size = 128` prevents burst `Errno 104` resets."
        ),
        "diagram": (
            "TLS 1.2 (Unpooled): [SYN] -> [TLS RTT 1] -> [TLS RTT 2] -> [HTTP] (4x RTT every call!)\n"
            "TLS 1.3 (HTTP/2):   [SYN] -> [TLS 1.3 1-RTT] ══► [Multiplexed Streams 1..N (1x RTT each)]"
        ),
        "gotcha": (
            "macOS silently bumps small `listen(5)` backlogs up to 128 in the kernel, so a 32-thread burst passes on a MacBook "
            "but crashes on Linux (`ubuntu-latest`) CI unless you explicitly set `request_queue_size = 128`!"
        ),
        "visualizerId": "cs-tcp-tls-handshake",
        "labSlug": "01-tcp-tls-and-proxy-inspector",
        "quiz": {
            "question": "At 50ms network RTT, how much total time do 10 sequential requests take over pooled HTTP/2 + TLS 1.3 compared to unpooled HTTP/1.1 + TLS 1.2?",
            "options": [
                "600ms (pooled TLS 1.3) vs. 2,000ms (unpooled TLS 1.2)",
                "2,000ms vs. 2,000ms (TLS version does not affect latency)",
                "50ms vs. 500ms",
                "1,500ms vs. 600ms"
            ],
            "correctIndex": 0,
            "explanation": "Pooled TLS 1.3 pays 1 TCP RTT (50ms) + 1 TLS 1.3 RTT (50ms) once (100ms), plus 10 * 50ms requests = 600ms. Unpooled TLS 1.2 pays 4 RTTs (200ms) on all 10 requests = 2,000ms."
        }
    },
    {
        "id": "card-cs-db-wal-occ",
        "category": "Database Internals",
        "title": "SQLite WAL Ring-Buffers & Optimistic Concurrency Control (CAS)",
        "readTime": "75 sec",
        "difficulty": "Senior SDET",
        "tags": ["SQLite WAL", "ACID Isolation", "OCC / CAS", "Storage"],
        "mentalModel": (
            "Instead of locking the entire filing cabinet every time someone edits a page (pessimistic lock), "
            "Optimistic Concurrency Control stamps a version number `v=1` on the page. When you save, the DB checks: "
            "'Is the page still `v=1`?' If another thread already bumped it to `v=2`, your stale write is rejected!"
        ),
        "mechanics": (
            "• Write-Ahead Logging (`PRAGMA journal_mode=WAL`): Appends sequentially to a `-wal` file so readers never block writers.\n"
            "• Bounded FIFO Ring-Buffer: Caps local offline endpoint storage at $K$ records, evicting oldest entries first.\n"
            "• Compare-And-Swap (`CAS`): `UPDATE seats SET owner=?, version=v+1 WHERE id=? AND version=v` prevents Lost Updates."
        ),
        "diagram": (
            "Thread A reads v=1 ──► CAS(expected_v=1) ──► SUCCESS (Row becomes v=2)\n"
            "Thread B reads v=1 ──► CAS(expected_v=1) ──► REJECTED (Row is already v=2 -> No Lost Update!)"
        ),
        "gotcha": (
            "Default SQLite rollback journals (`DELETE` mode) lock the entire database file during writes, causing `SQLITE_BUSY` "
            "errors in multi-threaded endpoint agents. Always enable `WAL` mode for concurrent local read/write!"
        ),
        "visualizerId": "arch-endpoint-cloud-sync",
        "labSlug": "01-wal-and-isolation-anomalies",
        "quiz": {
            "question": "Which database anomaly occurs when two transactions read the same row version simultaneously and the second commit silently overwrites the first commit?",
            "options": [
                "Phantom Read",
                "Dirty Read",
                "Lost Update",
                "Index B-Tree Split"
            ],
            "correctIndex": 2,
            "explanation": "A Lost Update happens when two concurrent transactions read the same initial state and both write back updates without checking if the underlying row version changed in between."
        }
    },
    {
        "id": "card-sd-consistent-hashing",
        "category": "System Design",
        "title": "Consistent Hashing Rings with Virtual Nodes (vnodes) vs. Modulo Sharding",
        "readTime": "75 sec",
        "difficulty": "Staff SDET",
        "tags": ["Consistent Hashing", "Sharding", "Distributed Grids"],
        "mentalModel": (
            "If you shard keys across 4 servers using `hash(key) % 4` and 1 server crashes (`hash(key) % 3`), "
            "75% of all keys suddenly point to the wrong server! Consistent Hashing arranges servers on a 360-degree "
            "clock ring so when 1 server leaves, only its ~25% slice is handed to its clockwise neighbor."
        ),
        "mechanics": (
            "• Hash Ring $[0, 2^{32}-1]$: Both nodes and keys are hashed onto a sorted circular ring (`TreeMap` in Java / `bisect` in Python).\n"
            "• Virtual Nodes (`vnodes`): Each physical server gets 64+ virtual positions on the ring (`node1#v0..v63`) to eliminate hot-spots.\n"
            "• Node Removal Invariant: Removing 1 of $N$ nodes only remaps $\\approx 1/N$ of keys; keys on healthy nodes never move!"
        ),
        "diagram": (
            "Ring [0 .. 2^32-1]:  ──► (node1#v1) ──► [Key A] ──► (node4#v2 [CRASHED]) ──► (node2#v0 [Takes Key A!])"
        ),
        "gotcha": (
            "Consistent hashing with only 1 position per physical node creates severe load skew (one node might own 60% of the circle). "
            "Always assign at least 64–256 Virtual Nodes (`vnodes`) per physical server!"
        ),
        "visualizerId": "arch-concurrency-isolation",
        "labSlug": "02-consistent-hashing-and-grid-sharding",
        "quiz": {
            "question": "In a 4-node Consistent Hashing ring, approximately what percentage of keys are remapped when 1 node crashes (compared to ~75% with `hash(k) % N`)?",
            "options": [
                "0% of keys",
                "~25% (1/N) of keys",
                "~50% of keys",
                "100% of keys"
            ],
            "correctIndex": 1,
            "explanation": "Only the keys that belonged to the crashed node (~1/N = 25%) move clockwise to the next healthy virtual node on the ring."
        }
    },
    {
        "id": "card-ai-self-healing-ast",
        "category": "AI & RAG",
        "title": "Self-Healing UI Locators: Multi-Signal DOM Scoring & Destructive Action Guards",
        "readTime": "75 sec",
        "difficulty": "Staff SDET",
        "tags": ["Self-Healing", "AST Patching", "Playwright", "AI QE"],
        "mentalModel": (
            "When `#btn-book` breaks because a developer renamed it to `#confirm-booking-cta`, a naive fuzzy healer "
            "might click `#btn-cancel-booking` because both buttons share the words 'Flight Booking'! A production healer "
            "combines multi-signal DOM weights with a strict Destructive Action Guard."
        ),
        "mechanics": (
            "• Multi-Signal Fingerprint: Score `role+tag` (0.25) + `aria-label` Jaccard (0.35) + `text` Jaccard (0.25) + `parent_form` (0.15).\n"
            "• Destructive Polarity Guard: Reject any candidate containing `cancel`, `delete`, `remove`, or `revoke` if the baseline was non-destructive.\n"
            "• Confidence Gate ($\\ge 0.75$): Auto-heal in memory and open a PR patching the test's AST with `page.getByRole()`."
        ),
        "diagram": (
            "Broken `#btn-book` ──► Score Candidates ──► Reject `Cancel` (Destructive Guard) ──► Heal `Confirm` (0.91 >= 0.75)"
        ),
        "gotcha": (
            "Never silently auto-heal broken locators forever in CI without emitting an AST patch or alert—otherwise "
            "tests slowly drift from reality and mask real accessibility regressions!"
        ),
        "visualizerId": "arch-playwright-vs-selenium",
        "labSlug": "02-self-healing-locators-and-ast",
        "quiz": {
            "question": "What is the biggest danger of using a naive string-similarity self-healing locator without a destructive-keyword guard?",
            "options": [
                "It increases CSS bundle size",
                "It can auto-heal 'Confirm Flight Booking' onto 'Cancel Flight Booking' and mask a P0 bug",
                "It disables WebSocket compression",
                "It prevents Java compilation"
            ],
            "correctIndex": 1,
            "explanation": "'Confirm Flight Booking' and 'Cancel Flight Booking' share 2 out of 3 words. Without a polarity/destructive action guard, fuzzy matching can click 'Cancel' or 'Delete'!"
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


DSA_CHAPTER_CATALOG: Dict[str, Dict[str, Any]] = {
    "Arrays & Hashing": {
        "number": "01",
        "folder": "01-arrays-and-hashing",
        "mentalModelTitle": "Mental Model: O(1) Instant Lookup via Canonical Signatures vs O(N) Linear Scan",
        "mentalModelSummary": "Pre-index complements or 26-letter frequency signatures in a Hash Table so inner search loops collapse from O(N) to O(1).",
        "tiles": [{"label": "E", "sub": "a·e·t"}, {"label": "A", "sub": "a·e·t"}, {"label": "T", "sub": "a·e·t"}],
        "diagramFormula": "key = tuple(count[26])",
        "diagramCaption": "O(1) hash bucket lookup",
    },
    "Two Pointers": {
        "number": "02",
        "folder": "02-two-pointers",
        "mentalModelTitle": "Mental Model: Converging L & R Pointers Collapse O(N²) Pair Scans to O(N)",
        "mentalModelSummary": "Exploit sorted order or monotonic container heights to discard an entire row/column of suboptimal pairs on every pointer step.",
        "tiles": [{"label": "L→", "sub": "idx 0"}, {"label": "⇄", "sub": "O(N)"}, {"label": "←R", "sub": "idx N-1"}],
        "diagramFormula": "while L < R: move min side",
        "diagramCaption": "Converging boundary scan",
    },
    "Sliding Window": {
        "number": "03",
        "folder": "03-sliding-window",
        "mentalModelTitle": "Mental Model: Elastic Window [L..R] Maintains Substring Invariants in O(N)",
        "mentalModelSummary": "Expand right pointer R to ingest elements and contract left pointer L only when the window constraint is violated.",
        "tiles": [{"label": "[L", "sub": "shrink"}, {"label": "WIN", "sub": "valid"}, {"label": "R]", "sub": "expand"}],
        "diagramFormula": "window_len = R - L + 1",
        "diagramCaption": "Amortized 2N pointer moves",
    },
    "Stack & Queue": {
        "number": "04",
        "folder": "04-stack-and-queue",
        "mentalModelTitle": "Mental Model: Monotonic LIFO Stack Resolves Next-Greater Boundaries in O(N)",
        "mentalModelSummary": "Hold unresolved indices in a monotonic stack; the first element that breaks monotonicity resolves all smaller/larger items on top.",
        "tiles": [{"label": "PUSH", "sub": "idx i"}, {"label": "TOP", "sub": "mono"}, {"label": "POP", "sub": "resolve"}],
        "diagramFormula": "while stack and cur > top: pop()",
        "diagramCaption": "Monotonic boundary resolution",
    },
    "Binary Search": {
        "number": "05",
        "folder": "05-binary-search",
        "mentalModelTitle": "Mental Model: Monotonic T/F Predicate Halves the Search Space in O(log N)",
        "mentalModelSummary": "Binary search works on any monotonic boolean condition (sorted rotated halves or answer-space feasibility).",
        "tiles": [{"label": "LO", "sub": "False"}, {"label": "MID", "sub": "check()"}, {"label": "HI", "sub": "True"}],
        "diagramFormula": "mid = lo + (hi - lo) // 2",
        "diagramCaption": "Logarithmic boundary bisection",
    },
    "Linked List": {
        "number": "06",
        "folder": "06-linked-list",
        "mentalModelTitle": "Mental Model: Fast/Slow Tortoise-Hare Pointers & Dummy Sentinel Nodes",
        "mentalModelSummary": "Use a dummy head to eliminate null-head edge cases and 2x/1x pointers to locate midpoints or cycles in O(1) space.",
        "tiles": [{"label": "PREV", "sub": "node"}, {"label": "CURR", "sub": "flip"}, {"label": "NEXT", "sub": "save"}],
        "diagramFormula": "nxt = cur.next; cur.next = prev",
        "diagramCaption": "In-place pointer rewiring",
    },
    "Trees & BST": {
        "number": "07",
        "folder": "07-trees-and-bst",
        "mentalModelTitle": "Mental Model: Bottom-Up Post-Order Heights & Top-Down BST Range Bounds",
        "mentalModelSummary": "Pass range invariants (min_val, max_val) down the tree in Pre-Order, and aggregate subtree heights/diameters up in Post-Order.",
        "tiles": [{"label": "LEFT", "sub": "< root"}, {"label": "ROOT", "sub": "(lo,hi)"}, {"label": "RIGHT", "sub": "> root"}],
        "diagramFormula": "1 + max(dfs(L), dfs(R))",
        "diagramCaption": "Recursive subtree decomposition",
    },
    "Heaps & Priority Queue": {
        "number": "08",
        "folder": "08-heaps-priority-queue",
        "mentalModelTitle": "Mental Model: Bounded K-Element Min-Heap Tracks Stream Leaders in O(N log K)",
        "mentalModelSummary": "Maintain a Min-Heap of size K so the K-th largest element always sits at heap[0] in O(1) peek time.",
        "tiles": [{"label": "MIN", "sub": "heap[0]"}, {"label": "LOG K", "sub": "sift"}, {"label": "TOP K", "sub": "stream"}],
        "diagramFormula": "if len(heap) > k: heappop(heap)",
        "diagramCaption": "Bounded priority frontier",
    },
    "Backtracking": {
        "number": "09",
        "folder": "09-backtracking",
        "mentalModelTitle": "Mental Model: Choose → Explore → Unchoose State-Space Decision Tree",
        "mentalModelSummary": "Mutate shared path state in-place before recursing and undo the mutation immediately upon return.",
        "tiles": [{"label": "+X", "sub": "choose"}, {"label": "DFS", "sub": "explore"}, {"label": "-X", "sub": "unchoose"}],
        "diagramFormula": "path.append(x); dfs(); path.pop()",
        "diagramCaption": "State tree pruning",
    },
    "Graphs": {
        "number": "10",
        "folder": "10-graphs",
        "mentalModelTitle": "Mental Model: Multi-Source BFS Wavefronts & Kahn's Topological Indegrees",
        "mentalModelSummary": "Use BFS queues for unweighted shortest paths and 3-color DFS / Indegree queues for dependency cycle detection.",
        "tiles": [{"label": "U", "sub": "indeg 0"}, {"label": "──►", "sub": "edge"}, {"label": "V", "sub": "queue"}],
        "diagramFormula": "indegree[v] -= 1; if 0: push(v)",
        "diagramCaption": "Topological & wavefront traversal",
    },
    "1D Dynamic Programming": {
        "number": "11",
        "folder": "11-dynamic-programming",
        "mentalModelTitle": "Mental Model: Optimal Substructure Folded into Rolling O(1) State Registers",
        "mentalModelSummary": "Express state i in terms of i-1 and i-2 so exponential recursion collapses into a single linear scan.",
        "tiles": [{"label": "prev2", "sub": "dp[i-2]"}, {"label": "prev1", "sub": "dp[i-1]"}, {"label": "curr", "sub": "dp[i]"}],
        "diagramFormula": "dp[i] = max(dp[i-1], dp[i-2] + val)",
        "diagramCaption": "Rolling state recurrence",
    },
    "2D Dynamic Programming": {
        "number": "12",
        "folder": "11-dynamic-programming",
        "mentalModelTitle": "Mental Model: 2D Grid & Prefix Alignment Transitions (i, j)",
        "mentalModelSummary": "Transition each cell (i, j) from its top (i-1, j), left (i, j-1), and diagonal (i-1, j-1) subproblems.",
        "tiles": [{"label": "TOP", "sub": "(r-1,c)"}, {"label": "DIAG", "sub": "(r-1,c-1)"}, {"label": "CELL", "sub": "(r,c)"}],
        "diagramFormula": "dp[i][j] = 1 + dp[i-1][j-1]",
        "diagramCaption": "2D state lattice transition",
    },
    "Greedy & Intervals": {
        "number": "13",
        "folder": "12-greedy-and-intervals",
        "mentalModelTitle": "Mental Model: Sort Intervals by Start/End to Resolve Overlaps Locally",
        "mentalModelSummary": "Sorting intervals by start time guarantees that overlapping intervals appear contiguously.",
        "tiles": [{"label": "[S1,E1]", "sub": "prev"}, {"label": "∪", "sub": "S2 ≤ E1"}, {"label": "[S1,E2]", "sub": "merged"}],
        "diagramFormula": "if cur.start <= prev.end: merge()",
        "diagramCaption": "Greedy sweep-line invariant",
    },
    "Design & Concurrency": {
        "number": "14",
        "folder": "13-design-and-concurrency",
        "mentalModelTitle": "Mental Model: O(1) HashMap + Doubly-Linked Node & Condition-Variable Locks",
        "mentalModelSummary": "Combine HashMaps with doubly-linked lists for O(1) eviction and guard bounded queues with Condition wait/notify.",
        "tiles": [{"label": "LOCK", "sub": "mutex"}, {"label": "WAIT", "sub": "not_full"}, {"label": "NOTIFY", "sub": "not_empty"}],
        "diagramFormula": "while len(q) == cap: cond.wait()",
        "diagramCaption": "Thread-safe data structure invariants",
    },
    "Bit Manipulation": {
        "number": "15",
        "folder": "14-bit-manipulation",
        "mentalModelTitle": "Mental Model: XOR Self-Cancellation (x ^ x = 0) & Kernighan's Bit Clear",
        "mentalModelSummary": "Use bitwise XOR to cancel paired duplicates and n & (n - 1) to strip the lowest set bit in O(1) space.",
        "tiles": [{"label": "X ^ X", "sub": "== 0"}, {"label": "N & N-1", "sub": "drop 1"}, {"label": "O(1)", "sub": "registers"}],
        "diagramFormula": "n = n & (n - 1)",
        "diagramCaption": "Bitwise register arithmetic",
    },
}


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
            slug = re.sub(r"^\d+-", "", p.name.lower())
            mapping[slug] = rel
            mapping[p.name.lower()] = rel
    return mapping


def get_dsa_overview() -> Dict[str, Any]:
    """Parse dsa/MASTER_SHEET.md and enrich with local runnable status and 15-Chapter Roadmap metadata."""
    local_folders = discover_local_dsa_folders()
    problems = []

    problem_diagrams = {
        "two-sum": ("need = target - x", "Pair complement sum"),
        "contains-duplicate": ("x in seen_set", "O(1) duplicate check"),
        "valid-anagram": ("[A][E] ⇄ [E][A]", "26-slot balance scale"),
        "group-anagrams": ("key = tuple(count[26])", "Canonical frequency bucket"),
        "top-k-frequent-elements": ("buckets[freq].append(x)", "Bounded frequency buckets"),
        "product-of-array-except-self": ("prefix[i] * suffix[i]", "Two-pass prefix/suffix"),
        "encode-and-decode-strings": ("len(s) + '#' + s", "Length-prefixed framing"),
        "longest-consecutive-sequence": ("(x - 1) not in set", "Sequence head detection"),
        "subarray-sum-equals-k": ("prefix_sum - k in map", "Prefix sum complement"),
        "first-missing-positive": ("swap nums[i] to idx x-1", "Cyclic index placement"),
    }

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
                # Also match shortened folder slugs like lowest-common-ancestor-of-bst
                local_path = local_folders.get(slug)
                if not local_path:
                    for k, v in local_folders.items():
                        if slug.startswith(k) or k.startswith(slug[:18]):
                            local_path = v
                            break
                folder_slug = Path(local_path).name if local_path else f"{prob_id:03d}-{slug}"

                visualizer_map = {
                    "two-sum": "dsa-two-sum",
                    "valid-anagram": "dsa-valid-anagram",
                    "group-anagrams": "dsa-group-anagrams",
                }
                ch_meta = DSA_CHAPTER_CATALOG.get(pattern, DSA_CHAPTER_CATALOG["Arrays & Hashing"])
                diag_formula, diag_caption = problem_diagrams.get(
                    slug, (ch_meta["diagramFormula"], ch_meta["diagramCaption"])
                )

                problems.append({
                    "id": prob_id,
                    "title": title,
                    "slug": slug,
                    "folderSlug": folder_slug,
                    "localPath": local_path,
                    "hasLocalFiles": bool(local_path),
                    "visualizerId": visualizer_map.get(slug, "dsa-group-anagrams"),
                    "url": url,
                    "pattern": pattern,
                    "chapterNumber": ch_meta["number"],
                    "chapterFolder": ch_meta["folder"],
                    "diagramFormula": diag_formula,
                    "diagramCaption": diag_caption,
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
    chapters_list: List[Dict[str, Any]] = []
    for pat_name, ch_meta in DSA_CHAPTER_CATALOG.items():
        ch_probs = [p for p in problems if p["pattern"] == pat_name]
        ch_done = sum(1 for p in ch_probs if p["bothDone"])
        ch_scaf = sum(1 for p in ch_probs if p["hasLocalFiles"])
        by_pattern[pat_name] = {
            "total": len(ch_probs),
            "done": ch_done,
            "scaffolded": ch_scaf,
        }
        chapters_list.append({
            "chapterId": f"ch-{ch_meta['number']}",
            "number": ch_meta["number"],
            "pattern": pat_name,
            "title": f"Ch {ch_meta['number']}: {pat_name}",
            "folder": ch_meta["folder"],
            "mentalModelTitle": ch_meta["mentalModelTitle"],
            "mentalModelSummary": ch_meta["mentalModelSummary"],
            "tiles": ch_meta["tiles"],
            "total": len(ch_probs),
            "done": ch_done,
            "scaffolded": ch_scaf,
            "problems": ch_probs,
        })

    # Dynamic recommendation: prefer scaffolded-but-unmastered problem, else first unmastered
    next_unmastered = next(
        (p for p in problems if p["hasLocalFiles"] and not p["bothDone"]),
        next((p for p in problems if not p["bothDone"]), problems[0] if problems else None)
    )

    return {
        "total": len(problems),
        "bothDone": both_done,
        "localScaffolded": local_scaffolded,
        "completionPct": round((both_done / total) * 100, 1),
        "byPattern": by_pattern,
        "chapters": chapters_list,
        "recommendedProblem": next_unmastered,
        "problems": problems
    }


def update_dsa_mastery(
    prob_id: int,
    java_done: bool = None,
    py_done: bool = None,
    score: str = None,
    status: str = None
) -> bool:
    """Update a problem row in dsa/MASTER_SHEET.md when test suites pass."""
    if not MASTER_SHEET.exists():
        return False
    content = MASTER_SHEET.read_text(encoding="utf-8")
    row_pattern = re.compile(rf"^\|\s*{prob_id}\s*\|")
    updated = False
    new_lines = []
    for line in content.splitlines():
        if row_pattern.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 8:
                if java_done is not None:
                    cells[4] = "[x]" if java_done else "[ ]"
                if py_done is not None:
                    cells[5] = "[x]" if py_done else "[ ]"
                if score is not None:
                    cells[6] = score
                if status is not None:
                    cells[7] = status
                line = f"| {' | '.join(cells)} |"
                updated = True
        new_lines.append(line)
    if updated:
        MASTER_SHEET.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return updated


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


def get_architecture_and_cs_labs() -> List[Dict[str, Any]]:
    """Discover all hands-on dual-language labs across core-cs/, system-design/, ai-engineering/, and frameworks/."""
    viz_lookup = {
        "01-memory-and-handle-leak-detector": "cs-os-leak-detector",
        "01-tcp-tls-and-proxy-inspector": "cs-tcp-tls-handshake",
        "01-wal-and-isolation-anomalies": "arch-endpoint-cloud-sync",
        "01-endpoint-to-cloud-sync-and-jitter": "arch-endpoint-cloud-sync",
        "02-consistent-hashing-and-grid-sharding": "arch-concurrency-isolation",
        "01-rag-triad-evaluator": "ai-rag-triad-gate",
        "02-self-healing-locators-and-ast": "arch-playwright-vs-selenium",
        "01-distributed-concurrency-isolation": "arch-concurrency-isolation",
    }

    pillar_roots = [
        ("Core CS", REPO_ROOT / "core-cs"),
        ("System Design", REPO_ROOT / "system-design"),
        ("AI Engineering", REPO_ROOT / "ai-engineering"),
        ("SDET Frameworks", REPO_ROOT / "frameworks" / "design-challenges"),
        ("SDET System Design", REPO_ROOT / "frameworks" / "sdet-system-design"),
    ]

    labs = []
    for pillar_label, root_dir in pillar_roots:
        if not root_dir.exists():
            continue
        for r, _, files in os.walk(root_dir):
            if "/." in r or "__pycache__" in r:
                continue
            has_java = "Solution.java" in files
            has_py = "solution.py" in files
            if has_java or has_py:
                p = Path(r)
                folder_slug = p.name
                labs.append({
                    "pillar": pillar_label,
                    "folderSlug": folder_slug,
                    "title": folder_slug.replace("-", " ").title(),
                    "localPath": str(p.relative_to(REPO_ROOT)),
                    "hasJava": has_java,
                    "hasPy": has_py,
                    "bothDone": has_java and has_py,
                    "visualizerId": viz_lookup.get(folder_slug),
                })

    labs.sort(key=lambda x: (x["pillar"], x["folderSlug"]))
    return labs


def get_dashboard_payload() -> Dict[str, Any]:
    """Return full unified dashboard payload for the Web UI."""
    db = load_db()
    dsa_data = get_dsa_overview()
    cycle_data = get_practice_cycle()
    arch_labs = get_architecture_and_cs_labs()

    pillars = [
        {
            "id": "dsa",
            "title": "1. DSA Patterns",
            "completed": dsa_data["bothDone"],
            "total": dsa_data["total"],
            "description": "128 Curated MAANG Problems (Java 17 & Python 3)"
        },
        {
            "id": "core-cs",
            "title": "2. Core CS Internals",
            "completed": sum(1 for l in arch_labs if l["pillar"] == "Core CS" and l["bothDone"]),
            "total": sum(1 for l in arch_labs if l["pillar"] == "Core CS"),
            "description": "Operating Systems, Computer Networks & Database WAL/Isolation"
        },
        {
            "id": "system-design",
            "title": "3. System Design",
            "completed": sum(1 for l in arch_labs if l["pillar"] == "System Design" and l["bothDone"]),
            "total": sum(1 for l in arch_labs if l["pillar"] == "System Design"),
            "description": "Endpoint-to-Cloud Sync, Full Jitter & Consistent Hashing Rings"
        },
        {
            "id": "ai-engineering",
            "title": "4. AI Engineering & QE",
            "completed": sum(1 for l in arch_labs if l["pillar"] == "AI Engineering" and l["bothDone"]),
            "total": sum(1 for l in arch_labs if l["pillar"] == "AI Engineering"),
            "description": "RAG Triad Evaluator, Negation Traps & Self-Healing AST Locators"
        },
        {
            "id": "frameworks",
            "title": "5. SDET Frameworks & AUT",
            "completed": sum(1 for l in arch_labs if "SDET" in l["pillar"] and l["bothDone"]),
            "total": sum(1 for l in arch_labs if "SDET" in l["pillar"]),
            "description": "AeroCart Microservice AUT, 32-Worker Concurrency & Design Katas"
        },
        {
            "id": "mock-interviews",
            "title": "6. Bar-Raiser Mock Sims",
            "completed": 1,
            "total": 5,
            "description": "Staff/Lead SDET Architectural Evaluations & Mastery Guides"
        }
    ]

    # Calculate dynamic Readiness Score out of 1000
    base_score = 605
    phase2_pillar_bonus = len(arch_labs) * 15  # +195 pts for Phase 2 runnable Core CS, System Design & AI labs
    card_bonus = len(db.get("completedCards", [])) * 10
    dsa_bonus = dsa_data["bothDone"] * 10
    readiness_score = min(1000, base_score + phase2_pillar_bonus + card_bonus + dsa_bonus)

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
        "pillars": pillars,
        "architectureLabs": arch_labs,
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
        "categories": [
            "All",
            "DSA Invariants",
            "OS Internals",
            "Computer Networks",
            "Database Internals",
            "System Design",
            "AI & RAG"
        ]
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
