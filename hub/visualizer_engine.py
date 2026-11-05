#!/usr/bin/env python3
"""
Universal Step-by-Step Visualizer Engine for the Antigravity Learning Hub.
Generates deterministic execution traces for:
1. DSA Algorithms (with custom input support):
   - Group Anagrams (003-group-anagrams)
   - Two Sum (001-two-sum)
   - Valid Anagram (002-valid-anagram)
2. Architecture & Core CS Simulators:
   - Playwright CDP WebSocket vs. Selenium W3C HTTP Protocol
   - Distributed Concurrency: 32 Workers Shared Collision vs. Dynamic Tenant UUIDs
   - Endpoint-to-Cloud Continuous Sync & Backpressure (SASE / Netskope Pattern)
"""

from typing import Dict, Any, List


def list_visualizers() -> List[Dict[str, Any]]:
    """Return metadata for all available interactive visualizers."""
    return [
        {
            "id": "dsa-group-anagrams",
            "type": "dsa",
            "title": "DSA #003: Group Anagrams (26-Slot Frequency Fingerprint)",
            "category": "Arrays & Hashing",
            "complexity": {"time": "O(M · N)", "space": "O(M · N)"},
            "defaultInput": {"strs": ["eat", "tea", "tan", "ate", "nat", "bat"]},
            "description": "Step through how each string is converted into a 26-letter frequency key in O(N) time and bucketed into a HashMap without sorting."
        },
        {
            "id": "dsa-two-sum",
            "type": "dsa",
            "title": "DSA #001: Two Sum (Single-Pass HashMap Complement)",
            "category": "Arrays & Hashing",
            "complexity": {"time": "O(N)", "space": "O(N)"},
            "defaultInput": {"nums": [2, 11, 7, 15], "target": 9},
            "description": "Watch the single-pass pointer compute `complement = target - nums[i]` and query the seen HashMap in O(1) time."
        },
        {
            "id": "dsa-valid-anagram",
            "type": "dsa",
            "title": "DSA #002: Valid Anagram (Simultaneous +/- Frequency Balance)",
            "category": "Arrays & Hashing",
            "complexity": {"time": "O(N)", "space": "O(1) [26 slots]"},
            "defaultInput": {"s": "anagram", "t": "nagaram"},
            "description": "Watch `zip(s, t)` increment counts for `s[i]` and decrement counts for `t[i]` simultaneously across a fixed 26-slot array."
        },
        {
            "id": "arch-playwright-vs-selenium",
            "type": "architecture",
            "title": "Architecture: Playwright CDP WebSocket vs. Selenium W3C HTTP",
            "category": "Automation Internals & Networks",
            "complexity": {"time": "~4ms vs ~180ms", "space": "20MB Context vs 500MB Process"},
            "defaultInput": {"action": "Login Flow (fill user, fill pass, click submit)"},
            "description": "Interactive packet-level comparison of Selenium's stateless HTTP roundtrips vs. Playwright's persistent full-duplex WebSocket & BrowserContext model."
        },
        {
            "id": "arch-concurrency-isolation",
            "type": "architecture",
            "title": "Architecture: 32 Parallel CI Workers — Collision vs. Dynamic Tenant UUIDs",
            "category": "Distributed System Design",
            "complexity": {"time": "32 Threads Concurrent", "space": "Tenant-Scoped Partitions"},
            "defaultInput": {"mode": "comparison"},
            "description": "Watch why 31/32 parallel workers crash with HTTP 409 on shared staging data, and how `X-Test-Tenant-ID` isolates every worker."
        },
        {
            "id": "arch-endpoint-cloud-sync",
            "type": "architecture",
            "title": "Architecture: Endpoint-to-Cloud Sync, Ring Buffers & Thundering Herd Jitter",
            "category": "OS & Cloud Scale (SASE/Endpoint)",
            "complexity": {"time": "Exponential Backoff + Jitter", "space": "Bounded SQLite WAL Queue"},
            "defaultInput": {"endpoints": 10000},
            "description": "Step through how a local macOS/Windows security agent buffers events during a network drop and prevents a backend DDoS upon reconnection."
        }
    ]


def trace_group_anagrams(custom_input: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate step-by-step execution trace for Group Anagrams."""
    strs = (custom_input or {}).get("strs", ["eat", "tea", "tan", "ate", "nat", "bat"])
    if isinstance(strs, str):
        strs = [w.strip() for w in strs.split(",") if w.strip()]

    steps = []
    buckets: Dict[str, List[str]] = {}

    steps.append({
        "stepIndex": 0,
        "title": "Initialize Empty Hash Map (`anagram_map`)",
        "narration": f"We receive {len(strs)} strings: {strs}. We initialize `anagram_map = defaultdict(list)` to map each 26-letter frequency fingerprint to its list of anagrams.",
        "codeLine": "anagram_map = defaultdict(list)",
        "currentWordIndex": -1,
        "currentWord": None,
        "activeLetters": {},
        "fingerprintKey": None,
        "buckets": {},
        "words": strs
    })

    for idx, word in enumerate(strs):
        counts = [0] * 26
        active_letters = {}
        for ch in word.lower():
            if "a" <= ch <= "z":
                pos = ord(ch) - ord("a")
                counts[pos] += 1
                active_letters[ch] = counts[pos]

        # Compact readable key for UI display + full 26-slot key
        compact_parts = [f"{chr(ord('a') + i)}:{counts[i]}" for i in range(26) if counts[i] > 0]
        compact_key = "{" + ", ".join(compact_parts) + "}" if compact_parts else "{empty}"
        raw_key = "#".join(str(c) for c in counts)

        # Step A: Compute frequency array
        steps.append({
            "stepIndex": len(steps),
            "title": f"Word [{idx}] = \"{word}\" → Count 26 Character Frequencies",
            "narration": (
                f"Iterate over each character in \"{word}\". Increment `count[ord(c) - ord('a')]`. "
                f"Non-zero slots: {compact_key}. Converting `tuple(count)` (Python) or `\"#{raw_key[:15]}...\"` (Java) gives an O(1) hashable key!"
            ),
            "codeLine": "for char in s: count[ord(char) - ord('a')] += 1",
            "currentWordIndex": idx,
            "currentWord": word,
            "activeLetters": dict(active_letters),
            "fingerprintKey": compact_key,
            "buckets": {k: list(v) for k, v in buckets.items()},
            "words": strs
        })

        # Step B: Insert into bucket
        buckets.setdefault(compact_key, []).append(word)
        steps.append({
            "stepIndex": len(steps),
            "title": f"Bucket \"{word}\" under Key `{compact_key}`",
            "narration": (
                f"Append \"{word}\" to `anagram_map[{compact_key}]`. "
                f"Current group for this fingerprint now has {len(buckets[compact_key])} word(s): {buckets[compact_key]}."
            ),
            "codeLine": "anagram_map[tuple(count)].append(s)",
            "currentWordIndex": idx,
            "currentWord": word,
            "activeLetters": dict(active_letters),
            "fingerprintKey": compact_key,
            "highlightedBucket": compact_key,
            "buckets": {k: list(v) for k, v in buckets.items()},
            "words": strs
        })

    result_groups = list(buckets.values())
    steps.append({
        "stepIndex": len(steps),
        "title": f"Return Grouped Anagrams ({len(result_groups)} Groups)",
        "narration": f"All {len(strs)} strings processed in linear O(M · N) time! Return `list(anagram_map.values())` = {result_groups}.",
        "codeLine": "return list(anagram_map.values())",
        "currentWordIndex": len(strs),
        "currentWord": None,
        "activeLetters": {},
        "fingerprintKey": "COMPLETE",
        "buckets": {k: list(v) for k, v in buckets.items()},
        "words": strs,
        "finalResult": result_groups
    })

    return {
        "visualizerId": "dsa-group-anagrams",
        "type": "dsa-group-anagrams",
        "title": "Group Anagrams — Step-by-Step Execution Trace",
        "steps": steps
    }


def trace_two_sum(custom_input: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate step-by-step execution trace for Two Sum."""
    inp = custom_input or {}
    nums = inp.get("nums", [2, 11, 7, 15])
    if isinstance(nums, str):
        nums = [int(x.strip()) for x in nums.split(",") if x.strip()]
    target = int(inp.get("target", 9))

    steps = []
    seen: Dict[int, int] = {}

    steps.append({
        "stepIndex": 0,
        "title": f"Initialize `seen = {{}}` (Target = {target})",
        "narration": f"We scan `nums = {nums}` once. For each `nums[i]`, we compute `complement = {target} - nums[i]` and check if `complement` is already in `seen`.",
        "codeLine": "seen = {}  # value -> index",
        "nums": nums,
        "target": target,
        "currentIndex": -1,
        "complement": None,
        "seen": {},
        "matchedIndices": []
    })

    found = False
    for i, num in enumerate(nums):
        comp = target - num
        if comp in seen:
            match_idx = seen[comp]
            steps.append({
                "stepIndex": len(steps),
                "title": f"Index i={i} (`nums[{i}] = {num}`) → Complement `{comp}` FOUND at Index {match_idx}!",
                "narration": (
                    f"Calculate `complement = {target} - {num} = {comp}`. "
                    f"Lookup `{comp}` in `seen` → Hit! `seen[{comp}] == {match_idx}`. "
                    f"Return `[{match_idx}, {i}]` immediately in O(N) time!"
                ),
                "codeLine": "if complement in seen: return [seen[complement], i]",
                "nums": nums,
                "target": target,
                "currentIndex": i,
                "complement": comp,
                "seen": dict(seen),
                "matchedIndices": [match_idx, i]
            })
            found = True
            break
        else:
            seen[num] = i
            steps.append({
                "stepIndex": len(steps),
                "title": f"Index i={i} (`nums[{i}] = {num}`) → Store `seen[{num}] = {i}`",
                "narration": (
                    f"Calculate `complement = {target} - {num} = {comp}`. "
                    f"`{comp}` is not in `seen` yet. Record `seen[{num}] = {i}` and advance pointer."
                ),
                "codeLine": "seen[num] = i",
                "nums": nums,
                "target": target,
                "currentIndex": i,
                "complement": comp,
                "seen": dict(seen),
                "matchedIndices": []
            })

    if not found:
        steps.append({
            "stepIndex": len(steps),
            "title": "Scan Complete — No Pair Found",
            "narration": "Reached end of array without finding two numbers summing to target. Return `[]`.",
            "codeLine": "return []",
            "nums": nums,
            "target": target,
            "currentIndex": len(nums),
            "complement": None,
            "seen": dict(seen),
            "matchedIndices": []
        })

    return {
        "visualizerId": "dsa-two-sum",
        "type": "dsa-two-sum",
        "title": "Two Sum — Single-Pass HashMap Trace",
        "steps": steps
    }


def trace_valid_anagram(custom_input: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate step-by-step execution trace for Valid Anagram."""
    inp = custom_input or {}
    s = str(inp.get("s", "anagram")).strip().lower()
    t = str(inp.get("t", "nagaram")).strip().lower()

    steps = []
    counts: Dict[str, int] = {}

    if len(s) != len(t):
        steps.append({
            "stepIndex": 0,
            "title": f"Length Mismatch (`len(s)={len(s)} != len(t)={len(t)}`) → Return False",
            "narration": "Strings of different lengths can never be anagrams. Fail fast in O(1) time!",
            "codeLine": "if len(s) != len(t): return False",
            "s": s,
            "t": t,
            "pointer": -1,
            "counts": {},
            "isAnagram": False
        })
        return {"visualizerId": "dsa-valid-anagram", "type": "dsa-valid-anagram", "title": "Valid Anagram Trace", "steps": steps}

    steps.append({
        "stepIndex": 0,
        "title": "Initialize 26-Slot Frequency Array `count = [0] * 26`",
        "narration": f"Both strings have length {len(s)}. We iterate with `zip(s, t)`, adding +1 for `s[i]` and -1 for `t[i]`.",
        "codeLine": "count = [0] * 26",
        "s": s,
        "t": t,
        "pointer": -1,
        "counts": {},
        "isAnagram": None
    })

    for i in range(len(s)):
        cs, ct = s[i], t[i]
        counts[cs] = counts.get(cs, 0) + 1
        counts[ct] = counts.get(ct, 0) - 1
        steps.append({
            "stepIndex": len(steps),
            "title": f"Step {i+1}: `s[{i}]='{cs}'` (+1), `t[{i}]='{ct}'` (-1)",
            "narration": (
                f"At index {i}: increment bucket `'{cs}'` and decrement bucket `'{ct}'`. "
                f"If `s` and `t` are anagrams, every +1 will eventually be canceled out by a -1."
            ),
            "codeLine": "count[ord(char_s) - ord('a')] += 1; count[ord(char_t) - ord('a')] -= 1",
            "s": s,
            "t": t,
            "pointer": i,
            "counts": dict(counts),
            "isAnagram": None
        })

    is_valid = all(v == 0 for v in counts.values())
    steps.append({
        "stepIndex": len(steps),
        "title": f"Final Verification: All Buckets Zero? → `{is_valid}`",
        "narration": (
            "All 26 frequency buckets returned to exactly 0! The strings are valid anagrams."
            if is_valid else
            f"Non-zero buckets remain: {[k for k, v in counts.items() if v != 0]}. Not an anagram!"
        ),
        "codeLine": "return all(c == 0 for c in count)",
        "s": s,
        "t": t,
        "pointer": len(s),
        "counts": dict(counts),
        "isAnagram": is_valid
    })

    return {
        "visualizerId": "dsa-valid-anagram",
        "type": "dsa-valid-anagram",
        "title": "Valid Anagram — Simultaneous Frequency Balance Trace",
        "steps": steps
    }


def trace_architecture(viz_id: str) -> Dict[str, Any]:
    """Generate step-by-step interactive architecture simulations."""
    if viz_id == "arch-playwright-vs-selenium":
        steps = [
            {
                "stepIndex": 0,
                "title": "1. Connection Initialization & Handshake",
                "narration": "Selenium starts an external `chromedriver` proxy process and makes stateless HTTP calls. Playwright opens a single persistent HTTP `101 Switching Protocols` WebSocket directly to the Browser CDP port.",
                "codeLine": "Playwright: ws://127.0.0.1:9222/devtools/browser/<id> | Selenium: HTTP POST /session",
                "leftTitle": "Selenium W3C HTTP (Stateless)",
                "rightTitle": "Playwright CDP WebSocket (Stateful)",
                "leftMetrics": {"Roundtrips": "1 HTTP POST", "Latency": "45ms", "RAM": "520 MB (1 OS Process)"},
                "rightMetrics": {"Roundtrips": "1 WS Upgrade", "Latency": "3ms", "RAM": "22 MB (BrowserContext)"},
                "activePhase": "handshake"
            },
            {
                "stepIndex": 1,
                "title": "2. Parallel Scaling: 32 Concurrent Test Workers",
                "narration": "To run 32 parallel tests, Selenium must spawn 32 separate Chrome OS processes (~16 GB RAM). Playwright keeps 1 Browser process and spawns 32 isolated `BrowserContext` incognito sessions (~650 MB total)!",
                "codeLine": "BrowserContext ctx = browser.newContext(); // 15ms startup, isolated cookies/storage",
                "leftTitle": "Selenium: 32 Chrome Processes",
                "rightTitle": "Playwright: 1 Browser + 32 Contexts",
                "leftMetrics": {"Processes": "32 OS Processes", "Startup": "4,200ms", "RAM": "~16.4 GB"},
                "rightMetrics": {"Processes": "1 OS Process", "Startup": "18ms / context", "RAM": "~680 MB"},
                "activePhase": "scaling"
            },
            {
                "stepIndex": 2,
                "title": "3. Actionability & Dynamic DOM Auto-Waiting",
                "narration": "Selenium's `WebDriverWait` polls over HTTP every 500ms (`findElement` -> `isDisplayed`). Playwright runs actionability checks inside the browser engine loop on every animation frame (Attached, Visible, Stable, Enabled, Receives Events).",
                "codeLine": "page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(\"Confirm\")).click();",
                "leftTitle": "Selenium Explicit Polling (500ms intervals)",
                "rightTitle": "Playwright Engine-Native Event Push (<1ms)",
                "leftMetrics": {"HTTP Polls": "6 Roundtrips", "Wait Waste": "500ms-1000ms", "Overlay Check": "No"},
                "rightMetrics": {"WS Frames": "1 JSON-RPC Frame", "Wait Waste": "0ms (Event Push)", "Overlay Check": "Yes (Hit-Test)"},
                "activePhase": "autowait"
            },
            {
                "stepIndex": 3,
                "title": "4. The SSR Hydration Trap & Staff SDET Mitigation",
                "narration": "In Next.js/React SSR apps, the HTML button renders before JS attaches `onClick`. Playwright sees the button is visible/enabled and clicks too early! Solution: wait for hydration state or intercept network readiness.",
                "codeLine": "page.waitForResponse(res -> res.url().contains(\"/api/ready\") && res.status() == 200, () -> btn.click());",
                "leftTitle": "Uncaught SSR Hydration Race",
                "rightTitle": "Deterministic Network/Hydration Gate",
                "leftMetrics": {"Click Result": "Swallowed (No Listener)", "Test Outcome": "Flaky Timeout"},
                "rightMetrics": {"Click Result": "Fires after Hydration", "Test Outcome": "100% Deterministic"},
                "activePhase": "hydration"
            }
        ]
        return {"visualizerId": viz_id, "type": "architecture-compare", "title": "Playwright CDP vs. Selenium W3C Internals", "steps": steps}

    if viz_id == "arch-concurrency-isolation":
        steps = [
            {
                "stepIndex": 0,
                "title": "1. The Anti-Pattern: 32 Parallel CI Workers Hit Shared Entity `Flight AI-202, Seat 1A`",
                "narration": "All 32 CI workers run `POST /api/v1/orders` with `{flight: 'AI-202', seat: '1A'}` and NO tenant header. Worker #1 locks Seat 1A; Workers #2..#32 crash with `HTTP 409 Conflict`!",
                "codeLine": "POST /api/v1/orders {\"flightNumber\": \"AI-202\", \"seat\": \"1A\"} // No Tenant Header!",
                "leftTitle": "Naive Shared State (31/32 FAIL)",
                "rightTitle": "Dynamic Tenant Partitioning (32/32 PASS)",
                "leftMetrics": {"201 Created": "1 / 32", "409 Conflict": "31 / 32 (96.9% Fail)", "DB State": "Corrupted / Contended"},
                "rightMetrics": {"Status": "Awaiting Tenant Key...", "Isolation": "N/A", "DB State": "Clean"},
                "activePhase": "collision"
            },
            {
                "stepIndex": 1,
                "title": "2. Why Local `ThreadLocal` Variables Alone Fail",
                "narration": "A common misconception is storing variables in `ThreadLocal` inside the test runner. `ThreadLocal` only isolates JVM/Python heap memory on the test machine—the remote PostgreSQL database still sees 32 requests fighting for the same row!",
                "codeLine": "// WRONG: ThreadLocal only isolates client RAM, not the remote microservice database!",
                "leftTitle": "Client RAM (Isolated)",
                "rightTitle": "Remote Microservice DB (Still Shared!)",
                "leftMetrics": {"Runner Heap": "32 Separate Objects", "Network Payload": "Identical `seat: 1A`"},
                "rightMetrics": {"Postgres Row Lock": "1 Row (`AI-202-1A`)", "Result": "31 Deadlocks / 409s"},
                "activePhase": "misconception"
            },
            {
                "stepIndex": 2,
                "title": "3. Staff SDET Solution: Cryptographic Tenant Key Injection (`X-Test-Tenant-ID`)",
                "narration": "Each parallel worker generates `tenant_id = f'tenant_{worker_id}_{uuid4().hex[:6]}'` and injects `X-Test-Tenant-ID` in the HTTP header. AeroCart partitions the inventory table by `(tenant_id, flight_id, seat)`. All 32 workers book Seat 1A in their own namespace in 71ms!",
                "codeLine": "headers = {\"X-Test-Tenant-ID\": f\"tenant_{worker_id}_{uuid.uuid4().hex[:6]}\"}",
                "leftTitle": "Naive Mode Result",
                "rightTitle": "Tenant-Isolated Mode Result",
                "leftMetrics": {"Passed": "1 / 32", "Failed": "31 / 32"},
                "rightMetrics": {"Passed": "32 / 32 (100%)", "Failed": "0 / 32", "Total Time": "71.5ms"},
                "activePhase": "isolated"
            }
        ]
        return {"visualizerId": viz_id, "type": "architecture-compare", "title": "Distributed Concurrency & Tenant Isolation", "steps": steps}

    # Default: arch-endpoint-cloud-sync
    steps = [
        {
            "stepIndex": 0,
            "title": "1. Steady-State Endpoint-to-Cloud Telemetry Sync",
            "narration": "On macOS/Windows, the local endpoint agent monitors OS events (USB mount, file I/O, network sockets) and streams batches over persistent mTLS HTTP/2 to the cloud ingestion gateway.",
            "codeLine": "Agent (RSS: 48MB, FDs: 64) ══mTLS HTTP/2══► Cloud Gateway ──► Kafka ──► Analytics DB",
            "leftTitle": "Local Endpoint Agent (macOS/Win)",
            "rightTitle": "Cloud Ingestion Pipeline",
            "leftMetrics": {"CPU / RAM": "1.2% / 48 MB", "File Descriptors": "64 open", "Local Queue": "0 buffered"},
            "rightMetrics": {"Throughput": "12,000 events/s", "Gateway p99": "18ms", "Error Rate": "0.00%"},
            "activePhase": "steady"
        },
        {
            "stepIndex": 1,
            "title": "2. Network Outage → Local SQLite WAL Ring-Buffer Activation",
            "narration": "Wi-Fi drops or cloud gateway returns 503. Instead of leaking RAM by holding events in an unbounded in-memory list, the agent flushes events to a bounded on-disk SQLite WAL ring-buffer (max 100MB, FIFO eviction).",
            "codeLine": "if network_down: sqlite_wal_ring_buffer.insert_with_fifo_cap(event, max_mb=100)",
            "leftTitle": "Endpoint Offline Mode",
            "rightTitle": "Cloud Backend (Unreachable)",
            "leftMetrics": {"RAM Footprint": "49 MB (Flat! Zero Leak)", "Disk Ring-Buffer": "14.2 MB / 100 MB", "Data Loss": "0 events"},
            "rightMetrics": {"Connection": "Offline / Packet Loss 100%", "Status": "Awaiting Reconnect"},
            "activePhase": "offline"
        },
        {
            "stepIndex": 2,
            "title": "3. Reconnection: Naive Retry (Thundering Herd) vs. Full Jitter + Idempotency",
            "narration": "When network recovers, if 50,000 endpoints retry immediately, the cloud crashes with HTTP 503. Using Exponential Backoff with Full Jitter `sleep(random(0, min(60, 2 ** attempt)))` + UUID `idempotency_key` smooths ingestion with zero duplicates!",
            "codeLine": "delay = random.uniform(0, min(MAX_CAP, BASE * (2 ** attempt))) # Full Jitter",
            "leftTitle": "Naive Reconnect (No Jitter)",
            "rightTitle": "Exponential Backoff + Full Jitter",
            "leftMetrics": {"Peak Burst": "50,000 req/sec spike", "Gateway Status": "503 Crash (Self-DDoS)", "Duplicates": "High"},
            "rightMetrics": {"Peak Burst": "1,200 req/sec smooth", "Gateway Status": "200 OK (Healthy)", "Duplicates": "0 (Idempotent UUID)"},
            "activePhase": "reconnect"
        }
    ]
    return {"visualizerId": viz_id, "type": "architecture-compare", "title": "Endpoint-to-Cloud Sync & Backpressure Architecture", "steps": steps}


def generate_trace(viz_id: str, custom_input: Dict[str, Any] = None) -> Dict[str, Any]:
    """Dispatch trace generation to the appropriate DSA or Architecture engine."""
    if viz_id == "dsa-group-anagrams":
        return trace_group_anagrams(custom_input)
    if viz_id == "dsa-two-sum":
        return trace_two_sum(custom_input)
    if viz_id == "dsa-valid-anagram":
        return trace_valid_anagram(custom_input)
    return trace_architecture(viz_id)

