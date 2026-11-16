# 🎙️ Mock Technical Interview Session #6: Production AI Engineering & Agentic QE — Hybrid RRF, Judge Calibration & MCP Agents (Phase 5 Exit Gate)

**Target Role:** Staff AI Quality & LLM Evaluation Systems Architect  
**Roadmap Milestone:** Phase 5 Exit Gate  
**Session Guidelines:** Draft structured Staff-level architectural responses for all 5 questions in the **Candidate Architectural Response Studio** (`Q1`–`Q5`) and click **`▶ Evaluate Session (100-Pt Rubric)`** for instant deterministic Bar-Raiser scoring across *Mechanisms (30)*, *Math & SLAs (20)*, *Trade-Offs & Failure Modes (25)*, *Operability (15)*, and *Clarity (10)*.

---

### Question 1: Hybrid BM25 + HNSW Vector Retrieval, RRF Math & Cross-Encoder Reranking
**Scenario:**  
Dense embeddings alone miss exact flight numbers (`AC-409`, `EU-261`) and chunking mid-table splits fee amounts from cabin headers.

**Your Task as Staff Architect:**
1. Architect structure-aware chunking + Contextual Retrieval + Hybrid BM25 + HNSW fused via Reciprocal Rank Fusion (`k=60`).
2. Explain why two-stage Bi-Encoder top-50 -> Cross-Encoder top-5 reranking improves precision while keeping p95 latency < 150ms.
3. Measure offline retrieval quality (`Recall@K`, `MRR`, `NDCG@K`) before touching LLM prompts.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 2: LLM-as-a-Judge Bias Modes & Rogan-Gladen Prevalence Calibration
**Scenario:**  
Your GPT/Gemini judge reports `84%` pass-rate, exhibits verbosity & position bias in A/B comparisons, and drifts across judge versions.

**Your Task as Staff Architect:**
1. Derive and apply **Rogan-Gladen** prevalence calibration (`p_hat = (p_obs + q0 - 1) / (q1 + q0 - 1)`) using a human-labeled gold audit set.
2. Mitigate pairwise position bias, verbosity bias, and self-preference bias in automated evals.
3. Compute bootstrap 95% confidence intervals so noisy 2% swings don't trigger false CI blocks.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 3: Negation Flips, Numeric Hallucinations & Abstention (`IDK`) Metamorphic QA
**Scenario:**  
An airline bot passes cosine-similarity checks even when it says `'Economy tickets ARE refundable after 24h'` (policy says `'NOT refundable'`).

**Your Task as Staff Architect:**
1. Explain why embedding cosine similarity fails catastrophically on negation flips, numeric swaps (`$75` vs `$750`), and entity swaps.
2. Design claim-decomposition NLI entailment + deterministic numeric/policy-rule extractors.
3. Build Metamorphic & Unanswerable-Query (`Abstention`) tests verifying the bot refuses out-of-scope legal/competitor questions.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 4: Multi-Turn MCP Tool-Calling Agent QA, Replay Cassettes & Indirect Prompt Injection
**Scenario:**  
A customer-support MCP agent can read emails/policies and call `issue_refund(order_id, cents)`; an attacker embeds hidden instructions inside a support ticket.

**Your Task as Staff Architect:**
1. Test multi-turn tool trajectories deterministically in CI without spending `$50` or hitting flaky live LLMs (`SHA-256` replay cassettes + mock MCP servers).
2. Architect defense-in-depth against **Indirect Prompt Injection** & confused-deputy tool escalation (untrusted data -> destructive tool).
3. Enforce JSON-Schema bounds, maximum dollar caps, human-in-the-loop (HITL) step-up auth, and `max_steps` loop breakers.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---

### Question 5: LLM Inference Economics — KV-Cache Prefix Caching, PagedAttention & Quantization QA
**Scenario:**  
Self-hosted vLLM latency spikes (`TTFT > 3.5s`, `ITL > 90ms`) under concurrent agent traffic, and `INT4 AWQ` quantization subtly degrades JSON tool-call validity.

**Your Task as Staff Architect:**
1. Calculate KV-Cache memory growth with context length and explain how **PagedAttention** + **Prefix Caching** cut `TTFT`.
2. Design a rigorous Quantization Regression Benchmark (`BF16` vs `FP8` vs `INT4`) measuring perplexity, RAG faithfulness, and constrained JSON/grammar accuracy.
3. Define streaming SSE load-test SLIs (`TTFT`, `ITL/TPOT`, `E2E latency`, token throughput) under realistic prompt-length distributions.

#### ✍️ Candidate Answer:
<!-- Draft your response in the Response Studio on the right -->

---
