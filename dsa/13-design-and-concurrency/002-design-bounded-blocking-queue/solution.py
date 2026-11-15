"""Problem #123: Design Bounded Blocking Queue (Medium)"""
from typing import List, Optional, Dict
from collections import Counter, defaultdict, deque, OrderedDict
from bisect import bisect_left
import heapq
import threading
from utils.dsa_helpers import ListNode, TreeNode, RandomNode, GraphNode


class BoundedBlockingQueue:
    def __init__(self, capacity: int):
        raise NotImplementedError("Write your solution here")
    def enqueue(self, element: int) -> None:
        raise NotImplementedError("Write your solution here")
    def dequeue(self) -> int:
        return 0
    def size(self) -> int:


if __name__ == "__main__":
    # Run test cases & Code Coach via Coding Studio (`▶ Run & Coach`) or `./run.sh test design-bounded-blocking-queue`
    print("Starter ready for #123 Design Bounded Blocking Queue.")
