# 003. Group Anagrams

- **Difficulty**: Medium
- **Pattern**: Arrays & Hashing
- **LeetCode Link**: [LeetCode #49 - Group Anagrams](https://leetcode.com/problems/group-anagrams/)

---

## Problem Statement

Given an array of strings `strs`, group the **anagrams** together. You can return the answer in **any order**.

---

## Examples

### Example 1:
```text
Input: strs = ["eat","tea","tan","ate","nat","bat"]
Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
```

### Example 2:
```text
Input: strs = [""]
Output: [[""]]
```

### Example 3:
```text
Input: strs = ["a"]
Output: [["a"]]
```

---

## Constraints
- $1 \le \text{strs.length} \le 10^4$
- $0 \le \text{strs}[i].\text{length} \le 100$
- `strs[i]` consists of lowercase English letters.

---

## Target Complexities
- **Optimal Time Complexity**: $O(M \times N)$ or $O(M \times N \log N)$ where $M$ is number of strings, $N$ is max string length.
- **Optimal Space Complexity**: $O(M \times N)$

---

## Follow-up Interview Questions
1. How does character frequency tuple keying compare to sorting each string in terms of time complexity when strings are very long?
2. What if strings are millions of characters long and cannot fit in memory at once?
