#!/usr/bin/env python3
"""Staff Reference Architecture — AI Build 2/4: RAG Triad & Rogan-Gladen Judge Calibration."""
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Set

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_STOPWORDS: Set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for",
    "from", "get", "how", "i", "if", "in", "is", "it", "my", "of", "on", "or",
    "our", "the", "their", "to", "what", "when", "with", "within", "you", "your",
}
_NEGATIONS: Set[str] = {"no", "not", "never", "non", "nonrefundable", "cannot", "without", "zero"}


def _content_tokens(text: str) -> Set[str]:
    toks = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {t for t in toks if t not in _STOPWORDS and len(t) > 1}


def _numbers(text: str) -> Set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text or ""))


def _has_negation(text: str) -> bool:
    toks = set(re.findall(r"[a-z0-9]+", (text or "").lower()))
    return bool(toks & _NEGATIONS) or "non-refundable" in (text or "").lower()


@dataclass(frozen=True)
class EvalSample:
    question: str
    answer: str
    retrieved_contexts: List[str]
    expected_facts: List[str]


class ClaimEntailmentScorer:
    """Scores RAG Faithfulness, Context Recall, and Answer Relevance deterministically."""

    def score_faithfulness(self, answer: str, contexts: List[str]) -> float:
        claims = [c.strip() for c in re.split(r"[.!?\n]+", answer or "") if c.strip()]
        if not claims or not contexts:
            return 0.0

        ctx_joined = " ".join(contexts)
        ctx_tokens = _content_tokens(ctx_joined)
        ctx_nums = _numbers(ctx_joined)
        ctx_neg = _has_negation(ctx_joined)

        supported = 0
        for claim in claims:
            c_tokens = _content_tokens(claim)
            if not c_tokens:
                continue
            c_nums = _numbers(claim)
            if c_nums and not c_nums.issubset(ctx_nums):
                continue
            if _has_negation(claim) != ctx_neg and len(c_tokens & ctx_tokens) >= 2:
                continue
            overlap = len(c_tokens & ctx_tokens) / len(c_tokens)
            if overlap >= 0.45:
                supported += 1

        return round(supported / len(claims), 4)

    def score_context_recall(self, expected_facts: List[str], contexts: List[str]) -> float:
        if not expected_facts:
            return 1.0
        if not contexts:
            return 0.0
        ctx_tokens = _content_tokens(" ".join(contexts))
        ctx_nums = _numbers(" ".join(contexts))
        recalled = 0
        for fact in expected_facts:
            f_tokens = _content_tokens(fact)
            f_nums = _numbers(fact)
            if not f_tokens:
                continue
            nums_ok = f_nums.issubset(ctx_nums)
            tok_ok = (len(f_tokens & ctx_tokens) / len(f_tokens)) >= 0.5
            if nums_ok and tok_ok:
                recalled += 1
        return round(recalled / len(expected_facts), 4)

    def score_answer_relevance(self, question: str, answer: str) -> float:
        q_tokens = _content_tokens(question)
        a_tokens = _content_tokens(answer)
        if not q_tokens or not a_tokens:
            return 0.0
        shared = len(q_tokens & a_tokens)
        recall_q = shared / len(q_tokens)
        concise_bonus = min(1.0, len(a_tokens & q_tokens) / max(1, min(len(q_tokens), 4)))
        return round(min(1.0, 0.65 * recall_q + 0.35 * concise_bonus), 4)


class RoganGladenCalibrator:
    """Debiases raw binary judge pass-rates given judge sensitivity (tpr) and specificity (tnr)."""

    def __init__(self, tpr: float, tnr: float) -> None:
        if not (0.0 <= tpr <= 1.0 and 0.0 <= tnr <= 1.0):
            raise ValueError("tpr and tnr must be in [0.0, 1.0]")
        if (tpr + tnr - 1.0) <= 1e-6:
            raise ValueError("Degenerate judge: tpr + tnr must strictly exceed 1.0")
        self.tpr = tpr
        self.tnr = tnr

    def debias(self, observed_pass_rate: float) -> float:
        if not (0.0 <= observed_pass_rate <= 1.0):
            raise ValueError("observed_pass_rate must be in [0.0, 1.0]")
        raw = (observed_pass_rate + self.tnr - 1.0) / (self.tpr + self.tnr - 1.0)
        return round(max(0.0, min(1.0, raw)), 4)


class RegressionGate:
    """CI quality gate combining RAG Triad metrics and Rogan-Gladen judge calibration."""

    def __init__(self, min_faithfulness: float = 0.85, min_relevance: float = 0.60) -> None:
        self.min_faithfulness = min_faithfulness
        self.min_relevance = min_relevance
        self.scorer = ClaimEntailmentScorer()

    def evaluate_dataset(self, samples: List[EvalSample], calibrator: RoganGladenCalibrator) -> Dict[str, Any]:
        if not samples:
            return {"passed": False, "calibratedFaithfulness": 0.0, "avgRelevance": 0.0, "avgRecall": 0.0}

        faith_scores = [self.scorer.score_faithfulness(s.answer, s.retrieved_contexts) for s in samples]
        rel_scores = [self.scorer.score_answer_relevance(s.question, s.answer) for s in samples]
        rec_scores = [self.scorer.score_context_recall(s.expected_facts, s.retrieved_contexts) for s in samples]

        raw_pass_rate = sum(1 for f in faith_scores if f >= 0.8) / len(samples)
        calibrated_faith = calibrator.debias(raw_pass_rate)
        avg_rel = round(sum(rel_scores) / len(rel_scores), 4)
        avg_rec = round(sum(rec_scores) / len(rec_scores), 4)
        passed = calibrated_faith >= self.min_faithfulness and avg_rel >= self.min_relevance
        return {
            "passed": passed,
            "rawPassRate": round(raw_pass_rate, 4),
            "calibratedFaithfulness": calibrated_faith,
            "avgRelevance": avg_rel,
            "avgRecall": avg_rec,
        }


def _self_test() -> None:
    from apps.aerocart.client import AeroCartClient

    client = AeroCartClient(in_process=True)
    ok_res = client.ask_concierge("What is the 24 hour refund policy for cancelled flights?", mode="grounded")["data"]
    bad_res = client.ask_concierge("What is the 24 hour refund policy for cancelled flights?", mode="hallucinated")["data"]

    scorer = ClaimEntailmentScorer()
    f_ok = scorer.score_faithfulness(ok_res["answer"], ok_res["retrievedContexts"])
    f_bad = scorer.score_faithfulness(bad_res["answer"], bad_res["retrievedContexts"])
    assert f_ok >= 0.9 and f_bad < 0.5, (f_ok, f_bad)

    cal = RoganGladenCalibrator(tpr=0.92, tnr=0.88)
    assert abs(cal.debias(0.84) - 0.90) <= 0.01
    gate = RegressionGate(min_faithfulness=0.85, min_relevance=0.45)
    verdict = gate.evaluate_dataset(
        [EvalSample("24 hour refund policy?", ok_res["answer"], ok_res["retrievedContexts"], ["24 hours full refund"])],
        cal,
    )
    assert verdict["passed"] is True, verdict
    print("[PASS] AI-02 RAG Triad Claim-Entailment & Rogan-Gladen Judge Calibration verified.")


if __name__ == "__main__":
    _self_test()
