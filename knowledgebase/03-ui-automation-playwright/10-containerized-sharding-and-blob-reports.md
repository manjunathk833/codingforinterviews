---
slug: pw-10-containerized-sharding-and-blob-reports
course_id: 03-ui-automation-playwright
track: core-cs
volume: "03. Zero to Mastery: UI Automation (Playwright-Focused)"
module_number: 4
module_title: "Module 4: Forensics, Visual/a11y Gates & Sharded CI"
chapter_number: 10
level_tag: "Staff Platform Engineer"
title: "Containerized CI Sharding, `/dev/shm` OOM Physics & Blob Report Merging"
summary: "Running 2,000+ Playwright tests in <4 minutes across Kubernetes/GitHub shards without `/dev/shm` `TargetClosedError` crashes, unified via Blob report merging and flake budgets."
reading_time_minutes: 21
visualizer_id: pw-network-auth-sharding
lab_path: frameworks/sdet-system-design/02-ci-shard-bin-packer-and-tia
tags: ["ci-sharding", "docker-shm", "ipc-host", "blob-reporter", "merge-reports", "kubernetes-ci", "flake-budget"]
---

# Containerized CI Sharding, `/dev/shm` OOM Physics & Blob Report Merging

```json pretraining
[
  {
    "term": "Docker `/dev/shm` 64MB Trap",
    "formula": "Default Container `/dev/shm` == 64MB -> Chromium Renderer `SIGBUS` / `Target closed`!",
    "meaning": "Docker defaults POSIX shared memory (`/dev/shm`) to a tiny 64MB tmpfs; Chromium uses `/dev/shm` for raster tile buffers, crashing mid-test unless `--ipc=host` or `--shm-size=2g` is set!"
  },
  {
    "term": "Horizontal Shard Wall-Clock Math",
    "formula": "T_wall = T_boot + ceil(N_tests / (M_shards * W_workers)) * t_avg + T_tail_skew",
    "meaning": "Splitting 1,600 tests across `M = 8` machines (`--shard=1/8`..`8/8`) with `W = 4` workers per machine (`32` concurrent browsers) collapses a 48m serial run under 3 minutes."
  },
  {
    "term": "Blob Reporter Fan-In (`merge-reports`)",
    "formula": "Shard 1..M (`blob-1.zip`..`blob-M.zip`) -> `merge-reports` -> 1 Unified HTML/JSON",
    "meaning": "Instead of hunting through 16 disconnected CI job artifacts, `reporter: 'blob'` emits raw protocol events merged post-fan-in into one searchable HTML + Trace dashboard."
  },
  {
    "term": "Worker-CPU Contention Knee",
    "formula": "Optimal Workers/Pod ≈ 0.5x to 1.0x vCPUs (e.g., 4 vCPU Pod -> 2–4 Browser Workers)",
    "meaning": "Scheduling 16 headless Chromium workers onto a 2-vCPU Kubernetes pod starves `requestAnimationFrame` and inflates timeout flakes—scale horizontally via shards instead!"
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

## Part I — First-Principles Mental Model: Horizontal CI Scaling & Container Kernel Physics

At **2,000+ E2E tests**, vertical scaling on a single VM hits a hard physical wall: a Chromium instance actively rendering modern React SPAs consumes `~0.7–1.2` vCPU cores during navigation and hydration. Packing 24 workers onto an 8-vCPU runner causes **CPU run-queue starvation**—JavaScript hydration stretches from `150ms` to `6,200ms`, exceeding 5-second assertion budgets and creating phantom CI flakiness!

A **Staff Platform Engineer** scales horizontally across **stateless containerized shards** governed by four architectural pillars:

### 1. Container Kernel Hygiene (`--ipc=host` / `/dev/shm` + `init` Zombie Reaping)
- **Shared Memory (`/dev/shm`)**: Chromium's multi-process sandbox shares composited tiles via `/dev/shm`. Always run Docker with `--ipc=host` or `--shm-size=2g` (and K8s pods with `medium: Memory` volume on `/dev/shm`). Avoid relying solely on `--disable-dev-shm-usage` unless constrained, because redirecting IPC buffers to `/tmp` overlayfs adds measurable disk I/O latency!
- **PID 1 Zombie Process Reaping (`--init` / `tini`)**: Browser tests spawn and kill hundreds of renderer/utility child subprocesses. If PID 1 inside your container doesn't call `waitpid()`, defunct `<zombie>` processes accumulate and exhaust the container PID table (`pids.max`)! Always pass `docker run --init`.

### 2. Deterministic LPT Bin-Packed Sharding (`1/M .. M/M`)
Naive alphabetical file splitting puts all eight 90-second checkout files onto Shard 3 (`12m` wall time) while Shard 7 finishes light login tests in `1m 20s` (**10m 40s tail skew!**). Historical duration bin-packing (**Longest Processing Time First — LPT**) balances every shard within $\pm 8\text{s}$ of the mean!

### 3. Fan-Out Shards $\to$ Fan-In Blob Report Merging
Each CI matrix shard emits a compact binary/zip event archive (`blob-report/report-shard-k.zip`). A lightweight `20s` fan-in job downloads all $M$ blobs and runs `playwright merge-reports --reporter=html,junit ./all-blob-reports`, producing **one unified HTML report** with embedded failure `trace.zip` viewers!

```mermaid
flowchart LR
  Plan["CI Matrix Fan-Out (Pinned Docker + 2GB /dev/shm)"] -->|Shard 1/4| S1["Pod 1 (4 vCPU, 3 Workers) -> blob-1.zip"]
  Plan -->|Shard 2/4| S2["Pod 2 (4 vCPU, 3 Workers) -> blob-2.zip"]
  Plan -->|Shard 3..4| S3["Pod 3..4 -> blob-3..4.zip"]
  S1 & S2 & S3 -->|Fan-In Job (15s)| Merge["merge-reports -> Unified HTML + Flake Ledger"]
```

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
    "Pins `mcr.microsoft.com/playwright:v1.50.0-noble` with `--init --ipc=host` (or 2Gi RAM `/dev/shm` in K8s)",
    "Caps concurrency at `0.75 * vCPU` per pod and scales horizontally via LPT duration-balanced shards",
    "Merges all shard blobs into 1 unified HTML + JUnit report and enforces a `<0.5%` rolling 7-day flake budget"
  ]
}
```

---

## Part II — Container & CI Sharding Reference Architecture

Explore the **`pw-network-auth-sharding`** simulator to tune shard count $M$, worker-per-pod concurrency $W$, `/dev/shm` allocation, and LPT bin-packing skew.

| Infrastructure Parameter | Anti-Pattern / Dangerous Default | Staff Production Standard | Why It Matters |
| :--- | :--- | :--- | :--- |
| **Container Base Image** | `:latest` floating tag or unpinned `ubuntu` + runtime `playwright install` | Exact digest/version `mcr.microsoft.com/playwright:v1.50.0-noble` | Saves `90s` browser download per shard & locks exact FreeType/Chromium binaries. |
| **Shared Memory (`/dev/shm`)** | Docker/K8s `64MB` default | `--ipc=host` or `--shm-size=2g` (K8s `Memory` `emptyDir: 2Gi`) | Prevents silent Chromium renderer `SIGBUS` / `Page crashed` deaths. |
| **PID 1 Process Reaping** | Bare `python -m pytest` as PID 1 | `docker run --init` (or `shareProcessNamespace` / `tini`) | Reaps orphaned headless renderer zombie processes cleanly. |
| **Workers per 4-vCPU Pod** | `workers = 12` (CPU thrashing!) | `workers = 3` or `4` ($\le 1\text{ worker / vCPU}$) | Keeps `rAF` & React hydration latencies deterministic under load. |

---

## Part III — Production Implementation Blueprints (Python 3 & Java 17)

### Python 3 Blueprint: Deterministic LPT Duration Shard Planner (`pytest` Collection Plugin)
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

    # Deterministic tie-break by nodeid so every independent CI pod computes the EXACT same partition!
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

### Java 17 Blueprint: Containerized `/dev/shm` Health Preflight & Shard Partition Filter
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
> **Staff Interview Gotcha — Splitting `module`/`class`-Scoped Fixtures Across Naive Round-Robin Shards**:
> Look closely at the last line of both LPT blueprints above:
> 1. **Unit of Sharding**: If 12 tests inside `TestHeavyCheckoutClass` share an expensive `class`/`module`-scoped dataset seed (`6s`), round-robin sharding *individual test methods* across 8 shards forces **all 8 shards** to pay that `6s` class setup (`8 * 6s = 48s` duplicated setup)! Bin-pack at the **file / test-class granularity** (or group by module after LPT assignment) so shared module fixtures execute on only one shard!
> 2. **Zero-Flake Quarantine SLA**: A Staff CI gate tracks `FLAKY` (failed attempt 1, passed retry 2) separately from `PASSED`. Any test exceeding a **1% rolling 7-day flake rate** automatically opens an owner-assigned Jira/GitHub issue and moves to a non-blocking quarantine lane with a **72-hour fix-or-delete SLA** so PR merge velocity never degrades!

---

## Part IV — Scenario Retrieval-Practice Mastery Gate

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
