---
slug: aiqa-05-llm-judge-biases-and-pairwise-swap-debiasing
course_id: 06-ai-engineering-qa-focused
track: ai-engineering
volume: "06. Zero to Mastery: AI Engineering — QA Focused"
module_number: 3
module_title: "Module 3: Calibrating LLM-as-a-Judge (AeroEval v0.5 → v0.6)"
chapter_number: 5
level_tag: "🌳 Senior → Staff AI QA"
title: "Build AeroEval v0.5: LLM-as-a-Judge Biases, Pairwise (A,B)/(B,A) Swaps & Binary Rubrics"
summary: "Why naive 1-to-10 LLM judges reward bloated essays and favor Slot 1, and how to upgrade AeroEval v0.5 with Bidirectional Pairwise Swap Debiasing and Evidence-First Binary Rubrics."
reading_time_minutes: 22
visualizer_id: "aiqa-judge-calibration"
lab_path: "ai-engineering/04-llm-judge-calibration-and-redteam"
tags: ["ai-engineering", "ai-qa", "aeroeval", "llm-as-a-judge", "position-bias", "verbosity-bias", "pairwise-swap", "rubric-design"]
---

# Build AeroEval v0.5: LLM-as-a-Judge Biases, Pairwise (A,B)/(B,A) Swaps & Binary Rubrics

```json continuity
{
  "previously": "In Chapter 04, we built `AeroEval v0.4` with per-citation span checks, numeric entity guards, NLI cross-encoder contradiction scoring, and the 2x2 Abstention Matrix.",
  "painPoint": "Our team wanted to compare `AeroBrain Prompt V2` against `Prompt V1` on 200 complex customer scenarios using an LLM-as-a-Judge. When we put V2 in Slot A and V1 in Slot B, the judge said V2 won 64% of the time! But when an engineer swapped the slots (V1 in Slot A, V2 in Slot B), the exact same judge said V1 won 58% of the time!",
  "unlock": "Upgrade to `AeroEval v0.5`: neutralize Position Bias with Bidirectional `(A,B)/(B,A)` Swap Debiasing, defeat Verbosity Bias, and enforce Evidence-First Binary Decomposition Rubrics!"
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Slide 1 / 4 · Catching the Slot-1 Primacy Illusion",
    "caption": "LLM judges love whichever answer is shown first (or last)! If you always pass your new prompt in Slot 1, a 22% Position Bias makes a useless prompt change look like a massive breakthrough.",
    "code": "# Pass 1: Judge(Slot1=V2, Slot2=V1) -> Picks 'SLOT_1' (V2)\n# Pass 2: Judge(Slot1=V1, Slot2=V2) -> Picks 'SLOT_1' (V1!)\n# Both passes just picked Slot 1! It's Position Bias, not a real win!"
  },
  {
    "time": "0:25",
    "badge": "Slide 2 / 4 · Bidirectional (A,B) + (B,A) Swap Protocol",
    "caption": "AeroEval v0.5 runs EVERY pairwise comparison twice: once as (X, Y) and once flipped as (Y, X). A candidate only wins if the judge selects that exact candidate in BOTH positions; otherwise it's scored as a Tie (0.5)!",
    "code": "pick_forward = judge(slot1=resp_x, slot2=resp_y)  # -> 'X'\npick_reverse = judge(slot1=resp_y, slot2=resp_x)  # -> 'X'\nwinner = pick_forward if (pick_forward == pick_reverse) else 'TIE'"
  },
  {
    "time": "0:53",
    "badge": "Slide 3 / 4 · Why JSON Key Order Changes Accuracy by 12%!",
    "caption": "LLMs generate JSON strictly left-to-right! If 'passed: true' is the FIRST key in your schema and 'reasoning' is SECOND, the model guesses true on token #1 and rationalizes an excuse after! Always put evidence BEFORE the boolean!",
    "code": "# ✗ Bad Schema:  {\"passed\": true, \"critique\": \"...\"}\n# ✓ Staff Schema: {\"evidence_quotes\": [...], \"critique\": \"...\", \"passed\": true}"
  },
  {
    "time": "1:18",
    "badge": "Slide 4 / 4 · Replacing 1-10 Likert Scales with Binary Checklists",
    "caption": "What is the difference between a 7/10 and an 8/10? Even the LLM doesn't know! AeroEval v0.5 replaces mushy 1-10 scores with 4 crystal-clear YES/NO boolean checks.",
    "code": "rubric = {\n    \"grounded_in_context\": True,\n    \"answers_user_intent\": True,\n    \"free_of_redundant_fluff\": False  # Penalizes Verbosity Bias!\n}"
  }
]
```

```json pretraining
[
  {
    "term": "Position Bias (Slot Asymmetry)",
    "formula": "Judge(A, B) ≠ Judge(B, A)",
    "meaning": "When comparing two answers side-by-side, LLM judges systematically favor whichever answer is placed in Slot 1 (or Slot 2), flipping their vote on 15%–35% of close comparisons when you swap the order."
  },
  {
    "term": "Verbosity / Formatting Bias",
    "formula": "Score ∝ TokenLength + MarkdownBullets",
    "meaning": "Unchecked LLM judges give higher scores to long, polite, bullet-pointed essays even when a crisp 2-sentence answer is more accurate."
  },
  {
    "term": "Self-Preference (Narcissism) Bias",
    "formula": "P(Judge_M prefers Output_M) > Human",
    "meaning": "An LLM judge grades answers written by its own model family more generously because the wording matches its own favorite writing style."
  },
  {
    "term": "Binary Rubric Decomposition",
    "formula": "Evidence First → Σ boolean_check_i ∈ {0, 1}",
    "meaning": "Replacing unstable 1-to-10 ratings with specific YES/NO checklist questions where the judge must quote evidence before outputting true or false."
  }
]
```

```json poe
{
  "question": "You pit Prompt V2 against Prompt V1 using an LLM-as-a-Judge pairwise prompt where V2 is always passed as 'Assistant A' and V1 as 'Assistant B'. The judge reports V2 wins 64% of cases! When you swap the template slots (V1 as 'Assistant A', V2 as 'Assistant B'), V1 wins 58% of cases! What happened, and what is the unbiased win rate?",
  "options": [
    "Both V1 and V2 improved simultaneously during evaluation",
    "The judge exhibits strong Primacy Position Bias (~22% slot-1 tilt); any pair where Judge(A,B) and Judge(B,A) both pick 'Slot 1' is positionally inconsistent and must be scored as a Tie (0.5), revealing V2's true consistent win rate is ~53% (statistically flat)",
    "Pairwise evaluation is mathematically invalid and must be replaced with 1-100 integer scores",
    "Setting judge temperature to 1.2 eliminates position bias"
  ],
  "answerIndex": 1,
  "explanation": "Zheng et al. (MT-Bench / Chatbot Arena) proved LLM judges exhibit heavy slot primacy/recency bias. Running BOTH orders (A,B) and (B,A) and only awarding a win when BOTH orders select the exact same underlying model response cancels first-order slot bias."
}
```

## 🌱 Step 1: Plain-English Story — The Four Cognitive Biases of `LLM-as-a-Judge`

Using a strong LLM (`LLM-as-a-Judge`) to grade thousands of `AeroBrain` answers overnight feels like magic—until you discover that an uncalibrated judge behaves like a tired professor grading essays at 2:00 AM:

1. **Position Bias (`15%–35%` Flip Rate)**: When asked *"Which answer is better: Assistant A or Assistant B?"*, LLM judges have a massive habit of picking whichever answer sits in Slot A! If you always put your new prompt in Slot A, you will celebrate fake "wins" every week.
2. **Verbosity & Pretty-Formatting Bias**: Add three repetitive bullet points and a polite *"I would be delighted to help!"* to a mediocre answer, and a naive judge boosts its score by **$+20\%$**!
3. **Self-Preference (Narcissism) Bias**: If `Model X` judges a contest between `Model X` and `Model Y`, it prefers `Model X`'s phrasing style.
4. **The `7-out-of-10` Mushy Scale**: Ask an LLM to *"Rate this answer from 1 to 10,"* and it gives `7` or `8` to almost everything—while flipping between `7` and `8` randomly across runs!

```mermaid
flowchart LR
  Pair["Candidate Pair (Resp_X, Resp_Y)"] -->|Pass 1: Order (X, Y)| J1["Judge Call 1 (Quote Evidence First)"]
  Pair -->|Pass 2: Swapped (Y, X)| J2["Judge Call 2 (Quote Evidence First)"]
  J1 & J2 --> Gate["Did Both Calls Pick the Same Candidate?"]
  Gate -->|Yes: Consistent!| Win["Award True Win (X or Y)"]
  Gate -.->|No: Slot Flip!| Tie["Score as 0.5 Tie (Position Bias Cancelled)"]
```

Let's upgrade **`AeroEval v0.5`** with **Bidirectional `(A,B)/(B,A)` Swap Debiasing** and **Evidence-First Binary Rubrics**!

## 🔨 Step 2: First Lines of Code — Build the Bidirectional Swap Judge in 14 Lines!

Look how `AeroEval v0.5` eliminates **Position Bias**: we call the judge twice—once with `(resp_x, resp_y)` and once swapped as `(resp_y, resp_x)`—and only award a win if **both** calls pick the exact same underlying candidate!

```python
from typing import Callable


def judge_pairwise_debiased(
    query: str,
    resp_x: str,
    resp_y: str,
    raw_judge: Callable[[str, str, str], str],
) -> str:
    """
    AeroEval v0.5: raw_judge(query, slot_1, slot_2) returns 'SLOT_1', 'SLOT_2', or 'TIE'.
    Runs both (X, Y) and (Y, X) so Slot-1 primacy bias cancels out completely!
    """
    v_xy = raw_judge(query, resp_x, resp_y)
    pick_1 = "X" if v_xy == "SLOT_1" else ("Y" if v_xy == "SLOT_2" else "TIE")

    v_yx = raw_judge(query, resp_y, resp_x)  # Swapped slots!
    pick_2 = "Y" if v_yx == "SLOT_1" else ("X" if v_yx == "SLOT_2" else "TIE")

    return pick_1 if (pick_1 == pick_2) else "TIE"


# Even if a biased judge ALWAYS returns "SLOT_1", watch how AeroEval v0.5 forces a fair "TIE":
print("Verdict:", judge_pairwise_debiased("Refund rule?", "Ans X", "Ans Y", lambda q, s1, s2: "SLOT_1"))
```

### Java 17 Equivalent

```java
import java.util.function.BiFunction;

public class AeroEvalV05SwapJudge {
    public enum SlotPick { SLOT_1, SLOT_2, TIE }

    public static String judgePairwiseDebiased(
            String respX, String respY, BiFunction<String, String, SlotPick> rawJudge) {
        SlotPick forward = rawJudge.apply(respX, respY);
        String pick1 = (forward == SlotPick.SLOT_1) ? "X" : (forward == SlotPick.SLOT_2 ? "Y" : "TIE");

        SlotPick reverse = rawJudge.apply(respY, respX); // Swapped slots!
        String pick2 = (reverse == SlotPick.SLOT_1) ? "Y" : (reverse == SlotPick.SLOT_2 ? "X" : "TIE");

        return pick1.equals(pick2) ? pick1 : "TIE";
    }
}
```

## ⚡ Step 3: Where It Breaks in Real Life — Why JSON Field Order Breaks Chain-of-Thought!

Here is a subtle failure mode that trips up even Senior AI Engineers when building structured `LLM-as-a-Judge` evaluators:

Suppose you use Structured Outputs (`response_format` / Pydantic / Java Record) for your judge, and you define the schema like this:
`{"passed": bool, "reasoning": str}`

**Why does putting `"passed"` first drop judge accuracy by `8%–15%`?**
Because LLMs generate tokens **strictly left-to-right (autoregressively)**! When `"passed"` is the first key in the JSON object, the LLM is forced to output `true` or `false` on its **very first token**—*before* it has done a single step of reasoning! Then, when it generates `"reasoning"` second, it simply writes an excuse to justify whatever boolean it already guessed!

By flipping the schema order so `"evidence_quotes"` and `"step_critique"` come **before** `"passed"`, the boolean token attends over the completed reasoning!

```json contrast
{
  "title": "LLM-as-a-Judge Prompt & Scoring Architecture",
  "naiveTitle": "Single-Pass 1-10 Likert Score",
  "naiveMetric": "κ = 0.34 Human Agreement · Verbose Bias",
  "naivePoints": [
    "Asks 'Score helpfulness from 1 to 10' with verdict emitted on the first JSON key",
    "Evaluates pairwise A/B in a single fixed slot order (Candidate_New always in Slot A)",
    "Uses the exact same model checkpoint as both Generator and Judge",
    "Rewards 600-word rambling essays over crisp, complete 80-word answers"
  ],
  "staffTitle": "Swap-Debiased Binary Rubric + Length Penalty",
  "staffMetric": "κ = 0.81 Human Agreement · Slot-Invariant",
  "staffPoints": [
    "Decomposes quality into 4 orthogonal YES/NO binary checks with CoT evidence generated BEFORE boolean keys",
    "Executes mandatory (A,B) + (B,A) bidirectional swap; inconsistent flips default to Tie",
    "Uses cross-family judge (or held-out human calibration set) to eliminate self-preference",
    "Applies conciseness check / length-controlled win-rate normalization against fluff padding"
  ]
}
```

## 🚀 Step 4: Staff Engineer Deep-Dive — Swap-Debiased Win Rate & Verbosity Skew Math

Let $J(A, B) \in \{1, 0, \frac{1}{2}\}$ denote the raw judge's score for candidate $A$ when presented in order $(A, B)$, where $J(A, B) = 1$ means Slot 1 won and $J(A, B) = 0$ means Slot 2 won. If the judge suffers from additive slot primacy bias $+\delta$, then in a single fixed order:

$$\mathbb{E}[J(X, Y)] = p_{\text{true}}(X \succ Y) + \delta$$

By running **both** $(X, Y)$ and $(Y, X)$ across $N$ evaluation pairs and defining the **Swap-Debiased Score** $S_i(X, Y)$:

$$S_i(X, Y) = \frac{J(X_i, Y_i) + \bigl(1 - J(Y_i, X_i)\bigr)}{2} \in \{1.0, \; 0.5, \; 0.0\}$$

the first-order slot bias $+\delta$ in pass 1 and $-\delta$ in pass 2 cancel identically! We also track the **Position-Flip Diagnostic Rate** ($\text{FlipRate} = \frac{1}{N}\sum \mathbb{I}[\text{pick}_{XY} \ne \text{pick}_{YX}]$) and **Verbosity Skew Ratio** (fraction of decisive wins where the winning response was $>1.3\times$ longer than the loser).

| Judge Topology | API Cost per Case | Best Use Case | Primary Bias Vulnerability | Mandatory Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Pointwise Binary Rubric** (`PASS`/`FAIL` per criterion) | $1\times$ Judge call | Absolute CI/CD release gates (`Faithfulness`, `Tone`, `Abstention`) | Mild leniency drift ("Yes-man" sycophancy) | Include explicit negative few-shot anchors + calibrate $TPR/TNR$ on human gold set |
| **Pairwise Bidirectional Swap** (`(A,B)` + `(B,A)`) | $2\times$ Judge calls | Prompt A vs. Prompt B or Model bake-offs on subtle quality | Verbosity & Markdown formatting bias | Enforce `Swap Consistency` + strip decorative formatting / penalize redundant length |
| **Reference-Guided Judge** *(Compares against `must_include_claims`)* | $1\times$ Judge call | Complex domain math, legal clauses, multi-hop reasoning | Over-penalizing valid extra context | Anchor strictly on atomic claim checklist rather than surface phrasing |

### Production Blueprint: Bidirectional Pairwise Swap Judge & Verbosity-Bias Auditor

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PairwiseOutcome:
    winner: str  # "X", "Y", or "TIE"
    position_consistent: bool
    length_ratio_xy: float


def evaluate_pairwise_debiased(
    query: str,
    resp_x: str,
    resp_y: str,
    raw_judge_fn: Callable[[str, str, str], str],
) -> PairwiseOutcome:
    """
    raw_judge_fn(query, slot_1, slot_2) returns 'SLOT_1', 'SLOT_2', or 'TIE'.
    Executes both (X, Y) and (Y, X) to cancel slot position bias.
    """
    # Forward pass: Slot_1 = X, Slot_2 = Y
    v_forward = raw_judge_fn(query, resp_x, resp_y)
    forward_pick = "X" if v_forward == "SLOT_1" else ("Y" if v_forward == "SLOT_2" else "TIE")

    # Swapped pass: Slot_1 = Y, Slot_2 = X
    v_reverse = raw_judge_fn(query, resp_y, resp_x)
    reverse_pick = "Y" if v_reverse == "SLOT_1" else ("X" if v_reverse == "SLOT_2" else "TIE")

    consistent = forward_pick == reverse_pick
    final_winner = forward_pick if consistent else "TIE"
    len_ratio = round(len(resp_x.split()) / max(1, len(resp_y.split())), 3)
    return PairwiseOutcome(winner=final_winner, position_consistent=consistent, length_ratio_xy=len_ratio)


def summarize_ab_tournament(outcomes: list[PairwiseOutcome]) -> dict:
    n = max(1, len(outcomes))
    x_wins = sum(1 for o in outcomes if o.winner == "X")
    y_wins = sum(1 for o in outcomes if o.winner == "Y")
    ties = sum(1 for o in outcomes if o.winner == "TIE")
    inconsistent = sum(1 for o in outcomes if not o.position_consistent)

    # Check verbosity bias: how often did the strictly longer (>1.3x words) answer win?
    longer_wins = sum(
        1 for o in outcomes
        if (o.winner == "X" and o.length_ratio_xy > 1.3)
        or (o.winner == "Y" and o.length_ratio_xy < (1.0 / 1.3))
    )
    decisive = max(1, x_wins + y_wins)

    return {
        "xWinRate": round((x_wins + 0.5 * ties) / n, 4),
        "positionFlipRate": round(inconsistent / n, 4),
        "verbositySkewRatio": round(longer_wins / decisive, 4),
        "wins": {"X": x_wins, "Y": y_wins, "TIE": ties},
    }
```

### Java 17 Equivalent

```java
import java.util.List;

public final class DebiasedJudgeEngine {
    public enum SlotChoice { SLOT_1, SLOT_2, TIE }

    /**
     * Notice field order: evidenceQuotes and stepCritique MUST precede boolean verdicts
     * in JSON generation so autoregressive decoding reasons BEFORE committing to a boolean!
     */
    public record BinaryRubricVerdict(
            List<String> evidenceQuotes,
            String stepCritique,
            boolean groundedInContext,
            boolean answersUserIntent,
            boolean freeOfRedundantFluff) {
        public boolean overallPass() {
            return groundedInContext && answersUserIntent && freeOfRedundantFluff;
        }
    }

    public static String reconcileBidirectionalSwap(SlotChoice forwardXY, SlotChoice reverseYX) {
        String pick1 = switch (forwardXY) {
            case SLOT_1 -> "CANDIDATE_X";
            case SLOT_2 -> "CANDIDATE_Y";
            case TIE -> "TIE";
        };
        String pick2 = switch (reverseYX) {
            case SLOT_1 -> "CANDIDATE_Y"; // In reverse pass, Slot 1 holds Y!
            case SLOT_2 -> "CANDIDATE_X";
            case TIE -> "TIE";
        };
        return pick1.equals(pick2) ? pick1 : "TIE_POSITION_BIAS_CANCELLED";
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Why JSON Key Order Inside Structured Outputs Alters Judge Accuracy by `8%–15%`**:
> With constrained decoding (`response_format` / JSON Schema), tokens are sampled strictly in the order keys appear in the schema. If `"pass": boolean` is the **first** field in your Pydantic/Record schema and `"reasoning": str` is the **second**, Chain-of-Thought happens *after* the decision is already locked in! Always place `evidence_spans` and `critique` **above** `verdict` in your structured judge schema.

**Up Next in Chapter 06**: Even after we debias slot order and use binary rubrics in `AeroEval v0.5`, no LLM judge is 100% accurate—what if our judge has `92%` Sensitivity and `80%` Specificity? In Chapter 06, we'll see why a `90%`-accurate judge still distorts your dashboard pass rate by `5%+`, and upgrade to **`AeroEval v0.6`: Cohen's Kappa ($\kappa$) & Rogan-Gladen Prevalence Correction**!

```json quiz
[
  {
    "id": "aiqa-05-q1",
    "question": "In a Pairwise Swap evaluation between Model X and Model Y, Pass 1 (Slot1=X, Slot2=Y) outputs 'SLOT_1' and Pass 2 (Slot1=Y, Slot2=X) ALSO outputs 'SLOT_1'. How must the harness score this test case?",
    "options": [
      "Award 1 win to Model X because Pass 1 ran first",
      "Record an inconclusive TIE (0.5 each) and increment the Position-Flip diagnostic metric, because the judge selected Slot 1 regardless of which model occupied it",
      "Average the character lengths of X and Y",
      "Re-run Pass 1 until it outputs SLOT_2"
    ],
    "answerIndex": 1,
    "explanation": "When both (X,Y) and (Y,X) pick 'SLOT_1', the judge's preference was driven by slot primacy rather than response quality; treating flips as ties neutralizes first-order position bias."
  },
  {
    "id": "aiqa-05-q2",
    "question": "Why must structured JSON schemas for LLM-as-a-Judge place 'extracted_evidence' and 'critique' fields BEFORE the boolean 'passed' field?",
    "options": [
      "Because alphabetical JSON sorting fails in Python",
      "Because autoregressive LLMs condition each token only on preceding tokens; emitting 'passed' first forces a zero-step intuition guess followed by post-hoc rationalization, whereas generating critique first conditions the verdict on explicit reasoning",
      "Because HTTP/2 streams drop boolean fields at byte 0",
      "Because Pydantic rejects boolean fields in position 0"
    ],
    "answerIndex": 1,
    "explanation": "Causal attention masks mean token t can only attend to tokens < t. Placing reasoning keys first gives the verdict token full attention over the extracted evidence and critique."
  },
  {
    "id": "aiqa-05-q3",
    "question": "Why do Staff AI QA teams replace 1–10 Likert prompts ('Rate quality 1 to 10') with orthogonal Binary Decomposition checklists?",
    "options": [
      "Because JSON does not support integer types",
      "Because unanchored mid-scale integers (e.g., 6 vs 7 vs 8) have high inter-run variance and low human agreement, whereas concrete YES/NO propositions (e.g., 'Are all numbers present in context?') yield interpretable diagnostics and high Cohen's kappa",
      "Because LLMs cannot count past 5",
      "Because binary rubrics double verbosity bias"
    ],
    "answerIndex": 1,
    "explanation": "Decomposing vague 'quality' into concrete boolean criteria eliminates arbitrary mid-scale calibration drift and tells engineers exactly which dimension regressed."
  }
]
```
