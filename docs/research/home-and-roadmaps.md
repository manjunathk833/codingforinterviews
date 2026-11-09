# Home page UX research: interview-prep learning hub

**How sure I am of each claim:**
- ✅ **Verified directly.** I fetched the live page, its production JS/CSS bundle, or an official blog post.
- 🔶 **Secondary.** The claim comes from search summaries of reviews, Reddit, or docs that I couldn't open myself.
- ❓ **Unverified.** It's from memory or inference. Treat it as a hypothesis.

AlgoExpert is a client-rendered single-page app. curl gets back "Unsupported browser", so most of the AlgoExpert detail is 🔶 or ❓. Frontend Masters now redirects to and brands itself as **Master.dev** ✅ (https://frontendmasters.com/learn/).

---

## 1. AlgoExpert (algoexpert.io): main reference for UI quality

**Home/dashboard layout**
- Top nav with a product switcher covering AlgoExpert, SystemsExpert, FrontendExpert, MLExpert and others. One account, one look across all products. 🔶 (https://www.algoexpert.io/product). Clicking a product you haven't paid for opens an upsell paywall, which breaks your study flow. 🔶
- Product tabs: Questions, Assessments, Mock Interviews, Data Structures Crash Course, and Behavioral/Certificates. 🔶
- Questions page: about 200 curated questions in about 15 categories. You can group by category or show a flat list, and filter by difficulty. 🔶
- Difficulty has four tiers: Easy, Medium, Hard, Very Hard. 🔶
- Overall progress is a bar with an "X / 200 completed" count. Each category header has a mini counter (e.g. 3/12). 🔶
- Solved questions get a checkmark. You can also flag or star a question to come back to it. 🔶

**System design (SystemsExpert)**
- Two tiers: a linear "Fundamentals" course (client-server, caching, sharding, …) and a separate grid of design case studies. 🔶
- Progress there is "watched/completed" rather than tests passed. 🔶

**Visual style**
- Dark-first, low clutter, high signal. Reviewers consistently call it clean and distraction-free compared with LeetCode's endless list. 🔶
- Fonts ✅ (from the algoexpert.io HTML head): Open Sans and Lato for UI, Source Code Pro for code. Ubuntu and Jura are also loaded.
- The workspace has a light/dark toggle and puts the prompt, editor, tests, hints and video in one split-pane view. 🔶

**Weak spots**
- Reddit's main complaints: the small question set (~200), a shallow system design product, price, and no refunds. None of these are UI complaints. 🔶
- I found no evidence of streaks, a daily goal or spaced review. Motivation comes almost entirely from progress bars and certificates. 🔶/❓

**Worth copying**
- The product switcher.
- Group-by-category list with a counter per group.
- Few items, heavily curated.
- One design language across every product.
- A two-tier structure for System Design: linear fundamentals, then a grid of case studies.

---

## 2. roadmap.sh: interactive roadmaps

**Node states** ✅ (read from roadmap.sh's production bundles at https://roadmap.sh/frontend)
- The status enum is `pending | learning | done | skipped`, plus `removed` for personalized roadmaps.
- Action menu:
  - "In progress": violet.
  - "Done": green, shortcut **D**.
  - "Skip": zinc, shortcut **S**.
- Mouse shortcuts:
  - **Right-click** marks Done.
  - **Shift+click** marks In progress.
  - **Alt/Option+click** marks Skipped.
  - Clicking again on the same status toggles it back to pending.
- Visual treatment, from the CSS:
  - Done: grey fill `#cbcbcb` with line-through text.
  - Learning: lavender fill `#dad1fd` with **underlined** text.
  - Skipped: dark teal fill `#496b69` with line-through text.
  - Status is shown with fill **and** text decoration, not color alone. That's good for accessibility.

**Progress counts** ✅
- The roadmap page computes progress as **(done + skipped) / total**. Skipping counts as "dealt with", which is a good idea for a senior learner who can skip what they already know.
- The progress dialog shows separate counts for done, learning, skipped and **"today"**.
- There's a "personalized" mode: you describe your background and irrelevant topics are skipped in bulk.
- After a few visits it shows a "progress nudge" suggesting you start tracking. ✅

**Home page** ✅ (https://roadmap.sh)
- ⌘K search in the header.
- Roadmaps grouped by tabs (Most popular / AI / Web / Data / DevOps / Languages / Interview) and by type (role-based 31, skill-based 61, best practices 5).
- Below that: lesson packs, videos and guides. It's a catalog, not a personal "today" page.
- Logged-in users get a dashboard listing the roadmaps they track with a % for each, and an activity/streak view. 🔶

**Weak spots** 🔶
- The constant Reddit complaint: roadmaps are overwhelming, with far too many nodes. Experienced devs say "treat it as a menu, not a checklist".
- A huge zoomable graph makes it hard to answer "where am I?" quickly.

**Worth copying**
- The four-state model with fill plus text decoration.
- Keyboard shortcuts for changing state.
- Counting skipped toward %.
- A "today" counter.

---

## 3. NeetCode (neetcode.io)

**Roadmap** 🔶, with category list ✅
- A top-down dependency tree of pattern nodes, starting at Arrays & Hashing. It branches to Two Pointers / Stack, then Binary Search / Sliding Window / Linked List, then Trees, and so on, ending at 2-D DP, Advanced Graphs and Math.
- Each node shows a thin progress bar with a count such as 3/9.
- Clicking a node opens a panel with that topic's problems: difficulty, a link and the video solution.
- The category list in the bundle ✅: Arrays & Hashing, Two Pointers, Sliding Window, Binary Search, Linked List, Stack, Trees, Tries, Backtracking, Heap/PQ, Graphs, Advanced Graphs, 1-D DP, 2-D DP, Greedy, Intervals, Bit Manipulation, Math & Geometry (plus JavaScript).
- The bundle's CSS has a 6px `.progress-bar` component. ✅

**Progress** 🔶
- Overall "X / 150" with an Easy/Medium/Hard breakdown.
- A list view with collapsible category sections, each with its own bar.
- You can switch between lists: Blind 75, NeetCode 150, NeetCode 250, All.

**Habit mechanics** ✅
- The navbar profile dropdown shows `currentStreak` as "**Nd streak**".
- There's a notification type `STREAK_REPAIR_EARNED`: "You earned a streak repair! (N-day streak)". Repairs are **earned at streak milestones**, not bought.

**Visual style**
- Dark theme by default, with light as an option ✅ (the theme is read from localStorage before render).
- Geist font ✅.
- Tailwind palette with orange, amber, emerald, cyan and rose accents ✅.

**Weak spots** 🔶/❓
- The graph is a pannable canvas, which is a bit heavy for a "where am I?" glance.
- Pro-gated items are mixed into free lists.

**Worth copying**
- A pattern dependency graph with a count and bar inside each node.
- Click a node to open a side panel instead of navigating away.
- A streak chip in the nav.
- Streak repairs earned at milestones.

---

## 4. Duolingo: the path and the habit loop

**The path** ✅ (https://blog.duolingo.com/new-duolingo-home-screen-design/, launched 1 Nov 2022)
- It replaced the skill tree with a **single guided path** because learners weren't sure they were using the app "the correct way".
- Lessons are grouped into small **units**, and each unit has a **guidebook** (the old "Tips").
- Practice and review are built into the path using **spaced repetition**: earlier concepts come back between new ones, mimicking the "hover method".
- "Legendary" status now applies to a whole unit.
- Quests and Practice Hub moved to bottom tabs.
- Characters cheer you along the path.

**Streak findings** ✅ (https://blog.duolingo.com/how-duolingo-streak-builds-habit/)
- Learners who reach a 7-day streak are **3.6× more likely to complete their course**.
- New streak-extension and milestone animations raised day-7 retention for new learners by **+1.7%**. See also https://blog.duolingo.com/streak-milestone-design-animation/ (exists, not read).
- Long streaks lean on **loss aversion**.
- Duolingo admits that breaking a streak demotivates people, and that fear of breaking one stops some from starting at all.
- The **Streak Freeze** is grounded in Penn/UCLA research showing that some "slack" beats rigid rules. Allowing **2 equipped freezes** raised daily active learners by +0.38%.
- Also exists, not read: https://blog.duolingo.com/improving-the-streak/

**Complaints** 🔶 (r/duolingo)
- Loss of freedom: you can't hover across several skills or look far ahead.
- Endless scrolling down a path makes it hard to revisit old material.
- Streaks turn into "the bare minimum to keep the number alive". The same Goodhart's-law critique shows up in HN discussions about streak anxiety.

**Helpful vs gimmicky for a senior engineer**
- Helpful:
  - A clear "next step".
  - Spaced review woven into the path.
  - Freezes, i.e. forgiveness.
  - A satisfying but brief completion moment.
- Gimmicky:
  - Guilt notifications, mascots, leagues and gems.
  - Strict linear locking.

---

## 5. Frontend Masters, now Master.dev

**Learning paths** ✅ (https://frontendmasters.com/learn/ and https://frontendmasters.com/learn/javascript/)
- The paths index is a card grid.
  - **Career paths:** Beginner, Professional, Expert (Lead/Staff), Computer Science (DSA), Fullstack, Design-to-Code.
  - **Topic paths:** JavaScript, React, AI Engineering, Node, and so on.
  - Each card has a tagline and a **total time** (e.g. "71 hours, 1 minute").
- A path page has:
  - The title with a **% progress** badge ("JavaScript 0%").
  - A one-paragraph promise.
  - A prerequisite line.
  - **"Core Coursework – Take these in order"**: the first item is labeled **"Up First"** and later items **"Up Next"**. Each comes with a **one-sentence reason** for why it comes at that point.
  - **"Elective Coursework – Optional, take in any order."**
  - Testimonials.
- Style: calm and editorial, with lots of whitespace and instructor faces. ❓

**Habit mechanics**
- Minimal. Motivation comes from the path % and curation, not streaks. 🔶/❓

**Worth copying**
- **"Up Next" with a reason**.
- Core (in order) vs Elective (any order).
- Total time per path.
- % on the path header.

---

## 6. Others worth knowing

**Exercism** 🔶
- Each language track has a **concept map** (a graph).
- Concept states: Locked (prerequisites missing; clicking explains which), Available, Completed (core exercise done), and **Mastered** (core plus all linked practice exercises).
- "Learning mode" enforces the order, and you can turn it off.
- Worth copying: separating **completed** from **mastered**.

**LeetCode Study Plans** 🔶
- Plans like Top Interview 150 are grouped by topic, with a progress ring broken down by Easy/Medium/Hard and a badge when finished.
- The daily challenge streak has **Time Travel Tickets** to make up missed days: 3 per month, current calendar year only.
- That's another forgiveness mechanic, but a heavily rule-bound one.

**Educative** 🔶 (generic sources, low confidence)
- A "Continue learning" card at the top of the dashboard that drops you back at the exact lesson.
- Course % bars, a streak counter, and Skill Paths that bundle courses.
- Users find the streak gimmicky for long reading sessions and the big paths overwhelming.

**Brilliant** 🔶/❓
- Single "continue" CTA at the top.
- A colourful node path.
- Animated streak flame built with Rive state machines (Rive case study, rive.app).
- Polished micro-interactions are its main appeal.

---

## SYNTHESIS for this platform

The repo already maps onto clean tracks:

| Track | Repo location |
|---|---|
| DSA | `dsa/01..13`, `MASTER_SHEET.md` |
| SDET Frameworks | `frameworks/{api-automation,ui-automation,design-challenges,sdet-system-design}` |
| System Design | `system-design/` |
| Core CS | `core-cs/` |
| AI Engineering | `ai-engineering/` |
| Mock Interviews | `mock-interviews/interview-N` |

`tools/tracker.py` and `tools/cycle.py` plus `PRACTICE_CYCLE.md` are the natural data sources for "where am I" and "what's next".

### A. Recommended home page, top to bottom

1. **Slim top bar** (AlgoExpert switcher plus roadmap.sh ⌘K)
   - Brand.
   - Track switcher dropdown, so you can jump straight to a track page.
   - ⌘K search over problems and topics.
   - **Consistency chip** in the NeetCode style, e.g. "🔥 12d · 5/7 this week".
   - Theme toggle, dark by default.
2. **"Today" hero card** (Duolingo/Brilliant/Educative single CTA plus Frontend Masters' "Up Next" reason)
   - One large primary button: **Continue: 3. Longest Substring w/o Repeat (Sliding Window)**.
   - A one-line *why*: "Next in Stage 1 of Cycle 4; unlocks Two-Pointer review."
   - At most 2–3 secondary items:
     - "Review due: 2 problems".
     - "Cycle stage: SDET framework module".
     - "Minimum day: 1 review (~15 min)".
3. **Readiness strip** (one quiet row)
   - Overall MAANG-readiness ring, e.g. a weighted % across tracks.
   - A 12-week activity heatmap.
   - Latest bar-raiser score trend, as a sparkline of `/interviewer` scores.
4. **Track cards grid**: 6 cards, 3×2 on desktop. This is the core "where am I" view. Each card has:
   - Track icon and accent color.
   - Big % plus counts, e.g. "47/150 · 31%".
   - **Mini-roadmap strip**: a segmented bar where each segment is a roadmap node coloured by state, with a ▲ "you are here" marker.
   - A "Now: Sliding Window (3/6)" line.
   - A "Next: …" line.
   - Last-touched time.
   - Click goes to the track's own page.
5. **Review queue**: a spaced-review list of items due to re-solve or re-explain, each with its interval. Duolingo builds review into the path, so this should feed the Today card too.
6. **Recent milestones and activity**: passed problems with scores, finished modules, mock interview results. Low emphasis, optionally collapsed.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◆ PrepHub   [Tracks ▾]        ⌘K Search…           🔥12d · 5/7 wk   ☾        │
├──────────────────────────────────────────────────────────────────────────────┤
│  Good morning, Yeshwin                                         Cycle 4 · S1  │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ CONTINUE ▸  Longest Substring Without Repeating Chars   [ Sliding Window ]│ │
│ │ Why next: finishes Sliding Window (3/6) → unlocks Two-Pointer review      │ │
│ │ [ ▶ Resume  ./run.sh test longest-substring ]                             │ │
│ │ ○ 2 reviews due  ○ SDET: RestAssured builder module  ○ Min day: 1 review  │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
│  Readiness ◔ 38%   ▁▂▃▅▃▆▇ last 12 wks   Bar-raiser trend 72→81→85           │
├──────────────────────────────────────────────────────────────────────────────┤
│ ┌── DSA ───────────────┐ ┌── SDET Frameworks ───┐ ┌── System Design ─────┐   │
│ │ 47/150 · 31%         │ │ 9/24 modules · 38%   │ │ Fund 6/12 · Cases 1/8│   │
│ │ ■■■■■■▣□□□□□□  ▲     │ │ ■■■▣□□□□             │ │ ■■■■■▣□□ | ■□□□□□□□  │   │
│ │ Now: Sliding Win 3/6 │ │ Now: API · Builder   │ │ Now: Caching         │   │
│ │ Next: Stack          │ │ Next: Allure report  │ │ Next: Design URL svc │   │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘   │
│ ┌── Core CS ───────────┐ ┌── AI Engineering ────┐ ┌── Mock Interviews ───┐   │
│ │ OS 40% Net 15% DB 0% │ │ 3/14 · 21%           │ │ 1 done · last 78/100 │   │
│ │ ■■▣□□ ■▣□□□ □□□□□    │ │ ■■■▣□□□□□□□□□□       │ │ score ▁▅  gaps: DS…  │   │
│ │ Now: Paging & VM     │ │ Now: RAG eval        │ │ Next: #2 (SDET arch) │   │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│ Review queue (due)           │ Recent                                        │
│ • Two Sum II — 7d interval   │ ✓ 3Sum passed 86/100 · 2d ago                 │
│ • Valid Parens — 3d interval │ ✓ API client module done · 4d ago             │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Why this design:**
- **One primary action above the fold.** Duolingo's path exists because people didn't know the "correct" next step ✅. Brilliant and Educative also lead with a single continue CTA 🔶.
- **Track cards rather than one giant graph.** roadmap.sh shows how a huge graph overwhelms 🔶, while AlgoExpert's product switcher and Frontend Masters' path card grid make several products easy to scan ✅.
- **Progress shown as a mini segmented strip.** It fuses NeetCode's per-node bars with roadmap.sh's per-node states into a glanceable "where am I".
- **Calm visual style.** Dark-first, one accent color per track, 6px bars like NeetCode, Geist or Inter for UI and a mono code font as AlgoExpert does. The one meaningful animation should be on completion, because that's what Duolingo measured to matter (+1.7% day-7 retention) ✅. Respect `prefers-reduced-motion`.

### B. Roadmap visualization per track (on each track's own page)

| Track | Visualization | Borrowed from | Notes |
|---|---|---|---|
| **DSA** | **Pattern dependency graph** (DAG of the 13 `dsa/` folders), each node showing a 6px bar and a count; clicking opens a **side panel** with the problems (Java ✓ / Python ✓ / score / review due) | NeetCode roadmap; Exercism concept map | Prerequisites are **soft** ("recommended after Two Pointers") and never hard-locked, which avoids the Duolingo/Exercism rigidity complaints. Add a list/accordion toggle like NeetCode and AlgoExpert's group-by-category view. |
| **SDET Frameworks** | **Module grid by layer** (API · UI · Design challenges · SDET system design), each with a checklist; within a module, **Core (in order) vs Elective** | Frontend Masters path page | Each module gets an "Up Next because…" line. |
| **System Design** | **Two tiers**: a linear Fundamentals path, then a case-study **card grid** (each card shows status plus self-rating) | SystemsExpert | Progress is "studied / drawn / explained aloud", not pass/fail. |
| **Core CS** | **Topic tree in 3 columns** (OS / Networks / DB) with roadmap.sh's four states and **Skip counting toward %** | roadmap.sh | A senior candidate can skip what they already know without hurting the %. |
| **AI Engineering** | **Linear path with optional side branches** (units with a "guidebook" summary note each) | Duolingo units/guidebook; roadmap.sh | Keep it short, with no more than about 15 nodes visible at once. |
| **Mock Interviews** | **Timeline of sessions** plus a **score trend line** and gap tags per rubric dimension; the next session shows as a "ghost" node | (Original; LeetCode badge idea) | The gaps should feed the review queue and the Today card. |

**One set of node states across all tracks** (roadmap.sh and Exercism, color plus text decoration so it never relies on color alone):
- `Not started`: outline only.
- `Up next`: accent ring with a soft pulse. Only **one** per track.
- `In progress`: violet fill with underlined label. This is roadmap.sh's `learning`.
- `Done`: green check, muted fill. For DSA this means both languages pass tests.
- `Mastered`: gold, like Duolingo's Legendary or Exercism's Mastered. For DSA: score ≥80 from `/interviewer` **plus** one spaced re-solve passed.
- `Skipped`: dim with strikethrough, and counted toward %.
- `Review due`: small amber dot overlaid on any done or mastered node.

Keyboard shortcuts on track pages, as in roadmap.sh: **D** done, **L** in progress, **S** skip.

### C. "Continue where you left off" and the daily loop
1. **Open → Today card.** The resume target comes from the last-touched item. If that item is finished, it comes from the cycle's active stage (`tools/cycle.py status`) and then the track's "Up next".
2. **Show one reason.** Frontend Masters writes "Up Next" with a reason, and that makes the suggestion trustworthy.
3. **Keep the floor low.** Offer a "minimum day" (one review or about 15 min) so the habit survives busy days. This follows Duolingo's own guidance about doing something quick to keep the streak.
4. **Mix in review.** Spaced re-solve intervals of roughly 1d → 3d → 7d → 21d after a pass. Duolingo builds review into the path ✅.
5. **Finish with a brief, tasteful celebration** (about 600ms: a check animation plus the track bar filling), then show **"Tomorrow: …"** so the next session is already decided.
6. **Make consistency forgiving.**
   - Lead with a **weekly target** (e.g. 5 of 7 days) and show the streak second.
   - Apply **2 freezes automatically** (Duolingo ✅) and **earn repairs at milestones** (NeetCode ✅).
   - No notifications or guilt copy. This is a local app you open by choice.
7. **Weekly recap** on the first open of the week: progress across tracks, review debt, the next cycle stage.

### D. Steal list
- AlgoExpert: a product/track switcher and one consistent design language; a curated list grouped by category with a counter per group; the two-tier System Design layout.
- roadmap.sh: the four states with fill **plus** text decoration; D/L/S shortcuts; skipped counts toward %; a "today" counter; ⌘K search.
- NeetCode: a pattern DAG with a mini bar inside each node; click opens a side panel; a streak chip in the nav; repairs earned at milestones; dark default with Geist.
- Duolingo: one obvious next step; spaced review woven into the path; units with guidebooks; Legendary/Mastered tier; freezes for forgiveness; animate only the completion moment.
- Frontend Masters: "Up First / Up Next" with a reason; Core (in order) vs Elective (any order); total time and % on each path header.
- Exercism: separate *completed* from *mastered*; locked nodes explain which prerequisites are missing (use as hints, not locks).

### E. Avoid list
- One giant zoomable graph as the home page. That's roadmap.sh's overwhelm problem; keep big graphs on the track pages.
- Hard-locked linear paths. That's the core Duolingo complaint, and a senior engineer needs to be able to jump around.
- Streak-only motivation, loss-aversion copy, mascots, leagues, XP and gems. They lead to bare-minimum Goodhart behaviour.
- Rule-heavy recovery like LeetCode's 3 tickets per month in the current year only.
- Pure done/not-done progress with no mastery or review signal. Users criticize Educative's progress for being binary 🔶.
- Upsell walls or anything gated, which is irrelevant locally. Also avoid dead-end "coming soon" tiles; show a planned track as a ghost card with a short outline instead.
- Dense dashboards with many equal-weight widgets. There should be one hero, one strip and one grid.

**What I couldn't verify:**
- AlgoExpert's exact layout, colors and per-category counter details.
- The per-node bar visuals on NeetCode's roadmap.
- The Educative and Brilliant specifics.

These came from search summaries rather than rendered pages. Checking the logged-in AlgoExpert and NeetCode screens by hand would be worthwhile before matching them pixel for pixel.
