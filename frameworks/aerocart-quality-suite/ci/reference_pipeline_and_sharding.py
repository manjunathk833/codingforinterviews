"""Reference Solution — Capstone Layer 4/4: LPT CI Matrix Sharding, Flaky Quarantine & Release Gate."""
import heapq
from typing import Any, Dict, List, Tuple


def plan_lpt_shards(specs: List[Tuple[str, float]], num_shards: int) -> List[List[str]]:
    if num_shards <= 0:
        raise ValueError("num_shards must be >= 1")
    buckets: List[List[str]] = [[] for _ in range(num_shards)]
    heap: List[Tuple[float, int]] = [(0.0, idx) for idx in range(num_shards)]
    heapq.heapify(heap)

    ordered = sorted(specs, key=lambda item: (-float(item[1]), item[0]))
    for spec_name, dur in ordered:
        load, shard_idx = heapq.heappop(heap)
        buckets[shard_idx].append(spec_name)
        heapq.heappush(heap, (round(load + float(dur), 6), shard_idx))
    return buckets


def evaluate_ci_gate(results: List[Dict[str, Any]], max_flake_rate: float = 0.05) -> Dict[str, Any]:
    blocking: List[str] = []
    flakes: List[str] = []
    total = len(results)
    for rec in results:
        tid = str(rec["id"])
        attempts = [bool(x) for x in rec.get("attempts", [])]
        if not attempts or not any(attempts):
            blocking.append(tid)
        elif not attempts[0] and any(attempts[1:]):
            flakes.append(tid)
    flake_rate = round((len(flakes) / total), 4) if total > 0 else 0.0
    approved = (len(blocking) == 0) and (flake_rate <= max_flake_rate)
    return {
        "releaseApproved": approved,
        "blockingFailures": blocking,
        "quarantinedFlakes": flakes,
        "flakeRate": flake_rate,
    }
