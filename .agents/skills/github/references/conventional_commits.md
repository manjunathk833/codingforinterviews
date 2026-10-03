# Conventional Commits Guide for Antigravity

This repository strictly adheres to **[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)**.

---

## 1. Structure

```text
<type>(<scope>): <short imperative summary>

[optional body explaining context, Big-O analysis, design decisions]

[optional footer referencing scores, issue IDs, PRs]
```

---

## 2. Commit Types

| Type | When to Use | Example |
| :--- | :--- | :--- |
| **`feat`** | Solved a DSA problem or added framework feature | `feat(dsa/002-valid-anagram): solve Valid Anagram in Java & Python` |
| **`fix`** | Bug fix in solution logic or test runner | `fix(runner): resolve Windows path resolution in runner.py` |
| **`docs`** | Updates to documentation or curriculum guides | `docs(curriculum): add Sliding Window pattern notes` |
| **`refactor`** | Optimization (e.g. $O(N^2) \to O(N)$) without changing output | `refactor(dsa/001-two-sum): replace brute force with single-pass hash map` |
| **`test`** | Additional test edge cases or assertions | `test(dsa/003-3sum): add negative numbers and duplicate triplets test` |
| **`chore`** | Maintenance, gitignore, build tooling | `chore(security): upgrade .gitignore with secret patterns` |

---

## 3. Scopes

- `dsa/<pattern-slug>` (e.g. `dsa/001-two-sum`, `dsa/arrays-and-hashing`)
- `frameworks/<module>` (e.g. `frameworks/restassured`, `frameworks/playwright`)
- `tools` (e.g. `tools/runner`, `tools/tracker`)
- `security` (e.g. `security/audit`)

---

## 4. Full DSA Problem Commit Example

```text
feat(dsa/001-two-sum): complete Two Sum in Java and Python (Score: 93/100)

- Java: O(N) Time, O(N) Space via single-pass HashMap
- Python: O(N) Time, O(N) Space via dict enumerate()
- Handled edge cases: negative numbers, duplicate values, zero targets
- Verified with native runner: ./run.sh test 001-two-sum

Interviewer-Score: 93/100
Status: Passed
```
