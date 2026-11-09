---
trigger: always_on
---

# Mandatory Pre-Plan Sandbox Dry Run, Plan Optimization & UI Gate

## 1. Direct Question Exemption

- If the user asks a conceptual, architectural, or informational question that requires a simple answer, **answer directly and concisely** without planning boilerplate or dry-run ceremony.

---

## 2. Mandatory Pre-Plan Sandbox Dry Run & Plan Optimization (Before Presenting Any Plan)

For any request that creates, modifies, or deletes production code, database schemas, backend services, or UI layouts:

1. **Zero Production File Edits in the Initial Turn**:
   - **NEVER** modify production workspace files (`hub/`, `dsa/`, `frameworks/`, `knowledgebase/`, `tools/`) before presenting a plan and receiving explicit user approval.
2. **Execute a Pre-Plan Sandbox Dry Run in `scratch/` First**:
   - Before writing or presenting the plan, delegate to `dry_run_agent` (or execute directly in `<appDataDir>/brain/<conversation-id>/scratch/`) to validate technical assumptions in isolation:
     - **For Backend / DB / Parser / Service Tasks**: Write a temporary spike script (`scratch/spike_<feature>.py`) to test SQLite `FTS5` schemas, BM25 queries, Markdown/YAML parsers, or API contracts against temporary in-memory/scratch databases.
     - **For UI / Layout / Visual Tasks (Rule `ii-a`)**:
       1. Invoke the **`image-generator` subagent (Gemini visual generation capability)** to generate high-resolution visual design mockup(s) in the Zen Editorial aesthetic (`#FAF7F2` warm alabaster, Fraunces serif, JetBrains Mono, 3D tactile cards).
       2. Build an **interactive HTML prototype** (`docs/prototypes/<feature>-prototype.html` or `scratch/preview_<feature>.html`) demonstrating the layout, typography, and interactive controls.
   - Record all concrete measurements, edge cases discovered, and design adjustments in `<appDataDir>/brain/<conversation-id>/scratch/dry_run_findings.md`.
3. **Tweak & Optimize the Plan Based on Findings**:
   - Refine the proposed schema, API contract, or UI layout using the empirical findings from `scratch/dry_run_findings.md` so the plan presented to the user is already de-risked and optimized.
4. **Present the Evidence-Backed Plan & Wait for Approval**:
   - Present the concise, optimized plan containing:
     - **Pre-Plan Dry-Run Findings & Optimizations Applied** (linking `scratch/dry_run_findings.md`, plus the Gemini mockup image and HTML prototype for UI tasks).
     - **Target Files & Step-by-Step Production Changes**.
     - **Post-Implementation 3-Layer Verification Plan**.
   - **STOP** and wait for explicit user approval (`"PROCEED"`, `"yes"`, `"go ahead"`, or artifact approval) before modifying production files.
