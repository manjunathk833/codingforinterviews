#!/usr/bin/env python3
"""
AI Engineering Lab 03: Scaled Dot-Product Causal Attention & Reciprocal Rank Fusion (RRF).
"""

import math
from typing import Dict, List, Tuple


def scaled_dot_product_attention(
    Q: List[List[float]],
    K: List[List[float]],
    V: List[List[float]],
    causal: bool = True,
) -> Tuple[List[List[float]], List[List[float]]]:
    seq_len = len(Q)
    d_k = len(Q[0])
    scale = math.sqrt(float(d_k))

    weights: List[List[float]] = []
    outputs: List[List[float]] = []
    d_v = len(V[0])

    for i in range(seq_len):
        logits: List[float] = []
        for j in range(seq_len):
            if causal and j > i:
                logits.append(float("-inf"))
            else:
                dot = sum(Q[i][m] * K[j][m] for m in range(d_k))
                logits.append(dot / scale)

        max_logit = max(logits)
        exps = [0.0 if lg == float("-inf") else math.exp(lg - max_logit) for lg in logits]
        denom = sum(exps)
        row_probs = [e / denom for e in exps]
        weights.append(row_probs)

        out_vec = [
            sum(row_probs[j] * V[j][col] for j in range(seq_len))
            for col in range(d_v)
        ]
        outputs.append(out_vec)

    return weights, outputs


def reciprocal_rank_fusion(ranked_lists: List[List[str]], k: int = 60) -> List[Tuple[str, float]]:
    scores: Dict[str, float] = {}
    for ranked in ranked_lists:
        for rank_idx, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / float(k + rank_idx)
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


if __name__ == "__main__":
    Q = [[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]]
    K = [[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]]
    V = [[10.0, 1.0], [20.0, 2.0], [30.0, 3.0]]

    attn_probs, out = scaled_dot_product_attention(Q, K, V, causal=True)
    # Row 0 can ONLY attend to token 0 (future tokens 1 & 2 masked out)
    assert abs(attn_probs[0][0] - 1.0) < 1e-9
    assert attn_probs[0][1] == 0.0 and attn_probs[0][2] == 0.0
    assert abs(out[0][0] - 10.0) < 1e-9
    # Every row sums to 1.0
    for r in attn_probs:
        assert abs(sum(r) - 1.0) < 1e-9

    # Hybrid RAG RRF: doc_err_409 ranks #1 in BM25 (exact code) and #2 in Dense -> wins RRF!
    bm25_ranks = ["doc_err_409", "doc_retry_guide", "doc_general_faq"]
    dense_ranks = ["doc_concurrency_overview", "doc_err_409", "doc_retry_guide"]
    fused = reciprocal_rank_fusion([bm25_ranks, dense_ranks], k=60)
    assert fused[0][0] == "doc_err_409", f"Expected doc_err_409 ranked #1 after RRF, got {fused}"

    print("All 2 Python Causal Self-Attention & Hybrid RRF Retrieval test cases passed!")
