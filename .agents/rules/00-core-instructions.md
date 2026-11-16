---
trigger: always_on
---
# Core System Hygiene & Branch Governance

1. **Branch & Safety Gate**:
   - Never commit or push directly to `main`; use `develop` or a feature branch and open PRs via `gh pr create --base main --head develop`.
   - Always run `./tools/safety/safety_check.sh` before staging or pushing commits.
2. **Static Data & Modular UI**:
   - Keep static catalogs in `hub/data/*.json` (not giant Python dict modules).
   - Edit UI CSS/JS inside the modular files under `hub/static/css/` and `hub/static/js/`, never re-monolithing `hub/static/index.html`.
3. **Process & Subagent Hygiene**:
   - Before ending a multi-step implementation turn, verify `manage_task(Action="list")` and `manage_subagents(Action="list")` leave zero orphaned non-daemon tasks (only `hub/server.py` with `IsDaemon=true` on port `8090` may remain).
