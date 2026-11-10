# AI Engineering Lab 04: LLM-as-a-Judge Statistical Calibration (Rogan-Gladen $\hat{p}$, Cohen's $\kappa$) & Red-Team Guardrails

This 100% deterministic AI QA lab implements:
1. **Rogan-Gladen Prevalence Bias Correction ($\hat{p} = \frac{p_{\text{obs}} + q_0 - 1}{q_1 + q_0 - 1}$)** calibrating raw noisy LLM-judge pass rates using human-labeled sensitivity ($q_1$) and specificity ($q_0$).
2. **Pairwise Position-Swap Judge Debiasing** eliminating first-slot position bias by requiring consistent verdicts across `(A, B)` and `(B, A)`.
3. **Indirect Prompt-Injection & PII Exfiltration Guardrail Scanner** blocking untrusted tool/document instructions from invoking privileged MCP actions.

## Run Locally (Zero AI)
```bash
./run.sh test 04-llm-judge-calibration-and-redteam
```
