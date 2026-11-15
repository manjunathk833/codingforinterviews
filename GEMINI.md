# The Hub of Learning — Core Project Contract

Local-first engineering mastery studio (`http://127.0.0.1:8090`, `hub/server.py`, SQLite `WAL` + `FTS5` in `hub/hub.db`).

## 4 Track Archetypes
1. **Textbook & Pulse (`knowledgebase/`, `hub/storage.py`)**: 12 source-grounded courses (`114` chapters), inline simulators (`hub/visualizer_engine.py`), quizzes, and Pulse newsfeed.
2. **Coding Studio (`dsa/`, `hub/dsa_catalog.py`, `hub/code_coach.py`)**: `128` DSA problems + `12` warmup drills, Python 3 & Java 17 runners, `4s` sandbox, `0–100` Code Coach.
3. **Testing Architecture Workbench (`frameworks/`, `apps/aerocart/`)**: Multi-file UI/API/CI/Concurrency/SQL/Perf/Security frameworks verified 100% locally with zero AI dependency.
4. **Staff Mock Simulator (`mock-interviews/`)**: 100-point rubric architectural evaluations synced with SQLite.

## Non-Negotiable Governance
- **Git**: NEVER commit or push directly to `main`. Commit to `develop` (or feature branch) after `./tools/safety/safety_check.sh` and required CI; merge via PR.
- **UI**: Modular assets live in `hub/static/index.html`, `hub/static/css/theme.css`, and `hub/static/js/*.js` using semantic CSS variables (`var(--bg-*)`, `var(--ink-*)`, `var(--accent-*)`) — never hardcode light-mode hexes.
- **Orchestration**: Follow `.agents/rules/` for Carbon (read-only planning) $\leftrightarrow$ Hydrogen (guarded execution & verification).
