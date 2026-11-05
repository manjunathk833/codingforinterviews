# 🧠 AI Lab 01: The RAG Evaluation Triad & Negation Hallucination Gate

**Domain:** LLM-as-a-Judge, Ragas / DeepEval Metrics & Deterministic AI CI Gates  
**Target Role:** Senior / Staff SDET & AI Quality Architect  
**Interactive Visualizer:** `ai-rag-triad-gate` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

Why do naive `cosine_similarity(answer, expected) > 0.85` assertions fail catastrophically in production CI?
1. **The Negation Trap**:
   - **Ground-Truth Policy**: *"Passengers may cancel within 24 hours for a 100% full refund with no fee."*
   - **Hallucinated LLM Output**: *"Passengers may **not** cancel within 24 hours for a 100% full refund."*
   - **Vector Cosine Similarity**: **`0.96` (96% similar!)** — because 12 out of 13 words are identical! A naive similarity test passes a 100% contradictory legal policy!
2. **The RAG Evaluation Triad**:
   - **Context Recall** (Retrieval): What fraction of required ground-truth facts were retrieved by the Vector DB?
   - **Faithfulness / Groundedness** (Generation): Break the LLM's response into atomic claims $C_1 \dots C_k$ and verify each claim is entailed by the retrieved context without polarity inversion (negation mismatch) or fabricated numbers.
   - **Answer Relevance** (Generation): Does the response actually address the user's question intent?

---

## 🧪 2. Running Verification

```bash
./run.sh test 01-rag-triad-evaluator
```

