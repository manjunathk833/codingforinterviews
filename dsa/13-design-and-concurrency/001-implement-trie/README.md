# 001. Implement Trie (Prefix Tree)

- **Difficulty**: Medium
- **Pattern**: Design & Concurrency / Tree
- **LeetCode Link**: [LeetCode #208 - Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/)

---

## Problem Statement
A **trie** (pronounced as "try") or **prefix tree** is a tree data structure used to efficiently store and retrieve keys in a dataset of strings.
Implement the `Trie` class:
- `Trie()` Initializes the trie object.
- `void insert(String word)` Inserts the string `word` into the trie.
- `boolean search(String word)` Returns `true` if the string `word` is in the trie, and `false` otherwise.
- `boolean startsWith(String prefix)` Returns `true` if there is a previously inserted string `word` that has the prefix `prefix`.

---

## Target Complexities
- **Optimal Time Complexity**: $O(L)$ for `insert`, `search`, and `startsWith` where $L$ is word length.
- **Optimal Space Complexity**: $O(\Sigma \times L \times N)$
