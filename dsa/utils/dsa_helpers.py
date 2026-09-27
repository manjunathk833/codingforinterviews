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
