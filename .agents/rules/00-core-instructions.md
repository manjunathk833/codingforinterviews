---
trigger: always_on
---

# The Hub of Learning — Core System & Engineering Instructions

## 1. Platform Identity & 4 Track Execution Archetypes

This repository is **"The Hub of Learning"** — a local-first, multi-modal engineering mastery & living knowledgebase platform running at `http://127.0.0.1:8090` (`hub/server.py`) backed by SQLite `WAL` + `FTS5` (`hub/hub.db`) and Markdown/Code on disk.

Every track in the platform strictly follows one of 4 execution archetypes:

1. **Dynamic Interactive Textbook & Knowledgebase (`System Design`, `AI Engineering`, `Core CS`) + Engineering Pulse Newsfeed**:
   - **Location**: `knowledgebase/<track>/`, `core-cs/`, `system-design/`, `ai-engineering/`, and `hub/newsfeed_engine.py`.
   - **Experience**: Long-form book-style chapters with First-Principles Mental Models, Mermaid architectural diagrams, inline interactive step-by-step simulators (`hub/visualizer_engine.py`), dual-language production blueprints (Java 17 & Python 3), End-of-Chapter Quizzes + Practice Labs, and cross-linked **Engineering Pulse Newsfeed** articles keeping the textbook anchored in current AI & software trends.
2. **In-Browser Algorithmic Studio (`DSA`)**:
   - **Location**: `dsa/<chapter>/<number-problem-slug>/` (`README.md`, `solution.py`, `Solution.java`, `tests.json`).
   - **Experience**: 50/50 Editorial Split Studio (`WS 1`) with 3D tactile visualizers, 4-Tier Socratic Hints, and live browser code editor synced atomically to disk with `sha256` optimistic locking.
3. **Local IDE Engineering Workbench (`SDET & Automation Frameworks`)**:
   - **Location**: `frameworks/` and `apps/aerocart/` (`AeroCart` system under test).
   - **Experience**: Multi-file frameworks (`Playwright`, `REST Assured`, `Pytest`, `Selenium`, concurrency & design katas) built locally in the user's IDE and verified **100% deterministically on the local machine with strictly zero AI dependency**.
4. **Interactive Mock Interview Simulator (`Mock Interviews`)**:
   - **Location**: `mock-interviews/interview-N/` (`interviewquestions.md`, `evaluation-and-feedback.md`, `conceptual-mastery-guide.md`).
   - **Experience**: Multi-part Staff/Senior architectural interview scenarios evaluated against the 100-point rubric and deep-linked to Knowledgebase textbook chapters.

---

## 2. Git, Branching & PR Governance

- **HARD NO on Direct Commits or Pushes to `main`**:
  - NEVER commit or push directly to `main`.
  - All feature work, textbook chapters, and bug fixes must be committed to `develop` (or a dedicated feature branch).
  - Merges into `main` happen exclusively via GitHub Pull Requests (`gh pr create --base main --head develop`) after user review.
- **Pre-Push Safety Gate**:
  - Always run `./tools/safety/safety_check.sh` before staging or pushing commits to ensure zero leaked secrets, API tokens, PII, or build artifacts.

---

## 3. Background Process & Subagent Hygiene

- Before concluding any multi-step task, run `manage_task(Action="list")` and `manage_subagents(Action="list")` to verify that no orphaned one-off tasks or hung subagents remain running.
- Only persistent development servers explicitly started with `IsDaemon=true` (`./run.sh hub` on port `8090`) should remain active when needed for browser inspection.
