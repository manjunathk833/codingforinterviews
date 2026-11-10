---
trigger: always_on
---

# Mandatory True-Zero Pedagogy, Udemy Continuity & 4-Step Chain of Information

Whenever authoring, editing, or reviewing any **Textbook Course** chapter (`knowledgebase/**/*.md`), you MUST strictly follow this pedagogical chain of information so a **complete newcomer (Absolute Zero)** can read effortlessly from Day 1 all the way to **Staff Mastery** without ever getting lost in cold jargon or math walls.

---

## 1. Law 1 — Relentless Udemy-Style Continuity ("The Red Thread")

1. **One Continuous Build-Along Project Per Course**:
   - Never write disconnected academic essays. Every course evolves **one continuous, tangible project** across Chapters `01 -> N` anchored in this repo:
     - *Course 01 (`Zero to Staff SDET`)*: Protecting **`AeroCart`** (`apps/aerocart/`) from a 3-line ticket check to a 32-worker Staff CI platform.
     - *Course 02 (`Building Testing Frameworks`)*: Building **`MiniTest`** from an empty `.py`/`.java` file (`v0.1` crashing `assert` $\to$ `v0.2` loop runner $\to$ `v0.3` `@fixture` LIFO stack $\to$ ... $\to$ `v1.0` parallel SDK), then mapping 1-to-1 onto Pytest & JUnit 5.
     - *Courses 03–08*: Evolving `AeroBot` (Playwright), `AeroClient` (API), `AeroBrain` (AI/ML), `AeroEval` (AI QA), scaling 1 laptop `AeroCart` to 100k users (System Design), and tracing `python3 server.py` inside hardware (Core CS).
2. **Mandatory ```` ```json continuity ```` Bridge at the Top of Every Chapter**:
   - Every chapter MUST open with a ```` ```json continuity ```` block connecting causally to the previous chapter:
     - `"previously"`: What we just built (or `"Welcome to Day 1! Zero prior background needed."` in `Ch 01`).
     - `"painPoint"`: The **one concrete real-world friction point** our previous code just hit (*Pain Before Solution*).
     - `"unlock"`: The plain-English superpower we will build in the next 10–12 minutes.

---

## 2. Law 2 — Strict 4-Step Progressive Chain of Information (`Concrete -> Representational -> Abstract`)

Every chapter MUST be structured into **4 sequential `##` micro-lesson steps** (`~180–300` words per step) in this exact order:

1. **`## 🌱 Step 1: Plain-English Story — ...` (`Zero Jargon · 2–3 min`)**:
   - Start with a warm, conversational, real-life story or analogy (*Head First / Grokking / Colt Steele* tone) + a clean `mermaid` diagram (`<= 6` nodes).
   - **HARD BAN IN STEP 1**: **ZERO** `$$` display-math equations, **ZERO** undefined acronyms (`PEP 451`, `ECDHE`, `PGD->PTE`, `KL-divergence`), and **ZERO** `> 20`-line code walls!
2. **`## 🔨 Step 2: First Lines of Code — ...` (`Immediate Baby-Step Win · 3 min`)**:
   - Give the reader a minimal, self-contained **5–20 line** working code example in **Python 3** followed immediately by **`### Java 17 Equivalent`** (so the UI collapses them into `[🐍 Python 3 | ☕ Java 17]` tabs), evolving the previous chapter's code.
3. **`## ⚡ Step 3: Where It Breaks in Real Life — ...` (`Pain Before Architecture · 4 min`)**:
   - Show the *one* concrete limitation when scaling up (e.g., wall-clock flake, `4,096` dropdown explosion, dirty DB leak) + a ```` ```json contrast ```` card (`Naive` vs. `Pro/Staff`) + a beginner-accessible ```` ```json poe ```` prediction prompt paired with the inline simulator.
4. **`## 🚀 Step 4: Staff Engineer Deep-Dive — ...` (`High Ceiling · 5 min`)**:
   - **ONLY in Step 4** (once intuition is 100% earned in Steps 1–3!) introduce formal mathematical laws ($P_{\text{suite}} = p^N$, Rogan-Gladen $\hat{p}$, $QK^T/\sqrt{d_k}$), architectural trade-off tables, full dual-language production blueprints, a `> [!WARNING]` **Staff Interview Gotcha**, a cliffhanger bridge to `Ch N+1`, and a 3-question ```` ```json quiz ````.

---

## 3. Law 3 — Need-Before-Name Vocabulary ("No Top-of-Page Symbol Shock")

- Every chapter's ```` ```json pretraining ```` block powers the Right-Rail **Just-in-Time Jargon Unlocks** (`1/4` -> `4/4`).
- Each `"meaning"` MUST be written in **friendly plain English** (explaining the idea *after* the reader meets it in the story), never an opaque academic definition.

---

## 4. Law 4 — Modular Audio/Visual Boundary & Linter Gate

- Keep chapter Markdown prose **100% self-sufficient** without depending on the experimental audio/visual walkthrough widget (which is maintained as a separate UI player track).
- Before declaring any chapter edit complete, run `./tools/safety/pedagogy_lint.py` to verify zero chain-of-information or Step-1 symbol-shock violations.
