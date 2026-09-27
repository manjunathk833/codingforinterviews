# 002. Valid Anagram

- **Difficulty**: Easy
- **Pattern**: Arrays & Hashing
- **LeetCode Link**: [LeetCode #242 - Valid Anagram](https://leetcode.com/problems/valid-anagram/)

---

## Problem Statement

Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.

An **Anagram** is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

---

## Examples

### Example 1:
```text
Input: s = "anagram", t = "nagaram"
Output: true
```

### Example 2:
```text
Input: s = "rat", t = "car"
Output: false
```

---

## Constraints
- $1 \le \text{s.length, t.length} \le 5 \times 10^4$
- `s` and `t` consist of lowercase English letters.

---

## Target Complexities
- **Optimal Time Complexity**: $O(N)$
- **Optimal Space Complexity**: $O(1)$ (using a fixed-size 26-element frequency bucket or $O(K)$ where $K$ is distinct characters)

---

## Follow-up Interview Questions
1. What if the inputs contain Unicode characters? How would you adapt your solution?
2. How does sorting approach compare to hash table / array counting approach in terms of memory vs speed?
