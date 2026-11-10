---
name: release
description: Pre-push safety scan, full CI gate, conventional commit to develop, and GitHub Pull Request creation for The Hub of Learning. Triggers on /release, /github, /pr, or /push.
---

# Release & GitHub PR Automation Skill (`release`)

Use this skill when the user wants to commit, push, or open/update a Pull Request for **"The Hub of Learning"**.

## 1. Pre-Push Safety & Secret Audit (Mandatory)
Always run the repository safety scanner before staging or committing:
```bash
./tools/safety/safety_check.sh
```
Confirm exit code `0` (zero secrets, private keys, PII, or build artifacts).

## 2. Pre-PR Full Local CI Gate
Before pushing to `develop` or opening/updating a PR to `main`, execute the 4-stage CI suite:
```bash
./run.sh ci
```

## 3. Branch Protection & Conventional Commits (`develop` Only)
- **NEVER commit or push directly to `main`.**
- Ensure you are on `develop` (or a feature branch):
  ```bash
  git branch --show-current
  ```
- Stage intentional files and commit using Conventional Commits:
  - `feat(hub): ...`
  - `feat(knowledgebase): ...`
  - `feat(dsa/<slug>): ...`
  - `feat(frameworks): ...`
  - `chore(agents): ...`

## 4. Push & Create/Update GitHub Pull Request
```bash
git push -u origin develop
gh pr create --base main --head develop --title "<title>" --body-file .github/pull_request_template.md
```
If an open PR from `develop` to `main` already exists, view and update it via `gh pr view` / `gh pr edit`.
