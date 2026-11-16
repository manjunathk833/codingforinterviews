"""Problem #5: Top K Frequent Elements (Medium)"""
from typing import List, Optional, Dict
from collections import Counter, defaultdict, deque, OrderedDict
from bisect import bisect_left
import heapq
import threading
from utils.dsa_helpers import ListNode, TreeNode, RandomNode, GraphNode


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        raise NotImplementedError("Write your solution here")


if __name__ == "__main__":
    # Run test cases & Code Coach via Coding Studio (`▶ Run & Coach`) or `./run.sh test top-k-frequent-elements`
    print("Starter ready for #5 Top K Frequent Elements.")
