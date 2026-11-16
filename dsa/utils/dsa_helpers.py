"""Shared Data Structure Helpers for Python DSA Problems (ListNode, TreeNode, etc.)"""
from typing import Optional, List
from collections import deque


class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    @classmethod
    def from_list(cls, arr: list) -> Optional['ListNode']:
        if not arr:
            return None
        dummy = cls(0)
        curr = dummy
        for v in arr:
            curr.next = cls(v)
            curr = curr.next
        return dummy.next

    def to_list(self) -> list:
        res = []
        curr = self
        while curr:
            res.append(curr.val)
            curr = curr.next
        return res

    def __repr__(self) -> str:
        return " -> ".join(map(str, self.to_list()))


class TreeNode:
    def __init__(self, val: int = 0, left: Optional['TreeNode'] = None, right: Optional['TreeNode'] = None):
        self.val = val
        self.left = left
        self.right = right

    @classmethod
    def from_list(cls, values: List[Optional[int]]) -> Optional['TreeNode']:
        if not values or values[0] is None:
            return None
        root = cls(values[0])
        queue = deque([root])
        i = 1
        while queue and i < len(values):
            node = queue.popleft()
            if i < len(values) and values[i] is not None:
                node.left = cls(values[i])
                queue.append(node.left)
            i += 1
            if i < len(values) and values[i] is not None:
                node.right = cls(values[i])
                queue.append(node.right)
            i += 1
        return root

    def to_list(self) -> List[Optional[int]]:
        res = []
        queue = deque([self])
        while queue:
            node = queue.popleft()
            if node:
                res.append(node.val)
                queue.append(node.left)
                queue.append(node.right)
            else:
                res.append(None)
        while res and res[-1] is None:
            res.pop()
        return res


class RandomNode:
    """Node for Copy List with Random Pointer (#40): [[val, random_index_or_None], ...]."""

    def __init__(self, x: int, next: Optional['RandomNode'] = None, random: Optional['RandomNode'] = None):
        self.val = int(x)
        self.next = next
        self.random = random

    @classmethod
    def from_pairs(cls, pairs: list) -> Optional['RandomNode']:
        if not pairs:
            return None
        nodes = [cls(p[0]) for p in pairs]
        for idx, node in enumerate(nodes):
            if idx + 1 < len(nodes):
                node.next = nodes[idx + 1]
            r_idx = pairs[idx][1]
            if r_idx is not None and 0 <= r_idx < len(nodes):
                node.random = nodes[r_idx]
        return nodes[0]

    def to_pairs(self) -> list:
        nodes = []
        idx_map = {}
        curr = self
        while curr:
            idx_map[id(curr)] = len(nodes)
            nodes.append(curr)
            curr = curr.next
        return [[n.val, idx_map.get(id(n.random)) if n.random is not None else None] for n in nodes]


class GraphNode:
    """Node for Clone Graph (#77): 1-indexed adjacency list [[2,4],[1,3],...]."""

    def __init__(self, val: int = 0, neighbors: Optional[List['GraphNode']] = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

    @classmethod
    def from_adj_list(cls, adj: list) -> Optional['GraphNode']:
        if not adj:
            return None
        nodes = [cls(i + 1) for i in range(len(adj))]
        for i, nbrs in enumerate(adj):
            nodes[i].neighbors = [nodes[j - 1] for j in nbrs]
        return nodes[0]

    def to_adj_list(self) -> list:
        visited = {}
        queue = deque([self])
        visited[self.val] = self
        while queue:
            curr = queue.popleft()
            for nb in curr.neighbors:
                if nb.val not in visited:
                    visited[nb.val] = nb
                    queue.append(nb)
        if not visited:
            return []
        max_v = max(visited.keys())
        return [[nb.val for nb in visited[i].neighbors] if i in visited else [] for i in range(1, max_v + 1)]

