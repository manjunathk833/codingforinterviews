---
name: token-lean-workflow
description: >-
  Token-lean navigation, targeted testing, and Carbon-Hydrogen execution runbook
  for The Hub of Learning. Activate when planning or executing multi-file edits
  across hub/, dsa/, or frameworks/.
---

# Token-Lean & Carbon–Hydrogen Execution Workflow

1. **Targeted Reads Over Full-File Reads**:
   - Locate exact line numbers with `grep -n` first, then call `read_file` with `StartLine` and `EndLine` (`<= 150` lines).
   - Never read static JSON catalogs (`hub/data/*.json`) directly into context; inspect schemas via 5-line Python one-liners when needed.
2. **Modular Static Assets (`hub/static/`)**:
   - HTML layout: `hub/static/index.html`
   - Theme & tokens: `hub/static/css/theme.css`
   - JS controllers: `hub/static/js/data-seeds.js`, `core.js`, `textbook.js`, `coding-studio.js`, `workbench.js`
   - Edit only the specific module file; `hub/server.py` serves `/static/*` directly and dynamically composes `GET /` in memory.
3. **Fast Iteration Before Full CI**:
   - Run single unittest methods during iteration:
     `python3 -m unittest hub.tests.test_hub_phase1.TestHubAndArchitectureCI.test_23_wave1_coding_dojo_catalog_coach_warmups_and_dark_ui`
   - Delegate full `./run.sh ci` + Playwright checks to `dry_run_agent` when keeping main conversation context lean.
