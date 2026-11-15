---
trigger: always_on
---
# Carbon–Hydrogen Anti-Corner-Cutting Guardrails

When executing plans (especially during Hydrogen execution phases), strictly uphold these quality invariants — **fail loudly rather than faking green tests so Orchestrator escalates back to Carbon**:

1. **Zero No-Op / Toy Test Harnesses**:
   - Unimplemented starter contracts (`pass` / `NotImplementedError` / empty Java stubs) MUST fail verification with `0` correctness points (`score == 0`), never pass with `0` assertions.
   - Every DSA problem must carry **$\ge 5$ structured test cases** (happy path, empty/minimal, boundary/negative/duplicate) and every Workbench build must enforce **$\ge 4$ black-box checkpoints**.
2. **Zero Unintended Spoilers**:
   - Blank starters (`solution.py`, `Solution.java`, Workbench contracts) must contain **only** imports, class/method signatures, neutral docstrings, and `pass` / `raise NotImplementedError` — never pre-print hints, pattern names, target Big-O, or step outlines until the user clicks `Help Me Start` / `Hints`.
3. **Strict CSS Token Hygiene**:
   - Use defined `:root` tokens (`--accent-terra`, `--accent-terra-soft`, `--accent-sage`, `--accent-blue`, `--bg-card`, `--bg-subtle`, `--ink-primary`, `--border-warm`); verify token existence before use.
