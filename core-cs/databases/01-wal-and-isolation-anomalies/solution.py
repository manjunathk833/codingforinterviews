#!/usr/bin/env python3
"""
Databases Lab 01: Bounded WAL Ring-Buffer & Optimistic Concurrency Control (OCC).
"""

from collections import deque
from typing import Dict, Any, List


class BoundedWalRingBuffer:
    """Simulates an on-disk SQLite WAL ring-buffer with strict FIFO eviction cap."""

    def __init__(self, max_capacity: int):
        self.max_capacity = max_capacity
        self.queue = deque()
        self.evicted_count = 0

    def append_event(self, event_id: str, payload: str) -> None:
        if len(self.queue) >= self.max_capacity:
            self.queue.popleft()
            self.evicted_count += 1
        self.queue.append({"event_id": event_id, "payload": payload})

    def drain_batch(self, batch_size: int) -> List[Dict[str, str]]:
        batch = []
        while self.queue and len(batch) < batch_size:
            batch.append(self.queue.popleft())
        return batch


class OptimisticVersionStore:
    """Prevents Lost Update anomalies using Compare-And-Swap (CAS) version numbers."""

    def __init__(self):
        self.rows: Dict[str, Dict[str, Any]] = {}

    def put_initial(self, key: str, value: Any) -> int:
        self.rows[key] = {"value": value, "version": 1}
        return 1

    def read(self, key: str) -> Dict[str, Any]:
        return dict(self.rows[key])

    def compare_and_swap(self, key: str, expected_version: int, new_value: Any) -> bool:
        current = self.rows.get(key)
        if not current or current["version"] != expected_version:
            return False
        current["value"] = new_value
        current["version"] += 1
        return True


class Solution:
    def verify_wal_and_occ(self) -> Dict[str, Any]:
        wal = BoundedWalRingBuffer(max_capacity=3)
        for i in range(1, 6):
            wal.append_event(f"evt_{i}", f"data_{i}")

        # Since max_capacity=3 and 5 events were written, evt_1 and evt_2 were evicted
        remaining = wal.drain_batch(10)

        store = OptimisticVersionStore()
        v1 = store.put_initial("seat_1A", "AVAILABLE")

        # Worker A and Worker B both read version 1 simultaneously
        worker_a_ok = store.compare_and_swap("seat_1A", expected_version=v1, new_value="BOOKED_BY_A")
        worker_b_ok = store.compare_and_swap("seat_1A", expected_version=v1, new_value="BOOKED_BY_B")

        return {
            "wal_evicted": wal.evicted_count,
            "wal_retained_ids": [e["event_id"] for e in remaining],
            "worker_a_committed": worker_a_ok,
            "worker_b_committed": worker_b_ok,
            "final_row": store.read("seat_1A"),
        }


if __name__ == "__main__":
    sol = Solution()
    res = sol.verify_wal_and_occ()

    assert res["wal_evicted"] == 2, f"Expected 2 FIFO evictions, got {res}"
    assert res["wal_retained_ids"] == ["evt_3", "evt_4", "evt_5"]
    assert res["worker_a_committed"] is True
    assert res["worker_b_committed"] is False, "Worker B stale version must be rejected by OCC!"
    assert res["final_row"] == {"value": "BOOKED_BY_A", "version": 2}

    print("All 3 Python Database WAL Ring-Buffer & OCC Isolation test cases passed!")

