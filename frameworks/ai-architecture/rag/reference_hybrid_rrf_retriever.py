#!/usr/bin/env python3
"""Staff Reference Architecture — AI Build 1/4: Hybrid BM25 + Cosine Vector + RRF RAG Engine."""
from collections import Counter
from dataclasses import dataclass
import hashlib
import math
import re
from typing import Dict, List, Tuple


_SYNONYM_CANON: Dict[str, str] = {
    "cancel": "refund",
    "cancelled": "refund",
    "cancellation": "refund",
    "money": "refund",
    "reimburse": "refund",
    "reimbursement": "refund",
    "suitcase": "baggage",
    "luggage": "baggage",
    "carryon": "baggage",
    "bag": "baggage",
    "delayed": "compensation",
    "delay": "compensation",
    "tarmac": "compensation",
    "voucher": "compensation",
    "pet": "cabin_animal",
    "dog": "cabin_animal",
    "cat": "cabin_animal",
}


_BM25_STOPWORDS = {"a", "an", "and", "are", "for", "in", "is", "of", "on", "or", "the", "to", "under", "up", "within"}


def _tokenize(text: str) -> List[str]:
    return [
        tok
        for tok in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", (text or "").lower())
        if tok and tok not in _BM25_STOPWORDS
    ]


@dataclass(frozen=True)
class PolicyChunk:
    chunk_id: str
    title: str
    text: str


class BM25Index:
    """Lexical Okapi BM25 index over policy chunks."""

    def __init__(self, chunks: List[PolicyChunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = list(chunks)
        self.k1 = k1
        self.b = b
        self.doc_tokens: List[Counter[str]] = []
        self.doc_lens: List[int] = []
        self.df: Counter[str] = Counter()

        for ch in self.chunks:
            toks = _tokenize(f"{ch.title} {ch.text}")
            counts = Counter(toks)
            self.doc_tokens.append(counts)
            self.doc_lens.append(len(toks))
            for term in counts:
                self.df[term] += 1

        total_docs = len(self.chunks)
        self.avgdl = (sum(self.doc_lens) / total_docs) if total_docs else 1.0

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        q_terms = _tokenize(query)
        if not q_terms or not self.chunks or top_k <= 0:
            return []

        n_docs = len(self.chunks)
        scored: List[Tuple[str, float]] = []
        for idx, ch in enumerate(self.chunks):
            tf_map = self.doc_tokens[idx]
            dl = self.doc_lens[idx] or 1
            score = 0.0
            for term in q_terms:
                tf = tf_map.get(term, 0)
                if tf == 0:
                    continue
                df_t = self.df.get(term, 0)
                idf = math.log(1.0 + (n_docs - df_t + 0.5) / (df_t + 0.5))
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / self.avgdl))
                score += idf * ((tf * (self.k1 + 1.0)) / denom)
            if score > 0.0:
                scored.append((ch.chunk_id, round(score, 6)))

        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[:top_k]


class DenseVectorIndex:
    """Deterministic local normalized n-gram/concept vector index with cosine similarity."""

    def __init__(self, chunks: List[PolicyChunk], dim: int = 128) -> None:
        if dim <= 0:
            raise ValueError("dim must be > 0")
        self.chunks = list(chunks)
        self.dim = dim
        self.vectors: Dict[str, List[float]] = {
            ch.chunk_id: self.embed(f"{ch.title} {ch.text}") for ch in self.chunks
        }

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = _tokenize(text)
        if not tokens:
            return vec

        features: List[Tuple[str, float]] = []
        for tok in tokens:
            canon = _SYNONYM_CANON.get(tok, tok)
            features.append((f"w:{canon}", 1.4))
            if len(canon) >= 4:
                for i in range(len(canon) - 2):
                    features.append((f"g:{canon[i:i+3]}", 0.45))

        for feat, weight in features:
            digest = hashlib.sha256(feat.encode("utf-8")).digest()
            slot = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            vec[slot] += sign * weight

        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0.0:
            return vec
        return [v / norm for v in vec]

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if not (query or "").strip() or not self.chunks or top_k <= 0:
            return []
        q_vec = self.embed(query)
        if all(v == 0.0 for v in q_vec):
            return []

        scored: List[Tuple[str, float]] = []
        for ch in self.chunks:
            d_vec = self.vectors[ch.chunk_id]
            sim = sum(a * b for a, b in zip(q_vec, d_vec))
            if sim > 0.0:
                scored.append((ch.chunk_id, round(sim, 6)))

        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[:top_k]


class HybridRRFRetriever:
    """Combines BM25Index and DenseVectorIndex rankings via Reciprocal Rank Fusion."""

    def __init__(self, chunks: List[PolicyChunk], rrf_k: int = 60) -> None:
        if rrf_k <= 0:
            raise ValueError("rrf_k must be > 0")
        self.chunks = {c.chunk_id: c for c in chunks}
        self.rrf_k = rrf_k
        self.bm25 = BM25Index(chunks)
        self.dense = DenseVectorIndex(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[PolicyChunk, float]]:
        if not (query or "").strip() or not self.chunks or top_k <= 0:
            return []

        pool_k = max(top_k * 3, len(self.chunks))
        bm25_hits = self.bm25.search(query, top_k=pool_k)
        dense_hits = self.dense.search(query, top_k=pool_k)

        fused: Dict[str, float] = {}
        for rank, (cid, _) in enumerate(bm25_hits, start=1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)
        for rank, (cid, _) in enumerate(dense_hits, start=1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)

        ranked = sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
        return [(self.chunks[cid], round(score, 6)) for cid, score in ranked]


def _self_test() -> None:
    corpus = [
        PolicyChunk("POL-REF-24", "24-Hour Risk-Free Refund", "Tickets cancelled within 24 hours of booking receive a 100% full refund to original payment."),
        PolicyChunk("POL-EU-261", "Regulation EU-261 Delay Compensation", "Flights delayed over 3 hours arriving in EU qualify for 600 EUR compensation."),
        PolicyChunk("POL-BAG-09", "Checked Baggage Allowance", "Economy passengers may check 1 bag up to 23kg; overweight baggage incurs a 75 USD fee."),
        PolicyChunk("POL-PET-04", "Cabin Animal Transport", "Small dogs and cats under 8kg in ventilated carriers are permitted under the seat."),
    ]
    retriever = HybridRRFRetriever(corpus, rrf_k=60)
    exact_top = retriever.retrieve("EU-261 600 EUR", top_k=2)
    assert exact_top and exact_top[0][0].chunk_id == "POL-EU-261"
    semantic_top = retriever.retrieve("suitcase weight limit and extra luggage charge", top_k=2)
    assert semantic_top and semantic_top[0][0].chunk_id == "POL-BAG-09"
    assert retriever.retrieve("   ", top_k=3) == []
    print("[PASS] AI-01 Hybrid BM25 + Cosine Vector + RRF RAG Engine verified.")


if __name__ == "__main__":
    _self_test()
