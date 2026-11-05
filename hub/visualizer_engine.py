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
        },
        {
            "id": "cs-os-leak-detector",
            "type": "architecture",
            "title": "Core CS (OS): GC Sawtooth vs. True Post-GC RSS & File Descriptor Leaks",
            "category": "Operating Systems Internals",
            "complexity": {"time": "24h Soak Linear Regression", "space": "Post-GC Floor vs ulimit -n"},
            "defaultInput": {"max_fd_limit": 1024},
            "description": "Compare a healthy JVM/Python GC sawtooth wave against a true post-GC heap leak and an OS file-descriptor exhaustion crash (EMFILE)."
        },
        {
            "id": "cs-tcp-tls-handshake",
            "type": "architecture",
            "title": "Core CS (Networks): TLS 1.2 + HTTP/1.1 vs. TLS 1.3 + HTTP/2 & SYN Backlogs",
            "category": "Computer Networks & Protocols",
            "complexity": {"time": "4 RTT per req vs 1 RTT Multiplexed", "space": "listen(128) SYN Queue"},
            "defaultInput": {"rtt_ms": 50, "requests": 10},
            "description": "Step through packet roundtrips for TCP 3-way handshake, TLS 1.2 vs 1.3 key exchange, and why Linux listen(5) drops 32-worker bursts."
        },
        {
            "id": "ai-rag-triad-gate",
            "type": "architecture",
            "title": "AI Engineering: RAG Triad Claim-Entailment vs. Negation Hallucination Trap",
            "category": "AI & LLM Quality Engineering",
            "complexity": {"time": "Context Recall + Faithfulness", "space": "Polarity & Entailment Gate"},
            "defaultInput": {"threshold": 0.80},
            "description": "See why naive 96% cosine similarity passes a contradictory 'CANNOT cancel' hallucination, and how the RAG Triad Faithfulness gate blocks it."
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

    if viz_id == "cs-os-leak-detector":
        steps = [
            {
                "stepIndex": 0,
                "title": "1. The GC Sawtooth Illusion (Why Raw RSS Graphs Mislead Engineers)",
                "narration": "Between t=0m and t=30m, RSS climbs from 48 MB to 138 MB. A naive alert flags a memory leak! In reality, once Full GC runs at t=60m, RSS drops right back to the 48.5 MB live-object floor.",
                "codeLine": "gc_points = [s for s in snapshots if s['gc_triggered']] # Filter post-GC floor!",
                "leftTitle": "Naive Raw RSS Check (False Alarm)",
                "rightTitle": "Post-GC Baseline Floor Analysis",
                "leftMetrics": {"t=0m -> t=30m": "48 MB -> 138 MB", "Naive Verdict": "FALSE POSITIVE LEAK", "Ignored Factor": "Uncollected Young/Old Gen"},
                "rightMetrics": {"t=0m (GC) -> t=120m (GC)": "48.0 MB -> 49.0 MB", "Post-GC Slope": "+0.5 MB/hr (<= 5.0 threshold)", "True Verdict": "HEALTHY SAWTOOTH"},
                "activePhase": "sawtooth"
            },
            {
                "stepIndex": 1,
                "title": "2. Detecting a True Post-GC Heap Leak (Unbounded Cache / Listener Retention)",
                "narration": "When an endpoint daemon registers event listeners or caches telemetry batches without eviction, even after Full GC runs, the floor climbs from 50 MB -> 86 MB -> 122 MB (+36 MB/hr slope).",
                "codeLine": "slope_mb_per_hr = (last_gc['rss_mb'] - first_gc['rss_mb']) / delta_hours # 36.0 MB/hr > 5.0",
                "leftTitle": "Healthy Daemon Post-GC Floor",
                "rightTitle": "Leaking Daemon Post-GC Floor",
                "leftMetrics": {"GC #1 / #2 / #3": "48 MB / 48.5 MB / 49 MB", "Slope": "0.5 MB/hr", "24h Projection": "~60 MB (Stable)"},
                "rightMetrics": {"GC #1 / #2 / #3": "50 MB / 86 MB / 122 MB", "Slope": "36.0 MB/hr (LEAK!)", "24h Projection": "914 MB -> OOM Kill"},
                "activePhase": "heap_leak"
            },
            {
                "stepIndex": 2,
                "title": "3. Silent File-Descriptor / Handle Exhaustion (`EMFILE: Too many open files`)",
                "narration": "Each leaked socket or file handle consumes almost zero RAM (RSS stays flat at 50 MB), but increments the OS kernel handle table (`lsof -p <pid>`). At 890/1024 handles (86.9% of `ulimit -n`), the daemon is minutes away from crashing on every `socket()` syscall!",
                "codeLine": "fd_leak = (peak_fds / max_fd_limit >= 0.80) or monotonic_fd_growth",
                "leftTitle": "RAM Profiler Only (Misses Bug!)",
                "rightTitle": "OS Handle + Post-GC Dual Profiler",
                "leftMetrics": {"RSS Memory": "50.4 MB (Flat)", "RAM Verdict": "Looks Healthy", "Production Outcome": "Crashes with Errno 24 EMFILE"},
                "rightMetrics": {"Open FDs": "80 -> 340 -> 890 / 1024", "FD Utilization": "86.9% (>= 80% Gate)", "Verdict": "FD_LEAK CAUGHT IN CI"},
                "activePhase": "fd_leak"
            }
        ]
        return {"visualizerId": viz_id, "type": "architecture-compare", "title": "OS Internals: Post-GC Heap & File-Descriptor Leak Detection", "steps": steps}

    if viz_id == "cs-tcp-tls-handshake":
        steps = [
            {
                "stepIndex": 0,
                "title": "1. Cold Connection Tax: TCP 3-Way Handshake + TLS 1.2 vs. TLS 1.3",
                "narration": "At 50ms RTT, TLS 1.2 requires 1 RTT for TCP (`SYN`/`SYN-ACK`/`ACK`) + 2 RTTs for TLS key exchange + 1 RTT for HTTP = 200ms per unpooled request. TLS 1.3 embeds key shares in `ClientHello`, cutting TLS to 1 RTT!",
                "codeLine": "TLS 1.2 Cold = 4 * RTT (200ms) | TLS 1.3 Cold = 3 * RTT (150ms)",
                "leftTitle": "HTTP/1.1 (No Pool) + TLS 1.2",
                "rightTitle": "HTTP/2 Multiplexed + TLS 1.3",
                "leftMetrics": {"1st Request": "200ms (1 TCP + 2 TLS + 1 HTTP)", "10 Sequential Reqs": "2,000ms total", "Handshake Waste": "1,500ms (75% overhead)"},
                "rightMetrics": {"1st Request": "150ms (1 TCP + 1 TLS + 1 HTTP)", "10 Pooled Reqs": "600ms total (70% Faster!)", "Handshake Waste": "100ms (Paid Once)"},
                "activePhase": "handshake"
            },
            {
                "stepIndex": 1,
                "title": "2. The Linux Kernel `listen(backlog)` SYN Queue Overflow (`Errno 104`)",
                "narration": "When 32 parallel CI workers burst-connect simultaneously to a server with `request_queue_size = 5` (`listen(5)`), Linux accepts 5 connections into the SYN/Accept queue and sends TCP `RST` (`ConnectionResetError`) to the other 27 workers!",
                "codeLine": "class ThreadedHTTPServer(ThreadingMixIn, HTTPServer): request_queue_size = 128",
                "leftTitle": "Default `listen(5)` under 32-Thread Burst",
                "rightTitle": "Tuned `listen(128)` under 32-Thread Burst",
                "leftMetrics": {"Accepted Connections": "5 / 32", "Dropped (TCP RST)": "27 / 32 (Errno 104)", "CI Stability": "Flaky / Broken on Linux"},
                "rightMetrics": {"Accepted Connections": "32 / 32 (100%)", "Dropped (TCP RST)": "0 / 32", "CI Stability": "100% Deterministic"},
                "activePhase": "backlog"
            },
            {
                "stepIndex": 2,
                "title": "3. SASE Forward Proxy mTLS Inspection (Endpoint -> Cloud SWG -> Origin)",
                "narration": "In enterprise SASE architectures (e.g., Netskope), the local endpoint agent tunnels traffic over persistent mTLS HTTP/2 to the Cloud Proxy, which inspects DLP/threat policies in-memory before forwarding to the origin.",
                "codeLine": "[Endpoint] ==mTLS 1.3 Tunnel==> [SASE Cloud Proxy (DLP/AV)] ==TLS 1.3==> [Origin API]",
                "leftTitle": "Unpooled Per-Request MITM Proxy",
                "rightTitle": "Persistent mTLS Tunnel + Session Reuse",
                "leftMetrics": {"Dual Handshakes": "Every request re-handshakes", "Added Proxy Latency": "+180ms p99"},
                "rightMetrics": {"Tunnel State": "Pre-warmed HTTP/2 mTLS", "Added Proxy Latency": "+6ms p99 (Wire-Speed)"},
                "activePhase": "sase"
            }
        ]
        return {"visualizerId": viz_id, "type": "architecture-compare", "title": "Computer Networks: TCP/TLS Handshakes, SYN Backlogs & SASE Proxies", "steps": steps}

    if viz_id == "ai-rag-triad-gate":
        steps = [
            {
                "stepIndex": 0,
                "title": "1. Vector Retrieval: Measuring Context Recall (`doc_24h_rule`)",
                "narration": "User asks: 'Can I cancel within 24 hours for a full refund?' The retriever fetches `doc_24h_rule`: 'Passengers may cancel within 24 hours of booking for a 100% full refund if purchased 7 days prior.' Both ground-truth facts are present -> Context Recall = 1.00.",
                "codeLine": "context_recall = covered_ground_truth_facts / total_ground_truth_facts # 2/2 = 1.00",
                "leftTitle": "Broken Keyword Retriever (Bug Caught Earlier)",
                "rightTitle": "Tuned Policy Retriever (`doc_24h_rule`)",
                "leftMetrics": {"Matched Chunk": "doc_eu261 (Matched word 'hour')", "Context Recall": "0.00 (Wrong Document!)"},
                "rightMetrics": {"Matched Chunk": "doc_24h_rule (US DOT 24h Rule)", "Context Recall": "1.00 (100% Facts Retrieved)"},
                "activePhase": "retrieval"
            },
            {
                "stepIndex": 1,
                "title": "2. The Negation Hallucination Trap (Why 96% Cosine Similarity Fails)",
                "narration": "Suppose the LLM hallucinates: 'Passengers CANNOT cancel their reservation within 24 hours for a 100% full refund.' Because 12/13 words match the policy, naive embedding cosine similarity scores 0.96 and PASSES a contradictory legal policy!",
                "codeLine": "contradictory_negation = bool(ans_negations - ctx_negations) # Detects 'cannot' polarity flip!",
                "leftTitle": "Naive Cosine Similarity Gate (> 0.85)",
                "rightTitle": "RAG Triad Faithfulness & Polarity Gate",
                "leftMetrics": {"Generated Answer": "'Passengers CANNOT cancel...'", "Cosine Similarity": "0.96 (96% Overlap)", "Gate Outcome": "FALSE PASS (P0 Legal Bug Escapes!)"},
                "rightMetrics": {"Generated Answer": "'Passengers CANNOT cancel...'", "Faithfulness Score": "0.19 (Polarity Inversion Penalty)", "Gate Outcome": "BLOCKED IN CI (Hallucination Caught)"},
                "activePhase": "negation_trap"
            },
            {
                "stepIndex": 2,
                "title": "3. Full RAG Triad CI Gate (Recall >= 0.80, Faithfulness >= 0.80, Relevance >= 0.70)",
                "narration": "Only when Context Recall (1.00), Claim Faithfulness (1.00), and Answer Relevance (1.00) all clear their thresholds does the CI pipeline approve the RAG prompt/model release.",
                "codeLine": "passed_ci_gate = (context_recall >= 0.80 and faithfulness >= 0.80 and answer_relevance >= 0.70)",
                "leftTitle": "Hallucinated / Irrelevant Outputs",
                "rightTitle": "Grounded Policy Output",
                "leftMetrics": {"Negated Faithfulness": "0.19 (FAIL)", "Pet Policy Relevance": "0.00 (FAIL)", "CI Status": "Release Blocked"},
                "rightMetrics": {"Context Recall": "1.00 (PASS)", "Faithfulness & Relevance": "1.00 / 1.00 (PASS)", "CI Status": "Release Approved"},
                "activePhase": "triad_pass"
            }
        ]
        return {"visualizerId": viz_id, "type": "architecture-compare", "title": "AI Engineering: RAG Evaluation Triad & Negation Trap Gate", "steps": steps}

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

