---
trigger: always_on
---

# Mandatory Post-Implementation 3-Layer Verification & Smart CI Gate

After the user approves a plan and production edits are applied, you MUST verify the live system across all 3 layers (directly or via `dry_run_agent`) before declaring the task complete:

## 1. The 3-Layer Post-Implementation Verification Checklist

1. **Layer 1 — Service Requests & Responses**:
   - Execute real HTTP requests (`GET`, `POST`, `PUT`) against `http://127.0.0.1:8090` (or `hub.server.dispatch_request`) for every new or modified endpoint.
   - Verify HTTP status codes (`200`, `400`, `404`, `409`), headers (`ETag`, `Content-Type`, CORS), and JSON response schemas.
2. **Layer 2 — Database & Filesystem State**:
   - Query the production SQLite database (`hub/hub.db`) and `FTS5` virtual tables (`kb_search_fts`) to confirm rows, indexes, and foreign keys are populated cleanly and zero test-fixture artifacts leaked into production tables.
   - For filesystem operations (`dsa/`, `frameworks/`, `knowledgebase/`, `mock-interviews/`), verify `sha256` checksums, file permissions (`chmod +x` on local runner scripts), and Markdown/YAML integrity.
3. **Layer 3 — Live Browser Verification (`http://127.0.0.1:8090`)**:
   - Ensure `./run.sh hub` is running on `http://127.0.0.1:8090` and verify the live UI in the browser:
     - Confirm all views, chapters, visualizers, newsfeed cards, and interactive controls render cleanly with zero console errors or broken links.

---

## 2. Smart Conditional Regression Gate

- **Fast Targeted Verification During Iteration**:
  - Because automated GitHub Actions CI (`.github/workflows/ci.yml`) and local `./run.sh ci` are established, **do not run the full 4-stage regression suite on every isolated edit**:
    - *Knowledgebase / Newsfeed / Hub API changes* $\to$ Run `python3 hub/tests/test_hub_phase1.py`.
    - *Single DSA problem changes* $\to$ Run `./run.sh test <problem-slug>`.
    - *Single Framework Lab changes* $\to$ Run that specific lab's local deterministic test script (`verify.sh` / `pytest` / `solution.py`).
- **Full `./run.sh ci` Gate When Required**:
  - Run the complete 4-stage `./run.sh ci` pipeline **only** when:
    1. Shared core infrastructure (`hub/server.py`, `hub/storage.py`, `tools/runner.py`) is modified, OR
    2. Immediately before committing/pushing to `develop` and opening a Pull Request to `main`.
