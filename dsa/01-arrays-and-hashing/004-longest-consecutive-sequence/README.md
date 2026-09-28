# 004. Longest Consecutive Sequence

- **Difficulty**: Medium
- **Pattern**: Arrays & Hashing
- **LeetCode Link**: [LeetCode #128 - Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/)

---

## Problem Statement
Given an unsorted array of integers `nums`, return the length of the *longest consecutive elements sequence*.
You must write an algorithm that runs in $O(N)$ time.

---

## Examples
### Example 1:
```text
Input: nums = [100,4,200,1,3,2]
Output: 4
Explanation: The longest consecutive elements sequence is [1, 2, 3, 4]. Its length is 4.
```

### Example 2:
```text
Input: nums = [0,3,7,2,5,8,4,6,0,1]
Output: 9
```

---

## Constraints
- $0 \le \text{nums.length} \le 10^5$
- $-10^9 \le \text{nums}[i] \le 10^9$

---

## Target Complexities
- **Optimal Time Complexity**: $O(N)$
- **Optimal Space Complexity**: $O(N)$

---

## Follow-up Interview Questions
1. Why does checking `!set.contains(num - 1)` ensure that the overall runtime remains $O(N)$?
2. What if numbers arrive as a data stream? Can we use Disjoint Set Union (Union-Find) to maintain connected components?
