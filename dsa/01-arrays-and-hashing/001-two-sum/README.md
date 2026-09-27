# 001. Two Sum

- **Difficulty**: Easy
- **Pattern**: Arrays & Hashing
- **LeetCode Link**: [LeetCode #1 - Two Sum](https://leetcode.com/problems/two-sum/)

---

## Problem Statement

Given an array of integers `nums` and an integer `target`, return *indices of the two numbers such that they add up to `target`*.

You may assume that each input would have **exactly one solution**, and you may not use the *same* element twice.

You can return the answer in any order.

---

## Examples

### Example 1:
```text
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

### Example 2:
```text
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

### Example 3:
```text
Input: nums = [3,3], target = 6
Output: [0,1]
```

---

## Constraints
- $2 \le \text{nums.length} \le 10^4$
- $-10^9 \le \text{nums}[i] \le 10^9$
- $-10^9 \le \text{target} \le 10^9$
- **Only one valid answer exists.**

---

## Target Complexities
- **Optimal Time Complexity**: $O(N)$
- **Optimal Space Complexity**: $O(N)$

---

## Follow-up Interview Questions
1. What if the input array is already sorted? Can we solve it in $O(1)$ auxiliary space?
2. What if there are duplicate elements and we need all unique pairs that sum up to target?
3. What if the array is too large to fit in memory?
