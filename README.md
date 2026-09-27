# 🚀 MAANG Coding & Automation Interview Preparation Hub

A structured daily practice repository engineered for **Senior SDET / SWE-Infra / Software Engineer** candidates preparing for MAANG-tier technical interviews (Google, Meta, Amazon, Apple, Netflix).

---

## ⚡ Quick Start

### 1. Run Tests on Any Problem (Native Java & Python)
```bash
# Test a problem across both Java and Python
./run.sh test 001-two-sum

# Test Java only
./run.sh test 001-two-sum --lang java

# Test Python only
./run.sh test 001-two-sum --lang python

# List all problems and implementation status
./run.sh list
```

### 2. View Preparation Metrics & Readiness
```bash
python3 tools/tracker.py summary
```

---

## 🤖 Antigravity AI Agents (VS Code Integration)

You have specialized AI agents integrated into your Antigravity chat window:

| Slash Command | Agent Persona | Description |
| :--- | :--- | :--- |
| **`/interviewer`** (or `/review`) | **Bar Raiser / MAANG Interviewer** | Evaluates `Solution.java` and `solution.py`, runs automated tests, scores against the **100-point MAANG rubric**, asks realistic follow-up questions, and enforces a **$\ge 80/100$ threshold** to update the Master Sheet. |
| **`/hint`** (or `/mentor`) | **Socratic Algorithmic Coach** | Provides **4-tier progressive hints** (Mental Models $\to$ Patterns $\to$ Algorithmic Invariants $\to$ Scaffolding) and assists with debugging without spoiling the code. |
| **`/progress`** | **Curriculum Advisor** | Summarizes completion rates across difficulty and patterns, and recommends the next best problems to solve for maximum continuity. |

---

## 📂 Project Organization

```text
codingforinterviews/
├── .agents/
│   └── skills/
│       ├── interviewer/SKILL.md     # Slash command: /interviewer
│       ├── hint/SKILL.md            # Slash command: /hint
│       └── progress/SKILL.md        # Slash command: /progress
├── .vscode/
│   ├── tasks.json                   # 1-click Run Java, Run Python, Test Both
│   └── settings.json
├── GEMINI.md                        # Workspace rules & interview rubrics
├── tools/
│   ├── runner.py                    # Unified native compiler & test executor
│   └── tracker.py                   # Master sheet status updater
├── dsa/
│   ├── MASTER_SHEET.md              # 128 curated problems ordered Easy -> Medium -> Hard
│   ├── utils/                       # Shared ListNode & TreeNode helpers (Java & Python)
│   ├── 01-arrays-and-hashing/
│   ├── 02-two-pointers/
│   ├── 03-sliding-window/
│   └── ...
└── frameworks/
    ├── MASTER_FRAMEWORKS.md         # Framework architectures & live coding challenges
    ├── api-automation/              # REST Assured (Java) & Pytest Requests (Python)
    ├── ui-automation/               # Playwright (Python & Java) & Selenium (Java)
    └── design-challenges/           # Real MAANG SDET live coding problems
```

---

## 🎯 Daily Practice Workflow

1. Open **`dsa/MASTER_SHEET.md`** and select the next unsolved problem.
2. Open the problem folder (e.g. `dsa/01-arrays-and-hashing/001-two-sum/`).
3. Implement `twoSum` in **`Solution.java`** and **`solution.py`**.
4. Test locally using `./run.sh test 001-two-sum` or press `⌘+Shift+B` in VS Code to run task **"Test Current Problem"**.
5. Once your tests pass, open the Antigravity chat and type:
   > `/interviewer Review my solution for Two Sum`
6. If stuck at any time, type:
   > `/hint Give me a Tier 1 hint for Two Sum`
7. Check off the problem in the Master Sheet once you score $\ge 80/100$!
