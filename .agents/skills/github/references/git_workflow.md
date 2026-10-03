# Git Branching Strategy & PR Workflow

This repository uses a structured **GitFlow-inspired branching strategy**:

---

## 1. Branch Hierarchy

```text
main (Protected)
  ▲
  │  (Release / Milestone Pull Request)
  │
develop (Active Integration Branch)
  ▲
  │  (Feature / Problem Work)
  │
feat/dsa-002-valid-anagram (Optional local task branch)
```

1. **`main` (Production Branch)**:
   - Protected: Direct commits and direct pushes are strictly prohibited.
   - Represents verified, production-ready curriculum and framework releases.
   - Updated exclusively via Pull Requests from `develop`.

2. **`develop` (Integration Branch)**:
   - Default active working branch for daily problem solving and framework development.
   - All completed DSA problems and framework components are pushed to `develop`.

3. **Feature Branches (`feat/...`)**:
   - Optional branches created when implementing complex multi-file framework modules or multi-problem batches.

---

## 2. Pull Request Lifecycle

1. **Daily Practice**:
   - Complete problem in `develop`.
   - Native tests pass: `./run.sh test <slug>`.
   - Interviewer evaluation passed: `/interviewer`.
   - Push to `develop`: `/github push`.

2. **Milestone Review (e.g. End of Pattern or Major Framework Module)**:
   - Run `/github pr`.
   - Agent audits safety, pushes branch, and provides the PR link.
   - Candidate inspects diff on GitHub, verifies checks, and merges into `main`.
