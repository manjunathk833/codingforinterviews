# The Hub of Learning — Engineering Mastery & Living Knowledgebase Rules

Welcome to **The Hub of Learning** (`http://127.0.0.1:8090`).
This platform combines interactive first-principles textbooks (`System Design`, `AI Engineering`, `Core CS`), a live **Engineering Pulse Newsfeed**, an **In-Browser Algorithmic Studio (`DSA`)**, a **100% Local Deterministic Automation Workbench (`Frameworks`)**, and **Staff/Senior Mock Interview Simulations**.

---

## 1. The 4-Step Closed-Loop Execution Lifecycle (Always On)

All rules in `.agents/rules/` are always active:

1. **Direct Question Exemption (`.agents/rules/01-planning-and-ui-gate.md`)**:
   - If the user asks a simple conceptual or informational question, answer directly and concisely without planning ceremony.
2. **Pre-Plan Sandbox Dry Run & Plan Optimization (Before Presenting Any Plan)**:
   - Never modify production files (`hub/`, `dsa/`, `frameworks/`, `knowledgebase/`, `tools/`) in your initial turn.
   - First execute a **Pre-Plan Sandbox Dry Run** in `<appDataDir>/brain/<conversation-id>/scratch/` (via `dry_run_agent` or directly):
     - **Backend / DB / Parser Tasks**: Run a temporary spike script (`scratch/spike_<feature>.py`) to validate SQLite `FTS5` schemas, BM25 queries, parsers, and API contracts in isolation. Save concrete observations to `scratch/dry_run_findings.md`.
     - **UI / Visual Tasks**: Generate visual mockup(s) using the **`image-generator` subagent (Gemini capability)** and build an **interactive HTML prototype** (`docs/prototypes/` or `scratch/preview_*.html`).
   - **Tweak & Optimize the Plan** based on `scratch/dry_run_findings.md`, then present the evidence-backed plan + visuals and wait for explicit user approval (`"PROCEED"` / `"yes"` / artifact approval).
3. **Post-Implementation 3-Layer Verification (`.agents/rules/02-verification-and-ci-gate.md`)**:
   - After user-approved production edits are applied, verify all 3 layers (via `dry_run_agent` or directly):
     1. **Service Requests & Responses**: Live HTTP calls against `http://127.0.0.1:8090/api/*`.
     2. **Database & Disk State**: Query production SQLite (`hub/hub.db` & `FTS5` virtual index) and verify local files (`sha256`, `+x` permissions).
     3. **Live Browser Check**: Verify DOM rendering and interactive controls on `http://127.0.0.1:8090`.
4. **Smart Conditional Regression Gate**:
   - **During Iteration**: Run targeted verification (`python3 hub/tests/test_hub_phase1.py`, `./run.sh test <slug>`, or local lab `verify.sh`) since automated CI is established.
   - **Core Infra / Pre-PR**: Run full `./run.sh ci` when shared core infrastructure (`hub/server.py`, `hub/storage.py`, `tools/runner.py`) changes or before opening/updating a PR.

---

## 2. The 4 Track Execution Archetypes

| Archetype | Tracks | Storage & Execution Model |
| :--- | :--- | :--- |
| **1. Dynamic Interactive Textbook & Pulse Newsfeed** | `System Design`, `AI Engineering`, `Core CS` | Markdown chapters (`knowledgebase/`, `core-cs/`, `system-design/`, `ai-engineering/`) indexed in SQLite `FTS5` (`kb_chapters`, `kb_search_fts`), inline `visualizer_engine.py` simulations, quizzes (`kb_quizzes`), and cross-linked **Engineering Pulse Newsfeed** (`newsfeed_articles`). |
| **2. In-Browser Algorithmic Studio** | `DSA` (15 Chapters, 128 Problems) | `dsa/<chapter>/<number-slug>/` (`README.md`, `solution.py`, `Solution.java`, `tests.json`) synced atomically with `WS 1` 50/50 Split Studio. |
| **3. Local IDE Engineering Workbench** | `SDET & Automation Frameworks` | `frameworks/` & `apps/aerocart/` (`AeroCart` AUT). Built locally in the user's IDE and verified **100% deterministically locally with strictly zero AI dependency**. |
| **4. Interactive Mock Interview Simulator** | `Mock Interviews` | `mock-interviews/interview-N/` synced with SQLite `mock_interview_sessions`, evaluated on the 100-point rubric, and deep-linked to Knowledgebase chapters. |

---

## 3. Optimal Specialized Agents (`.agents/agents/`) & Skills (`.agents/skills/`)

- **`dry_run_agent`** (`.agents/agents/dry_run_agent.md`):
  - **Phase A**: Pre-Plan Sandbox Spikes (`scratch/spike_*.py`, `scratch/dry_run_findings.md`) + Gemini UI mockups (`image-generator`) + HTML prototypes.
  - **Phase B**: Post-Implementation 5-Checkpoint Live Browser, SQLite DB, Service API & Smart CI audit.
- **`knowledgebase_architect`** (`.agents/agents/knowledgebase_architect.md`):
  - Authors 4-Part Interactive Textbook chapters (`System Design`, `AI Engineering`, `Core CS`), maintains SQLite `FTS5` search, and curates cross-linked **Engineering Pulse Newsfeed** articles.
- **`socratic_bar_raiser`** (`.agents/agents/socratic_bar_raiser.md`):
  - Unified 4-Tier Socratic Mentor (`/hint`), 100-Point Bar-Raiser Evaluator (`/review` / `/interviewer`), and Staff Mock Interview Simulator (`/mock-interview`).
- **`release` Skill** (`.agents/skills/release/SKILL.md`):
  - Runs `./tools/safety/safety_check.sh` and `./run.sh ci`, commits to `develop` (never directly to `main`), and manages GitHub PRs.
