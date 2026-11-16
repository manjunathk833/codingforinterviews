---
trigger: always_on
---
# Carbon–Hydrogen Planning & UI Gate

1. **Direct Questions**: Answer conceptual, architectural, or navigation questions directly and concisely with zero planning ceremony.
2. **Read-Only Planning Phase (Optimized for `Orchestrator (Carbon)`)**:
   - Do **not** modify production files (`hub/`, `dsa/`, `frameworks/`, `knowledgebase/`, `tools/`) before user approval.
   - Keep architectural exploration **read-only** (`read_file` with `StartLine`/`EndLine`, targeted `grep`) so Carbon completes planning cleanly without premature file-write handoffs:
     - Output a **Hydrogen-Ready Execution Spec**: exact target file paths, function/API contracts, edge-case invariants, and verification commands.
     - **UI Layout Changes Only**: When introducing a net-new screen or major visual redesign, generate a mockup via `image-generator` (matching Dark Ink / Zen Editorial CSS tokens) and wait for explicit user approval (`PROCEED` / artifact approval).
