---
slug: aiqa-02-golden-dataset-engineering-and-stratification
course_id: 06-ai-engineering-qa-focused
track: ai-engineering
volume: "06. Zero to Mastery: AI Engineering — QA Focused"
module_number: 1
module_title: "Module 1: Deterministic Harnesses for Probabilistic Systems"
chapter_number: 2
level_tag: "Foundations → Senior"
title: "Golden Dataset Engineering: Stratified Taxonomies, Failure Mining & Contamination Guards"
summary: "Architecting 200-to-1,000-tuple Golden Evaluation Datasets from production failure logs, Evol-Instruct perturbations, and strict train/prompt-example decontamination."
reading_time_minutes: 21
visualizer_id: "ai-rag-triad-gate"
lab_path: "ai-engineering/01-rag-triad-evaluator"
tags: ["ai-engineering", "ai-qa", "golden-dataset", "stratification", "evol-instruct", "data-contamination", "evals"]
---

# Golden Dataset Engineering: Stratified Taxonomies, Failure Mining & Contamination Guards

```json pretraining
[
  {
    "term": "Golden Eval Tuple",
    "formula": "(Q, Persona, C_gold, Claims+, Claims-)",
    "meaning": "A versioned test fixture pairing input query and persona with expected retrieval chunk IDs, mandatory atomic facts, and forbidden hallucinated claims."
  },
  {
    "term": "Stratified Variance Reduction",
    "formula": "Var(p̂_strat) ≤ Var(p̂_SRS)",
    "meaning": "Partitioning eval cases across explicit risk strata (multi-hop, negation, adversarial, unanswerable) guarantees tail-risk coverage and tighter confidence intervals."
  },
  {
    "term": "MinHash Decontamination",
    "formula": "Jaccard(n-grams) < τ_leak",
    "meaning": "Ensuring zero n-gram or semantic leakage between Golden Eval queries and few-shot prompt examples or fine-tuning corpora."
  },
  {
    "term": "Evol-Instruct Perturbation",
    "formula": "Q_0 → Constrain / Multi-Hop / Noise(Q_0)",
    "meaning": "Controlled synthetic evolution of seed queries to stress-test reasoning depth, distracting context, and ambiguous user phrasing, verified by human review."
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

## Part I — Anatomy of a Production-Grade Golden Tuple

Most teams fail at AI QA before writing a single evaluator because their "eval set" is a spreadsheet of 30 happy-path prompts written by the same engineer who wrote the system prompt. When that engineer leaves, nobody knows *why* a verbose reference paragraph was marked "gold."

Instead of storing a monolithic "ideal essay" (which penalizes valid alternative phrasings), a Staff-grade **Golden Evaluation Tuple** decomposes expectations across retrieval, positive entailment, and negative safety rails:
- `id` & `stratum`: Immutable UUID + risk slice (`"multi_hop_temporal"`, `"unanswerable_abstention"`, `"adversarial_injection"`).
- `query` & `tenant_context`: Raw user prompt (including realistic typos/slang) + RBAC/region metadata (`tier="Basic"`, `jurisdiction="EU"`).
- `gold_chunk_ids`: Canonical document chunk IDs that **must** appear in top-$K$ retrieval (`Recall@K` oracle).
- `must_include_claims`: Atomic facts that **must** be entailed by the answer (`["24-hour window", "7-day advance purchase"]`).
- `must_not_claim`: Explicit forbidden hallucinations or cross-tier leaks (`["full refund after 48 hours", "waived fee for Basic"]`).

```mermaid
flowchart LR
  Logs["Prod Telemetry (Thumbs-Down, Retry Loops, Escalations)"] -->|PII Scrub + Cluster| Mine["Failure Taxonomy Mining"]
  Mine -->|Stratified Quotas| Draft["Candidate Tuple + Evol-Instruct Variants"]
  Draft -->|Dual-SME Adjudication| Decon["MinHash / Embedding Decontamination Gate"]
  Decon -->|Zero Few-Shot Overlap| Gold["Versioned Golden JSONL (200-1,000 Cases)"]
```

---

## Part II — Stratified Allocation, `Evol-Instruct` & Decontamination

A high-signal **200-to-1,000 case Golden Suite** balances five intentional strata rather than mirroring raw traffic volume:
1. **Core Happy-Path Single-Hop ($25\%$)** — Baseline factual lookup sanity check.
2. **Multi-Hop & Temporal Versioning ($25\%$)** — Combining two policy docs or resolving a `2026` policy superseding a deprecated `2024` doc.
3. **Boundary, Numeric & Negation Traps ($20\%$)** — Exact threshold cutoffs (`$99.99` vs `$100.00`, `non-refundable` exceptions).
4. **Unanswerable / Out-of-Scope Abstention ($15\%$)** — Missing evidence where the model **must abstain** rather than extrapolate.
5. **Adversarial / Messy User Input ($15\%$)** — Typos, conflicting premises, and indirect prompt injection payloads.

When cold-starting a new feature before production logs exist, use **Controlled `Evol-Instruct` Synthesis**: take seed policy chunks, systematically apply transformation operators (*Add Constraint*, *Require 2-Doc Join*, *Remove Critical Premise*), and **mandate human SME verification** on every synthetic tuple (never let the same unverified LLM invent both the question and the gold answer!).

Finally, enforce **Strict Benchmark Decontamination**: if an engineer copies a failing Golden Eval example into the system prompt's few-shot examples (or fine-tuning JSONL), the benchmark is **contaminated** (Goodhart's Law). Run an automated `n`-gram Jaccard (`5`-gram $> 0.35$) and cosine similarity ($> 0.92$) gate in CI between `prompts/few_shot/*` and `evals/golden.jsonl`.

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

---

## Part III — Trade-Off Matrix: Golden Dataset Sizing & Sourcing

| Sourcing Method | Realism | Labeling Cost | Primary Strength | Failure Mode to Mitigate |
| :--- | :--- | :--- | :--- | :--- |
| **Production Failure Flywheel** *(Thumbs-down, user re-asks, ticket escalations)* | **Highest** (Real slang, real edge cases) | Medium (SME adjudication + PII redaction) | Directly targets real user pain and regressions | Raw PII leakage into Git—must pass deterministic scrubbing before commit |
| **`Evol-Instruct` Synthetic Perturbation** | Medium–High | Low draft cost + Mandatory SME sign-off | Rapidly populates rare strata (multi-hop, abstention) pre-launch | **Circular LLM Bias** if synthetic answers aren't verified against source docs |
| **Uniform Production Reservoir Sample** | High | Medium | Measures true traffic-weighted user experience | **Power-law dilution**: rare catastrophic bugs represent $<0.5\%$ of samples |

---

## Part IV — Production Implementation Blueprints (Python 3 & Java 17)

### Python 3 Blueprint: Stratified Sampler + 5-Gram Jaccard Decontamination Verifier
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

### Java 17 Blueprint: Golden Tuple Schema Validator & Decontamination Gate
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

---

## Part V — End-of-Chapter Mastery Check

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
