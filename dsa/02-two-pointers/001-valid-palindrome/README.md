# 001. Valid Palindrome

- **Difficulty**: Easy
- **Pattern**: Two Pointers
- **LeetCode Link**: [LeetCode #125 - Valid Palindrome](https://leetcode.com/problems/valid-palindrome/)

---

## Problem Statement

A phrase is a **palindrome** if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.

Given a string `s`, return `true` if it is a **palindrome**, or `false` otherwise.

---

## Examples

### Example 1:
```text
Input: s = "A man, a plan, a canal: Panama"
Output: true
Explanation: "amanaplanacanalpanama" is a palindrome.
```

### Example 2:
```text
Input: s = "race a car"
Output: false
Explanation: "raceacar" is not a palindrome.
```

### Example 3:
```text
Input: s = " "
Output: true
Explanation: s is an empty string "" after removing non-alphanumeric characters.
Since an empty string reads the same forward and backward, it is a palindrome.
```

---

## Constraints
- $1 \le \text{s.length} \le 2 \times 10^5$
- `s` consists only of printable ASCII characters.

---

## Target Complexities
- **Optimal Time Complexity**: $O(N)$
- **Optimal Space Complexity**: $O(1)$ (In-place two-pointer scan, no extra filtered string)
