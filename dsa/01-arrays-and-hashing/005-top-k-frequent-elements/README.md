# 005. Top K Frequent Elements

- **Difficulty**: Medium
- **Pattern**: Arrays & Hashing / Bucket Sort
- **LeetCode Link**: [LeetCode #347 - Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/)

---

## Problem Statement
Given an integer array `nums` and an integer `k`, return the `k` *most frequent elements*. You may return the answer in **any order**.

---

## Examples
### Example 1:
```text
Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
```

### Example 2:
```text
Input: nums = [1], k = 1
Output: [1]
```

---

## Target Complexities
- **Optimal Time Complexity**: $O(N)$ using Bucket Sort (or $O(N \log K)$ using Min-Heap)
- **Optimal Space Complexity**: $O(N)$
