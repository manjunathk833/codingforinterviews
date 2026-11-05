# 🤖 AI Engineering, RAG Evaluation & Agentic QE (`ai-engineering/`)

Welcome to the **AI Engineering Pillar** of the Antigravity Learning Hub.
Modern Senior/Staff SDET roles require rigorous engineering for non-deterministic LLM/RAG pipelines, claim-entailment evaluators, and AST-backed self-healing test infrastructure.

---

## 📊 AI Engineering Curriculum & Lab Tracker

| # | Domain | Lab / Module | Key Concepts Covered | Java | Python | Visualizer ID | Status |
| :-: | :--- | :--- | :--- | :-: | :-: | :--- | :---: |
| **1** | **RAG & LLM Evals** | [`01-rag-triad-evaluator`](01-rag-triad-evaluator/) | Context Recall, Faithfulness (Claim Entailment), Answer Relevance, Catching Negation Hallucinations | [x] | [x] | `ai-rag-triad-gate` | `Completed` |
| **2** | **Agentic Automation** | [`02-self-healing-locators-and-ast`](02-self-healing-locators-and-ast/) | Multi-Attribute DOM Similarity Scoring, Confidence Gate ($\ge 0.75$), False-Positive Prevention | [x] | [x] | `arch-playwright-vs-selenium` | `Completed` |

---

## 🚀 How to Run AI Engineering Labs

```bash
# Test RAG Triad & Claim-Entailment Evaluator (Java 17 & Python 3)
./run.sh test 01-rag-triad-evaluator

# Test Self-Healing DOM Locator & AST Confidence Engine (Java 17 & Python 3)
./run.sh test 02-self-healing-locators-and-ast
```

