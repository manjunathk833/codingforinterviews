---
name: progress
description: Analyze Master Sheet and Framework preparation metrics, readiness status, and recommend the next problems or patterns to tackle.
---

# MAANG Preparation Progress Agent

When invoked (via `/progress` or when asked about readiness, metrics, or what to solve next):

1. **Run Tracker Summary**:
   - Execute:
     `python3 tools/tracker.py summary`
   - Read `dsa/MASTER_SHEET.md` and `frameworks/MASTER_FRAMEWORKS.md`.

2. **Report Metrics**:
   - Total questions tracked, solved in Java, solved in Python, dual-stack completed, and interviewer-passed ($\ge 80$).
   - Breakdown across difficulty (Easy / Medium / Hard).
   - Breakdown across algorithmic patterns.

3. **Provide Targeted Recommendation**:
   - Identify weak or underrepresented topics.
   - Recommend the next 2-3 logical problems to tackle to maximize learning continuity (e.g. progressing from Two Sum -> Valid Anagram -> Group Anagrams -> Top K Frequent).
