---
trigger: model_decision
description: "Load whenever modifying backend code, SQLite schemas, DSA/Workbench runners, or UI files to run 3-layer post-implementation verification and smart conditional CI."
---
# Post-Implementation 3-Layer Verification & Smart CI Gate

After user-approved production edits are applied, verify all 3 layers before declaring completion (directly or via `dry_run_agent` to keep logs out of main context):

1. **Layer 1 — Service Contracts**: Hit modified `/api/*` endpoints (`http://127.0.0.1:8090` or `hub.server.dispatch_request`) checking status codes, `ETag`/CORS headers, and JSON schemas.
2. **Layer 2 — SQLite & Disk State**: Confirm `hub/hub.db` (`kb_chapters`, `kb_fts`, `roadmap_items`, `workbench_runs`) has zero leaked test fixtures and modified disk files keep clean permissions/checksums.
3. **Layer 3 — Live Browser / Headless Playwright**: Verify rendered DOM, interactive buttons, Dark Ink contrast (zero hardcoded light hexes), and `0` console/page errors on `http://127.0.0.1:8090`.

## Smart Conditional Regression Gate
- **Targeted Iteration**: Run `python3 -m unittest hub.tests.test_hub_phase1.TestHubAndArchitectureCI.<test_name>` or `./run.sh test <slug>`.
- **Full `./run.sh ci` (5 Stages)**: Run when core infra (`hub/server.py`, `hub/storage.py`, `tools/runner.py`) changes or before committing/opening a PR.
