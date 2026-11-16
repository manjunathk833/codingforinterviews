## 🧠 Conceptual Mastery Guide — Session #6: Production AI, RAG & Agentic QE

**Milestone:** `Phase 5 Exit Gate` · **Target Bar:** `>= 85 / 100` across all 5 Staff dimensions.

## Core Architectural Mental Models & Benchmark Blueprints

### Q1: Hybrid BM25 + HNSW Vector Retrieval, RRF Math & Cross-Encoder Reranking
- **Problem Core:** Dense embeddings alone miss exact flight numbers (`AC-409`, `EU-261`) and chunking mid-table splits fee amounts from cabin headers.
- **Staff Benchmark Synthesis:** Keep Markdown/HTML tables intact with prepended document/section headers (Contextual Retrieval), fuse Okapi BM25 + HNSW dense hits via scale-invariant RRF `sum(1 / (60 + rank))`, rerank top-50 candidates to top-5 with a Cross-Encoder (`<80ms`), and gate index changes on `Recall@5` and `NDCG@5`.
- ** Trap / Anti-Patterns to Reject:** `naive fixed 500-char split cutting markdown tables`, `cross-encode all 1M docs`

### Q2: LLM-as-a-Judge Bias Modes & Rogan-Gladen Prevalence Calibration
- **Problem Core:** Your GPT/Gemini judge reports `84%` pass-rate, exhibits verbosity & position bias in A/B comparisons, and drifts across judge versions.
- **Staff Benchmark Synthesis:** Calibrate binary atomic rubrics (`temperature=0`) against a 200-sample human gold set (`Cohen's kappa >= 0.75`) to measure judge `TPR (q1)` and `TNR (q0)`, debiasing raw `p_obs` via `p_hat = clip((p_obs + q0 - 1)/(q1 + q0 - 1), 0, 1)` with bootstrap 95% CIs, and run A/B pairwise evals in both `(A,B)` and `(B,A)` orders.
- ** Trap / Anti-Patterns to Reject:** `uncalibrated 1-10 vague rubric`, `single-order pairwise comparison`

### Q3: Negation Flips, Numeric Hallucinations & Abstention (`IDK`) Metamorphic QA
- **Problem Core:** An airline bot passes cosine-similarity checks even when it says `'Economy tickets ARE refundable after 24h'` (policy says `'NOT refundable'`).
- **Staff Benchmark Synthesis:** `'Tickets are refundable'` and `'Tickets are NOT refundable'` share >0.96 cosine similarity! Decompose answers into atomic claims verified by 3-way NLI (`ENTAILMENT / NEUTRAL / CONTRADICTION`) + exact regex number/currency subset checks against cited chunks, and maintain an unanswerable/perturbed metamorphic suite asserting clean abstention.
- ** Trap / Anti-Patterns to Reject:** `grade rag answers using only embedding cosine similarity`

### Q4: Multi-Turn MCP Tool-Calling Agent QA, Replay Cassettes & Indirect Prompt Injection
- **Problem Core:** A customer-support MCP agent can read emails/policies and call `issue_refund(order_id, cents)`; an attacker embeds hidden instructions inside a support ticket.
- **Staff Benchmark Synthesis:** Run PR trajectory tests against deterministic `SHA-256(messages + tool_schemas)` cassettes + stateful mock MCP sandboxes (paired with a small nightly live-model canary). Enforce strict JSON-Schema validation, hard policy caps in code (never prompt-only!), taint-tracking/HITL confirmation whenever untrusted ticket/email text precedes write tools, and `max_steps` loop breakers.
- ** Trap / Anti-Patterns to Reject:** `let llm pass raw sql`, `auto-execute unbounded refunds from untrusted text`

### Q5: LLM Inference Economics — KV-Cache Prefix Caching, PagedAttention & Quantization QA
- **Problem Core:** Self-hosted vLLM latency spikes (`TTFT > 3.5s`, `ITL > 90ms`) under concurrent agent traffic, and `INT4 AWQ` quantization subtly degrades JSON tool-call validity.
- **Staff Benchmark Synthesis:** Keep static system prompts + tool schemas byte-identical at prefix index 0 (moving timestamps/user IDs to the tail) so vLLM PagedAttention shares KV-cache blocks (`-60% TTFT`, `<4%` fragmentation). Benchmark `FP8`/`INT4` against `BF16` on hard tool-call + math/negation evals with FSM constrained decoding, and load-test SSE streams measuring `p95 TTFT` (prefill) separately from `p95 ITL/TPOT` (decode).
- ** Trap / Anti-Patterns to Reject:** `put dynamic timestamp at the very start of system prompt breaking prefix cache`

## Deep-Linked Textbook Chapters
- `aie-06-inference-mechanics-kv-cache-pagedattention-quantization`
- `aie-09-hybrid-rag-chunking-hnsw-bm25-and-rrf`
- `ai-01-rag-triad-and-claim-verification`
- `aiqa-06-statistical-judge-calibration-kappa-and-rogan-gladen`
- `ai-02-self-healing-ast-and-dom-confidence`
- `aiqa-08-agent-trajectory-qa-and-mock-mcp-sandboxes`
