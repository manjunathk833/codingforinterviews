#!/usr/bin/env python3
"""
System Design Lab 02: Consistent Hashing Ring with Virtual Nodes (vnodes).
"""

import bisect
import zlib
from typing import List, Dict


class ConsistentHashRing:
    def __init__(self, nodes: List[str] = None, vnodes_per_node: int = 64):
        self.vnodes_per_node = vnodes_per_node
        self.ring_keys: List[int] = []
        self.ring_map: Dict[int, str] = {}
        for n in (nodes or []):
            self.add_node(n)

    def _hash(self, key: str) -> int:
        return zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF

    def add_node(self, node: str) -> None:
        for v in range(self.vnodes_per_node):
            h = self._hash(f"{node}#vnode{v}")
            if h not in self.ring_map:
                bisect.insort(self.ring_keys, h)
                self.ring_map[h] = node

    def remove_node(self, node: str) -> None:
        for v in range(self.vnodes_per_node):
            h = self._hash(f"{node}#vnode{v}")
            if h in self.ring_map and self.ring_map[h] == node:
                del self.ring_map[h]
                idx = bisect.bisect_left(self.ring_keys, h)
                if idx < len(self.ring_keys) and self.ring_keys[idx] == h:
                    self.ring_keys.pop(idx)

    def get_node(self, key: str) -> str:
        if not self.ring_keys:
            raise ValueError("Hash ring is empty")
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring_keys, h)
        if idx == len(self.ring_keys):
            idx = 0
        return self.ring_map[self.ring_keys[idx]]


if __name__ == "__main__":
    nodes = ["worker-node-1", "worker-node-2", "worker-node-3", "worker-node-4"]
    ring = ConsistentHashRing(nodes, vnodes_per_node=64)

    test_keys = [f"test_suite_{i}" for i in range(400)]
    initial_routing = {k: ring.get_node(k) for k in test_keys}

    # 1. Verify all 4 nodes receive a balanced share of suites
    counts = {n: 0 for n in nodes}
    for assigned in initial_routing.values():
        counts[assigned] += 1
    assert all(c > 40 for c in counts.values()), f"Expected balanced vnode distribution, got {counts}"

    # 2. Remove worker-node-4 and verify only ~25% of keys are remapped (vs ~75% in modulo hashing!)
    ring.remove_node("worker-node-4")
    after_routing = {k: ring.get_node(k) for k in test_keys}
    remapped = sum(1 for k in test_keys if initial_routing[k] != after_routing[k])
    remap_ratio = remapped / float(len(test_keys))

    assert 0.15 <= remap_ratio <= 0.38, f"Expected ~25% remapping on 1/4 node removal, got {remap_ratio:.2%}"
    # Every key that was NOT on worker-node-4 must stay on its exact original node!
    unchanged_survivors = all(
        initial_routing[k] == after_routing[k]
        for k in test_keys
        if initial_routing[k] != "worker-node-4"
    )
    assert unchanged_survivors is True, "Keys on healthy nodes must never move when a peer crashes!"

    print("All 2 Python Consistent Hashing Ring & Virtual Node Sharding test cases passed!")

