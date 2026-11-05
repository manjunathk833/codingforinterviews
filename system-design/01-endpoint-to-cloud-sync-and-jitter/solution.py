#!/usr/bin/env python3
"""
System Design Lab 01: Endpoint-to-Cloud Sync, Full Jitter & Idempotent Ingestion.
"""

import random
from collections import Counter
from typing import Dict, Any, List


class Solution:
    def simulate_reconnection_storm(
        self,
        num_endpoints: int = 1000,
        attempt: int = 3,
        base_sec: int = 2,
        max_cap_sec: int = 60,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """
        Compare peak per-second connection burst between:
          1. Naive Exponential Backoff (no jitter): delay = min(cap, base * 2^attempt)
          2. Full Jitter Exponential Backoff: delay = random.randint(0, min(cap, base * 2^attempt))
        """
        rng = random.Random(seed)
        window = min(max_cap_sec, base_sec * (2 ** attempt))

        # 1. No Jitter: every single endpoint picks the exact same second
        naive_buckets = Counter(window for _ in range(num_endpoints))
        naive_peak_rps = max(naive_buckets.values())

        # 2. Full Jitter: endpoints spread uniformly across [0..window] seconds
        jitter_buckets = Counter(rng.randint(0, window) for _ in range(num_endpoints))
        jitter_peak_rps = max(jitter_buckets.values())

        reduction_pct = round((1.0 - (jitter_peak_rps / float(naive_peak_rps))) * 100.0, 1)

        return {
            "window_sec": window,
            "naive_peak_rps": naive_peak_rps,
            "jitter_peak_rps": jitter_peak_rps,
            "peak_reduction_pct": reduction_pct,
        }

    def ingest_idempotent_batches(self, batches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deduplicate retried telemetry batches using deterministic idempotency_key."""
        seen_keys = set()
        committed_events = 0
        duplicates_dropped = 0

        for b in batches:
            key = b["idempotency_key"]
            if key in seen_keys:
                duplicates_dropped += 1
            else:
                seen_keys.add(key)
                committed_events += len(b.get("events", []))

        return {
            "unique_batches": len(seen_keys),
            "committed_events": committed_events,
            "duplicates_dropped": duplicates_dropped,
        }


if __name__ == "__main__":
    sol = Solution()

    # 1. Verify Full Jitter flattens a 1,000-endpoint reconnection storm by > 85%
    storm = sol.simulate_reconnection_storm(num_endpoints=1000, attempt=3, base_sec=2, max_cap_sec=60)
    assert storm["naive_peak_rps"] == 1000
    assert storm["jitter_peak_rps"] < 120, f"Expected jitter peak < 120 RPS, got {storm}"
    assert storm["peak_reduction_pct"] > 85.0

    # 2. Verify Idempotent Batch Deduplication drops duplicate retries cleanly
    batches = [
        {"idempotency_key": "batch-uuid-01", "events": ["usb_mount", "file_open"]},
        {"idempotency_key": "batch-uuid-01", "events": ["usb_mount", "file_open"]},  # Timeout retry
        {"idempotency_key": "batch-uuid-02", "events": ["tls_handshake"]},
    ]
    ingest = sol.ingest_idempotent_batches(batches)
    assert ingest["unique_batches"] == 2
    assert ingest["committed_events"] == 3
    assert ingest["duplicates_dropped"] == 1

    print("All 2 Python Endpoint-to-Cloud Sync, Full Jitter & Idempotency test cases passed!")

