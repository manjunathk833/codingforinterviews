# Mandatory Source-Grounded Curriculum, 5-Step Hiring Mastery, Udemy Continuity & New-Course SOP

Whenever authoring, editing, reviewing, or adding any **Textbook Course** (`knowledgebase/**/*.md`), you MUST strictly follow these 5 laws so a **complete newcomer (Absolute Zero)** gains 100% practitioner completeness and a **Senior/Staff Engineer** gains Big Tech production fluency and crisp interview command across **Guided Mode**, **Full Scroll**, and **Single-Page Master Compendium Mode**.

---

## 1. Law 1 — Relentless Udemy-Style Continuity Across the 12-Course Hiring Curriculum ("The Red Thread")

1. **One Continuous Build-Along Project Per Course (`01 -> 12`)**:
   - Never write disconnected essays. Every course evolves **one continuous, tangible project** across Chapters `01 -> N` anchored in `apps/aerocart/` and Senior-to-Staff AI-SDET hiring competencies:
     - *Course 01 (`01-zero-to-staff-sdet`)*: **`AeroCart` Quality Platform** (3-line check $\to$ 32-worker Staff OTel & DORA CI platform).
     - *Course 02 (`02-building-testing-frameworks`)*: **`MiniTest` SDK** (`v0.1` runner loop $\to$ `@fixture` LIFO stack $\to$ `v1.0` parallel SDK mapped 1-to-1 to Pytest, JUnit 5 & TestNG).
     - *Course 03 (`03-ui-automation-playwright`)*: **`AeroBot`** (Day-0 setup & click $\to$ zero-flake CDP/BiDi, StorageState, Network Routing, Clock Virtualization & Sharded Traces).
     - *Course 04 (`04-api-and-api-automation`)*: **`AeroClient`** (HTTP fundamentals $\to$ pooled HTTP/2, OAuth2/mTLS, Pydantic + REST Assured, GraphQL, gRPC & Pact contracts).
     - *Course 05 (`05-ai-engineering`)*: **`AeroBrain`** (Cross-Entropy classifier $\to$ Transformers, KV-Cache, Hybrid `BM25 + HNSW + RRF` RAG, LoRA/Ollama & MCP Agents).
     - *Course 06 (`06-ai-engineering-qa-focused`)*: **`AeroEval`** (Hard schema contracts $\to$ Golden Datasets, RAG Triad, Rogan-Gladen Judge Calibration, Red-Teaming & AST Self-Healing).
     - *Course 07 (`07-distributed-system-design`)*: **`AeroCart` at 100k RPS** (DNS/LB/Capacity $\to$ Ring Buffers, Consistent Hashing, Kafka Outbox CDC, Singleflight & Raft Quorums).
     - *Course 08 (`08-core-cs-internals`)*: **`AeroCart` Kernel & Storage Trace** (Stack/Heap & Virtual Memory $\to$ TCP/TLS 1.3, B+Trees vs LSM/WAL, MESI/CAS & `epoll`/`cgroups v2`).
     - *Course 09 (`09-sql-and-data-engineering`)*: **`AeroLedger`** (Day-0 schema & joins $\to$ Window Functions, `EXPLAIN ANALYZE` Indexes, `SELECT FOR UPDATE` Seat-12A Isolation, Synthetic Seeders & Kafka-to-DB Reconciliation).
     - *Course 10 (`10-docker-cicd-and-cloud-infra`)*: **`AeroPipe`** (Multi-stage `Dockerfile`s & `Testcontainers` $\to$ Kubernetes Pods/Probes/`kubectl` RCA, Dynamic Matrix Sharding & Ephemeral PR Envs).
     - *Course 11 (`11-performance-chaos-and-sre`)*: **`AeroPulse`** (`k6`/Locust load & soak harnesses $\to$ Little's Law & Coordinated Omission `p99`, `HikariCP`/Flamegraph Profiling, `Toxiproxy` Chaos & SLO Error Budgets).
     - *Course 12 (`12-app-api-and-ai-security`)*: **`AeroShield`** (Proxy inspection & OWASP API Top 10 `BOLA`/JWT/SSRF/SQLi $\to$ PCI Payment Safety, CI SAST/DAST/SCA & OWASP LLM Top 10 Gates).
2. **Mandatory ```` ```json continuity ```` Bridge at the Top of Every Chapter**:
   - Every chapter MUST open with ```` ```json continuity ```` (`"previously"`, `"painPoint"`, `"unlock"`). `Ch 01` of every course MUST be **True Day-0 Onboarding** (zero prior domain knowledge assumed).

---

## 2. Law 2 — Systematic 4-Pillar Source Grounding (Never Pure LLM Generation!)

1. **Canonical `knowledgebase/<course-id>/COURSE_MANIFEST.json` Before Writing Prose**:
   - Every v2 course MUST maintain a verified `COURSE_MANIFEST.json` triangulating **4 Ground-Truth Pillars** (researched via live docs/web & repo code, never guessed from parametric memory):
     1. **Official Vendor Docs Sitemaps & Protocol RFCs** (`Playwright`, `Pytest`, `JUnit 5`, `PostgreSQL`, `Docker/K8s`, `k6`, `OWASP`, IETF RFCs) — ensuring 100% practitioner feature coverage.
     2. **Canonical Reference Books & Papers** (*DDIA*, *OSTEP*, *AI Engineering*, *SWE at Google*, *Google SRE*, *Use The Index, Luke!*).
     3. **Validated Day-0 $\to$ Staff Prerequisite DAG**: Each chapter declares `"prerequisites"` (acyclic) and `"competencies"`.
     4. **Big Tech Production Case Studies & Hiring Loops** (*Google Testing Blog*, *Netflix TechBlog*, *Uber Eng*, *Stripe Eng*, *Airbnb*, *Anthropic*).
2. **Per-Chapter YAML Grounding**:
   - Every v2 chapter MUST include `prerequisites: [...]` and `primary_sources: [...]` (verified official docs/RFC/blog citations) in its YAML frontmatter, and extract exact API signatures, CLI flags, and config defaults *before* compiling prose.

---

## 3. Law 3 — The 5-Step Hiring-Grade Mastery Chain (`Diátaxis` + `Subgoal Labeling` + `Big Tech Hiring`)

Every v2 chapter MUST follow **5 sequential `##` steps** (no artificial `350w` cap on Steps 2–5; keep Step 1 concise `< 350w`):

1. **`## 🌱 Step 1: Plain-English Mental Model — ...`** (*Novice Intuition*):
   - Warm real-world analogy + `<= 6`-node `mermaid` diagram. **HARD BAN IN STEP 1**: ZERO `$$` display math, ZERO undefined acronyms, ZERO `> 20`-line code walls.
2. **`## 🔨 Step 2: Zero-to-Running Starter & CLI — ...`** (*Diátaxis Tutorial + Subgoal Labels*):
   - Exact **Terminal Setup & Run block (```` ```bash ````)** + minimal runnable **Python 3** & **`### Java 17 Equivalent`** starter code annotated with explicit `# Subgoal 1..N:` comments and a brief walkthrough so a Day-0 learner runs and understands every line.
3. **`## 🛠️ Step 3: Everyday Practitioner Workflows & Where Naive Code Breaks — ...`** (*Diátaxis How-To*):
   - Idiomatic day-to-day project usage (configs, fixtures/hooks, CLI flags, debugging) bridging the starter-to-Staff gap + ```` ```json contrast ```` card (`Naive` vs `Staff`) + ```` ```json poe ```` simulator prompt.
4. **`## 🏢 Step 4: How Big Tech Runs It at Scale, Staff Math & Production Blueprint — ...`** (*Industry & Hiring Depth*):
   - **`🏢 In the Wild` Big Tech Case Study**: How Tier-1 orgs (*Netflix, Uber, Stripe, Google, Airline GDS, Quick-Commerce*) run this across `30–500+` microservices.
   - Formal `$$...$$` sizing/reliability equations + architectural trade-off table (*including when NOT to use it*).
   - Complete runnable dual-language (`Python 3` + `Java 17`) production blueprint + `> [!WARNING]` **Hiring Bar-Raiser Callout** + `>= 3` ```` ```json quiz ```` questions.
5. **`## 📋 Step 5: Master Cheat-Sheet, 60-Second Interview Pitch & Verified Sources — ...`** (*Diátaxis Reference*):
   - Scannable `Python 3` vs `Java 17` API/CLI lookup table + **`🎙️ 60-Second Interview Soundbite`** (ready-to-speak Senior/Staff answer) + clickable **Verified Primary Sources**.

*(Backward Compatibility Note: Legacy v1 4-Step chapters in Courses `01–08` remain valid during phased migration until upgraded to v2 in Milestone 3; all new courses `09–12` enforce strict v2 5-Step compliance immediately.)*

---

## 4. Law 4 — Multi-Format Parity & Need-Before-Name Cognitive Aids

- Every chapter includes ```` ```json pretraining ```` (`3–4` plain-English terms) and ```` ```json walkthrough ```` (`4` slides).
- Powers **Guided Mode** (`Step 1 -> 5`), **Full Scroll Mode**, and **Single-Page Master Compendium (`⚡ Revise Course`)**, where `Step 5` powers the 1-click **`[5. Cheat-Sheets & Interview Pitch]`** cram filter.

---

## 5. Law 5 — Deterministic Verification & New-Course SOP (`Course N+1`)

1. Build `knowledgebase/<course-id>/COURSE_MANIFEST.json` (4 pillars + acyclic DAG) and register metadata in `TEXTBOOK_COURSES_CATALOG` & `FOLDER_TO_COURSE_ID` in `hub/storage.py`.
2. Author `01-*.md` $\to$ `N-*.md` following the continuous project thread and strict 5-Step Hiring-Grade chain, binding valid `visualizer_id` (`hub/visualizer_engine.py`) and deterministic `lab_path`.
3. Register the course in `REQUIRED_V2_SOURCED_COURSES` and paths in `REQUIRED_TRUE_ZERO_RELPATHS` in `tools/safety/pedagogy_lint.py`.
4. Run `./tools/safety/pedagogy_lint.py --report`, `./tools/safety/snippet_verify.py` (verifying `100%` Python AST + stdlib execution with `from __future__ import annotations` + `javac` compilation), and `python3 hub/tests/test_hub_phase1.py` with **zero errors**.
