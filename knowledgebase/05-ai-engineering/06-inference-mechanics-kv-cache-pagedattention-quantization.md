---
slug: aie-06-inference-mechanics-kv-cache-pagedattention-quantization
course_id: 05-ai-engineering
track: ai-engineering
volume: "05. Zero to Mastery: AI Engineering"
module_number: 2
module_title: "Module 2: Transformer Architecture & Modern LLM Internals"
chapter_number: 6
level_tag: "Senior → Staff Systems"
title: "LLM Inference Systems: KV-Cache Math, PagedAttention, Speculative Decode & Quantization"
summary: "Hardware roofline analysis of compute-bound Prefill vs memory-bandwidth-bound Decode, exact KV-Cache VRAM calculation, vLLM PagedAttention virtual-memory blocks & Continuous Batching, Speculative Decoding lossless rejection sampling, and BF16 vs FP8 vs INT4 AWQ quantization."
reading_time_minutes: 24
visualizer_id: ai-transformer-kv-cache
lab_path: ai-engineering/03-hybrid-rag-rrf-and-attention
tags: ["ai-engineering", "kv-cache", "paged-attention", "vllm", "continuous-batching", "speculative-decoding", "quantization"]
---

# LLM Inference Systems: KV-Cache Math, PagedAttention, Speculative Decode & Quantization

```json pretraining
[
  {
    "term": "Exact KV-Cache Bytes",
    "formula": "Bytes = 2 * n_layers * n_kv_heads * d_head * bytes_per_elem * B * L",
    "meaning": "The factor 2 stores both Key and Value tensors across all layers; GQA shrinks n_kv_heads (e.g., 64 -> 8) for an immediate 8x RAM win!"
  },
  {
    "term": "Roofline Intensity",
    "formula": "Prefill: MatMul [L x d] (Compute-Bound) | Decode: MatVec [1 x d] (HBM-Bound)",
    "meaning": "Generating 1 decode token at B=1 streams ALL 140GB of 70B BF16 weights over 3.35 TB/s HBM3 -> theoretical floor ~42ms/token!"
  },
  {
    "term": "vLLM PagedAttention",
    "formula": "Logical KV Sequence -> Non-Contiguous 16-Token Physical KV Blocks",
    "meaning": "Eliminates ~60-80% contiguous max_seq_len VRAM fragmentation via OS-inspired page tables + Copy-on-Write prefix sharing."
  },
  {
    "term": "Speculative Acceptance",
    "formula": "Accept Draft Token x ~ q(x) with prob min(1, p_target(x) / q_draft(x))",
    "meaning": "Verifies K=5 cheap draft tokens in ONE parallel target-model forward pass with mathematically identical output distribution to p_target!"
  }
]
```

```json poe
{
  "question": "Calculate the exact KV-Cache VRAM required to serve batch size B = 16 concurrent requests at sequence length L = 32,768 tokens on Llama-3 70B (n_layers = 80, n_q_heads = 64, n_kv_heads = 8 via GQA, d_head = 128) stored in BF16 (2 bytes/element).",
  "options": [
    "1,374.4 GB (using n_q_heads = 64)",
    "171.80 GB  (2 * 80 * 8 * 128 * 2 * 16 * 32,768 = 171,798,691,840 bytes ≈ 160.0 GiB / 171.8 GB!)",
    "21.47 GB",
    "4.29 GB"
  ],
  "answerIndex": 1,
  "explanation": "Per token: 2 (K+V) * 80 layers * 8 KV heads * 128 d_head * 2 bytes = 327,680 bytes (320 KiB/token). Multiply by B=16 * L=32,768 (524,288 tokens) = 171,798,691,840 bytes (exactly 160 GiB)—exceeding the static 140 GB BF16 model weights themselves! Without GQA (if n_kv_heads=64), it would require 1,280 GiB!"
}
```

## 1. Roofline Physics: Why Prefill Is Compute-Bound & Decode Is HBM Bandwidth-Bound

Serving LLMs in production consists of two hardware-orthogonal phases governed by the GPU **Arithmetic Intensity Roofline** ($\text{FLOPs} / \text{Bytes Transferred}$):
- On an **NVIDIA H100 SXM**, BF16 Tensor Core peak compute is **`989 TFLOP/s`**, while HBM3 memory bandwidth is **`3.35 TB/s`**, putting the Roofline ridge point at $\frac{989 \times 10^{12}}{3.35 \times 10^{12}} \approx \mathbf{295\text{ FLOPs/Byte}}$.
- **Phase 1 — Prefill (`TTFT` — Time To First Token)**: Processes all $L = 4,096$ prompt tokens **in parallel** via dense Matrix-Matrix multiplications (`[4096, d] @ [d, d]`). Arithmetic intensity exceeds `2,000 FLOPs/Byte` $\implies$ **strictly Compute-Bound** (`Tensor Cores` saturated near `100%`).
- **Phase 2 — Autoregressive Decode (`TPOT` — Time Per Output Token)**: Generates `1` new token per request using cached past Keys/Values (`KV-Cache`). At `batch_size = 1`, `[1, d] @ [d, d]` performs only `2 FLOPs` per `2-byte` BF16 weight read (**`1 FLOP/Byte` $\ll 295$!**). Tensor Cores sit **`99.6%` idle** waiting for `140 GB` of 70B weights to stream across the `3.35 TB/s` HBM bus ($\frac{140\text{ GB}}{3.35\text{ TB/s}} \approx 41.8\text{ ms/token}$, or `23.9 tokens/sec` hard physical ceiling!).

```mermaid
flowchart LR
  Req["Incoming Prompt Stream"] -->|Iteration-Level Slot| CB["Continuous Batching Scheduler"]
  CB -->|Prefill Chunked MatMul| Page["PagedAttention Block Table (16-Tok Pages)"]
  Page -->|HBM Stream FP8 / AWQ INT4| Dec["Autoregressive / Speculative Decode"]
  Dec -->|EOS Reached Early| Free["Immediate Block Reclamation (<1ms)"]
```

---

## 2. `PagedAttention`, Continuous Batching, Speculative Decoding & Quantization

```json contrast
{
  "title": "Naive Static Contiguous Batching vs vLLM / TensorRT-LLM Production Stack",
  "naiveTitle": "Static Batch + Contiguous KV + BF16",
  "naiveMetric": "72% Wasted KV VRAM · 8x Lower RPS",
  "naivePoints": [
    "Pre-allocates contiguous [B, max_seq_len=32768] KV tensors even when average request finishes in 450 tokens (70%+ waste)",
    "Static batching stalls short 30-token answers waiting for the longest 2,000-token essay in the batch to hit <EOS>",
    "Naive uniform INT4 round-to-nearest quantization destroys accuracy because 0.1% of activation channels have 100x outlier magnitudes!"
  ],
  "staffTitle": "Continuous Batching + PagedAttention + FP8/AWQ",
  "staffMetric": "<4% Fragmentation · 3-5x Higher Throughput",
  "staffPoints": [
    "PagedAttention allocates fixed 16-token physical KV blocks on demand via virtual page tables (<4% internal waste)",
    "Iteration-level Continuous Batching + Chunked Prefill evicts finished sequences immediately and injects waiting requests mid-flight",
    "Uses hardware Hopper FP8 (W8A8 + FP8 KV-Cache) or Activation-Aware INT4 (AWQ) scaling salient 1% outlier channels cleanly"
  ]
}
```

| Optimization Lever | What Hardware Wall It Attacks | Perplexity / Quality Impact | Production Trade-Off |
| :--- | :--- | :--- | :--- |
| **`PagedAttention` (`vLLM`)** | KV-Cache fragmentation $\to$ unlocks `4x` larger batch size $B$ | **Zero (`0.00%` exact)** | Indirection lookup kernel overhead (`<3%`) dwarfed by `4x` batch gain |
| **Chunked Prefill** | Prevents a `32k` prefill from stalling in-flight decode `TPOT` | **Zero (`0.00%` exact)** | Splits massive prefills into `512/1024`-token slices piggybacked with decode steps |
| **Speculative Decoding** | Cuts single-stream `TPOT` by verifying $K$ draft tokens in `1` weight read | **Mathematically Lossless!** | Helps deeply at low/medium batch sizes ($B \le 16$); hurts at saturated high-compute batches! |
| **`FP8` (`E4M3` W8A8 + KV)** | Halves weight & KV HBM bytes (`2B -> 1B`) + doubles H100 Tensor TFLOPs (`1979`) | Near-zero (`<0.3%` drift) | Requires Hopper (`H100`/`H200`) / Blackwell (`B200`) or Ada native FP8 Tensor Cores |
| **`AWQ` / `GPTQ` (`W4A16` INT4)** | Shrinks static weights `4x` (`70B`: `140GB -> ~38GB` fits `1x 48GB/80GB` GPU!) | Small (`~0.8–1.5%` on hard math/code) | Dequantizes `INT4 -> FP16` in registers (`W4A16`): accelerates low-batch HBM wall, NOT high-batch compute! |

---

## 3. Dual-Language Production Blueprints: `KV-Cache` Capacity Planner, `PagedAttention` & `AWQ`

### Python 3 Blueprint: Exact `KV-Cache` & Roofline Capacity Planner + Lossless Speculative Verifier
```python
from __future__ import annotations
from dataclasses import dataclass
import math
import random
from typing import Dict, List


@dataclass(frozen=True)
class ModelArchSpec:
    name: str
    params_billions: float
    n_layers: int
    n_kv_heads: int
    d_head: int


@dataclass(frozen=True)
class CapacityPlan:
    weight_gb: float
    kv_per_token_kb: float
    max_concurrent_seqs_at_ctx: int
    min_single_stream_tpot_ms: float


def plan_gpu_serving_capacity(
    arch: ModelArchSpec,
    gpu_vram_gb: float,
    gpu_hbm_bw_GBps: float,
    num_gpus_tp: int = 1,
    weight_bytes: float = 2.0,     # BF16=2.0, FP8=1.0, INT4_AWQ=0.55 (incl. group scales)
    kv_bytes: float = 2.0,         # BF16=2.0, FP8_KV=1.0
    target_ctx_len: int = 8192,
    vram_utilization: float = 0.90,
    activation_overhead_gb: float = 3.0,
) -> CapacityPlan:
    """Computes exact multi-GPU Tensor-Parallel VRAM budget & HBM roofline decode floor."""
    total_vram_gb = gpu_vram_gb * num_gpus_tp * vram_utilization
    weight_gb = arch.params_billions * weight_bytes  # 1e9 * bytes = GB (decimal)
    kv_bytes_per_token = 2 * arch.n_layers * arch.n_kv_heads * arch.d_head * kv_bytes

    avail_kv_bytes = (total_vram_gb - weight_gb - activation_overhead_gb) * 1_000_000_000.0
    if avail_kv_bytes <= 0:
        raise ValueError(f"OOM: Weights ({weight_gb:.1f} GB) exceed usable VRAM ({total_vram_gb:.1f} GB)")

    bytes_per_full_seq = kv_bytes_per_token * target_ctx_len
    max_seqs = int(avail_kv_bytes // bytes_per_full_seq)

    # Single-request decode latency floor = Weight Bytes / Aggregate TP HBM Bandwidth
    agg_bw_GBps = gpu_hbm_bw_GBps * num_gpus_tp
    min_tpot_ms = (weight_gb / agg_bw_GBps) * 1000.0
    return CapacityPlan(
        weight_gb=round(weight_gb, 2),
        kv_per_token_kb=round(kv_bytes_per_token / 1000.0, 2),
        max_concurrent_seqs_at_ctx=max_seqs,
        min_single_stream_tpot_ms=round(min_tpot_ms, 2),
    )


def speculative_rejection_step(
    draft_token: int,
    p_target: List[float],
    q_draft: List[float],
    rng: random.Random,
) -> int:
    """
    Leviathan et al. / Chen et al. Exact Lossless Speculative Decoding Step:
    Guarantees the emitted token is distributed IDENTICALLY to p_target(x)!
    """
    pt = p_target[draft_token]
    qd = max(1e-12, q_draft[draft_token])
    accept_prob = min(1.0, pt / qd)
    if rng.random() <= accept_prob:
        return draft_token

    # Rejected! Sample replacement token from residual max(0, p_target - q_draft) normalized
    residual = [max(0.0, p - q) for p, q in zip(p_target, q_draft)]
    total = sum(residual)
    r = rng.random() * total
    cum = 0.0
    for tok_id, mass in enumerate(residual):
        cum += mass
        if r <= cum:
            return tok_id
    return len(residual) - 1
```

### Java 17 Blueprint: `PagedAttention` Block Manager with Copy-on-Write (`CoW`) Prefix Sharing
```java
package com.hub.ai.serving;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Deterministic model of vLLM's PagedAttention Virtual-Memory Block Allocator:
 * - Allocates fixed `blockSize` (e.g. 16 tokens) physical KV blocks from a free-list.
 * - Supports zero-copy shared system-prompt prefixes with Copy-on-Write (refCount > 1) on divergence.
 */
public final class PagedKvBlockAllocator {

    private final int blockSizeTokens;
    private final Deque<Integer> freePhysicalBlocks = new ArrayDeque<>();
    private final Map<Integer, Integer> refCounts = new HashMap<>();
    private final Map<String, List<Integer>> pageTables = new HashMap<>();

    public PagedKvBlockAllocator(int totalPhysicalBlocks, int blockSizeTokens) {
        this.blockSizeTokens = blockSizeTokens;
        for (int b = 0; b < totalPhysicalBlocks; b++) {
            freePhysicalBlocks.addLast(b);
            refCounts.put(b, 0);
        }
    }

    public int allocateSequenceWithSharedPrefix(String seqId, List<Integer> sharedPrefixBlocks) {
        List<Integer> table = new ArrayList<>(sharedPrefixBlocks);
        for (int blk : sharedPrefixBlocks) {
            refCounts.put(blk, refCounts.get(blk) + 1);
        }
        pageTables.put(seqId, table);
        return freePhysicalBlocks.size();
    }

    public int appendTokenSlot(String seqId, int currentSeqLenTokens) {
        List<Integer> table = pageTables.get(seqId);
        int offsetInBlock = currentSeqLenTokens % blockSizeTokens;

        if (offsetInBlock == 0) {
            // Crossing 16-token boundary -> grab 1 fresh physical block on demand!
            Integer fresh = freePhysicalBlocks.pollFirst();
            if (fresh == null) {
                throw new IllegalStateException("KV Block Pool Exhausted -> Preempt/Swap Request");
            }
            refCounts.put(fresh, 1);
            table.add(fresh);
            return fresh;
        }

        // Writing into partially filled tail block: if shared (refCount > 1), execute Copy-on-Write!
        int lastIdx = table.size() - 1;
        int tailBlock = table.get(lastIdx);
        if (refCounts.get(tailBlock) > 1) {
            Integer cowBlock = freePhysicalBlocks.pollFirst();
            if (cowBlock == null) {
                throw new IllegalStateException("KV Pool Exhausted during Copy-on-Write");
            }
            refCounts.put(tailBlock, refCounts.get(tailBlock) - 1);
            refCounts.put(cowBlock, 1);
            table.set(lastIdx, cowBlock);
            return cowBlock;
        }
        return tailBlock;
    }

    public void freeSequence(String seqId) {
        List<Integer> table = pageTables.remove(seqId);
        if (table == null) return;
        for (int blk : table) {
            int nextRef = refCounts.get(blk) - 1;
            refCounts.put(blk, nextRef);
            if (nextRef == 0) {
                freePhysicalBlocks.addFirst(blk);
            }
        }
    }
}
```

> [!WARNING] **Staff Interview Gotcha — Why Naive `INT8`/`INT4` Quantization Fails Above `6.7B` Parameters ("Emergent Activation Outliers"):** As discovered in `LLM.int8()` (Dettmers et al.) and `AWQ` (Lin et al.), once Transformers pass `~6.7B` parameters, roughly **`0.1%` to `1%` of hidden feature channels systematically develop `20x–100x` larger activation magnitudes** across *every* token and layer! Naive per-tensor uniform quantization stretches the `INT4` grid `[-8, +7]` to fit that single `+65.0` outlier channel, crushing `99.9%` of normal `[-0.5, +0.5]` weights to **`0` (total catastrophic brain-damage)**! **AWQ (Activation-Aware Weight Quantization)** fixes this without mixed-precision hardware slowdowns by observing calibration activations and multiplying those `1%` salient weight channels up by scale $s > 1$ (while dividing the input activation by $s$) prior to `128`-element group `INT4` quantization!

---

## 4. Scenario Retrieval-Practice Mastery Gate

```json quiz
[
  {
    "id": "aie-06-q1",
    "question": "Why does doubling Tensor Parallelism from TP=1 to TP=2 across NVLink-connected H100 GPUs cut single-user Decode latency (TPOT) nearly in half (~42ms -> ~22ms for 70B BF16), whereas Pipeline Parallelism (PP=2) does NOT reduce single-user TPOT?",
    "options": [
      "Pipeline Parallelism disables the KV-Cache",
      "Single-user Decode is HBM memory-bandwidth bound: TP=2 shards every layer's weight matrices across 2 GPUs that stream HBM simultaneously in parallel (2 * 3.35 = 6.7 TB/s aggregate bandwidth!), whereas PP=2 runs layers 0..39 on GPU-0 while GPU-1 sits idle and then 40..79 on GPU-1 (1x active HBM bandwidth at any instant)",
      "NVLink is faster than SRAM",
      "PP=2 doubles total model parameter count"
    ],
    "answerIndex": 1,
    "explanation": "Tensor Parallelism aggregates HBM memory bandwidth simultaneously on every token step (slashing TPOT at the cost of 2 all-reduce syncs per layer over fast intra-node NVLink), whereas Pipeline Parallelism only increases multi-batch capacity/throughput."
  },
  {
    "id": "aie-06-q2",
    "question": "A customer sends a single 64,000-token RAG prompt to a vLLM cluster currently mid-way through streaming tokens to 40 interactive chat users. Without 'Chunked Prefill', what happens to those 40 chat users' streaming latency?",
    "options": [
      "Nothing, CUDA streams isolate HBM bandwidth completely",
      "Severe Inter-Token Latency (ITL / TPOT) Stall ('Generation Hiccup'): a monolithic 64k prefill monopolizes 100% of GPU compute for 2–4 full seconds, freezing token streaming for all 40 active chat users; Chunked Prefill slices the 64k prefill into e.g. 1,024-token chunks interleaved alongside active decode steps",
      "vLLM drops the 40 active connections with HTTP 503",
      "PagedAttention compresses 64k tokens into 1 block"
    ],
    "answerIndex": 1,
    "explanation": "Chunked Prefill bounds per-iteration prefill compute budget so active streaming users maintain smooth <50ms inter-token p99 SLAs even during giant prompt arrivals."
  },
  {
    "id": "aie-06-q3",
    "question": "Does Speculative Decoding (using a fast 1B draft model to propose 5 tokens verified in parallel by a 70B target model) slightly degrade output benchmark accuracy compared to pure 70B decoding?",
    "options": [
      "Yes, accuracy drops toward the 1B draft model whenever draft confidence exceeds 0.8",
      "NO—mathematically ZERO degradation! Speculative Rejection Sampling accepts with min(1, p_target/q_draft) and resamples rejections from normalized max(0, p_target - q_draft), guaranteeing the exact target distribution p_target(x) (up to floating-point precision); bad draft models only reduce speedup ratio, never output quality!",
      "Yes, unless temperature is strictly 0.0",
      "Only on coding tasks"
    ],
    "answerIndex": 1,
    "explanation": "Speculative decoding is a pure systems latency optimization whose rejection-sampling theorem recovers p_target(x) identically for any positive draft distribution q_draft(x)."
  }
]
```
