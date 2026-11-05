# 🩹 AI Lab 02: Self-Healing UI Locators & AST Confidence Gate

**Domain:** Agentic UI Automation, DOM Similarity Scoring & AST Code Patching  
**Target Role:** Senior / Staff SDET & Test Infrastructure Architect  
**Interactive Visualizer:** `arch-playwright-vs-selenium` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

When a frontend developer renames a CSS class or updates `id="btn-book"` to `id="confirm-booking-cta"` during a sprint:
1. **Why Blind LLM / Fuzzy Matching is Dangerous**:
   If a self-healing wrapper blindly clicks whichever button is closest on the page, it might click **`"Cancel & Delete Account"`** instead of **`"Confirm Booking"`**, masking a P0 bug!
2. **Staff SDET Pattern — Weighted Multi-Signal DOM Fingerprint + Confidence Threshold ($\ge 0.75$)**:
   - Before a test fails, compare the cached **Baseline Element Fingerprint** (`role`, `aria_label`, `inner_text`, `tag`, `parent_form`) against candidate DOM elements using weighted semantic similarity:
     - `role` + `tag` match: `0.25`
     - `aria_label` / accessible name similarity: `0.35`
     - `inner_text` similarity: `0.25`
     - `parent_context` match: `0.15`
   - **Destructive Action Guard**: If a candidate element contains destructive keywords (`delete`, `cancel`, `remove`, `logout`) that were NOT in the baseline, immediately score `0.0`!
   - **Auto-Heal + AST Patch**: Only heal if `confidence >= 0.75` and emit a deterministic locator replacement diff for PR review.

---

## 🧪 2. Running Verification

```bash
./run.sh test 02-self-healing-locators-and-ast
```

