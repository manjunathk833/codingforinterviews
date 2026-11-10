---
slug: aie-04-scaled-dot-product-attention-and-causal-masking
course_id: 05-ai-engineering
track: ai-engineering
volume: "05. Zero to Mastery: AI Engineering"
module_number: 2
module_title: "Module 2: Transformer Architecture & Modern LLM Internals"
chapter_number: 4
level_tag: "Beginner → Staff AI Engineer"
title: "Scaled Dot-Product Attention, Variance Scaling, Multi-Head Subspaces & Causal Masks"
summary: "Upgrade AeroBrain v0.4 with a differentiable search engine: why words look up past words using Queries, Keys, and Values, why dividing by the square root of head size saves training, how causal blinders stop future cheating, and how FlashAttention keeps GPU memory fast."
reading_time_minutes: 23
visualizer_id: ai-transformer-kv-cache
lab_path: ai-engineering/03-hybrid-rag-rrf-and-attention
tags: ["ai-engineering", "transformers", "self-attention", "multi-head-attention", "causal-masking", "flash-attention", "llm-internals"]
---

# Scaled Dot-Product Attention, Variance Scaling, Multi-Head Subspaces & Causal Masks

```json continuity
{
  "previously": "In Chapter 03, we upgraded AeroBrain v0.3 with BPE subword tokenization and 3D cosine vector embeddings so flight support tickets turn into rich numerical coordinates.",
  "painPoint": "However, static word vectors are context-blind! In 'The flight to Boston was delayed because it snowed there', the word 'there' has the exact same static vector whether the sentence talks about Boston or Miami. AeroBrain v0.3 cannot connect pronouns to earlier words in a long ticket.",
  "unlock": "We will build AeroBrain v0.4's Self-Attention router—giving every word a Query, Key, and Value badge so tokens dynamically look up relevant past tokens without peeking into the future."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "1. The Airport Mingling Room",
    "caption": "Imagine every word in an AeroCart support ticket walks into a room wearing three badges: a Query (what I am looking for), a Key (what I offer), and a Value (the actual message I share when matched).",
    "code": "query = token @ W_Q  # 'Who is the destination city?'\nkey   = token @ W_K  # 'I am a city noun (Boston)!'\nvalue = token @ W_V  # 'Pass along my Boston airport payload'"
  },
  {
    "time": "0:22",
    "badge": "2. Why Divide by Square Root?",
    "caption": "When two 128-number badges multiply together, their raw score swings wildly up to plus or minus 30, turning Softmax into a stubborn winner-take-all switch. Dividing by the square root of 128 calms the scores back down.",
    "code": "scale = 1.0 / math.sqrt(d_head)  # 1 / sqrt(128) = 0.0884\nraw_score = sum(q * k for q, k in zip(query, key)) * scale"
  },
  {
    "time": "0:48",
    "badge": "3. Causal Blinders Stop Cheating",
    "caption": "When AeroBrain predicts the next word during training, token 3 must never peek at token 4. We stamp minus infinity onto all future positions before Softmax so future weights become exact zero.",
    "code": "if key_pos > query_pos:\n    score = -float('inf')  # exp(-inf) == 0.0 after Softmax!"
  },
  {
    "time": "1:12",
    "badge": "4. FlashAttention SRAM Tiling",
    "caption": "Instead of writing a giant 128,000 by 128,000 score table to slow GPU main memory, FlashAttention streams tiny blocks inside ultra-fast on-chip cache using a running maximum.",
    "code": "new_max = max(running_max, tile_max)\nrunning_sum = running_sum * math.exp(running_max - new_max) + tile_sum"
  }
]
```

```json pretraining
[
  {
    "term": "Query, Key & Value (Q, K, V)",
    "formula": "Attn(Q, K, V) = softmax((Q * K^T) / sqrt(d_k) + M) * V",
    "meaning": "A soft search engine inside the neural network: a token's Query searches other tokens' Keys to compute percentage weights, then blends their Values together."
  },
  {
    "term": "Square-Root Variance Scaling",
    "formula": "StdDev(q . k) = sqrt(d_k)  ==>  Divide by sqrt(d_k)",
    "meaning": "Adding up d_k random products makes scores spread out by sqrt(d_k). Dividing by sqrt(d_k) keeps scores gentle so Softmax probabilities do not freeze at 100% and 0%."
  },
  {
    "term": "Causal Mask (M)",
    "formula": "M_{i, j} = 0 if j <= i else -infinity",
    "meaning": "A time-travel barrier added before Softmax that sets future token scores to negative infinity, ensuring exp(-inf) = 0 so a word can only read past and present words."
  },
  {
    "term": "FlashAttention Tiling",
    "formula": "Memory Footprint: O(L^2) Table -> O(L) Running Stats",
    "meaning": "An hardware-friendly trick that computes exact attention in tiny on-chip memory blocks using running averages, avoiding a massive L-by-L table in GPU memory."
  }
]
```

## 🌱 Step 1: Plain-English Story — The Airport Lounge Search Party

In Chapter 03, **AeroBrain `v0.3`** turned every word in a traveler's complaint into a coordinate vector. But imagine a passenger writes: *"My suitcase missed the connection in **Denver** because **it** was delayed."* What does the word **"it"** refer to—the suitcase or Denver? A fixed dictionary vector for `"it"` has no idea!

To solve this, **Self-Attention** turns every word into an active detective inside an airport lounge. Every token creates three short number lists from its vector:
1. **A Query (`Q` — "What I'm looking for")**: The word `"it"` broadcasts a search query asking, *"Hey, who earlier in this sentence is a physical item or flight that can be delayed?"*
2. **A Key (`K` — "My label on the shelf")**: Earlier words hold up their Key tags. `"Suitcase"` holds up a Key saying *"I am a physical baggage noun!"*
3. **A Value (`V` — "What I hand over")**: Once `"it"` matches strongly with `"suitcase"` by multiplying its Query with every earlier word's Key, it takes a weighted blend of their Values—absorbing `"suitcase"` directly into `"it"`'s updated meaning!

Why do we also need **Causal Blinders** and **Scale Cooling**? First, when AeroBrain learns to predict the next word in a sentence, word #4 must not cheat by reading word #5—so we place a one-way mirror (**Causal Mask**) that blocks every future word with `-infinity` before converting scores into percentages. Second, when we multiply long Query and Key lists together, the raw sum gets huge and forces our percentage converter (`Softmax`) into a frozen 100%-or-0% switch. Dividing by the square root of the badge length keeps the scores calm and learnable.

```mermaid
flowchart LR
  Tokens["Ticket Tokens ('suitcase', 'missed', 'it')"] --> Badges["Create Q, K, V Badges"]
  Badges --> Match["Match Q with Past Keys (Divide by sqrt(d))"]
  Match --> Mask["Block Future Words (-inf Mask)"]
  Mask --> Blend["Softmax % Weights * Values V"]
```

---

## 🔨 Step 2: First Lines of Code — AeroBrain `v0.4` Mini Causal Attention

Let's write a clean, dependency-free **AeroBrain `v0.4`** causal attention step for 3 tokens (`"Denver"`, `"flight"`, `"delayed"`), where each token can only attend to itself and earlier tokens (`j <= i`).

```python
import math

# 3 tokens ("Denver", "flight", "delayed"), each with a 2-number Q, K, V badge
Q = [[1.0, 0.0], [0.5, 1.0], [0.8, 0.9]]
K = [[1.0, 0.2], [0.4, 1.0], [0.9, 0.8]]
V = [[10.0, 0.0], [0.0, 20.0], [5.0, 5.0]]
scale = 1.0 / math.sqrt(len(Q[0]))

for i, q in enumerate(Q):
    # Causal rule: token i only scores past/present keys j <= i
    scores = [sum(q[d] * K[j][d] for d in range(2)) * scale for j in range(i + 1)]
    weights = [math.exp(s) for s in scores]
    weights = [w / sum(weights) for w in weights]
    blended_v = [sum(weights[j] * V[j][d] for j in range(i + 1)) for d in range(2)]
    print(f"Token {i} weights={[round(w, 2) for w in weights]} -> out={[round(x, 1) for x in blended_v]}")
```

### Java 17 Equivalent

```java
public class AeroBrainMiniAttention {
    public static void main(String[] args) {
        double[][] Q = {{1.0, 0.0}, {0.5, 1.0}, {0.8, 0.9}};
        double[][] K = {{1.0, 0.2}, {0.4, 1.0}, {0.9, 0.8}};
        double[][] V = {{10.0, 0.0}, {0.0, 20.0}, {5.0, 5.0}};
        double scale = 1.0 / Math.sqrt(Q[0].length);

        for (int i = 0; i < Q.length; i++) {
            double[] weights = new double[i + 1];
            double sumExp = 0.0;
            for (int j = 0; j <= i; j++) {
                double dot = (Q[i][0] * K[j][0] + Q[i][1] * K[j][1]) * scale;
                weights[j] = Math.exp(dot);
                sumExp += weights[j];
            }
            double out0 = 0.0, out1 = 0.0;
            for (int j = 0; j <= i; j++) {
                out0 += (weights[j] / sumExp) * V[j][0];
                out1 += (weights[j] / sumExp) * V[j][1];
            }
            System.out.printf("Token %d -> out=[%.1f, %.1f]%n", i, out0, out1);
        }
    }
}
```

---

## ⚡ Step 3: Where It Breaks in Real Life — Single-Head Compromise & The $O(L^2)$ Memory Wall

When we deploy `AeroBrain v0.4` on full-length airline policy manuals (`65,536` tokens), two real-world bottlenecks strike immediately:

1. **The Single-Head Averaging Trap**: If a word has only *one* Query badge, it produces only *one* Softmax percentage list. What if `"it"` needs to look at `"suitcase"` for its *noun meaning* **and** look at `"was"` for its *past-tense grammar* at the same time? A single attention head averages both locations into a muddy compromise. Splitting the vector into **Multi-Head Attention** (`32` independent mini-heads running in parallel) gives each word 32 separate spotlights!
2. **The $O(L^2)$ GPU Memory Explosion**: In our starter loop, we stored a list of `scores` for every pair of tokens. At `65,536` tokens across `32` heads, storing all `L × L` pairs at once demands **256 GB of GPU memory for a single layer**, crashing the server before generation even starts!

```json contrast
{
  "title": "Naive Materialized O(L^2) Attention vs IO-Aware FlashAttention Online Softmax",
  "naiveTitle": "Materialized S = Q @ K.T in GPU HBM",
  "naiveMetric": "O(L^2) HBM OOM @ 32k · Bandwidth Bound",
  "naivePoints": [
    "Allocates full [B, H, L, L] matrix in HBM: at L=65,536 & H=32 (FP16), ONE layer's score matrix eats 256 GB VRAM!",
    "Reads/writes huge L x L intermediates back and forth across slow HBM (~3 TB/s) while fast Tensor Cores stall idle",
    "Applies causal mask via boolean tensor allocation + masked_fill copy pass"
  ],
  "staffTitle": "FlashAttention-2/3 Tiled Online Softmax",
  "staffMetric": "O(L) Memory · Exact Math · 4-8x Faster",
  "staffPoints": [
    "Streams Q, K, V blocks into fast on-chip SRAM (~19 TB/s) and fuses QK^T, causal skip, online Softmax, and P*V in one kernel",
    "Uses Online Softmax rescaling exp(m_old - m_new) so the L x L matrix is NEVER written to HBM—exact zero-approximation output!",
    "Skips entire upper-triangular K/V blocks where min_col > max_row, immediately halving causal prefill FLOPs by 2x!"
  ]
}
```

```json poe
{
  "question": "During custom Transformer implementation, an engineer applies the causal mask AFTER softmax by zeroing out upper-triangular probabilities (P_masked = tril(softmax(QK^T / sqrt(d_k)))) instead of adding -infinity BEFORE softmax, AND omits the 1/sqrt(d_k) factor at d_k = 128. What TWO mathematical bugs occur immediately?",
  "options": [
    "Training speeds up by 2x with identical perplexity",
    "1) Post-softmax zeroing leaks future tokens through the Softmax denominator sum_j exp(s_ij) AND breaks row probability normalization (rows no longer sum to 1.0!); 2) Omitting 1/sqrt(128) inflates logit std-dev by ~11.3x, saturating Softmax to ~[1, 0, 0...] where Jacobian p_i*(1-p_i) ≈ 0 freezes Q and K weight updates!",
    "Matrix multiplication V throws a shape mismatch error",
    "LayerNorm automatically restores 1/sqrt(d_k) after V projection"
  ],
  "answerIndex": 1,
  "explanation": "If future logits j > i enter the Softmax denominator before zeroing, the magnitude of token i's remaining weights directly encodes information about future tokens j > i (causal data leak!), and rows sum to < 1.0. Adding -inf BEFORE Softmax guarantees exp(-inf) = 0."
}
```

---

## 🚀 Step 4: Staff Engineer Deep-Dive — Variance Proof, Multi-Head Subspaces & `FlashAttention`

### 1. Statistical Proof of $\frac{1}{\sqrt{d_k}}$ & Differentiable Routing

Self-Attention (Vaswani et al., 2017) turns every token position $i \in \{1..L\}$ into a direct content-addressable query over all permitted context positions $j \le i$ in $O(1)$ sequential graph depth:

$$Q = X W_Q, \quad K = X W_K, \quad V = X W_V \in \mathbb{R}^{L \times d_k}$$
$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^\top}{\sqrt{d_k}} + M\right) V$$

**Why $\sqrt{d_k}$ specifically (and NOT $d_k$)?** Suppose components $q_r, k_r$ are independent random variables with mean `0` and variance `1`. Each product $q_r k_r$ has $\mathbb{E}[q_r k_r] = 0$ and $\text{Var}(q_r k_r) = \mathbb{E}[q_r^2]\mathbb{E}[k_r^2] = 1$. Summing $d_k = 128$ independent terms yields:

$$\text{Var}(q \cdot k) = \sum_{r=1}^{d_k} \text{Var}(q_r k_r) = d_k \implies \text{StdDev}(q \cdot k) = \sqrt{d_k} \approx 11.31$$

Dividing by $\sqrt{d_k}$ scales variance by $(\frac{1}{\sqrt{d_k}})^2 = \frac{1}{d_k}$, restoring $\text{Var}\!\left(\frac{q \cdot k}{\sqrt{d_k}}\right) = 1$! Without this factor, logit gaps of `±25` drive Softmax outputs to `0.99999999` and `1e-11`. Because the Softmax Jacobian is $J_{ab} = p_a (\delta_{ab} - p_b)$, gradients with respect to $Q$ and $K$ vanish to $\approx 0$ at initialization!

| Context Length ($L$) | Materialized `L × L` Score Matrix (`B=1, H=32, FP16`) | `FlashAttention` HBM Footprint | Prefill Compute (`FLOPs`) Scaling |
| :--- | :--- | :--- | :--- |
| **`2,048` tokens** | `256 MB` | `< 2 MB` (`O(L)` logsumexp stats) | Baseline (`1x`) |
| **`16,384` tokens** | `16.0 GB` (OOMs consumer GPUs) | `~16 MB` | `64x` compute ($8^2$) |
| **`131,072` (`128k`)** | **`1,024 GB` (`1 TB` — Impossible!)** | `~128 MB` | `4,096x` compute ($64^2$ — Compute Bound!) |

### 2. Dual-Language Production Blueprints: Causal & Online Tiled `FlashAttention`

```python
from __future__ import annotations
import math
from typing import List

Matrix = List[List[float]]


def causal_scaled_dot_product_attention(Q: Matrix, K: Matrix, V: Matrix) -> Matrix:
    """Reference exact Causal Attention: softmax(Q @ K^T / sqrt(d_k) + M_causal) @ V."""
    seq_len, d_k = len(Q), len(Q[0])
    inv_sqrt_d = 1.0 / math.sqrt(d_k)
    out: Matrix = []

    for i in range(seq_len):
        scores = [
            sum(Q[i][r] * K[j][r] for r in range(d_k)) * inv_sqrt_d
            for j in range(i + 1)
        ]
        m_i = max(scores)
        exps = [math.exp(s - m_i) for s in scores]
        denom = sum(exps)
        weights = [e / denom for e in exps]

        row_out = [0.0] * len(V[0])
        for j, w in enumerate(weights):
            for c in range(len(V[0])):
                row_out[c] += w * V[j][c]
        out.append(row_out)
    return out


def flash_tiled_online_causal_attention(
    Q: Matrix, K: Matrix, V: Matrix, block_size: int = 4
) -> Matrix:
    """Exact Online-Softmax recurrence powering FlashAttention in O(d) per-row state."""
    seq_len, d_k, d_v = len(Q), len(Q[0]), len(V[0])
    inv_sqrt_d = 1.0 / math.sqrt(d_k)
    output: Matrix = []

    for i in range(seq_len):
        running_max = -float("inf")
        running_sum = 0.0
        acc_v = [0.0] * d_v

        for tile_start in range(0, i + 1, block_size):
            tile_end = min(i + 1, tile_start + block_size)
            tile_scores = [
                sum(Q[i][r] * K[j][r] for r in range(d_k)) * inv_sqrt_d
                for j in range(tile_start, tile_end)
            ]
            new_max = max(running_max, max(tile_scores))
            alpha = math.exp(running_max - new_max) if running_max > -float("inf") else 0.0
            running_sum *= alpha
            acc_v = [val * alpha for val in acc_v]

            for offset, s in enumerate(tile_scores):
                p_tilde = math.exp(s - new_max)
                running_sum += p_tilde
                v_row = V[tile_start + offset]
                for c in range(d_v):
                    acc_v[c] += p_tilde * v_row[c]
            running_max = new_max

        output.append([val / running_sum for val in acc_v])
    return output
```

### Java 17 Equivalent

```java
package com.hub.ai.transformer;

public final class CausalAttentionKernel {

    /**
     * Computes exact Single-Pass Online-Softmax Causal Attention for one head [L x dHead]
     * in O(1) auxiliary score memory per token (zero [L x L] allocation!).
     */
    public static double[][] causalOnlineAttention(double[][] q, double[][] k, double[][] v) {
        int seqLen = q.length;
        int dHead = q[0].length;
        double scale = 1.0 / Math.sqrt(dHead);
        double[][] out = new double[seqLen][dHead];

        for (int i = 0; i < seqLen; i++) {
            double runningMax = Double.NEGATIVE_INFINITY;
            double runningDenom = 0.0;
            double[] acc = new double[dHead];

            for (int j = 0; j <= i; j++) {
                double dot = 0.0;
                for (int r = 0; r < dHead; r++) {
                    dot = Math.fma(q[i][r], k[j][r], dot);
                }
                double score = dot * scale;

                if (score > runningMax) {
                    double correction = runningMax == Double.NEGATIVE_INFINITY
                        ? 0.0 : Math.exp(runningMax - score);
                    runningDenom = runningDenom * correction + 1.0;
                    for (int c = 0; c < dHead; c++) {
                        acc[c] = acc[c] * correction + v[j][c];
                    }
                    runningMax = score;
                } else {
                    double weight = Math.exp(score - runningMax);
                    runningDenom += weight;
                    for (int c = 0; c < dHead; c++) {
                        acc[c] = Math.fma(weight, v[j][c], acc[c]);
                    }
                }
            }
            for (int c = 0; c < dHead; c++) {
                out[i][c] = acc[c] / runningDenom;
            }
        }
        return out;
    }
}
```

> [!WARNING] **Staff Interview Gotcha — "`FlashAttention` Makes Transformers $O(L)$ Compute!" (FALSE!):** Candidates frequently claim in interviews that `FlashAttention` reduces Transformer time complexity from $O(L^2)$ to $O(L)$. **This is mathematically false—and an instant Staff Bar-Raiser red flag!** `FlashAttention` computes the **exact** attention equation (zero low-rank or sparse approximation), so arithmetic operations remain strictly **`O(L^2 · d)` FLOPs** (`4x` longer prompt still takes `16x` attention FLOPs during prefill!). What `FlashAttention` reduces from $O(L^2)$ to **$O(L)$ is HBM Memory Capacity and HBM Read/Write IO traffic**, yielding a `4–8x` wall-clock speedup by eliminating HBM memory-bandwidth stalls!

**Up Next in Chapter 05:** Even with `FlashAttention`, our `AeroBrain v0.4` attention engine still treats token positions like an unordered bag of words if two identical words appear twice, and storing 32 separate Key/Value heads per layer clogs GPU memory during live chat. In **Chapter 05**, we upgrade to **AeroBrain `v0.5`** with **Rotary Position Embeddings (`RoPE`)**, **`RMSNorm`**, **`SwiGLU`**, **Grouped-Query Attention (`GQA`)**, and **Mixture-of-Experts (`MoE`)**.

```json quiz
[
  {
    "id": "aie-04-q1",
    "question": "If q and k have zero-mean, unit-variance independent entries and head dimension d_k increases from 64 to 256, how much does the variance (and standard deviation) of the unscaled dot product q · k grow?",
    "options": [
      "Variance stays 1.0; standard deviation stays 1.0",
      "Variance grows 4x (from 64 to 256) and standard deviation grows 2x (from 8 to 16), which is why dividing by sqrt(d_k) (not d_k!) restores exact unit variance Var = 1",
      "Variance grows exponentially as 2^256",
      "Standard deviation shrinks by 4x due to Law of Large Numbers"
    ],
    "answerIndex": 1,
    "explanation": "For sum of d_k independent unit-variance products, Var(sum) = d_k and StdDev = sqrt(d_k). Dividing by c scales variance by 1/c^2, so c = sqrt(d_k) yields Var = d_k / d_k = 1."
  },
  {
    "id": "aie-04-q2",
    "question": "In PyTorch FP16 causal masking, an engineer writes scores.masked_fill(mask, -1e9) instead of -float('inf') or torch.finfo(torch.float16).min. What crashes immediately at runtime?",
    "options": [
      "Causal tokens attend backward in reverse order",
      "RuntimeError overflow: IEEE-754 float16 has a maximum finite range of ±65,504! Passing -1e9 overflows FP16 immediately (whereas -float('inf') or -65504.0 represents clean negative saturation in FP16/BF16)",
      "CUDA disables Tensor Cores on negative numbers",
      "Softmax outputs complex numbers"
    ],
    "answerIndex": 1,
    "explanation": "FP16 max representable magnitude is 65,504 (unlike BF16/FP32 which reach ~3.4e38); -1e9 overflows FP16 unless -inf or finfo(dtype).min is used."
  },
  {
    "id": "aie-04-q3",
    "question": "Why is Self-Attention COMPLETELY permutation-equivariant (treating 'Dog bites man' and 'Man bites dog' identically as a bag-of-words) if positional embeddings (e.g., RoPE) and causal masks are omitted?",
    "options": [
      "Because W_Q and W_K are symmetric matrices",
      "Every operation in Attention (row-wise linear projections X*W, all-pairs dot products Q*K^T, row-wise Softmax, and weighted value sum P*V) commutes with any row permutation matrix Pi: Attention(Pi*X) = Pi*Attention(X)—without causal masking or positional injection, token order does not exist!",
      "Because Softmax sorts scores in ascending order",
      "Because LayerNorm erases token indices"
    ],
    "answerIndex": 1,
    "explanation": "Unmasked dot-product attention is strictly set-equivariant; sequence order comes solely from causal asymmetry + positional encoding (such as RoPE)."
  }
]
```
