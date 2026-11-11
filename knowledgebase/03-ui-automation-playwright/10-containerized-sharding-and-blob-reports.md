---
slug: pw-10-containerized-sharding-and-blob-reports
course_id: 03-ui-automation-playwright
track: core-cs
volume: "03. Zero to Mastery: UI Automation (Playwright-Focused)"
module_number: 4
module_title: "Module 4: Forensics, Visual/a11y Gates & Sharded CI"
chapter_number: 10
level_tag: "Staff Platform Engineer"
title: "AeroBot v1.0: Containerized CI Sharding, `/dev/shm` OOM Physics & Blob Report Merging"
summary: "Ship AeroBot v1.0—running 2,000+ Playwright tests in <4 minutes across Kubernetes/GitHub shards without `/dev/shm` `TargetClosedError` crashes, unified via LPT bin-packing and Blob report merging."
reading_time_minutes: 21
visualizer_id: pw-network-auth-sharding
lab_path: frameworks/sdet-system-design/02-ci-shard-bin-packer-and-tia
tags: ["ci-sharding", "docker-shm", "ipc-host", "blob-reporter", "merge-reports", "kubernetes-ci", "flake-budget"]
---

# AeroBot v1.0: Containerized CI Sharding, `/dev/shm` OOM Physics & Blob Report Merging

```json continuity
{
  "previously": "In Chapter 09, AeroBot v0.9 added zero-overhead failure-only flight recording (`trace.zip`), automated WCAG 2.1 AA (`axe-core`) gates, and Docker-pinned masked visual regression.",
  "painPoint": "Success created a new problem: our AeroBot suite now has 2,000 UI tests! Running them on one machine takes 48 minutes, and when we containerize them on Docker or Kubernetes (`4Gi` RAM pods), Chromium mysteriously crashes mid-test with `TargetClosedError: Page crashed` even while 70% of pod RAM is completely free!",
  "unlock": "Ship AeroBot v1.0—eliminating container `/dev/shm` crashes, balancing 2,000 tests across horizontal shards in under 4 minutes, and merging every shard into one unified Blob HTML report!"
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Slide 1 / 4 · The Mystery of the 4GB Pod Crash (`/dev/shm`)",
    "caption": "Why does Chromium crash inside a 4GB Docker or Kubernetes container when 3GB of RAM is still free? Because containers default `/dev/shm` shared memory to a tiny 64MB Scratchpad—and Chromium paints page tiles there!",
    "code": "# Default Docker `/dev/shm` = 64MB -> Chromium `Page crashed`!\ndocker run --init --shm-size=2g mcr.microsoft.com/playwright:v1.50.0-noble"
  },
  {
    "time": "0:24",
    "badge": "Slide 2 / 4 · Don't Cram 24 Browsers Onto 1 Machine—Shard Horizontally!",
    "caption": "Putting 24 headless browsers on an 8-core VM starves the CPU and creates fake 5-second timeout flakes. Instead, run 3–4 workers per 4-core container and fan out across 8 parallel CI shards!",
    "code": "# Machine k of 8 runs 1/8th of the suite cleanly:\nnpx playwright test --shard=1/8 --workers=3 --reporter=blob"
  },
  {
    "time": "0:50",
    "badge": "Slide 3 / 4 · Balancing Heavy & Light Tests (LPT Bin-Packing)",
    "caption": "Splitting files alphabetically puts eight slow 90-second checkout files onto Shard 3 while Shard 7 finishes in 1 minute! Sorting slowest-first (LPT) balances every shard within seconds of each other.",
    "code": "ordered = sorted(specs, key=lambda s: (-s.estimated_ms, s.nodeid))\n# Assign each spec to the shard bin with the lowest total runtime!"
  },
  {
    "time": "1:15",
    "badge": "Slide 4 / 4 · One Unified Dashboard via Blob Report Merging",
    "caption": "Nobody wants to download 8 separate CI artifacts to hunt for one failed test. Each shard emits a lightweight `blob.zip`, and a 15-second fan-in job merges them into one searchable HTML + Trace report!",
    "code": "npx playwright merge-reports --reporter=html,junit ./all-blob-reports"
  }
]
```

```json pretraining
[
  {
    "term": "Docker `/dev/shm` 64MB Trap",
    "formula": "Default Container `/dev/shm` == 64MB -> Chromium Renderer Crash!",
    "meaning": "Docker and Kubernetes give shared memory (`/dev/shm`) only 64MB by default; because Chromium draws big page images inside `/dev/shm`, tabs crash mid-test unless you expand it to `2GB` (`--shm-size=2g`)."
  },
  {
    "term": "Horizontal CI Sharding (`1/M .. M/M`)",
    "formula": "8 Containers x 4 Browser Workers = 32 Parallel Browsers",
    "meaning": "Splitting a big test suite across multiple separate CI containers so 48 minutes of browser work finishes in about 3 minutes."
  },
  {
    "term": "Duration Bin-Packing (LPT)",
    "formula": "Sort Slowest Test Files First -> Deal Into Lightest Shard Bucket",
    "meaning": "Using yesterday's test timings to spread slow checkout tests evenly across every CI machine so one overloaded machine doesn't hold up the whole PR."
  },
  {
    "term": "Blob Report Fan-In (`merge-reports`)",
    "formula": "`blob-1.zip` .. `blob-8.zip` -> `merge-reports` -> 1 HTML Report",
    "meaning": "Combining the raw results and failure `trace.zip` recordings from all 8 CI machines into a single easy-to-read webpage."
  }
]
```

```json poe
{
  "question": "A platform team containerizes their Playwright suite on Kubernetes (`4Gi` RAM, `4` vCPU per pod). Tests pass 100% on laptops, yet inside Kubernetes pods Chromium randomly crashes mid-suite on graphic-heavy dashboard pages with `Error: Page crashed` / `Target page, context or browser has been closed`, even though `kubectl top pod` shows total pod memory is only `1.1Gi / 4Gi`! What OS/container limit was exhausted?",
  "options": [
    "Kubernetes pods block WebSockets over `localhost`",
    "Docker and Kubernetes `emptyDir` default **`/dev/shm` (POSIX shared memory)** to **`64MB`**! Chromium's Browser, GPU, and Renderer processes allocate shared-memory bitmaps inside `/dev/shm` regardless of free pod RAM—exhausting `64MB` triggers immediate renderer `SIGBUS`/crash! Fix: mount an in-memory `emptyDir: { medium: Memory, sizeLimit: 2Gi }` at `/dev/shm` (or `--ipc=host` / `--shm-size=2g` in Docker), with `--disable-dev-shm-usage` only as a disk-backed fallback",
    "Linux kernels limit headless browsers to 10 TCP sockets",
    "Playwright requires privileged root containers to click SVG elements"
  ],
  "answerIndex": 1,
  "explanation": "This is arguably the #1 real-world Staff SDET infrastructure interview question! Total container cgroup memory (`4Gi`) can be 70% free while the `64MB` `/dev/shm` mount hits `100%` utilization and kills Chromium's renderer process instantly. Sizing `/dev/shm` to `1–2Gi` (`--ipc=host` or `--shm-size=2g`) keeps shared-memory IPC in fast RAM instead of falling back to slow `/tmp` disk I/O."
}
```

## 🌱 Step 1: Plain-English Story — The Tiny 64MB Desk & The 8 Airport Security Lanes

Welcome to the finale of Course 03! Across Chapters 01 to 09, we grew **`AeroBot`** from a fragile 4-line click script into an isolated, accessible, visual-diffed browser suite. Now imagine **2,000 `AeroBot` tests** guarding every pull request at AeroCart.

When teams try to run 2,000 browser tests in CI, they hit two painful walls right away:

1. **The Tiny 64MB Desk Inside a Giant Room (`/dev/shm`)**:
   - Imagine renting a huge `4GB` warehouse for an artist, but giving them a **postage-stamp `64MB` desk** to lay out giant posters. The warehouse is 75% empty, yet the moment a poster overflows that tiny desk, everything crashes onto the floor!
   - Linux containers have a special fast-memory folder called **`/dev/shm`** that Chromium uses to pass rendered page images between browser tabs. Docker and Kubernetes quietly cap `/dev/shm` at **`64MB`** by default—causing mysterious `"Page crashed"` errors until you give `/dev/shm` a `2GB` desk (`--shm-size=2g`).
2. **Opening 8 Balanced Airport Lanes + Stapling One Master Receipt**:
   - Instead of cramming 32 browsers onto one overloaded computer (where they fight for CPU and cause fake timeouts), we open **8 separate 4-core containers** (`Shard 1/8` through `Shard 8/8`), deal the slowest test files evenly across them, and merge their `blob` outputs into **one unified HTML report**!

```mermaid
flowchart LR
  Plan["CI Fan-Out (Pinned Docker + 2GB /dev/shm)"] -->|Shard 1/4| S1["Pod 1 (4 vCPU, 3 Workers) -> blob-1.zip"]
  Plan -->|Shard 2/4| S2["Pod 2 (4 vCPU, 3 Workers) -> blob-2.zip"]
  Plan -->|Shard 3..4| S3["Pod 3..4 -> blob-3..4.zip"]
  S1 & S2 & S3 -->|Fan-In Job (15s)| Merge["merge-reports -> 1 Unified HTML + Trace Report"]
```

## 🔨 Step 2: First Lines of Code — Fail-Fast `/dev/shm` Guard & Shard Partition (`AeroBot v1.0`)

Before running a single browser test inside a Linux container, **`AeroBot v1.0`** runs a 10-line preflight check at startup: if someone forgot `--shm-size=2g` and left `/dev/shm` at Docker's `64MB` default, it tells the engineer *immediately* in plain English instead of flaking 12 minutes later!

```python
import os
import shutil


def assert_container_shm_ready(min_mib: int = 512) -> None:
    """Fails fast in 1ms if Docker/K8s left `/dev/shm` at the 64MB default!"""
    if not os.path.exists("/dev/shm"):
        return  # macOS / Windows developer laptop
    total_mib = shutil.disk_usage("/dev/shm").total // (1024 * 1024)
    if total_mib < min_mib:
        raise RuntimeError(
            f"/dev/shm is only {total_mib} MiB (<{min_mib} MiB)! "
            "Pass `--shm-size=2g` so Chromium never dies with Page crashed."
        )


def pick_round_robin_shard(files: list[str], shard_1_based: int, total: int) -> list[str]:
    return sorted(files)[shard_1_based - 1 :: total]
```

### Java 17 Equivalent

```java
import java.io.IOException;
import java.nio.file.*;
import java.util.*;

public class AeroBotV10ShardStarter {
    public static void assertContainerShmReady(long minMiB) throws IOException {
        Path shm = Path.of("/dev/shm");
        if (!Files.exists(shm)) return; // macOS / Windows laptop
        long totalMiB = Files.getFileStore(shm).getTotalSpace() / (1024L * 1024L);
        if (totalMiB > 0 && totalMiB < minMiB) {
            throw new IllegalStateException(
                "/dev/shm is only " + totalMiB + " MiB! Pass --shm-size=2g in Docker/K8s.");
        }
    }
}
```

## ⚡ Step 3: Where It Breaks in Real Life — CPU Starvation, Zombie Processes & Tail Skew

Even after fixing `/dev/shm`, three subtle infrastructure traps still ruin large CI pipelines:

1. **The Worker-CPU Contention Trap**: An actively rendering Chromium browser consumes `~0.75–1.0` vCPU core during React hydration. Scheduling `24` workers onto an `8-vCPU` VM starves the OS run-queue: hydration stretches from `150ms` to `6,200ms`, blowing past `5,000ms` assertion timeouts! Keep workers at **`0.75x – 1.0x vCPUs`** per pod and add more shards horizontally.
2. **Alphabetical Shard Skew**: Notice `sorted(files)[k::M]` in Step 2? If all eight `90-second` `test_checkout_*.py` files land on Shard 3 while Shard 7 gets tiny `5-second` login checks, Shard 7 sits idle while the PR waits `12 minutes` on Shard 3!
3. **Orphaned Zombie Processes (`--init`)**: Browser runs spawn and kill hundreds of renderer subprocesses. Inside Docker, if PID 1 doesn't reap exited child processes (`docker run --init`), `<defunct>` zombies fill up the container process table (`pids.max`)!

```json contrast
{
  "title": "Over-Subscribed Single VM & Default 64MB `/dev/shm` vs Right-Sized Shards & Blob Fan-In",
  "naiveTitle": "1 Giant VM (`-n 24` on 8 vCPU) + 64MB shm",
  "naiveMetric": "Renderer `TargetClosed` Crashes · 28m PR Wait",
  "naivePoints": [
    "Default 64MB `/dev/shm` triggers random `Page crashed` errors halfway through dashboard tests",
    "Over-subscribing 24 browsers onto 8 vCPUs starves V8 event loops, causing false-positive 5s assertion timeouts",
    "16 separate matrix jobs produce 16 separate HTML report zips—engineers click through 16 tabs hunting failures"
  ],
  "staffTitle": "8x `4-vCPU` Pods (`--shm-size=2g`) + Blob Merge",
  "staffMetric": "3m 10s Wall-Clock · 0 Renderer Crashes",
  "staffPoints": [
    "Pins `mcr.microsoft.com/playwright:v1.50.0-noble` with `--init --shm-size=2g` (or 2Gi RAM `/dev/shm` in K8s)",
    "Caps concurrency at `0.75x - 1.0x vCPU` per pod and scales horizontally via LPT duration-balanced shards",
    "Merges all shard blobs into 1 unified HTML + JUnit report and enforces a `<1%` rolling 7-day flake budget"
  ]
}
```

Explore the **`pw-network-auth-sharding`** simulator below to tune shard count $M$, worker-per-pod concurrency $W$, `/dev/shm` allocation, and LPT bin-packing skew!

## 🚀 Step 4: Staff Engineer Deep-Dive — LPT Makespan Math, Container Kernel Hygiene & Production Blueprints

When partitioning $N$ test files with historical durations $\{t_1, t_2, \dots, t_N\}$ across $M$ stateless CI shards (each running $W$ local workers with container boot time $T_{\text{boot}}$ and tail imbalance $T_{\text{skew}}$), end-to-end PR wall-clock latency obeys:

$$T_{\text{wall}}(M, W) = T_{\text{boot}} + \frac{\sum_{i=1}^{N} t_i}{M \cdot W} + T_{\text{skew}}$$

By sorting test files in **Longest-Processing-Time-First (LPT)** order ($t_1 \ge t_2 \ge \dots \ge t_N$) and greedily assigning each file to the shard with the smallest accumulated load via a min-heap, Graham's classic scheduling theorem bounds worst-case makespan $C_{\max}$ tightly against the theoretical optimum $C_{\max}^*$:

$$\frac{C_{\max}(\text{LPT})}{C_{\max}^*} \le \frac{4}{3} - \frac{1}{3M}$$

In practice across real Playwright suites (`2,000` specs across $M = 8$ pods), LPT shrinks $T_{\text{skew}}$ from **`+10m 40s`** (alphabetical splitting) down to **`< 8 seconds`**!

| Infrastructure Parameter | Anti-Pattern / Dangerous Default | Staff Production Standard (`AeroBot v1.0`) | Why It Matters |
| :--- | :--- | :--- | :--- |
| **Container Base Image** | `:latest` floating tag or runtime `playwright install` | Exact version `mcr.microsoft.com/playwright:v1.50.0-noble` | Saves `90s` browser download per shard & locks exact FreeType/Chromium binaries. |
| **Shared Memory (`/dev/shm`)** | Docker/K8s `64MB` default | `--shm-size=2g` or `--ipc=host` (K8s `Memory` `emptyDir: 2Gi`) | Prevents silent Chromium renderer `SIGBUS` / `Page crashed` deaths in RAM. |
| **PID 1 Process Reaping** | Bare test runner as PID 1 | `docker run --init` (or `shareProcessNamespace` / `tini`) | Reaps orphaned headless renderer `<zombie>` child processes cleanly. |
| **Workers per 4-vCPU Pod** | `workers = 12` (CPU thrashing!) | `workers = 3` or `4` ($\le 1\text{ worker / vCPU}$) | Keeps `requestAnimationFrame` & React hydration latencies deterministic. |
| **Artifact Fan-In** | 8 disconnected HTML artifacts | `--reporter=blob` on shards $\to$ `playwright merge-reports` | Produces 1 unified searchable HTML dashboard with embedded failure `trace.zip`s. |

### Production Blueprint: Deterministic LPT Duration Shard Planner (Python 3)

```python
from __future__ import annotations
from dataclasses import dataclass
import heapq
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class TimedSpecItem:
    nodeid: str
    estimated_ms: int


def assign_lpt_balanced_shard(
    all_items: Sequence[TimedSpecItem],
    shard_index_1_based: int,
    total_shards: int,
) -> List[str]:
    """
    Longest-Processing-Time-First (LPT) greedy bin-packer:
    Eliminates alphabetical tail skew across `--shard=k/M` CI pods!
    """
    if not (1 <= shard_index_1_based <= total_shards):
        raise ValueError(f"Invalid shard {shard_index_1_based}/{total_shards}")

    # Deterministic tie-break by nodeid so every isolated CI pod computes the EXACT same partition!
    ordered = sorted(all_items, key=lambda x: (-x.estimated_ms, x.nodeid))

    # Min-heap of (accumulated_ms, shard_0_idx)
    bins: List[tuple[int, int]] = [(0, idx) for idx in range(total_shards)]
    heapq.heapify(bins)
    assigned: Dict[int, List[str]] = {idx: [] for idx in range(total_shards)}

    for item in ordered:
        load_ms, bin_idx = heapq.heappop(bins)
        assigned[bin_idx].append(item.nodeid)
        heapq.heappush(bins, (load_ms + max(1, item.estimated_ms), bin_idx))

    # Return in canonical nodeid order so module-scoped fixtures group cleanly inside the pod!
    return sorted(assigned[shard_index_1_based - 1])
```

### Java 17 Equivalent: Container `/dev/shm` Preflight & LPT Shard Filter

```java
package com.aerocart.qa.sharding;

import java.io.IOException;
import java.nio.file.FileStore;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

public final class ContainerShardPreflight {

    private static final long MIN_DEV_SHM_BYTES = 512L * 1024L * 1024L; // 512 MiB minimum guardrail

    /**
     * Fails fast at t=0ms in Linux CI containers if `/dev/shm` was left at Docker's 64MB default!
     */
    public static void verifyLinuxSharedMemoryCapacity(Path shmPath) throws IOException {
        if (!Files.exists(shmPath)) return; // Non-Linux host (macOS/Windows)
        FileStore store = Files.getFileStore(shmPath);
        long totalBytes = store.getTotalSpace();
        if (totalBytes > 0 && totalBytes < MIN_DEV_SHM_BYTES) {
            throw new IllegalStateException(String.format(
                    "FATAL INFRA PREFLIGHT: /dev/shm is only %d MiB (<512 MiB)! "
                    + "Pass `--shm-size=2g` or mount a Memory emptyDir on /dev/shm to prevent Chromium SIGBUS crashes.",
                    totalBytes / (1024L * 1024L)));
        }
    }

    public record SpecWeight(String className, long historicalDurationMs) {}

    public static List<String> selectClassesForShard(
            List<SpecWeight> specs, int shardOneBased, int totalShards) {
        List<SpecWeight> sorted = new ArrayList<>(specs);
        sorted.sort(Comparator.comparingLong(SpecWeight::historicalDurationMs).reversed()
                .thenComparing(SpecWeight::className));

        PriorityQueue<long[]> minHeap = new PriorityQueue<>(
                Comparator.comparingLong((long[] a) -> a[0]).thenComparingLong(a -> a[1]));
        Map<Integer, List<String>> buckets = new HashMap<>();
        for (int i = 0; i < totalShards; i++) {
            minHeap.offer(new long[]{0L, i});
            buckets.put(i, new ArrayList<>());
        }
        for (SpecWeight sw : sorted) {
            long[] lightest = Objects.requireNonNull(minHeap.poll());
            int idx = (int) lightest[1];
            buckets.get(idx).add(sw.className());
            lightest[0] += Math.max(1L, sw.historicalDurationMs());
            minHeap.offer(lightest);
        }
        List<String> myShard = buckets.get(shardOneBased - 1);
        Collections.sort(myShard);
        return List.copyOf(myShard);
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Splitting `module`/`class`-Scoped Fixtures Across Naive Test-Level Shards**:
> Look closely at the unit of sharding in both LPT blueprints above:
> 1. **Unit of Sharding**: If 12 tests inside `TestHeavyCheckoutClass` share an expensive `class`/`module`-scoped dataset seed (`6s`), round-robin sharding *individual test methods* across 8 shards forces **all 8 shards** to pay that `6s` class setup (`8 * 6s = 48s` wasted setup)! Always bin-pack at the **file / test-class granularity** so shared module fixtures execute on only one shard!
> 2. **Zero-Flake Quarantine SLA**: A Staff CI gate tracks `FLAKY` (failed attempt 1, passed retry 2) separately from `PASSED`. Any test exceeding a **1% rolling 7-day flake rate** automatically opens an owner-assigned issue and moves to a non-blocking quarantine lane with a **72-hour fix-or-delete SLA** so PR velocity stays rock-solid!

**Course 03 Complete — Congratulations on Shipping `AeroBot v1.0`!** You took `AeroBot` from a single CDP/BiDi pipe message in Chapter 01 all the way to a 32-worker containerized CI platform with `0ms` `BrowserContext` isolation, strict role locators, Zero-UI auth, HAR/WebSocket control, virtualized clocks, WCAG 2.1 AA + visual gates, and LPT sharded Blob reporting. **Up Next in Course 04 (`04-api-and-api-automation`)**: We'll go beneath the browser and build **`AeroClient`**—mastering HTTP/2 connection pooling, OAuth2/PKCE & mTLS, Pydantic/REST Assured schemas, GraphQL, gRPC, and Pact contract testing!

```json quiz
[
  {
    "id": "pw-10-q1",
    "question": "Inside a Kubernetes CI pod with `4Gi` memory limit (`1.2Gi` used), Chromium tabs intermittently die with `TargetClosedError: Page crashed` on canvas/chart screens. What is the exact Kubernetes pod-spec fix?",
    "options": [
      "Increase pod memory limit from `4Gi` to `16Gi` without changing volumes",
      "Mount an in-memory volume (`emptyDir: { medium: Memory, sizeLimit: 2Gi }`) at `/dev/shm` so Chromium's shared-memory compositor buffers are not bottlenecked by the default `64MB` container `/dev/shm` ceiling",
      "Set `headless: false` inside Xvfb",
      "Switch from HTTP/2 to HTTP/1.1"
    ],
    "answerIndex": 1,
    "explanation": "Raising the container's overall cgroup RAM limit from `4Gi` to `16Gi` leaves `/dev/shm` stuck at `64MB`! Mounting `emptyDir: { medium: Memory, sizeLimit: 2Gi }` on `/dev/shm` directly lifts the POSIX shared-memory ceiling."
  },
  {
    "id": "pw-10-q2",
    "question": "Why does an LPT (Longest-Processing-Time-First) shard planner require a **deterministic secondary tie-breaker** (`(-estimated_ms, nodeid)`) when two test files have the exact same historical duration (`5,000ms`)?",
    "options": [
      "Heap data structures crash on duplicate integers",
      "Each CI shard pod (`1/8` .. `8/8`) computes the partition **independently without talking to other pods**! Without a deterministic `nodeid` tie-breaker, filesystem walk order differences across pods could assign `test_a.py` to Pod 1 on Pod 1 and to Pod 2 on Pod 2—running `test_b.py` twice and **skipping `test_a.py` completely**!",
      "Python's `sorted()` is unstable",
      "Blob reports require alphabetical execution timestamps"
    ],
    "answerIndex": 1,
    "explanation": "Decentralized sharding relies on pure mathematical determinism: given the same `timings.json` artifact, every isolated pod must compute the exact same partition bijection so `Union(S_1..S_M) = AllTests` and `S_i ∩ S_j = ∅`."
  },
  {
    "id": "pw-10-q3",
    "question": "What happens if you run a Playwright Docker container WITHOUT `--init` (or `tini`) across a long shard spawning hundreds of browser/renderer subprocesses?",
    "options": [
      "Fonts fail to load",
      "Orphaned child processes re-parented to PID 1 are never `wait()`-reaped when they exit, accumulating `<defunct>` zombie entries in the container process table until `pids.max` is exhausted (`Resource temporarily unavailable` / `EAGAIN`)",
      "Network routes stop intercepting HTTPS",
      "Blob reports cannot be compressed"
    ],
    "answerIndex": 1,
    "explanation": "On Linux, when an intermediate process exits, orphaned grandchildren are re-parented to PID 1 inside the PID namespace. Passing `--init` runs a tiny `tini` reaper as PID 1 so exited browser helper processes never leak PID slots."
  }
]
```
