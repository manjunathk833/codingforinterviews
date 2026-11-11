---
slug: aie-06-inference-mechanics-kv-cache-pagedattention-quantization
course_id: 05-ai-engineering
track: ai-engineering
volume: "05. Zero to Mastery: AI Engineering"
module_number: 2
module_title: "Module 2: Transformer Architecture & Modern LLM Internals"
chapter_number: 6
level_tag: "Beginner → Staff Systems"
title: "LLM Inference Systems: KV-Cache Math, PagedAttention, Speculative Decode & Quantization"
summary: "Scale AeroBrain v0.6 to serve 1,000 live flyers: why Prefill is math-heavy while Decode is memory-starved, exact KV-Cache sizing, vLLM PagedAttention 16-token virtual memory pages, Continuous Batching, AWQ quantization, and lossless Speculative Decoding."
reading_time_minutes: 24
visualizer_id: ai-transformer-kv-cache
lab_path: ai-engineering/03-hybrid-rag-rrf-and-attention
tags: ["ai-engineering", "kv-cache", "paged-attention", "vllm", "continuous-batching", "speculative-decoding", "quantization"]
---

# LLM Inference Systems: KV-Cache Math, PagedAttention, Speculative Decode & Quantization

```json continuity
{
  "previously": "In Chapter 05, we upgraded AeroBrain v0.5 with modern frontier internals—RoPE clock-hand positions, Pre-RMSNorm highways, Grouped-Query Attention (GQA), and Sparse Mixture-of-Experts (MoE).",
  "painPoint": "When we launch AeroBrain v0.5 to live passengers, generating a 500-word reply re-reads the entire conversation from Word #1 on every single step—slowing replies to a crawl! And when we cache past Keys and Values in giant pre-reserved memory slabs, 70% of our GPU memory sits empty and wasted.",
  "unlock": "We will build AeroBrain v0.6's high-throughput Inference Engine using an append-only KV-Cache notepad, PagedAttention 16-token memory blocks, Continuous Batching, and lossless Speculative Decoding."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "1. The KV-Cache Notepad",
    "caption": "Without a notepad, generating word 100 forces AeroBrain to recompute the Keys and Values for words 1 through 99 all over again. Caching past Keys and Values turns quadratic work into a fast single-word append.",
    "code": "kv_cache_k.append(new_token_k)\nkv_cache_v.append(new_token_v)  # Never recompute past words!"
  },
  {
    "time": "0:22",
    "badge": "2. Prefill vs Decode Roofline",
    "caption": "Reading the user's prompt happens all at once in parallel (Compute-Bound), while typing out the reply happens one word at a time, waiting on slow memory wires to stream 140 gigabytes of weights per word.",
    "code": "tpot_floor_ms = (weight_gb / gpu_bandwidth_gb_per_sec) * 1000.0"
  },
  {
    "time": "0:48",
    "badge": "3. PagedAttention 16-Token Pages",
    "caption": "Instead of reserving a massive 32,000-word table for a passenger who only asks a 20-word question, PagedAttention hands out small 16-word memory pages on demand like restaurant tables.",
    "code": "if current_tokens % 16 == 0:\n    page_table[req_id].append(free_blocks.pop())"
  },
  {
    "time": "1:12",
    "badge": "4. Speculative Draft Assistant",
    "caption": "A tiny, fast 1-billion assistant model drafts 5 words ahead, and our big 70-billion model grades all 5 words in one parallel pass with zero loss in quality.",
    "code": "accept_prob = min(1.0, p_target[draft_tok] / q_draft[draft_tok])"
  }
]
```

```json pretraining
[
  {
    "term": "KV-Cache Memory Formula",
    "formula": "Bytes = 2 * n_layers * n_kv_heads * d_head * bytes * B * L",
    "meaning": "The exact GPU memory needed to remember past Key and Value badges across all layers so AeroBrain never has to re-process old words."
  },
  {
    "term": "Prefill vs. Decode Phases",
    "formula": "Prefill = Parallel Prompt Read | Decode = 1-by-1 Word Stream",
    "meaning": "Prefill crunches the whole prompt at once (math-heavy), while Decode generates one reply word at a time (starved by how fast weights stream from memory)."
  },
  {
    "term": "PagedAttention (vLLM)",
    "formula": "Logical Chat -> Non-Contiguous 16-Token Physical Memory Pages",
    "meaning": "Splits the KV-Cache notepad into tiny 16-word pages allocated on demand, eliminating 70% of wasted pre-reserved GPU memory."
  },
  {
    "term": "Speculative Decoding",
    "formula": "Accept Draft x with probability min(1, p_target(x) / q_draft(x))",
    "meaning": "Uses a tiny fast model to guess 5 words ahead and lets the big model verify all 5 at once in a single memory read, giving 2-3x speedup with zero quality loss."
  }
]
```

## 🌱 Step 1: Plain-English Story — The Notepad, Restaurant Tables & Junior Drafts

In Chapter 05, **AeroBrain `v0.5`** gained a state-of-the-art brain (`RoPE`, `GQA`, and `MoE`). Now we turn on the live chat widget for 1,000 AeroCart passengers—and hit three real-world serving bottlenecks:

1. **Why Re-Read the Whole Book for Every Word? (`The KV-Cache Notepad`)**: When AeroBrain types out a reply (*"Your"` $\to$ `"bag"` $\to$ `"is"` $\to$ `"on"` $\to$ `"Carousel 4"*), Causal Masking guarantees that earlier words never change their Key or Value badges when a new word arrives. Instead of recalculating words `1..99` just to predict word `100`, we save every past word's Key and Value in a GPU memory notepad called the **`KV-Cache`**.
2. **Two Totally Different Jobs (`Prefill` vs. `Decode`)**: Answering a chat happens in two phases. First is **Prefill**: reading the passenger's 1,000-word ticket all at once in parallel (like grading 1,000 scantrons simultaneously—our GPU math cores work at 100%). Second is **Decode**: typing the reply **one word at a time** because word #2 depends on word #1. To type just *one* word, the GPU must haul all `140 GB` of model weights across its memory wires—leaving the math cores waiting `99%` of the time!
3. **Stop Reserving Empty Banquets (`PagedAttention` & `Continuous Batching`)**: We don't know ahead of time if a passenger's chat will last 20 words or 32,000 words. Reserving a contiguous 32,000-word slab per user wastes `70%+` of our GPU memory! Inspired by operating system virtual memory, **PagedAttention (`vLLM`)** hands out tiny **16-word memory pages** one by one only as the conversation grows, and immediately recycles them the millisecond a passenger finishes chatting.

```mermaid
flowchart LR
  Prompt["Passenger Ticket Arrives"] --> Prefill["1. Prefill Phase (Parallel Math)"]
  Prefill --> Pages["2. PagedAttention (16-Word KV Pages)"]
  Pages --> Decode["3. Decode Loop (Stream 1 Word/Step)"]
  Decode --> Free["4. Done -> Recycle KV Pages Instantly"]
```

---

## 🔨 Step 2: First Lines of Code — AeroBrain `v0.6` KV-Cache Sizer & 16-Token Page Allocator

Let's write a 17-line **AeroBrain `v0.6`** capacity sizer that computes the exact `KV-Cache` memory per token and allocates 16-token `PagedAttention` memory blocks on demand without wasting contiguous space.

```python
def kv_cache_kb_per_token(layers: int, kv_heads: int, d_head: int, bytes_per_val: int = 2) -> float:
    # Factor of 2 stores both Key (K) and Value (V) vectors at every layer
    return (2 * layers * kv_heads * d_head * bytes_per_val) / 1024.0

class MiniPagedAllocator:
    def __init__(self, total_blocks: int = 8, block_size: int = 16):
        self.free, self.block_size, self.tables = list(range(total_blocks)), block_size, {}

    def append_token(self, req_id: str, tok_idx: int) -> list[int]:
        if tok_idx % self.block_size == 0:  # Grab a new 16-token page only at boundary!
            self.tables.setdefault(req_id, []).append(self.free.pop(0))
        return self.tables[req_id]

alloc = MiniPagedAllocator()
for step in range(18):
    pages = alloc.append_token("ticket-42", step)
print(f"80L GQA KV/tok: {kv_cache_kb_per_token(80, 8, 128):.0f} KiB | Pages for 18 toks: {pages}")
```

### Java 17 Equivalent

```java
import java.util.*;

public class AeroBrainMiniPager {
    static double kvCacheKiBPerToken(int layers, int kvHeads, int dHead, int bytes) {
        return (2.0 * layers * kvHeads * dHead * bytes) / 1024.0;
    }

    public static void main(String[] args) {
        Deque<Integer> free = new ArrayDeque<>(List.of(0, 1, 2, 3, 4, 5));
        List<Integer> pages = new ArrayList<>();
        for (int step = 0; step < 18; step++) {
            if (step % 16 == 0) pages.add(free.pollFirst()); // Allocate 16-token page on demand
        }
        System.out.printf("80L GQA KV/tok: %.0f KiB | Pages for 18 toks: %s%n",
            kvCacheKiBPerToken(80, 8, 128, 2), pages);
    }
}
```

---

## ⚡ Step 3: Where It Breaks in Real Life — KV-Cache Explosion & Naive INT4 Outlier Brain-Damage

As traffic to `AeroBrain v0.6` surges during a winter storm, two production traps threaten to take down our GPU cluster:

1. **When the `KV-Cache` Grows Bigger Than the Model Itself**: Engineers often check that a `70B` model's weights (`140 GB`) fit across two `80 GB` GPUs and assume they are safe. Then 16 passengers open 32,768-token chats simultaneously: at `320 KiB` per token, `16 × 32,768` tokens demand **`160 GiB` of `KV-Cache` alone**—more memory than the entire 70-billion brain!
2. **Why Naive 4-Bit Compression (`INT4`) Destroys Accuracy**: To shrink weights by `4x`, an engineer rounds every weight into a 4-bit integer (`-8` to `+7`). Suddenly AeroBrain starts speaking gibberish! Why? In large models (`>6.7B`), roughly **1% of neuron channels carry 100x larger outlier spikes** than normal channels. Stretching a 16-step ruler to cover one giant `+65.0` spike squashes 99% of normal `[-0.5, +0.5]` weights down to **zero**—requiring **Activation-Aware Weight Quantization (`AWQ`)** to protect those 1% salient channels!

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

---

## 🚀 Step 4: Staff Engineer Deep-Dive — Roofline Physics, `PagedAttention` CoW & Speculative Decoding

### 1. Hardware Roofline Analysis & Exact `KV-Cache` Sizing

Serving LLMs in production consists of two hardware-orthogonal phases governed by the GPU **Arithmetic Intensity Roofline** ($\text{FLOPs} / \text{Bytes Transferred}$):

$$\text{KV-Cache Bytes} = 2 \times n_{\text{layers}} \times n_{\text{kv\_heads}} \times d_{\text{head}} \times \text{bytes\_per\_elem} \times B \times L$$

- On an **NVIDIA H100 SXM**, BF16 Tensor Core peak compute is **`989 TFLOP/s`**, while HBM3 memory bandwidth is **`3.35 TB/s`**, putting the Roofline ridge point at:
  $$I_{\text{ridge}} = \frac{989 \times 10^{12}\text{ FLOP/s}}{3.35 \times 10^{12}\text{ Bytes/s}} \approx \mathbf{295\text{ FLOPs/Byte}}$$
- **Phase 1 — Prefill (`TTFT` — Time To First Token)**: Processes all $L = 4,096$ prompt tokens **in parallel** via dense Matrix-Matrix multiplications (`[4096, d] @ [d, d]`). Arithmetic intensity exceeds `2,000 FLOPs/Byte` $\implies$ **strictly Compute-Bound**.
- **Phase 2 — Autoregressive Decode (`TPOT` — Time Per Output Token)**: Generates `1` new token per request. At `batch_size = 1`, `[1, d] @ [d, d]` performs only `1 FLOP/Byte` ($\ll 295$). Tensor Cores sit **`99.6%` idle** waiting for `140 GB` of 70B weights to stream across the `3.35 TB/s` HBM bus ($\frac{140\text{ GB}}{3.35\text{ TB/s}} \approx 41.8\text{ ms/token}$ floor).

| Optimization Lever | What Hardware Wall It Attacks | Perplexity / Quality Impact | Production Trade-Off |
| :--- | :--- | :--- | :--- |
| **`PagedAttention` (`vLLM`)** | KV-Cache fragmentation $\to$ unlocks `4x` larger batch size $B$ | **Zero (`0.00%` exact)** | Indirection lookup kernel overhead (`<3%`) dwarfed by `4x` batch gain |
| **Chunked Prefill** | Prevents a `32k` prefill from stalling in-flight decode `TPOT` | **Zero (`0.00%` exact)** | Splits massive prefills into `512/1024`-token slices piggybacked with decode steps |
| **Speculative Decoding** | Cuts single-stream `TPOT` by verifying $K$ draft tokens in `1` weight read | **Mathematically Lossless!** | Helps deeply at low/medium batch sizes ($B \le 16$); hurts at saturated high-compute batches! |
| **`FP8` (`E4M3` W8A8 + KV)** | Halves weight & KV HBM bytes (`2B -> 1B`) + doubles H100 Tensor TFLOPs (`1979`) | Near-zero (`<0.3%` drift) | Requires Hopper (`H100`/`H200`) / Blackwell (`B200`) or Ada native FP8 Tensor Cores |
| **`AWQ` / `GPTQ` (`W4A16` INT4)** | Shrinks static weights `4x` (`70B`: `140GB -> ~38GB` fits `1x 48GB/80GB` GPU!) | Small (`~0.8–1.5%` on hard math/code) | Dequantizes `INT4 -> FP16` in registers (`W4A16`): accelerates low-batch HBM wall, NOT high-batch compute! |

### 2. Dual-Language Production Blueprints: Roofline Planner, Speculative Verifier & `PagedAttention` CoW

```python
from __future__ import annotations
from dataclasses import dataclass
import random
from typing import List


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
    weight_bytes: float = 2.0,
    kv_bytes: float = 2.0,
    target_ctx_len: int = 8192,
    vram_utilization: float = 0.90,
    activation_overhead_gb: float = 3.0,
) -> CapacityPlan:
    """Computes exact multi-GPU Tensor-Parallel VRAM budget & HBM roofline decode floor."""
    total_vram_gb = gpu_vram_gb * num_gpus_tp * vram_utilization
    weight_gb = arch.params_billions * weight_bytes
    kv_bytes_per_token = 2 * arch.n_layers * arch.n_kv_heads * arch.d_head * kv_bytes

    avail_kv_bytes = (total_vram_gb - weight_gb - activation_overhead_gb) * 1_000_000_000.0
    if avail_kv_bytes <= 0:
        raise ValueError(f"OOM: Weights ({weight_gb:.1f} GB) exceed usable VRAM ({total_vram_gb:.1f} GB)")

    max_seqs = int(avail_kv_bytes // (kv_bytes_per_token * target_ctx_len))
    min_tpot_ms = (weight_gb / (gpu_hbm_bw_GBps * num_gpus_tp)) * 1000.0
    return CapacityPlan(
        weight_gb=round(weight_gb, 2),
        kv_per_token_kb=round(kv_bytes_per_token / 1000.0, 2),
        max_concurrent_seqs_at_ctx=max_seqs,
        min_single_stream_tpot_ms=round(min_tpot_ms, 2),
    )


def speculative_rejection_step(
    draft_token: int, p_target: List[float], q_draft: List[float], rng: random.Random
) -> int:
    """Lossless Speculative Decoding Step: guarantees emitted token matches p_target(x)."""
    pt = p_target[draft_token]
    qd = max(1e-12, q_draft[draft_token])
    if rng.random() <= min(1.0, pt / qd):
        return draft_token

    residual = [max(0.0, p - q) for p, q in zip(p_target, q_draft)]
    r = rng.random() * sum(residual)
    cum = 0.0
    for tok_id, mass in enumerate(residual):
        cum += mass
        if r <= cum:
            return tok_id
    return len(residual) - 1
```

### Java 17 Equivalent

```java
package com.hub.ai.serving;

import java.util.*;

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
        if (currentSeqLenTokens % blockSizeTokens == 0) {
            Integer fresh = freePhysicalBlocks.pollFirst();
            if (fresh == null) throw new IllegalStateException("KV Block Pool Exhausted");
            refCounts.put(fresh, 1);
            table.add(fresh);
            return fresh;
        }
        int lastIdx = table.size() - 1;
        int tailBlock = table.get(lastIdx);
        if (refCounts.get(tailBlock) > 1) {
            Integer cowBlock = freePhysicalBlocks.pollFirst();
            if (cowBlock == null) throw new IllegalStateException("KV Pool Exhausted on CoW");
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
            if (nextRef == 0) freePhysicalBlocks.addFirst(blk);
        }
    }
}
```

> [!WARNING] **Staff Interview Gotcha — Why Naive `INT8`/`INT4` Quantization Fails Above `6.7B` Parameters ("Emergent Activation Outliers"):** As discovered in `LLM.int8()` (Dettmers et al.) and `AWQ` (Lin et al.), once Transformers pass `~6.7B` parameters, roughly **`0.1%` to `1%` of hidden feature channels systematically develop `20x–100x` larger activation magnitudes** across *every* token and layer! Naive per-tensor uniform quantization stretches the `INT4` grid `[-8, +7]` to fit that single `+65.0` outlier channel, crushing `99.9%` of normal `[-0.5, +0.5]` weights to **`0` (total catastrophic brain-damage)**! **AWQ (Activation-Aware Weight Quantization)** fixes this without mixed-precision hardware slowdowns by observing calibration activations and multiplying those `1%` salient weight channels up by scale $s > 1$ (while dividing the input activation by $s$) prior to `128`-element group `INT4` quantization!

**Up Next in Chapter 07:** Our **AeroBrain `v0.6`** engine now streams tokens at blazing speed with `PagedAttention` and `AWQ`, but how do we control *which* words it picks so it never invents fake JSON keys or hallucinates non-existent flight numbers? In **Chapter 07**, we upgrade to **AeroBrain `v0.7`** with **Autoregressive Sampling (`Temperature`, `Top-K`, `Top-P`, `Min-P`)** and **FSM-Constrained Structured Decoding (`Outlines` / `XGrammar`)**.

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
