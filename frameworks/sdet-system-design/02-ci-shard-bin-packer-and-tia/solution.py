#!/usr/bin/env python3
"""
SDET System Design Lab 02: LPT CI Shard Bin-Packer, AST Test Impact Analysis & Flake Quarantine.
"""

import heapq
from collections import deque
from typing import Dict, List, Set, Tuple


def lpt_bin_pack_shards(specs: List[Tuple[str, float]], num_shards: int) -> Tuple[List[List[str]], float]:
    """Assign longest specs first to the currently least-loaded CI shard (O(N log K))."""
    sorted_specs = sorted(specs, key=lambda x: (-x[1], x[0]))
    heap: List[Tuple[float, int]] = [(0.0, idx) for idx in range(num_shards)]
    heapq.heapify(heap)
    buckets: List[List[str]] = [[] for _ in range(num_shards)]

    for spec_name, duration_sec in sorted_specs:
        load, shard_idx = heapq.heappop(heap)
        buckets[shard_idx].append(spec_name)
        heapq.heappush(heap, (round(load + duration_sec, 4), shard_idx))

    makespan = max(load for load, _ in heap)
    return buckets, makespan


def round_robin_makespan(specs: List[Tuple[str, float]], num_shards: int) -> float:
    loads = [0.0] * num_shards
    for idx, (_, dur) in enumerate(sorted(specs, key=lambda x: x[0])):
        loads[idx % num_shards] += dur
    return max(loads)


def select_impacted_tests(
    changed_files: List[str],
    reverse_imports: Dict[str, List[str]],
    all_tests: Set[str],
) -> Set[str]:
    """Compute transitive closure over reverse import graph; trigger full run on root infra changes."""
    global_triggers = {"pyproject.toml", "conftest.py", ".github/workflows/ci.yml"}
    if any(f in global_triggers for f in changed_files):
        return set(all_tests)

    visited: Set[str] = set(changed_files)
    queue = deque(changed_files)
    impacted: Set[str] = set()

    while queue:
        curr = queue.popleft()
        if curr in all_tests:
            impacted.add(curr)
        for dependent in reverse_imports.get(curr, []):
            if dependent not in visited:
                visited.add(dependent)
                queue.append(dependent)
    return impacted


if __name__ == "__main__":
    suite_timings = [
        ("a_checkout_e2e.py", 180.0),
        ("b_payment_3ds_e2e.py", 170.0),
        ("c_refund_saga_e2e.py", 160.0),
        ("d_auth_smoke.py", 25.0),
        ("e_search_filter.py", 30.0),
        ("f_baggage_calc.py", 35.0),
        ("g_seat_lock.py", 40.0),
        ("h_loyalty_tier.py", 40.0),
    ]
    # Alphabetical round-robin on 3 shards puts a_checkout (180s) + d (25s) + g (40s) = 245s or skewed heavy collisions
    # Let's test skewed alphabetical list where heavy specs land every 3rd index:
    skewed_specs = [
        ("01_heavy_checkout.py", 180.0),
        ("02_fast_unit.py", 10.0),
        ("03_fast_lint.py", 10.0),
        ("04_heavy_payments.py", 175.0),
        ("05_fast_schema.py", 15.0),
        ("06_fast_util.py", 15.0),
        ("07_heavy_concierge.py", 165.0),
        ("08_medium_api.py", 45.0),
        ("09_medium_auth.py", 45.0),
    ]
    rr_max = round_robin_makespan(skewed_specs, 3)
    shards, lpt_max = lpt_bin_pack_shards(skewed_specs, 3)
    assert rr_max >= 500.0, f"Expected alphabetical skew >= 500s, got {rr_max}"
    assert lpt_max <= 235.0, f"Expected LPT makespan <= 235s, got {lpt_max}"
    assert sum(len(s) for s in shards) == len(skewed_specs)

    rev_graph = {
        "pricing/tax.py": ["checkout/cart.py"],
        "checkout/cart.py": ["tests/test_cart.py", "tests/test_checkout_e2e.py"],
        "concierge/rag.py": ["tests/test_concierge.py"],
    }
    all_suite = {"tests/test_cart.py", "tests/test_checkout_e2e.py", "tests/test_concierge.py"}
    selected = select_impacted_tests(["pricing/tax.py"], rev_graph, all_suite)
    assert selected == {"tests/test_cart.py", "tests/test_checkout_e2e.py"}
    assert select_impacted_tests(["conftest.py"], rev_graph, all_suite) == all_suite

    print("All 3 Python LPT CI Shard Bin-Packer & AST Test Impact Analysis test cases passed!")
