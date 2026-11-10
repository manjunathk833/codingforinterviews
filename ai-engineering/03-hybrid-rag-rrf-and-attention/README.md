# AI Engineering Lab 03: Scaled Dot-Product Self-Attention & Hybrid RAG (`BM25 + Dense + RRF`)

This 100% deterministic, zero-external-dependency lab implements:
1. **Scaled Dot-Product Self-Attention ($\text{softmax}(QK^T / \sqrt{d_k} + M)V$)** with causal upper-triangular masking (`-inf`) verifying that token $t$ strictly assigns `0.0` attention probability to future tokens $t' > t$.
2. **Reciprocal Rank Fusion (`RRF`, $k=60$)** fusing lexical `BM25` keyword rankings (which catch exact error codes like `ERR_TLS_409`) with dense cosine semantic rankings into a unified top-$K$ context window.

## Run Locally (Zero AI)
```bash
./run.sh test 03-hybrid-rag-rrf-and-attention
```
