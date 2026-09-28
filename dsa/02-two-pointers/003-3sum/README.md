# 003. 3Sum

- **Difficulty**: Medium
- **Pattern**: Two Pointers / Sorting
- **LeetCode Link**: [LeetCode #15 - 3Sum](https://leetcode.com/problems/3sum/)

---

## Problem Statement
Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.
Notice that the solution set must **not contain duplicate triplets**.

---

## Examples
### Example 1:
```text
Input: nums = [-1,0,1,2,-1,-4]
Output: [[-1,-1,2],[-1,0,1]]
```

### Example 2:
```text
Input: nums = [0,1,1]
Output: []
```

---

## Target Complexities
- **Optimal Time Complexity**: $O(N^2)$
- **Optimal Space Complexity**: $O(1)$ or $O(N)$ depending on sort implementation
