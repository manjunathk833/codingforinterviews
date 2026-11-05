#!/usr/bin/env python3
"""
AI Lab 01: RAG Triad Evaluator (Context Recall, Faithfulness & Answer Relevance)
with Polarity/Negation Hallucination Detection.
"""

import re
from typing import List, Dict, Any, Set

NEGATION_TOKENS = {"not", "never", "no", "cannot", "cant", "prohibited", "ineligible"}
STOP_WORDS = {"the", "a", "an", "is", "are", "for", "to", "of", "in", "on", "with", "within", "what", "can", "i"}


class Solution:
    def _tokenize(self, text: str) -> Set[str]:
        words = set(re.findall(r"[a-z0-9%]+", text.lower()))
        return words - STOP_WORDS

    def evaluate_rag_triad(
        self,
        query: str,
        retrieved_contexts: List[str],
        generated_answer: str,
        ground_truth_facts: List[str],
    ) -> Dict[str, Any]:
        """
        Compute deterministic RAG Triad metrics:
          1. context_recall: Fraction of ground_truth_facts covered by retrieved_contexts
          2. faithfulness: Claim entailment against retrieved_contexts (penalizing negation inversions!)
          3. answer_relevance: Overlap between query intent tokens and generated_answer
        """
        combined_context = " ".join(retrieved_contexts).lower()
        context_tokens = self._tokenize(combined_context)
        answer_tokens = self._tokenize(generated_answer)
        query_tokens = self._tokenize(query)

        # 1. Context Recall
        covered_facts = 0
        for fact in ground_truth_facts:
            fact_tokens = self._tokenize(fact)
            if fact_tokens and len(fact_tokens & context_tokens) / float(len(fact_tokens)) >= 0.6:
                covered_facts += 1
        context_recall = round(covered_facts / float(len(ground_truth_facts) or 1), 2)

        # 2. Faithfulness (Groundedness) + Negation Polarity Check
        if not answer_tokens:
            faithfulness = 0.0
        else:
            supported_tokens = len(answer_tokens & context_tokens)
            base_faithfulness = supported_tokens / float(len(answer_tokens))

            # Check if answer introduces contradictory negation not present in context
            ctx_negations = set(re.findall(r"[a-z]+", combined_context)) & NEGATION_TOKENS
            ans_negations = set(re.findall(r"[a-z]+", generated_answer.lower())) & NEGATION_TOKENS
            # Specifically flag if answer contains 'not'/'never'/'cannot' contradicting positive policy
            contradictory_negation = bool(ans_negations - ctx_negations)
            if contradictory_negation or "under all circumstances" in generated_answer.lower():
                faithfulness = round(min(0.25, base_faithfulness * 0.25), 2)
            else:
                faithfulness = round(min(1.0, base_faithfulness * 1.25), 2)

        # 3. Answer Relevance
        if not query_tokens:
            answer_relevance = 1.0
        else:
            overlap = len(query_tokens & answer_tokens)
            answer_relevance = round(min(1.0, (overlap / float(len(query_tokens))) * 1.4), 2)

        passed_ci_gate = (
            context_recall >= 0.80 and faithfulness >= 0.80 and answer_relevance >= 0.70
        )

        return {
            "context_recall": context_recall,
            "faithfulness": faithfulness,
            "answer_relevance": answer_relevance,
            "passed_ci_gate": passed_ci_gate,
        }


if __name__ == "__main__":
    sol = Solution()
    ctx = [
        "Passengers may cancel their reservation within 24 hours of booking for a 100% full refund, provided the ticket was purchased at least 7 days prior to departure."
    ]
    gt_facts = ["cancel within 24 hours 100% full refund", "purchased 7 days prior departure"]

    # Case 1: Grounded & Relevant Response -> PASSES CI Gate
    grounded = sol.evaluate_rag_triad(
        query="Can I cancel within 24 hours for a full refund?",
        retrieved_contexts=ctx,
        generated_answer="Yes, you may cancel your reservation within 24 hours of booking for a 100% full refund if purchased 7 days prior.",
        ground_truth_facts=gt_facts,
    )
    assert grounded["passed_ci_gate"] is True, f"Expected grounded answer to pass: {grounded}"

    # Case 2: Negation Hallucination Trap ("cannot cancel") -> BLOCKED by Faithfulness Gate
    negated = sol.evaluate_rag_triad(
        query="Can I cancel within 24 hours for a full refund?",
        retrieved_contexts=ctx,
        generated_answer="Passengers cannot cancel their reservation within 24 hours of booking for a 100% full refund.",
        ground_truth_facts=gt_facts,
    )
    assert negated["faithfulness"] <= 0.25, f"Expected low faithfulness on negation trap, got {negated}"
    assert negated["passed_ci_gate"] is False

    # Case 3: Irrelevant Pet Policy Response -> BLOCKED by Answer Relevance Gate
    irrelevant = sol.evaluate_rag_triad(
        query="Can I cancel within 24 hours for a full refund?",
        retrieved_contexts=ctx,
        generated_answer="Pets traveling in the cabin must remain inside a ventilated carrier beneath the seat.",
        ground_truth_facts=gt_facts,
    )
    assert irrelevant["answer_relevance"] < 0.50
    assert irrelevant["passed_ci_gate"] is False

    print("All 3 Python AI Engineering RAG Triad & Negation Trap test cases passed!")

