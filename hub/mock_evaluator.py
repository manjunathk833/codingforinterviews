#!/usr/bin/env python3
"""
Deterministic 100-Point Staff Bar-Raiser Mock Interview Evaluator (`hub/mock_evaluator.py`).

- Zero external AI API required.
- Strictly gates empty / placeholder / `< 15`-word stub answers at `0 / 20` per question (`0 / 100` overall).
- Evaluates `q1..q5` across 5 weighted Staff dimensions:
  1. Architectural Mechanisms & Protocols (30 pts)
  2. Quantitative Math & SLA Bounds (20 pts)
  3. Trade-Offs & Failure Modes (25 pts, minus anti-pattern deductions)
  4. Production Operability & CI Governance (15 pts)
  5. Structure & Executive Clarity (10 pts)
"""
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

RUBRICS_PATH = Path(__file__).resolve().parent / "data" / "mock_rubrics.json"
_CACHE: Optional[Dict[str, Dict[str, Any]]] = None

_STUB_PHRASES = (
    "not sure",
    "i'm not sure",
    "im not sure",
    "idk",
    "i don't know",
    "need refresher",
    "haven't done this",
    "todo",
    "tbd",
    "pass",
)


def load_rubrics() -> Dict[str, Dict[str, Any]]:
    global _CACHE
    if _CACHE is None:
        raw = json.loads(RUBRICS_PATH.read_text(encoding="utf-8"))
        _CACHE = {s["sessionId"]: s for s in raw["sessions"]}
    return _CACHE


def get_session_rubric(session_id: str) -> Optional[Dict[str, Any]]:
    return load_rubrics().get(str(session_id or "").strip())


def _is_stub_answer(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return True
    words = re.findall(r"[a-z0-9]+", cleaned)
    if len(words) < 15:
        return True
    if len(words) < 35 and any(p in cleaned for p in _STUB_PHRASES):
        return True
    return False


def _group_hit(low_text: str, terms: List[str]) -> bool:
    return any(t.lower() in low_text for t in terms)


def evaluate_interview_session(session_id: str, responses: Dict[str, str]) -> Optional[Dict[str, Any]]:
    spec = get_session_rubric(session_id)
    if not spec:
        return None

    resp_map = {str(k): str(v or "") for k, v in (responses or {}).items()}
    mech_total = 0.0
    math_total = 0.0
    trade_total = 0.0
    oper_total = 0.0
    clarity_total = 0.0

    per_question: List[Dict[str, Any]] = []

    for q in spec["questions"]:
        qid = q["id"]
        ans = resp_map.get(qid, "").strip()
        low = ans.lower()
        words = re.findall(r"[a-z0-9]+", low)

        if _is_stub_answer(ans):
            per_question.append({
                "questionId": qid,
                "title": q["title"],
                "score": 0,
                "maxScore": 20,
                "status": "Unanswered / Diagnostic Stub",
                "missedMechanisms": [grp[0] for grp in q["mechanismGroups"]],
                "antiPatternsTriggered": [],
                "benchmarkAnswer": q["benchmarkAnswer"],
            })
            continue

        # 1. Mechanisms (max 6.0 per question -> 30 total)
        groups = q["mechanismGroups"]
        matched_groups = [g for g in groups if _group_hit(low, g)]
        missed_groups = [g[0] for g in groups if not _group_hit(low, g)]
        q_mech = 6.0 * (len(matched_groups) / max(1, len(groups)))

        # 2. Quantitative Math & SLAs (max 4.0 per question -> 20 total)
        math_hits = sum(1 for m in q["mathSignals"] if m.lower() in low)
        has_numeric = bool(re.search(r"(?:\b\d+(?:\.\d+)?|o\([^)]+\)|p9[059]\b)", low))
        has_unit_or_formula = bool(
            re.search(r"(?:\b\d+\s*(?:ms|s|m|h|d|mb|gb|gib|mib|%|x|rps)\b|[=^/]|>=|<=)", low)
        )
        q_math = min(
            4.0,
            (2.0 if math_hits >= 1 else 0.0)
            + (1.2 if has_numeric else 0.0)
            + (0.8 if (math_hits >= 2 or has_unit_or_formula) else 0.0),
        )

        # 3. Trade-Offs & Failure Modes (max 5.0 per question -> 25 total)
        tr_hits = sum(1 for t in q["tradeoffSignals"] if t.lower() in low)
        contrast_hits = sum(
            1
            for w in (
                " vs ", "versus", "whereas", "instead", "rather than", "trade-off", "tradeoff",
                "unlike", "prevent", "avoid", "mitigat", "fallback", "isolat", "collision",
                "race", "hallucinat", "drift", "starvation", "oom", "skew", "amplif",
                "against", "separately", "never", "debias", "contradict", "abstention",
                "cap", "bound", "guard", "breaker", "block", "reject", "lock", "dedup",
                "compensat", "mask", "fragmentation",
            )
            if w in f" {low} " or w in low
        )
        q_trade = min(5.0, (2.5 * min(1.0, tr_hits / 1.0) if tr_hits else 0.0) + min(3.5, contrast_hits * 1.25))

        # Deduct if anti-pattern is advocated without negation/warning
        triggered_anti: List[str] = []
        for ap in q.get("antiPatterns", []):
            ap_low = ap.lower()
            if ap_low in low and not any(
                neg in low for neg in ("never ", "avoid ", "instead of ", "don't ", "do not ", "rather than ", "without ")
            ):
                triggered_anti.append(ap)
                q_trade = max(0.0, q_trade - 2.5)

        # 4. Operability & CI Governance (max 3.0 per question -> 15 total)
        op_hits = sum(1 for o in q["operabilitySignals"] if o.lower() in low)
        gov_hits = sum(
            1
            for g in (
                "ci", "pr ", "gate", "shard", "docker", "k8s", "kubernetes", "otel", "trace",
                "slo", "sla", "canary", "rollback", "quarantine", "reaper", "ttl", "schema",
                "broker", "cassette", "explain", "hmac", "imdsv2", "ryuk",
            )
            if g in low
        )
        total_op_cues = op_hits + gov_hits
        q_oper = 3.0 if total_op_cues >= 2 else (2.0 if total_op_cues == 1 else 0.0)

        # 5. Executive Clarity & Structure (max 2.0 per question -> 10 total)
        structured = bool(re.search(r"(?:^|\n)\s*(?:1\.|-|\*)", ans)) or len(words) >= 40
        q_clar = 2.0 if (structured and len(words) >= 35) else (1.2 if len(words) >= 22 else 0.6)

        q_total = round(q_mech + q_math + q_trade + q_oper + q_clar, 1)
        mech_total += q_mech
        math_total += q_math
        trade_total += q_trade
        oper_total += q_oper
        clarity_total += q_clar

        per_question.append({
            "questionId": qid,
            "title": q["title"],
            "score": q_total,
            "maxScore": 20,
            "status": "Strong Staff Depth" if q_total >= 17 else ("Solid Senior" if q_total >= 13 else "Needs Deeper Mechanics"),
            "missedMechanisms": missed_groups,
            "antiPatternsTriggered": triggered_anti,
            "benchmarkAnswer": q["benchmarkAnswer"],
        })

    dims = {
        "mechanismsPts": int(round(mech_total)),
        "mathSlaPts": int(round(math_total)),
        "tradeoffsPts": int(round(trade_total)),
        "operabilityPts": int(round(oper_total)),
        "clarityPts": int(round(clarity_total)),
    }
    numeric_score = max(0, min(100, sum(dims.values())))

    if numeric_score >= 85:
        verdict = "HIRE — Staff / Principal Bar Cleared"
    elif numeric_score >= 70:
        verdict = "LEAN HIRE — Strong Senior (Close Remaining Staff Gaps)"
    elif numeric_score > 0:
        verdict = "DIAGNOSTIC IN PROGRESS — Review Benchmark Architecture"
    else:
        verdict = "UNATTEMPTED / STUB — Draft All 5 Architectural Responses"

    overall_label = f"{numeric_score} / 100 ({verdict.split(' — ')[0]})"

    md_lines = [
        f"## 📊 100-Point Bar-Raiser Scorecard — {spec['shortTitle']}",
        "",
        f"**Overall Score:** **{numeric_score} / 100** · **{verdict}**  ",
        f"**Milestone:** `{spec['phaseGate']}`",
        "",
        "| Dimension | Weight | Score |",
        "| :--- | :---: | :---: |",
        f"| **1. Architectural Mechanisms & Protocols** | 30 | **{dims['mechanismsPts']} / 30** |",
        f"| **2. Quantitative Math & SLA Bounds** | 20 | **{dims['mathSlaPts']} / 20** |",
        f"| **3. Trade-Offs & Failure Modes** | 25 | **{dims['tradeoffsPts']} / 25** |",
        f"| **4. Production Operability & CI Governance** | 15 | **{dims['operabilityPts']} / 15** |",
        f"| **5. Structure & Executive Clarity** | 10 | **{dims['clarityPts']} / 10** |",
        "",
        "---",
        "",
        "## Question-by-Question Diagnostic & Staff Benchmarks",
        "",
    ]

    for pq in per_question:
        md_lines.append(f"### {pq['title']} — `{pq['score']} / 20` ({pq['status']})")
        if pq["missedMechanisms"]:
            md_lines.append(f"- **Missed Core Primitives:** `{', '.join(pq['missedMechanisms'])}`")
        if pq["antiPatternsTriggered"]:
            md_lines.append(f"- **Anti-Pattern Warning:** `{', '.join(pq['antiPatternsTriggered'])}`")
        md_lines.append(f"- **Staff Benchmark Answer:** {pq['benchmarkAnswer']}")
        md_lines.append("")

    return {
        "sessionId": session_id,
        "numericScore": numeric_score,
        "overallScore": overall_label,
        "verdict": verdict,
        "dimensions": dims,
        "perQuestion": per_question,
        "evaluationMarkdown": "\n".join(md_lines).rstrip() + "\n",
    }
