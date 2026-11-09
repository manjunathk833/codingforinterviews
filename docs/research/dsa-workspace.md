# UX research: DSA track page and problem workspace (AlgoExpert-first)

## How reliable this is

- **Product details are only partly verified.** I ran about 20 web searches. When I tried to fetch the pages directly, the sites blocked me (for example, `learntocodewith.me` returned **HTTP 403 from Cloudflare**), so I could not look at the product pages themselves. I also had no screenshots.
- **Citations:** I cite the main product page for claims the searches backed up, for example https://www.algoexpert.io/product. The search tool only returned redirect links, not real article URLs.
- **Unverified claims are tagged.** **(UV)** means it comes from my own memory of the product and is not confirmed by any source I could reach. Check these against the live product before copying a pixel layout.
- **Repo context** (from `ls`): `dsa/` has 13 pattern folders, `01-arrays-and-hashing` through `13-design-and-concurrency`. Each problem has `README.md`, `Solution.java` and `solution.py`. The tracker is `tools/tracker.py` and the hint skill already uses 4 tiers. The design below is built to fit this.

---

## 1. AlgoExpert (main reference)

**What the searches confirmed** (https://www.algoexpert.io/product):
- About 200 hand-picked questions in 15 categories, with 4 difficulty levels: Easy, Medium, Hard, Very Hard.
- Every question has a video in two parts. Part one is a conceptual walkthrough on a whiteboard, including time and space complexity. Part two walks through the code line by line.
- Written solutions in 9 languages: JS, TS, Python, Swift, Kotlin, C++, Java, C#, Go.
- Hints for each question.
- A coding workspace with ready-made test cases.
- Extras: a data structures crash course, assessments and mock interviews.

**Workspace layout (UV, but I remember it fairly well):**
- The screen is a **2×2 grid of resizable panes**, each with tabs:
  - **Top-left:** `Prompt | Scratchpad`.
  - **Bottom-left:** `Our Solution(s) | Video Explanation`.
  - **Top-right:** `Your Solutions`, the editor, with tabs `Solution 1 / 2 / 3`. You can keep a brute-force version and an optimal version side by side.
  - **Bottom-right:** `Custom Output | Raw Output | Our Tests | Your Tests`.
- The searches confirmed these tab names exist: Our Solution, Video Explanation, Scratchpad, Your Tests, Our Tests. They did not confirm where each sits.
- A language dropdown sits above the editor. `Run Code` is a large button, and Cmd/Ctrl+Enter runs the code (the search mentions this, but loosely).
- Settings cover theme (light/dark), keybindings (Vim, Emacs, standard), font size and layout. The search summary mentions these, but I did not verify them first-hand.

**Learning flow and how solutions are kept hidden (UV):**
- The prompt shows the description, then a sample input and output.
- Below that are **`Hint 1…N` buttons**, each revealing one more hint. There is also a separate **"Optimal Space & Time Complexity"** button, so you can check the target Big-O without seeing the approach.
- The solution and the video are in their own tabs, so you only see them if you open them. Nothing is locked, but nothing is shown by default either. This "hidden until you open it" approach is AlgoExpert's main way of avoiding spoilers.

**Test experience (partly UV):**
- "Our Tests" is the fixed test suite. "Your Tests" lets you add your own cases.
- Test input is written as **JSON**. Trees and linked lists use a flat format: `{"nodes":[{"id","left","right","value"}],"root":"1"}` (the search confirmed this format).
- Results show one row per case, e.g. "Test Case N passed/failed". Each row expands to show **input, expected output and your output** (UV).
- "Raw Output" shows anything you printed (UV).

**Videos:**
- Recorded at 1080p. The instructor draws on a digital whiteboard, then codes in an editor.
- The video plays inside a workspace pane, so you can watch and type at the same time.
- Videos often run 20–40 minutes (UV).
- They are not linked to your code. No line highlighting, no chapter-to-step links (UV).

**Progress (UV):**
- The question list is grouped by category, with difficulty colours and a completed checkmark. A progress counter shows "X/200".
- There is no spaced review.

**Look and feel:** Clean, dark-first, lots of polish. Everything about one problem lives in one tab.

**Weaknesses people mention:**
- On Reddit, the common complaint is "the same explanations are free on YouTube" and the price.
- Others call the workspace a nice convenience rather than something unique.
- Some reviews of the companion products say the explanations are too high-level.
- My own guess, not sourced: four panes get cramped on a laptop, and the video pane is small.

## 2. LeetCode

**Layout:**
- The newer "dynamic layout" is made of tiles you can drag to resize and rearrange: Description / Editorial / Solutions / Submissions on one side, Code, then Testcase and Test Result.
- Panes can be maximised or collapsed, and opening the editorial can add a side panel. Source: https://leetcode.com, via the search summary.

**Keyboard shortcuts:** `Ctrl+'` runs, `Ctrl+Enter` submits, `Ctrl+M` toggles whether Tab indents or moves focus. Source: the search summary, from Reddit and LeetCode help pages.

**Tests:**
- **Run** uses the example cases. You can edit the case tabs or add a new one with "+".
- **Submit** runs the full hidden suite. It shows Accepted / Wrong Answer, runtime and memory percentiles, and for a failure, the input with your output and the expected output.
- Debugger with breakpoints and stepping, Premium only.

**Hiding spoilers (UV):** Hints sit as collapsed accordions at the bottom of the description. Topic tags are collapsed. The editorial is a separate tab, and many are Premium-only.

**Progress:** Study plans with daily schedules and progress bars, and favourites lists. There is no built-in spaced repetition (UV).

**Complaints on Reddit:**
- Buttons were moved: Run/Submit went to the top while your eyes stay at the console near the bottom.
- Menus keep changing.
- The editorial paywall.
- Custom test cases got harder to manage.
- Run results sometimes differ from Submit results.

## 3. NeetCode

**Structure:**
- The roadmap is an **interactive tree of about 18 pattern nodes**, each with a progress bar. Clicking a node opens that pattern's problem list with checkboxes, difficulty, a video link and a solution link. Source: https://neetcode.io/roadmap.
- Problem lists: Blind 75, NeetCode 150 and NeetCode 250.

**Problem page:**
- Left pane has tabs for Question, Solution and Video. Right pane is a code editor with Run and Submit. Source: https://neetcode.io, via the search summary.
- Written solutions are in many languages. Solving marks the problem done on the roadmap.

**Videos:**
- Free, on YouTube, usually 10–25 minutes (UV).
- The order is always the same: brute force and why it is too slow, then the optimal idea drawn by hand, then the code in Python.
- The drawings are rough and functional. The strength is clear thinking, not polish.

**Main lesson:** Order problems by pattern and dependency, and keep each video short and to the point.

**Weaknesses (UV):** Videos are Python-first, so Java users translate on their own. Videos are not linked to the code.

## 4. Educative, "Grokking the Coding Interview"

- **Patterns first:** Sliding Window, Two Pointers, Fast & Slow, Top-K, Monotonic Stack and so on. Each pattern has an intro lesson, then problems. Source: https://www.educative.io/courses/grokking-coding-interview.
- **Text, no videos.** Explanations use **slide decks you step through**: illustrations of arrays and pointers advancing one frame at a time with prev/next.
- **Runnable code** sits right in the lesson. A **"Try it yourself"** editor comes *before* the solution is shown, which is a simple spoiler gate.
- You pick a language for the whole course: Python, Java, JS, C++, Go or C#.
- An AI mentor explains highlighted text and gives feedback on your code.
- **Weaknesses (UV):** reading heavy, small editors, and a subscription paywall.

## 5. Algorithm visualizers

**VisuAlgo** (https://visualgo.net):
- Canvas in the centre, with **media-player controls**: play, pause, step back, step forward, speed slider.
- A **pseudocode box with the current line highlighted** at bottom-right.
- **A plain-English status line** explaining the current step (UV, but this is a defining feature).
- **Custom input:** create your own array, or draw your own graph.
- "e-Lecture" mode: slides with quizzes. Esc switches to free exploration, PageUp/PageDown flips slides.

**Python Tutor** (https://pythontutor.com):
- Code on the left. A **green arrow marks the line that just ran and a red arrow the next line.**
- Below the code: First, Prev, Next, Last buttons and a **slider to jump to any step**.
- On the right: **Frames** (the call stack) and **Objects** (the heap), with **arrows from variables to objects**. This is ideal for linked lists and aliasing. Output builds up below.
- **Supports Java, C, C++, JS and Python.**
- How it works: it runs the program once, records every step, then lets you replay them.
- Programs are capped at a step limit (UV).

**algorithm-visualizer.org** (https://algorithm-visualizer.org):
- You add **"tracer"** calls to your code (`Array1DTracer`, `GraphTracer`, `LogTracer`). Those calls emit visual commands, which play back with the matching code line highlighted. Source: https://github.com/algorithm-visualizer/tracers.js.
- **Downside:** the visualization calls clutter the solution code.

## 6. AlgoMonster (notable idea)

- **"Which pattern?" flowchart:** a decision tree that asks questions like "sorted input?" or "min/max?" and ends at a pattern. Source: https://algo.monster/flowchart.
- **A reusable code template** for each pattern.
- **Speedrun mode:** multiple-choice drills on recognising the pattern.
- The search summary notes there is no built-in spaced repetition.

---

## 7. How explanation videos get made

| Approach | Typical effort per finished minute | Value | Fit for a solo creator with AI help |
|---|---|---|---|
| Screen-recorded whiteboard plus code (NeetCode, AlgoExpert) | About 1–2 hours (estimate from the search summary) | Natural reasoning, high trust | Needs you on mic for every video. Clear but doesn't scale. |
| Excalidraw: pre-draw the structures, then record live | About 2–4 hours | Clean, flexible | Middle ground |
| Manim (Python), with the `manim-voiceover` plugin (TTS, `tracker.duration` timing) | **About 10–30+ hours** (Reddit estimate via the search) | Most polished | A slow render loop. AI can draft scenes, but debugging the layout eats time. Only worth it for a few signature pattern intros. |
| Motion Canvas (TypeScript, live timeline editor) | Less than Manim | Best for code-highlighting layouts | A good choice if you want rendered video files |
| **Narrated playback of the platform's own visualizer** | **Lowest once built:** step data plus TTS script per step, recorded headlessly | Visuals always match the interactive tool | **Recommended.** Reuses the same data and gives "chapters = steps" for free |

---

## 8. Synthesis: recommended design

### 8.1 DSA track page

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ DSA ▸ Track     [Search ⌘K]   Filter: Diff ▾  Status ▾  Lang: Py|Java|Both    │
├──────────────┬───────────────────────────────────────────────────────────────┤
│ PATTERNS     │  ▶ CONTINUE: 15-3sum (Java pending)   ⟳ REVIEW DUE: 4  [Start]│
│ ◐ 01 Arrays  │  Overall ███████░░░ 42/120 · Py 51 · Java 44 · Avg score 86   │
│ ◑ 02 Two Ptr │───────────────────────────────────────────────────────────────│
│ ○ 03 Sliding │  02 · TWO POINTERS        ██████░░ 6/9    [Pattern primer ▶]   │
│ ○ 04 Stack   │  Template · When to use · 3-min concept video · Which-pattern? │
│ ...          │───────────────────────────────────────────────────────────────│
│ ○ 13 Design  │  #   Problem            Diff  Py  Java Score Hints Next review│
│──────────────│  125 Valid Palindrome    E    ✓   ✓    92    0    in 12d      │
│ [Tree view]  │  15  3Sum                M    ✓   ·    —     2    —           │
│ [List view]  │  11  Container w/ Water  M    ·   ·    —     —    —   🎬 👁   │
└──────────────┴───────────────────────────────────────────────────────────────┘
```

- **Left rail:** the 13 pattern folders, each with a progress ring. Add a toggle for a NeetCode-style **tree view** that shows which patterns build on which.
- **Pattern header:** an Educative-style primer, an AlgoMonster-style template, a short concept video, and a link to the "Which pattern?" flowchart.
- **Problem rows:** show **Python and Java status separately**. A problem is "done" only when both pass. Show the interviewer score, hints used and next review date. Icons mark whether a video (🎬) or a visualization (👁) exists.
- **Top strip:** a "Continue" card and the **review queue**.

### 8.2 Problem workspace (AlgoExpert grid, adjusted)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ ← Two Pointers │ 15 · 3Sum  [M]  ⏱ 18:42   Py ✓  Java ●   ◀ ▶ │ Run ⌘↵ │ Check ⌘⇧↵ │
├──────────────────────────────┬───────────────────────────────────────────────────┤
│ Prompt│Hints│Scratch│Visual│ │ [Python] [Java]   dsa/02-two-pointers/15-3sum/     │
│ Solution🔒│Video🔒│Notes     │ solution.py   ● unsaved → ✓ saved to disk          │
│                              │ 1 class Solution:                                 │
│  Given an integer array...   │ 2   def threeSum(self, nums):                     │
│  Example 1: ...              │ 3     nums.sort()                                 │
│  Constraints: ...            │ ...                                               │
│  ─────────────               ├───────────────────────────────────────────────────┤
│  [Hint 1] [Hint 2] [Hint 3]  │ Tests │ Custom │ Output │ Diff                     │
│  [Hint 4: scaffold]          │ ✓ case1  ✓ case2  ✗ case3 [dupes]  ✓ case4        │
│  [Reveal optimal O()]        │ case3  input: [-1,0,1,2,-1,-4]                     │
│                              │   expected [[-1,-1,2],[-1,0,1]]  got [[-1,0,1]...] │
└──────────────────────────────┴───────────────────────────────────────────────────┘
   default: left 38% │ right 62% (editor 65% / console 35%) — all resizable, sizes remembered
```

**Panes:**
- **Left:** tabs Prompt (from `README.md`), Hints, Scratchpad, Visualize, Solution, Video, Notes.
- **Right top:** the editor, with Python/Java tabs, the real file path and a save indicator.
- **Right bottom:** tabs Tests, Custom, Output, Diff.

**Panel states:**

| State | Left | Editor | Console | Notes |
|---|---|---|---|---|
| Reading | 50% | 50% | collapsed | Prompt has focus, timer not started |
| Coding | 35% | 65% | 25% | Timer starts on first keystroke. Autosave about 1s after you stop typing |
| Running | 35% | 65% | grows to 40% | Jumps to the first failing case and opens Diff |
| Reviewing | 50% (Solution / Video / Visual) | 50%, read-only split diff of your code vs the reference | collapsed | Self-rating prompt for the review schedule |

**Keyboard shortcuts:**
- `⌘↵` run, `⌘⇧↵` check / mark as passed
- `⌘1` / `⌘2` switch Python / Java
- `⌘J` toggle console, `⌘B` toggle left pane, `⌘.` next hint
- In Visualize: `←` / `→` step, `Space` play/pause
- `⌘K` search problems

**Saving to real files:**
- Watch the file on disk. If it changes outside the browser (for example in your IDE), show a banner: **"Changed on disk — Reload / Keep mine"**.
- Put each language's file path in its tab.

**Tests:**
- Use **one shared `tests.json` per problem**, read by both a Python and a Java runner, so results come back case by case.
- Today the solutions only have assertions inside `main()`, which gives a single pass/fail.
- Show expected vs actual as a **structural diff** (JSON-aware, highlighting the differing element).
- Allow comparing unordered results for problems like "any order".
- Render trees and linked lists as small pictures, not raw JSON.

### 8.3 Learning flow and keeping solutions hidden

1. **Read.**
2. **Plan in the Scratchpad.** Optional prompt: "pattern? complexity target?"
3. **Code in language A.**
4. **Run.**
5. **Hints, 4 tiers**, matching the existing `/hint` skill: mental model → pattern → invariant → scaffold. Each reveal is a deliberate click and **gets recorded** (hints used, time).
6. **Pass in A, then port to language B.** Show a nudge listing Java vs Python gotchas.
7. **Solution, Video and Visual unlock** after both languages pass, *or* after 25 minutes / 3 failed runs. Before that they stay behind a soft gate: "Reveal anyway? This is logged."
8. **Review:** compare against the reference, give a 1–4 self-rating, and optionally hand off to `/interviewer`.
9. **Schedule the next review** with SM-2-style intervals (1, 3, 7, 14, 30 days). Shorten the interval if hints were used or the solution was revealed.

The "Optimal complexity" reveal stays separate and cheap, as on AlgoExpert.

### 8.4 How the visualizer and videos connect to the editor

**One step-data file per problem drives everything** (for example `trace.json`):
- Each step records the line in `solution.py` and the line in `Solution.java`.
- It records the state: arrays with labelled pointers (i, j, l, r), hash maps, stacks/queues, and trees or linked lists drawn with reference arrows (Python Tutor style).
- It holds a **one-sentence caption** (VisuAlgo's status line).

**How the file is produced:** run the Python reference solution with Python's line tracer (`sys.settrace`) or a small capture helper, then let AI write the captions. Keep any instrumentation **out of the solution files**, to avoid algorithm-visualizer.org's clutter problem.

**Visualize tab:**
- Canvas plus step controls, a speed slider and a scrub bar.
- Highlights the current line in the editor's *read-only reference view*. Green means the line just ran, red the next line (Python Tutor).
- Accepts custom input: re-run the trace on your own case, e.g. a failing test. Offer "Visualize this failing case" from the Diff tab.
- Stretch goal: trace the *user's own Python code* for debugging.

**Video:**
- Generated as a narrated playback of the same steps: TTS per caption, then a headless browser recording (Playwright) and ffmpeg.
- Chapters: **Concept (visual)**, then **Python walkthrough**, then **Java differences**.
- Clicking a chapter, or the transcript, jumps the visualizer to that step, and the reverse works too.
- Target length 5–10 minutes.
- Use Manim or Motion Canvas only for about 13 pattern intro videos.

### 8.5 Steal list
- AlgoExpert: the grid of tabbed panes, **multiple solution slots** (brute force vs optimal), hint buttons, the separate **"Optimal Space & Time" reveal**, the Raw Output tab, a two-part video (concept, then code), JSON test input with the flat tree format.
- LeetCode: tiles you can resize and collapse, with sizes remembered; Run vs Submit/Check split; a test-case tab per case with "+"; **expected vs output shown per case**; topic tags hidden by default.
- NeetCode: pattern roadmap tree with progress bars; brute force → optimal → code video structure; short videos.
- Educative: "Try it yourself" before the solution; step-through slides inside the explanation.
- VisuAlgo: media-player controls, pseudocode line highlight, **plain-English caption per step**, custom input.
- Python Tutor: green/red line arrows, step slider, frames/heap with reference arrows, Java support.
- AlgoMonster: "Which pattern?" flowchart, a template per pattern, a recognition speedrun.

### 8.6 Avoid list
- Moving Run/Check away from where your eyes are, as LeetCode did. Keep it in the top bar *and* bind it to `⌘↵`, and never move it.
- Hiding learning content behind a paywall or hard lock. Use logged soft gates instead.
- 30–40 minute videos with no chapters, and videos not linked to the code.
- Python-only explanations when the user also solves in Java. Always add a Java differences section.
- Visualization calls inside the solution files.
- A single pass/fail from assertions in `main()`. Report case by case.
- Showing the solution on the same screen as the prompt.
- Four panes cramped on a laptop. Offer a focus mode (editor plus console only) and remember pane sizes.
- Run results that differ from Check results. Run both through the same runner on the same files.
