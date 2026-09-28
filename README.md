# 🚀 MAANG Coding & Automation Interview Preparation Hub

A production-grade daily practice repository engineered for **Senior SDET / QA Architect / SWE-Infra** candidates preparing for MAANG-tier technical interviews (Google, Meta, Amazon, Apple, Netflix).

---

## 📚 Central Documentation Hub

| Document | Description |
| :--- | :--- |
| **[Architecture & Blueprint](docs/ARCHITECTURE.md)** | Monorepo layout, Antigravity AI agents orchestration, and compilation pipeline. |
| **[DSA Curriculum & Pattern Guide](docs/DSA_CURRICULUM_GUIDE.md)** | In-depth breakdown of the 13 core algorithmic patterns, Big-$O$ trade-offs, and mental models. |
| **[Frameworks & System Design Guide](docs/FRAMEWORKS_GUIDE.md)** | Architecture patterns for REST Assured, Pytest, Playwright, Selenium, and live coding challenges. |
| **[Interview Playbook (45-Min Protocol)](docs/INTERVIEW_PLAYBOOK.md)** | Timeline, out-loud communication, edge-case audit checklists, and handling follow-ups. |

---

## ⚡ Quick Start

### 1. Test Any Problem (Native Dual Java 17 & Python 3.9)
```bash
# Test a problem across both Java and Python
./run.sh test 001-two-sum

# Test Java only
./run.sh test 001-two-sum --lang java

# Test Python only
./run.sh test 001-two-sum --lang python

# List all discovered problems
./run.sh list

# Run test suite across all implemented problems
./run.sh test-all
```

### 2. View Preparation Metrics & Readiness
```bash
python3 tools/tracker.py summary
```

---

## 🤖 Antigravity AI Agents (VS Code Integration)

Switch personas directly in the chat panel using first-class slash commands:

| Slash Command | Agent Persona | Purpose & Workflow |
| :--- | :--- | :--- |
| **`/interviewer`** (or `/review`) | **MAANG Bar Raiser** | Evaluates `Solution.java` and `solution.py`, executes automated tests, scores against the **100-point rubric**, and enforces an **$\ge 80/100$ threshold** before marking the problem passed. |
| **`/hint`** (or `/mentor`) | **Socratic Coding Coach** | Provides **4-tier progressive hints** (Mental Model $\to$ Pattern $\to$ Invariants $\to$ Scaffolding) without spoiling code. |
| **`/progress`** | **Curriculum Advisor** | Displays completion stats across difficulty and patterns, and recommends the next logical questions. |

---

## 📂 Project Organization

```text
codingforinterviews/
├── .agents/skills/                  # Antigravity agent slash commands (/interviewer, /hint, /progress)
├── .vscode/                         # VS Code 1-click test tasks and language configurations
├── docs/                            # Central Documentation Hub
│   ├── ARCHITECTURE.md              # System design & compilation blueprint
│   ├── DSA_CURRICULUM_GUIDE.md      # Pattern identification & complexity guide
│   ├── FRAMEWORKS_GUIDE.md          # Enterprise QA framework architecture
│   └── INTERVIEW_PLAYBOOK.md        # MAANG interview communication & time management
├── GEMINI.md                        # Persistent workspace rules for Antigravity
├── tools/
│   ├── runner.py                    # Multi-language compiler & test harness
│   └── tracker.py                   # Master sheet parser & updater
├── dsa/                             # 13 Algorithmic Patterns
│   ├── MASTER_SHEET.md              # 128 curated problems tracker
│   ├── utils/                       # Shared ListNode & TreeNode helpers
│   ├── 01-arrays-and-hashing/
│   ├── 02-two-pointers/
│   ├── 03-sliding-window/
│   └── ... (all 13 patterns)
└── frameworks/                      # Automation & SDET System Design
    ├── MASTER_FRAMEWORKS.md         # Framework status & roadmap
    ├── api-automation/
    │   ├── restassured-java/        # Enterprise REST Assured suite with SpecFactory & POJOs
    │   └── pytest-requests-python/  # Pytest API suite with Pydantic contracts & session pooling
    ├── ui-automation/
    │   ├── playwright-python/       # Modern Playwright Page Object Model
    │   ├── playwright-java/         # Playwright Java with ThreadLocal Page
    │   └── selenium-java/           # Selenium 4 with ThreadLocal WebDriver
    └── design-challenges/           # Top-tier MAANG live coding challenges
        ├── 01-custom-retry-analyzer
        ├── 02-json-payload-diff-engine
        ├── 03-rate-limited-test-client
        ├── 04-test-data-builder
        └── 05-microservice-mocking
```

---

## 🎯 Daily Practice Workflow

1. Open **[dsa/MASTER_SHEET.md](dsa/MASTER_SHEET.md)** and pick an unsolved problem.
2. Open the problem folder (e.g. `dsa/01-arrays-and-hashing/001-two-sum/`).
3. Implement `twoSum` in **`Solution.java`** and **`solution.py`**.
4. Test locally using `./run.sh test 001-two-sum` or press `⌘+Shift+B` in VS Code.
5. In Antigravity chat, type:
   > `/interviewer Review my solution for 001-two-sum`
6. If you need conceptual guidance, type:
   > `/hint Give me a Tier 1 hint for 001-two-sum`
