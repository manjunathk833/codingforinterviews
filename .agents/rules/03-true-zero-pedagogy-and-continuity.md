---
trigger: always_on
---

# Mandatory True-Zero Pedagogy, Udemy Continuity, Dual-Modality & New-Course SOP

Whenever authoring, editing, reviewing, or adding any **Textbook Course** (`knowledgebase/**/*.md`), you MUST strictly follow these 5 laws so a **complete newcomer (Absolute Zero)** can learn effortlessly in **Guided 4-Step Mode** and a **Staff Engineer** can revise the entire course in one pass in **Single-Page Master Compendium Mode**.

---

## 1. Law 1 — Relentless Udemy-Style Continuity ("The Red Thread")

1. **One Continuous Build-Along Project Per Course**:
   - Never write disconnected academic essays. Every course evolves **one continuous, tangible project** across Chapters `01 -> N` anchored in this repo:
     - *Course 01 (`01-zero-to-staff-sdet`)*: Protecting **`AeroCart`** (`apps/aerocart/`) from a 3-line ticket check to a 32-worker Staff OTel CI platform.
     - *Course 02 (`02-building-testing-frameworks`)*: Building **`MiniTest`** from an empty `.py`/`.java` file (`v0.1` crashing `assert` $\to$ `v0.2` loop runner $\to$ `v0.3` `@fixture` LIFO stack $\to$ `v1.0` parallel SDK), mapped 1-to-1 onto Pytest & JUnit 5.
     - *Course 03 (`03-ui-automation-playwright`)*: Building **`AeroBot`** from a 4-line browser click to a zero-flake, sharded CDP/BiDi UI suite with Zero-UI Auth, Network Routing, Clock Virtualization & Trace Forensics.
     - *Course 04 (`04-api-and-api-automation`)*: Building **`AeroClient`** from a 5-line HTTP `GET` check to a pooled HTTP/2, OAuth2/mTLS, Pydantic + REST Assured, GraphQL, gRPC & Pact contract test harness.
     - *Course 05 (`05-ai-engineering`)*: Building **`AeroBrain`** from a 10-line flight-delay price predictor to a production Transformer + Hybrid RAG (`BM25 + HNSW + RRF`) + LoRA + MCP Agent concierge.
     - *Course 06 (`06-ai-engineering-qa-focused`)*: Building **`AeroEval`** from catching a first bot hallucination to a Golden Dataset, RAG Triad, Rogan-Gladen Calibrated LLM Judge, Red-Team & AST Self-Healing gate.
     - *Course 07 (`07-distributed-system-design`)*: Scaling **`AeroCart`** from 1 laptop crashing under 100 flyers to a 100,000-RPS distributed architecture (Ring Buffers, Consistent Hashing, Kafka Outbox CDC, Singleflight & Raft Quorums).
     - *Course 08 (`08-core-cs-internals`)*: Tracing **`python3 apps/aerocart/server.py`** inside the OS & hardware (Virtual Memory/RSS Leaks, TCP/TLS 1.3 Handshakes, B+Tree vs LSM/WAL Storage, MESI/CAS Atomics & Linux `epoll`/`cgroups v2`).
2. **Mandatory ```` ```json continuity ```` Bridge at the Top of Every Chapter**:
   - Every chapter MUST open with a ```` ```json continuity ```` block connecting causally to the previous chapter:
     - `"previously"`: What we just built (or `"Welcome to Day 1! Zero prior background needed."` in `Ch 01`).
     - `"painPoint"`: The **one concrete real-world friction point** our previous code just hit (*Pain Before Solution*).
     - `"unlock"`: The plain-English superpower we will build in the next 10–12 minutes.

---

## 2. Law 2 — Strict 4-Step Progressive Chain of Information (`Concrete -> Representational -> Abstract`)

Every chapter MUST be structured into **4 sequential `##` micro-lesson steps** (`~180–350` words per step) in this exact order:

1. **`## 🌱 Step 1: Plain-English Story — ...` (`Zero Jargon · 2–3 min`)**:
   - Start with a warm, conversational, real-life story or analogy (*Head First / Grokking / Colt Steele* tone) + a clean `mermaid` diagram (`<= 6` nodes).
   - **HARD BAN IN STEP 1**: **ZERO** `$$` display-math equations, **ZERO** undefined acronyms (`PEP 451`, `ECDHE`, `PGD->PTE`, `KL-divergence`), and **ZERO** `> 20`-line code walls!
2. **`## 🔨 Step 2: First Lines of Code — ...` (`Immediate Baby-Step Win · 3 min`)**:
   - Give the reader a minimal, self-contained **5–20 line** working starter code example in **Python 3** followed immediately by **`### Java 17 Equivalent`** (so the UI collapses them into `[🐍 Python 3 | ☕ Java 17]` tabs), evolving the previous chapter's code.
3. **`## ⚡ Step 3: Where It Breaks in Real Life — ...` (`Pain Before Architecture · 4 min`)**:
   - Show the *one* concrete limitation when scaling up + a ```` ```json contrast ```` card (`Naive` vs. `Pro/Staff`) + a beginner-accessible ```` ```json poe ```` prediction prompt paired with the inline simulator.
4. **`## 🚀 Step 4: Staff Engineer Deep-Dive — ...` (`High Ceiling · 5 min`)**:
   - **ONLY in Step 4** (once intuition is 100% earned in Steps 1–3!) introduce formal mathematical laws (`$$...$$`), architectural trade-off tables, full dual-language (`Python 3` + `Java 17`) production blueprints, a `> [!WARNING]` **Staff Interview Gotcha**, an `"Up Next in Chapter N+1"` cliffhanger bridge, and a `>= 3` question ```` ```json quiz ````.

---

## 3. Law 3 — Need-Before-Name Vocabulary & 90s Walkthrough Storyboard

- **```` ```json pretraining ```` (`3–4` terms)**: Powers the Right-Rail **Just-in-Time Jargon Unlocks** (`1/4 -> 4/4`) and the Single-Page Master Glossary. Every `"meaning"` MUST be written in warm, plain everyday English.
- **```` ```json walkthrough ```` (`4` slides)**: Powers the `#kb-walkthrough-shell` Audio/Visual Studio (`hub/tts_walkthrough_engine.py`). Each slide provides `"time"`, `"badge"`, conversational TTS-ready `"caption"`, and a concise `"code"` visual cue while keeping Markdown prose 100% self-sufficient.

---

## 4. Law 4 — Dual-Modality Compatibility (Guided 4-Step Mode + Single-Page Master Compendium)

Every chapter's 4-Step structure simultaneously powers **both** course learning modes with **100% unabridged fidelity**:
1. **Mode A (`🎯 Guided 4-Step Mode`)**: Interactive step-by-step micro-lessons (`Step 1 -> 4`), Audio/Visual Walkthrough Studio, POE Simulator (`hub/visualizer_engine.py`), 1-Click Lab Runner, and Mastery Quiz.
2. **Mode B (`⚡ Revise: Single-Page Master Compendium` via `GET /api/kb/course-compendium?course=<courseId>`)**: Compiles all `Ch 01 -> Ch N` into a single continuous page where `Step 1..4` map 1-to-1 onto the 4 Compendium Layer Filters (`[1. Story & Diagrams]`, `[2. Starter Code]`, `[3. Contrast & Failure Modes]`, `[4. Staff Math, Blueprints & Gotchas]`), the Global Language Switcher (`[🐍 All Python 3 | ☕ All Java 17 | ⚖️ Split Both]`), the Red-Thread Evolution Table, the Master Glossary, and the Self-Check Q&A Answer Key.

---

## 5. Law 5 — Standard Operating Procedure (SOP) for Adding Any New Course (`Course N+1`)

Whenever adding a new course (`09+`) or expanding an existing course:
1. **Register Course Metadata**: Add the course definition (`courseId`, `priorityRank`, `title`, `shortTitle`, `levelSpan`, `plannedModules`, `plannedChapters`, `accentColor`, `pillBg`, `tagline`) to `TEXTBOOK_COURSES_CATALOG` and `FOLDER_TO_COURSE_ID` in `hub/storage.py`.
2. **Design the Continuous Project Thread**: Define the single build-along project that evolves causally from a 10-line script in `Ch 01` to a Staff architecture in `Ch N`.
3. **Author Chapters (`knowledgebase/<course-id>/01-*.md` $\to$ `N-*.md`)**: Include complete YAML frontmatter (`slug`, `course_id`, `track`, `volume`, `module_number`, `module_title`, `chapter_number`, `level_tag`, `title`, `summary`, `reading_time_minutes`, `visualizer_id`, `lab_path`, `tags`), `continuity`, `walkthrough`, `pretraining`, `poe`, and the exact `Step 1..4` chain.
4. **Bind Interactive Visualizers & Local Labs**: Ensure every chapter's `visualizer_id` resolves in `hub/visualizer_engine.py` and `lab_path` points to a deterministic local verification lab.
5. **Enforce Automated Pedagogy & Compendium Gate**: Add all chapter relative paths to `REQUIRED_TRUE_ZERO_RELPATHS` in `tools/safety/pedagogy_lint.py` and verify `./tools/safety/pedagogy_lint.py --strict` + `python3 hub/tests/test_hub_phase1.py` pass with zero errors.
