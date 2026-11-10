---
slug: aiqa-02-golden-dataset-engineering-and-stratification
course_id: 06-ai-engineering-qa-focused
track: ai-engineering
volume: "06. Zero to Mastery: AI Engineering — QA Focused"
module_number: 1
module_title: "Module 1: Deterministic Harnesses for Probabilistic Systems (AeroEval v0.1 → v0.2)"
chapter_number: 2
level_tag: "🌱 Foundations → Senior AI QA"
title: "Build AeroEval v0.2: Golden Dataset Engineering, Stratified Taxonomies & Contamination Guards"
summary: "Why random production sampling hides catastrophic edge-case bugs (Simpson's Paradox), and how to build AeroEval v0.2 with decomposed Golden Tuples, Stratified SLAs, and 5-gram Jaccard Decontamination."
reading_time_minutes: 21
visualizer_id: "ai-rag-triad-gate"
lab_path: "ai-engineering/01-rag-triad-evaluator"
tags: ["ai-engineering", "ai-qa", "aeroeval", "golden-dataset", "stratification", "evol-instruct", "data-contamination", "evals"]
---

# Build AeroEval v0.2: Golden Dataset Engineering, Stratified Taxonomies & Contamination Guards

```json continuity
{
  "previously": "In Chapter 01, we built `AeroEval v0.1` with instant structural contracts (JSON + citations + zero PII), Metamorphic Context-Shuffle checks, and `pass^k` / Wilson confidence bounds.",
  "painPoint": "Our team ran `AeroEval v0.1` on 500 randomly sampled production chat logs and celebrated a 96.4% pass rate! Yet the next morning, enterprise flyers hit a 80% failure rate on multi-policy international refunds—because 470 of our 500 random logs were trivial 'How much is a carry-on?' FAQs!",
  "unlock": "Upgrade to `AeroEval v0.2`: design decomposed Golden Evaluation Tuples (`gold_chunk_ids`, `must_include_claims`, `must_not_claim`), enforce per-slice Stratified SLAs, and block developers from leaking Golden test cases into few-shot prompts!"
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Slide 1 / 4 · The Random Sampling Trap (Simpson's Paradox)",
    "caption": "Real airline chat traffic follows a steep power law: 85% are easy single-sentence FAQs, while <2% are high-stakes multi-hop refund overrides. A random 500-item sample buries a 20% pass rate on hard edge cases inside a 96.4% overall average!",
    "code": "# 470 Easy FAQs (99% pass) + 10 Multi-Hop Refunds (20% pass)\n# Aggregate Score = 97.4% PASS! -> Ships broken refund bot to prod!"
  },
  {
    "time": "0:25",
    "badge": "Slide 2 / 4 · Anatomy of a Decomposed Golden Tuple",
    "caption": "Never store a 3-paragraph 'ideal essay' as your expected answer! Instead, AeroEval v0.2 decomposes every Golden test case into expected retrieval doc IDs, mandatory atomic facts, and forbidden claims.",
    "code": "golden_case = {\n    \"id\": \"gold_042\", \"stratum\": \"multi_hop_refund\",\n    \"gold_chunk_ids\": [\"doc_14\", \"doc_eu261\"],\n    \"must_include_claims\": [\"24-hour window\", \"€600 EU compensation\"],\n    \"must_not_claim\": [\"non-refundable under EU261\"]\n}"
  },
  {
    "time": "0:54",
    "badge": "Slide 3 / 4 · Stratified Quotas & Per-Slice Blocking Gates",
    "caption": "We partition our 500-case Golden Suite into 5 intentional risk slices (Happy Path, Multi-Hop, Boundary/Negation, Unanswerable Abstention, Adversarial) and require EACH slice to pass its own floor!",
    "code": "stratum_slas = {\n    \"happy_path\": 0.95,\n    \"multi_hop_temporal\": 0.88,\n    \"unanswerable_abstention\": 0.95  # Cannot be masked by easy FAQs!\n}"
  },
  {
    "time": "1:20",
    "badge": "Slide 4 / 4 · Catching Prompt Contamination in CI",
    "caption": "What if a developer fixes a failing Golden test by copy-pasting that exact question into AeroBrain's system prompt as a few-shot example? AeroEval v0.2 runs a 5-gram Jaccard decontamination scan to block benchmark cheating!",
    "code": "if five_gram_jaccard(golden_query, system_prompt_example) >= 0.35:\n    raise AssertionError(\"BENCHMARK_CONTAMINATION: Golden case leaked into prompt!\")"
  }
]
```

```json pretraining
[
  {
    "term": "Golden Eval Tuple",
    "formula": "(Q, Persona, C_gold, Claims+, Claims-)",
    "meaning": "A structured test case that lists which documents should be retrieved, which key facts must appear, and which false claims must never appear—rather than one rigid paragraph."
  },
  {
    "term": "Stratified Variance Reduction",
    "formula": "Var(p̂_strat) ≤ Var(p̂_SRS)",
    "meaning": "Grouping test cases into specific risk buckets (like tricky negations or missing-policy questions) and grading each bucket separately so easy questions cannot hide severe bugs."
  },
  {
    "term": "MinHash / n-Gram Decontamination",
    "formula": "Jaccard(5-grams) < 0.35",
    "meaning": "An automated CI check that makes sure no one accidentally copied test questions from your Golden exam into the AI's system prompt or training data."
  },
  {
    "term": "Evol-Instruct Perturbation",
    "formula": "Q_0 → Constrain / Multi-Hop / Noise(Q_0)",
    "meaning": "Starting from a simple seed question and systematically adding realistic constraints or multi-document twists (verified by a human expert) to test hard edge cases before launch."
  }
]
```

```json poe
{
  "question": "An AI team builds a 500-example Golden Eval set by randomly sampling 500 production queries. Overall pass rate is 96.4%, yet enterprise customers report frequent catastrophic errors on multi-policy refund edge cases. Why did the 500-example eval miss this, and what fixes it?",
  "options": [
    "500 examples is too large and causes overfitting inside pytest",
    "Uniform random sampling mirrors power-law traffic (85% trivial FAQ queries, <1% high-severity edge cases), burying a 20% pass rate on multi-hop/abstention strata inside a 96.4% aggregate average; fix via stratified quotas + per-stratum blocking thresholds",
    "JSONL files lose floating-point precision after 250 lines",
    "Golden datasets should never include real user queries"
  ],
  "answerIndex": 1,
  "explanation": "Simpson's Paradox / power-law masking: if 470 of 500 random samples are easy greeting/FAQ lookups (99% pass) and only 10 are multi-hop edge cases (20% pass), overall accuracy still reads ~97.4%. Stratified allocation with independent per-slice CI gates prevents easy volume from masking high-severity failures."
}
```

## 🌱 Step 1: Plain-English Story — Why a Spreadsheet of 30 Happy Prompts Always Fails

Imagine studying for a pilot's license exam where 95 out of 100 questions ask *"What color is the sky?"* and only 2 questions ask *"How do you land in a crosswind?"* You could fail every single crosswind landing and still score a **98% A+**!

That is the exact trap teams fall into when they build an AI evaluation dataset by grabbing random chat logs—or worse, letting the engineer who wrote the prompt type 30 clean questions into a spreadsheet:
1. **Easy Volume Masks Rare Disasters**: In production, 85% of customer questions are basic FAQs (*"Where is my boarding pass?"*). If you only track one overall pass rate, a 99% score on FAQs completely hides a 0% score on international cancellation overrides!
2. **The "Ideal Essay" Trap**: If your spreadsheet stores one long reference paragraph as the "expected answer," your test fails whenever `AeroBrain` gives a shorter, clearer answer.
3. **Teaching to the Test (Contamination)**: When Test #14 fails in CI, a busy developer often copies Test #14 directly into the system prompt's few-shot examples! Now the test passes, but only because the AI memorized that specific sentence.

```mermaid
flowchart LR
  Logs["Prod Failures (Thumbs-Down & Escalations)"] -->|PII Scrub + Bucket| Mine["5 Risk Strata (Multi-Hop, Negation, Abstain...)"]
  Mine -->|Decompose Facts| Tuple["Golden Tuple (Gold Docs + Must-Include + Must-Not)"]
  Tuple -->|5-Gram Jaccard Check| Decon["Decontamination Gate vs Few-Shot Prompts"]
  Decon -->|Per-Slice SLAs| Gate["AeroEval v0.2 Stratified Release Gate"]
```

Let's upgrade **`AeroEval v0.2`** with decomposed **Golden Tuples** and **Per-Stratum Gates** so no edge case can ever hide behind easy questions again!

## 🔨 Step 2: First Lines of Code — Decomposed Golden Tuples & Per-Slice Gates

Instead of comparing against a rigid paragraph, look how `AeroEval v0.2` checks a **Golden Tuple** (`must_include` facts + `must_not_claim` forbidden hallucinations) and gates each **risk stratum** independently:

```python
def verify_golden_tuple(answer: str, must_include: list[str], must_not_claim: list[str]) -> bool:
    """Checks that required facts are present and forbidden claims are absent."""
    low = answer.lower()
    has_all_required = all(fact.lower() in low for fact in must_include)
    has_no_forbidden = all(bad.lower() not in low for bad in must_not_claim)
    return has_all_required and has_no_forbidden


def check_stratum_slas(slice_passes: dict[str, list[bool]], min_sla: dict[str, float]) -> dict[str, bool]:
    """Gates EACH risk slice separately so 99% on FAQs cannot hide 20% on Multi-Hop!"""
    return {
        stratum: (sum(outcomes) / len(outcomes)) >= min_sla[stratum]
        for stratum, outcomes in slice_passes.items()
    }


print(verify_golden_tuple("Cancel within 24 hours for $0 fee.", ["24 hours", "$0"], ["non-refundable"]))
print(check_stratum_slas({"faq": [True] * 10, "multi_hop": [True, False]}, {"faq": 0.95, "multi_hop": 0.85}))
```

### Java 17 Equivalent

```java
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class AeroEvalV02 {
    public static boolean verifyGoldenTuple(String answer, List<String> mustInclude, List<String> mustNotClaim) {
        String low = answer.toLowerCase(Locale.ROOT);
        boolean allReq = mustInclude.stream().allMatch(f -> low.contains(f.toLowerCase(Locale.ROOT)));
        boolean noBad = mustNotClaim.stream().noneMatch(b -> low.contains(b.toLowerCase(Locale.ROOT)));
        return allReq && noBad;
    }

    public static boolean allStrataMeetSla(Map<String, List<Boolean>> sliceOutcomes, Map<String, Double> minSla) {
        for (var entry : minSla.entrySet()) {
            List<Boolean> results = sliceOutcomes.getOrDefault(entry.getKey(), List.of());
            long passed = results.stream().filter(Boolean::booleanValue).count();
            double rate = results.isEmpty() ? 0.0 : (double) passed / results.size();
            if (rate < entry.getValue()) return false; // Fails build if ANY slice drops below floor!
        }
        return true;
    }
}
```

## ⚡ Step 3: Where It Breaks in Real Life — Circular Synthetic Data & Prompt Contamination

As your team scales `AeroEval v0.2` from 20 test cases to **500 stratified Golden Tuples**, two real-world pitfalls appear:

1. **Pitfall 1: Circular LLM Hallucinations in Synthetic Data**
   When launching a brand-new airline feature before real customer logs exist, teams use **`Evol-Instruct`** (taking a simple seed question and asking an LLM to add constraints or multi-doc hops). **Where it breaks**: If you let an unverified LLM generate *both* the tricky question *and* the "ground-truth" answer without a human expert checking the policy document, any hallucination the generator makes gets baked into your test suite—punishing `AeroBrain` when `AeroBrain` is actually right!
2. **Pitfall 2: Goodhart's Law & Few-Shot Contamination**
   During a sprint crunch, an engineer sees 6 failing Golden cases and pastes them into `system_prompt.txt` under `Here are examples of how to answer:`. Offline accuracy jumps from `88%` to `96%`, while live customer accuracy stays flat!

```json contrast
{
  "title": "Evaluation Dataset Curation & Governance",
  "naiveTitle": "Ad-Hoc Happy-Path Spreadsheet",
  "naiveMetric": "30 Prompts · Blind to Tail Risk",
  "naivePoints": [
    "Hand-written clean grammar queries authored by the prompt engineer",
    "Stores a single reference paragraph scored via ROUGE/BLEU lexical overlap",
    "Developers paste failing eval questions directly into few-shot system prompts",
    "Reports one global average score hiding 0% accuracy on abstention cases"
  ],
  "staffTitle": "Stratified, Decontaminated Golden Registry",
  "staffMetric": "500 Stratified Tuples · Per-Slice Gates",
  "staffPoints": [
    "Continuously Flywheel-mined from production thumbs-down, user rephrases, and human escalations",
    "Separates gold_chunk_ids, must_include_claims, and must_not_claim invariants",
    "Blocks PRs via automated 5-gram Jaccard decontamination against few-shot & LoRA train sets",
    "Enforces independent release gates per stratum (e.g., Abstention >= 95%, Multi-Hop >= 88%)"
  ]
}
```

## 🚀 Step 4: Staff Engineer Deep-Dive — Neyman Stratification & MinHash Decontamination Math

Why does **Stratified Sampling** mathematically outperform Simple Random Sampling (`SRS`) across $H$ risk strata with population weights $W_h = N_h / N$ and stratum variances $S_h^2 = p_h(1 - p_h)$?
Under **Neyman Optimal Allocation**, we allocate sample size $n_h \propto W_h S_h$ (oversampling high-variance, high-risk edge strata where $p_h \approx 0.50$ rather than easy FAQs where $p_h \approx 0.99$), shrinking estimator variance to:

$$\text{Var}(\hat{p}_{\text{strat}}) = \sum_{h=1}^{H} W_h^2 \frac{p_h(1 - p_h)}{n_h} \ll \text{Var}(\hat{p}_{\text{SRS}})$$

In practice, a high-signal **500-case Golden Suite** allocates dedicated quotas across five intentional risk strata:
1. **Core Happy-Path Single-Hop ($25\%$)** — Baseline factual lookup sanity check.
2. **Multi-Hop & Temporal Versioning ($25\%$)** — Combining two policy docs or resolving a `2026` policy superseding a deprecated `2024` doc.
3. **Boundary, Numeric & Negation Traps ($20\%$)** — Exact threshold cutoffs (`$99.99` vs `$100.00`, `non-refundable` exceptions).
4. **Unanswerable / Out-of-Scope Abstention ($15\%$)** — Missing evidence where the model **must abstain** rather than guess.
5. **Adversarial / Messy User Input ($15\%$)** — Typos, conflicting premises, and indirect prompt injection payloads.

To guarantee **Zero Benchmark Contamination**, every PR runs an $n$-gram Jaccard similarity gate ($n = 5$) between every Golden query $G_i$ and every few-shot exemplar or fine-tuning record $T_j$:

$$J_5(G_i, T_j) = \frac{|\text{ngrams}_5(G_i) \cap \text{ngrams}_5(T_j)|}{|\text{ngrams}_5(G_i) \cup \text{ngrams}_5(T_j)|} < \tau_{\text{leak}} \quad (\tau_{\text{leak}} = 0.35)$$

| Sourcing Method | Realism | Labeling Cost | Primary Strength | Failure Mode to Mitigate |
| :--- | :--- | :--- | :--- | :--- |
| **Production Failure Flywheel** *(Thumbs-down, user re-asks, ticket escalations)* | **Highest** (Real slang, real edge cases) | Medium (SME adjudication + PII redaction) | Directly targets real user pain and regressions | Raw PII leakage into Git—must pass deterministic scrubbing before commit |
| **`Evol-Instruct` Synthetic Perturbation** | Medium–High | Low draft cost + Mandatory SME sign-off | Rapidly populates rare strata (multi-hop, abstention) pre-launch | **Circular LLM Bias** if synthetic answers aren't verified against source docs |
| **Uniform Production Reservoir Sample** | High | Medium | Measures true traffic-weighted user experience | **Power-law dilution**: rare catastrophic bugs represent $<0.5\%$ of samples |

### Production Blueprint: Stratified Gate Evaluator + 5-Gram Jaccard Decontamination Verifier

```python
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class GoldenTuple:
    case_id: str
    stratum: str
    query: str
    gold_chunk_ids: tuple[str, ...]
    must_include_claims: tuple[str, ...]
    must_not_claim: tuple[str, ...]


def char_or_word_ngrams(text: str, n: int = 5) -> set[tuple[str, ...]]:
    tokens = [t.strip(".,!?;:\"'()").lower() for t in text.split() if t.strip()]
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def detect_prompt_contamination(
    golden_cases: Iterable[GoldenTuple],
    few_shot_examples: Iterable[str],
    max_jaccard: float = 0.35,
) -> list[dict]:
    """Flags any Golden Eval case leaked into few-shot prompts or fine-tuning corpora."""
    train_grams = [(idx, char_or_word_ngrams(ex, n=5)) for idx, ex in enumerate(few_shot_examples)]
    violations: list[dict] = []

    for case in golden_cases:
        q_grams = char_or_word_ngrams(case.query, n=5)
        if not q_grams:
            continue
        for ex_idx, t_grams in train_grams:
            if not t_grams:
                continue
            jaccard = len(q_grams & t_grams) / len(q_grams | t_grams)
            if jaccard >= max_jaccard:
                violations.append({
                    "caseId": case.case_id,
                    "fewShotIndex": ex_idx,
                    "jaccard5Gram": round(jaccard, 3),
                })
    return violations


def evaluate_stratified_gates(
    results: list[tuple[GoldenTuple, bool]],
    stratum_thresholds: dict[str, float],
) -> dict:
    """Enforces independent pass-rate SLAs per risk stratum so easy FAQs never mask tail failures."""
    totals: dict[str, int] = defaultdict(int)
    passes: dict[str, int] = defaultdict(int)
    for item, passed in results:
        totals[item.stratum] += 1
        if passed:
            passes[item.stratum] += 1

    slice_report = {}
    all_gates_passed = True
    for stratum, min_rate in stratum_thresholds.items():
        n = totals[stratum]
        rate = (passes[stratum] / n) if n > 0 else 0.0
        ok = n > 0 and rate >= min_rate
        if not ok:
            all_gates_passed = False
        slice_report[stratum] = {"count": n, "passRate": round(rate, 4), "threshold": min_rate, "passed": ok}

    return {"releaseApproved": all_gates_passed, "strata": slice_report}
```

### Java 17 Equivalent

```java
import java.util.*;

public final class GoldenDatasetValidator {
    public record GoldenCase(
            String id,
            String stratum,
            String query,
            Set<String> goldChunkIds,
            List<String> mustIncludeClaims,
            List<String> mustNotClaim) {}

    public static List<String> validateCatalogIntegrity(
            List<GoldenCase> catalog, List<String> fewShotPrompts, Map<String, Integer> minQuotaPerStratum) {
        List<String> errors = new ArrayList<>();
        Map<String, Integer> stratumCounts = new HashMap<>();

        for (GoldenCase c : catalog) {
            stratumCounts.merge(c.stratum(), 1, Integer::sum);
            if (!"unanswerable_abstention".equals(c.stratum()) && c.goldChunkIds().isEmpty()) {
                errors.add("MISSING_GOLD_CHUNKS:" + c.id());
            }
            if (c.mustIncludeClaims().isEmpty() && c.mustNotClaim().isEmpty()) {
                errors.add("EMPTY_CLAIM_ASSERTIONS:" + c.id());
            }
            for (String prompt : fewShotPrompts) {
                if (fiveGramJaccard(c.query(), prompt) >= 0.35) {
                    errors.add("BENCHMARK_CONTAMINATION:" + c.id());
                }
            }
        }

        minQuotaPerStratum.forEach((stratum, minCount) -> {
            int actual = stratumCounts.getOrDefault(stratum, 0);
            if (actual < minCount) {
                errors.add("STRATUM_UNDER_QUOTA:" + stratum + "(" + actual + "<" + minCount + ")");
            }
        });
        return errors;
    }

    private static double fiveGramJaccard(String a, String b) {
        Set<String> ga = ngrams(a, 5);
        Set<String> gb = ngrams(b, 5);
        if (ga.isEmpty() || gb.isEmpty()) return 0.0;
        long inter = ga.stream().filter(gb::contains).count();
        long union = ga.size() + gb.size() - inter;
        return (double) inter / union;
    }

    private static Set<String> ngrams(String text, int n) {
        String[] toks = text.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9\\s]", "").trim().split("\\s+");
        Set<String> out = new HashSet<>();
        if (toks.length < n) {
            if (toks.length > 0 && !toks[0].isEmpty()) out.add(String.join(" ", toks));
            return out;
        }
        for (int i = 0; i <= toks.length - n; i++) {
            out.add(String.join(" ", Arrays.copyOfRange(toks, i, i + n)));
        }
        return out;
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Never Let an Unverified LLM Generate Both Question and Ground-Truth Answer**:
> If you ask `GPT-4o` to generate 500 synthetic QA pairs from your docs without human adjudication or deterministic programmatic extraction, any hallucination or misinterpretation made by the generator becomes **baked into your Golden Oracle**—causing your CI pipeline to penalize models that actually read the policy accurately! Synthetic generation is for **query diversity (`Evol-Instruct`)**; ground-truth claims must trace back to verified document spans and SME sign-off.

**Up Next in Chapter 03**: Now that `AeroEval v0.2` has a clean, stratified Golden Dataset with `gold_chunk_ids` and atomic claims, how do we tell instantly whether a failed test was caused by **bad document retrieval** or **LLM hallucination**? In Chapter 03, we'll build **`AeroEval v0.3`: The RAG Evaluation Triad & Atomic Claim Entailment**!

```json quiz
[
  {
    "id": "aiqa-02-q1",
    "question": "Why should a Golden Evaluation Tuple store 'gold_chunk_ids', 'must_include_claims', and 'must_not_claim' separately instead of a single reference essay string?",
    "options": [
      "Because JSON arrays compress better than strings in SQLite",
      "Because separating retrieval chunk IDs from atomic positive/negative claims isolates Retriever failures from Generator hallucinations without penalizing valid stylistic rephrasings",
      "Because LLMs cannot generate paragraphs longer than two sentences",
      "Because embedding models reject punctuation characters"
    ],
    "answerIndex": 1,
    "explanation": "A single reference essay conflates retrieval, style, and factual correctness. Decomposed tuples pinpoint whether Recall@K failed, a required claim was omitted, or a forbidden claim leaked."
  },
  {
    "id": "aiqa-02-q2",
    "question": "During a sprint, an engineer fixes 12 failing Golden Eval cases by copying 6 of those exact Golden queries and answers into the system prompt's few-shot examples. Overall eval score jumps from 89% to 95%. What failed in QA governance?",
    "options": [
      "Nothing failed; few-shot prompting is always recommended",
      "Benchmark Data Contamination: leaking Golden test fixtures into few-shot prompts memorizes test IDs rather than generalizing capability, inflating offline metrics while leaving production accuracy unchanged",
      "Six few-shot examples exceed the HTTP header limit",
      "Few-shot examples only work with fine-tuned LoRA adapters"
    ],
    "answerIndex": 1,
    "explanation": "Eval sets must remain strictly held-out from system prompts, few-shot exemplars, and fine-tuning corpora. Always create *distinct* analogous examples for few-shot prompting and enforce automated n-gram/embedding decontamination in CI."
  },
  {
    "id": "aiqa-02-q3",
    "question": "What is the primary statistical advantage of Stratified Evaluation with per-stratum thresholds over reporting a single aggregate accuracy across a random traffic sample?",
    "options": [
      "It eliminates the need to version control the dataset",
      "It prevents high-volume trivial queries (e.g., 85% basic FAQs) from masking catastrophic regressions in low-frequency, high-liability strata (e.g., multi-hop policy overrides or abstention)",
      "It reduces LLM API token cost to zero",
      "It guarantees Cohen's kappa equals 1.0"
    ],
    "answerIndex": 1,
    "explanation": "Stratification allocates dedicated sample budget to critical risk slices and blocks deployment if any high-severity slice breaches its floor—eliminating Simpson's Paradox masking."
  }
]
```
