---
slug: aie-02-classification-metrics-calibration-and-drift
course_id: 05-ai-engineering
track: ai-engineering
volume: "05. Zero to Mastery: AI Engineering"
module_number: 1
module_title: "Module 1: Classical ML & Vector Representation Foundations"
chapter_number: 2
level_tag: "Foundations → Senior"
title: "Classification Metrics, Probability Calibration (ECE) & Production Drift (PSI)"
summary: "Base-rate fallacy math explaining why 99% accuracy and 0.96 ROC-AUC fail on rare-event fraud/safety classifiers, Precision/Recall/F_beta cost optimization, Expected Calibration Error (ECE) with Temperature Scaling, and PSI covariate vs concept drift."
reading_time_minutes: 22
visualizer_id: ai-ml-embeddings-loss
lab_path: ai-engineering/04-llm-judge-calibration-and-redteam
tags: ["ai-engineering", "pr-auc", "roc-auc", "calibration", "ece", "temperature-scaling", "psi-drift"]
---

# Classification Metrics, Probability Calibration (ECE) & Production Drift (PSI)

```json pretraining
[
  {
    "term": "Generalized F-Beta",
    "formula": "F_beta = (1 + beta^2) * (P * R) / (beta^2 * P + R)",
    "meaning": "Weights Recall beta times as important as Precision (F_2 favors catching rare fraud/cancer; F_0.5 favors low-false-alarm spam blocks)."
  },
  {
    "term": "ROC-AUC vs PR-AUC",
    "formula": "FPR = FP / (FP + TN)  vs  Precision = TP / (TP + FP)",
    "meaning": "Massive True Negatives (99.9% clean traffic) dilute FPR near 0, inflating ROC-AUC to 0.98 even when 80% of alerts are false positives!"
  },
  {
    "term": "Expected Calibration (ECE)",
    "formula": "ECE = sum_{m=1}^M (|B_m| / N) * |acc(B_m) - conf(B_m)|",
    "meaning": "Measures whether predicted confidence 0.85 actually succeeds 85% of the time; fixed post-hoc via Temperature Scaling z / T without changing argmax."
  },
  {
    "term": "Population Stability (PSI)",
    "formula": "PSI = sum_i (q_i - p_i) * ln(q_i / p_i)",
    "meaning": "Symmetric KL-divergence over binned feature/score quantiles: PSI < 0.10 stable, 0.10-0.25 moderate shift, >= 0.25 critical drift alert."
  }
]
```

```json poe
{
  "question": "A prompt-injection guardrail screens 1,000,000 live user prompts containing 1,000 real attacks (0.1% prevalence) and 999,000 benign prompts. The model catches 900 real attacks (TPR/Recall = 90%) and falsely flags 9,990 benign prompts (FPR = 1.0%). Its ROC-AUC is 0.975 and overall Accuracy is 98.99%. Why do enterprise customers churn within 48 hours of launch?",
  "options": [
    "90% Recall is mathematically below random guessing",
    "Base-Rate Fallacy in Precision: TP / (TP + FP) = 900 / (900 + 9990) = 8.26% Precision! Over 91.7% of blocked customer prompts are false alarms—massive TN (989,010) made FPR (1%) and ROC-AUC look stellar while PR-AUC exposed the disaster",
    "Temperature scaling inverted the decision boundary",
    "PSI exceeded 1.0 on the training split"
  ],
  "answerIndex": 1,
    "explanation": "Under 0.1% positive prevalence, a tiny 1% False Positive Rate generates 10x more False Positives (9,990) than True Positives (900). Rare-event classifiers MUST gate releases on PR-AUC and Precision@Recall>=0.90, never Accuracy or ROC-AUC."
}
```

## 1. Beyond Accuracy & `ROC-AUC`: Cost-Matrix Thresholding on Imbalanced Streams

In real-world AI systems—payment fraud (`0.08%` base rate), jailbreak guardrails (`0.1%`), retrieval relevance (`1%`), or manufacturing defect detection—predicting `0` (`benign`) on every input achieves **`99.9%` accuracy** while delivering zero business value.

1. **`ROC-AUC` (`TPR` vs. `FPR`) vs. `PR-AUC` (`Precision` vs. `Recall`)**: Because $\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$, adding `10,000,000` trivial negative examples balloons `TN` in the denominator, hiding thousands of false alarms. **Precision** ($\frac{\text{TP}}{\text{TP} + \text{FP}}$) never touches `TN`, making **PR-AUC** (Average Precision) the mandatory metric for skewed classes.
2. **Expected Business Cost Thresholding ($\tau^*$)**: Never hardcode `predict_proba(x) >= 0.50`! If a missed `$400` chargeback (`FN`) costs `$400` and a manual friction OTP challenge (`FP`) costs `$2`, Bayes-optimal thresholding triggers whenever calibrated probability $p(y=1 \mid x) \ge \frac{C_{\text{FP}}}{C_{\text{FP}} + C_{\text{FN}}} = \frac{2}{402} \approx 0.005$—**which works ONLY if $p(y=1 \mid x)$ is genuinely calibrated!**

```mermaid
flowchart LR
  Logits["Uncalibrated Model Logits z"] -->|Holdout NLL Fit| Temp["Temperature Scaling p = sigma(z / T)"]
  Temp -->|Verify ECE < 0.02| Thresh["Cost-Optimal Threshold tau*"]
  Thresh -->|Live Prod Stream| Monitor["Daily PSI Feature & Score Monitor"]
  Monitor -->|PSI >= 0.25 or Label Shift| Retrain["Trigger Shadow Eval & Retrain"]
```

---

## 2. Probability Calibration (`ECE` & Temperature Scaling) + Production Drift (`PSI`)

Modern deep neural networks and fine-tuned LLM classifiers are systematically **overconfident** (outputting `0.994` on inputs where empirical accuracy is `0.76`). **Temperature Scaling** (Guo et al., 2017) learns a **single scalar $T > 0$** on the validation set minimizing Negative Log-Likelihood (`NLL`): $\hat{p} = \text{softmax}(z / T)$. Because dividing all logits by $T > 0$ is strictly monotonic, **`argmax` top-1 accuracy and `ROC-AUC` remain `100%` unchanged**, while Expected Calibration Error (`ECE`) drops dramatically!

Once deployed, production models decay via two distinct distribution shifts:
- **Covariate / Feature Drift ($P(X)$ changes, $P(Y \mid X)$ initially fixed)**: New seasonal product SKUs, new iOS user-agent strings, or non-English queries arrive; detected immediately **without ground-truth labels** via **Population Stability Index (`PSI`)** or embedding centroid cosine shift.
- **Concept Drift ($P(Y \mid X)$ changes!)**: Attackers invent a brand-new jailbreak pattern or macroeconomic inflation shifts credit-default behavior for the *exact same* feature vector $x$. Feature `PSI` looks calm (`< 0.05`), so catching Concept Drift requires **delayed ground-truth label joins, canary human-audit sampling, or prediction-entropy monitoring**.

```json contrast
{
  "title": "0.50 Uncalibrated Accuracy Gate vs Calibrated Cost-Threshold + PSI Drift Telemetry",
  "naiveTitle": "Accuracy / ROC-AUC + Hardcoded p >= 0.5",
  "naiveMetric": "91% False Alarms · Silent Concept Decay",
  "naivePoints": [
    "Celebrates 99.2% Accuracy and 0.96 ROC-AUC on a 0.2% fraud dataset while Precision sits at an unusable 9%",
    "Multiplies raw uncalibrated neural-net scores (0.99) by transaction dollar value, mispricing expected risk by 4x",
    "Waits 90 days for chargeback labels before noticing a new mobile SDK broke an upstream input feature to NULL"
  ],
  "staffTitle": "PR-AUC + Temperature Calibration + PSI Alerts",
  "staffMetric": "ECE < 0.018 · Same-Hour Null/PSI Detection",
  "staffPoints": [
    "Gates CI on Precision@Recall=0.85, PR-AUC, and slice-level F_beta across minority languages and cohorts",
    "Fits post-hoc Temperature T on held-out calibration split so p * DollarLoss reflects true actuarial expected value",
    "Computes hourly PSI on top-20 input features + output probability deciles, paging on PSI >= 0.25 within 60 minutes"
  ]
}
```

| Metric / Signal | Requires Live Labels? | Target Regime | Healthy Production Gate |
| :--- | :--- | :--- | :--- |
| **`PR-AUC` & `Recall @ FPR <= 0.5%`** | Yes (Golden / Holdout) | Skewed safety, fraud, retrieval (`< 5%` positive) | Must beat baseline across **every** critical demographic/tenant slice |
| **`ECE` (10-Bin Calibration Error)** | Yes (Calibration Split) | Risk scoring (`p * cost`), abstention routing, LLM confidence | `ECE <= 0.025` after Temperature (`T`) or Platt (`a*z + b`) scaling |
| **Feature & Score `PSI`** | **No** (Zero label lag!) | Real-time covariate / pipeline breakage detection | `PSI < 0.10` green; `0.10–0.25` investigate; `>= 0.25` page on-call |
| **Canary Stratified Audit** | Sampled (`0.5%` human/oracle) | **Concept Drift** ($P(Y \mid X)$ shift where `PSI` stays low) | Weekly rolling Precision/Recall within `±2%` of launch SLA |

---

## 3. Dual-Language Production Blueprints: `F_beta`, `ECE` Calibration & `PSI` Monitor

### Python 3 Blueprint: `F_beta`, Temperature Scaling Calibration (`ECE`) & `PSI` Drift Engine
```python
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class ImbalancedEvalReport:
    precision: float
    recall: float
    f_beta: float
    fpr: float


def evaluate_at_threshold(
    y_true: Sequence[int], probs: Sequence[float], threshold: float, beta: float = 2.0
) -> ImbalancedEvalReport:
    tp = fp = tn = fn = 0
    for y, p in zip(y_true, probs):
        pred = 1 if p >= threshold else 0
        if y == 1 and pred == 1:
            tp += 1
        elif y == 0 and pred == 1:
            fp += 1
        elif y == 0 and pred == 0:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    b2 = beta * beta
    denom = b2 * precision + recall
    f_beta = ((1.0 + b2) * precision * recall / denom) if denom > 0 else 0.0
    return ImbalancedEvalReport(round(precision, 4), round(recall, 4), round(f_beta, 4), round(fpr, 5))


def sigmoid_with_temperature(logit: float, temperature: float) -> float:
    z = logit / max(temperature, 1e-6)
    return 1.0 / (1.0 + math.exp(-z)) if z >= 0 else math.exp(z) / (1.0 + math.exp(z))


def expected_calibration_error(
    y_true: Sequence[int], probs: Sequence[float], num_bins: int = 10
) -> float:
    """Computes M-bin Expected Calibration Error: sum (|B_m|/N) * |acc(B_m) - conf(B_m)|."""
    n = len(y_true)
    if n == 0:
        return 0.0
    bin_counts = [0] * num_bins
    bin_correct = [0.0] * num_bins
    bin_conf = [0.0] * num_bins

    for y, p in zip(y_true, probs):
        # For binary confidence calibration, evaluate max(p, 1-p) vs predicted label accuracy
        pred = 1 if p >= 0.5 else 0
        conf = p if pred == 1 else (1.0 - p)
        correct = 1.0 if pred == y else 0.0
        idx = min(num_bins - 1, int(conf * num_bins))
        bin_counts[idx] += 1
        bin_correct[idx] += correct
        bin_conf[idx] += conf

    ece = 0.0
    for m in range(num_bins):
        if bin_counts[m] > 0:
            acc_m = bin_correct[m] / bin_counts[m]
            conf_m = bin_conf[m] / bin_counts[m]
            ece += (bin_counts[m] / n) * abs(acc_m - conf_m)
    return round(ece, 5)


def fit_temperature_grid(logits: Sequence[float], y_true: Sequence[int]) -> Tuple[float, float]:
    """Finds optimal post-hoc Temperature T in [0.25, 5.0] minimizing Binary NLL on calibration split."""
    best_t, best_nll = 1.0, float("inf")
    for step in range(25, 505, 5):
        t = step / 100.0
        nll = 0.0
        for z, y in zip(logits, y_true):
            p = min(1.0 - 1e-12, max(1e-12, sigmoid_with_temperature(z, t)))
            nll -= y * math.log(p) + (1 - y) * math.log(1.0 - p)
        nll /= len(logits)
        if nll < best_nll:
            best_nll, best_t = nll, t
    return best_t, round(best_nll, 5)


def compute_psi(baseline_hist: Sequence[int], live_hist: Sequence[int], eps: float = 1e-4) -> float:
    """Computes Population Stability Index (PSI) across fixed baseline quantile bins."""
    base_total = max(1, sum(baseline_hist))
    live_total = max(1, sum(live_hist))
    psi = 0.0
    for b_cnt, q_cnt in zip(baseline_hist, live_hist):
        p = max(eps, b_cnt / base_total)
        q = max(eps, q_cnt / live_total)
        psi += (q - p) * math.log(q / p)
    return round(psi, 5)
```

### Java 17 Blueprint: Cost-Optimal Threshold Finder, `ECE` & `PSI` Drift Gate
```java
package com.hub.ai.metrics;

public final class CalibrationAndDriftMonitor {

    public record DriftVerdict(double psi, String status) {}

    public static double optimalBayesThreshold(double falsePositiveCost, double falseNegativeCost) {
        if (falsePositiveCost <= 0 || falseNegativeCost <= 0) {
            throw new IllegalArgumentException("Costs must be strictly positive");
        }
        return falsePositiveCost / (falsePositiveCost + falseNegativeCost);
    }

    public static double computeExpectedCalibrationError(int[] yTrue, double[] probs, int bins) {
        int n = yTrue.length;
        int[] counts = new int[bins];
        double[] sumCorrect = new double[bins];
        double[] sumConf = new double[bins];

        for (int i = 0; i < n; i++) {
            int pred = probs[i] >= 0.5 ? 1 : 0;
            double conf = pred == 1 ? probs[i] : (1.0 - probs[i]);
            int bucket = Math.min(bins - 1, (int) (conf * bins));
            counts[bucket]++;
            sumConf[bucket] += conf;
            if (pred == yTrue[i]) {
                sumCorrect[bucket] += 1.0;
            }
        }
        double ece = 0.0;
        for (int b = 0; b < bins; b++) {
            if (counts[b] > 0) {
                double acc = sumCorrect[b] / counts[b];
                double avgConf = sumConf[b] / counts[b];
                ece += ((double) counts[b] / n) * Math.abs(acc - avgConf);
            }
        }
        return ece;
    }

    public static DriftVerdict evaluatePopulationStabilityIndex(long[] baselineBins, long[] liveBins) {
        long baseSum = 0;
        long liveSum = 0;
        for (long c : baselineBins) baseSum += c;
        for (long c : liveBins) liveSum += c;

        double psi = 0.0;
        double eps = 1e-4;
        for (int i = 0; i < baselineBins.length; i++) {
            double p = Math.max(eps, (double) baselineBins[i] / Math.max(1L, baseSum));
            double q = Math.max(eps, (double) liveBins[i] / Math.max(1L, liveSum));
            psi += (q - p) * Math.log(q / p);
        }
        String level = psi >= 0.25 ? "CRITICAL_DRIFT" : (psi >= 0.10 ? "MODERATE_SHIFT" : "STABLE");
        return new DriftVerdict(psi, level);
    }
}
```

> [!WARNING] **Staff Interview Gotcha — Re-computing `PSI` Bin Boundaries on Live Data Destroys Drift Detection!** When implementing `PSI` on continuous features or predicted probabilities, a fatal bug is computing decile cut-points independently on the reference set AND independently on today's live set (`np.percentile(live, [10, 20, ..., 90])`). If you re-compute deciles on live data, **both histograms contain exactly `10%` of samples per bin by definition, yielding `PSI = 0.000` even if every feature shifted by `+100x`!** **Invariant:** Freeze quantile bin edges (`-inf, q10, q20, ..., q90, +inf` plus a dedicated `NULL/NaN` bucket!) **strictly on the training/reference baseline**, and count what fraction of live traffic lands inside those fixed baseline boundaries.

---

## 4. Scenario Retrieval-Practice Mastery Gate

```json quiz
[
  {
    "id": "aie-02-q1",
    "question": "Why does post-hoc Temperature Scaling (p = softmax(z / T) with T > 0 fit on a held-out validation split) reduce Expected Calibration Error (ECE) WITHOUT altering top-1 accuracy or ROC-AUC?",
    "options": [
      "Dividing logits by T adds random Gaussian noise that cancels out over large batches",
      "Because f(z) = z / T for T > 0 is a strictly order-preserving (monotonic) transformation across all classes/samples, neither argmax_i(z_i) nor the pairwise ranking of sample scores changes—only steep overconfident probability extremes soften toward empirical frequencies",
      "Temperature Scaling retrains the final linear projection matrix W_vocab",
      "Temperature Scaling sets all probabilities below 0.5 to exact zero"
    ],
    "answerIndex": 1,
    "explanation": "Scalar division by T > 0 preserves logit ordering (leaving top-1 accuracy and rank-based AUCs untouched) while stretching or compressing entropy to align predicted confidence with true empirical accuracy."
  },
  {
    "id": "aie-02-q2",
    "question": "Your fraud classifier's hourly Feature PSI and Output Score PSI both read 0.02 (green/stable), yet chargeback losses triple over a holiday weekend because a fraud ring started using stolen credentials from clean residential IPs matching normal cart sizes. What drift occurred and why did PSI miss it?",
    "options": [
      "Covariate shift caused by broken JSON serialization",
      "Pure Concept Drift (P(Y | X) shifted while marginal input distribution P(X) stayed identical!): the fraudsters mimicked normal feature distributions, so label-free PSI on X remained ~0.02; requires canary friction/human-review holdout sampling (e.g., auto-auditing 0.5% of approved traffic) to measure live P(Y | X)",
      "PSI cannot measure more than 5 features",
      "Floating-point underflow in ln(q / p)"
    ],
    "answerIndex": 1,
    "explanation": "PSI only measures marginal shifts in P(X) or P(y_hat). Adversarial adaptation that mimics normal X changes P(Y|X) (concept drift), which can only be observed via ground-truth/canary outcome sampling."
  },
  {
    "id": "aie-02-q3",
    "question": "Downstream mobile version 4.12 ships a bug sending user_account_age_days = NULL instead of an integer for 35% of traffic, and yourPSI SQL query filters WHERE user_account_age_days IS NOT NULL before binning. What happens?",
    "options": [
      "PostgreSQL automatically raises a PSI alert on NULL values",
      "Silent Blind Spot: filtering NULLs before binning hides the 35% missing-value spike from continuous PSI buckets while the model's median-imputer feeds constant defaults! Production PSI monitors must always allocate an explicit 11th bin for NULL/missing/out-of-range values",
      "PSI becomes negative when NULLs are excluded",
      "ROC-AUC rises to 1.0"
    ],
    "answerIndex": 1,
    "explanation": "Upstream schema/SDK null spikes are the #1 real-world ML failure mode; a dedicated NULL/NaN bin in PSI catches broken feature pipelines within minutes."
  }
]
```
