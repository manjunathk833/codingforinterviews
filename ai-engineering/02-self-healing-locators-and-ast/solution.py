#!/usr/bin/env python3
"""
AI Lab 02: Weighted Multi-Signal Self-Healing UI Locator Engine with Destructive Action Guard.
"""

from typing import Dict, Any, List

DESTRUCTIVE_KEYWORDS = {"delete", "cancel", "remove", "destroy", "revoke"}


class Solution:
    def _token_jaccard(self, a: str, b: str) -> float:
        sa = set(a.lower().replace("-", " ").replace("_", " ").split())
        sb = set(b.lower().replace("-", " ").replace("_", " ").split())
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / float(len(sa | sb))

    def heal_broken_locator(
        self,
        baseline: Dict[str, str],
        dom_candidates: List[Dict[str, str]],
        confidence_threshold: float = 0.75,
    ) -> Dict[str, Any]:
        """
        Score candidate DOM elements against a broken baseline element fingerprint.
        """
        base_text = (baseline.get("text", "") + " " + baseline.get("aria_label", "")).lower()
        base_is_destructive = any(k in base_text for k in DESTRUCTIVE_KEYWORDS)

        best_candidate = None
        best_score = 0.0

        for cand in dom_candidates:
            cand_text = (cand.get("text", "") + " " + cand.get("aria_label", "")).lower()
            cand_is_destructive = any(k in cand_text for k in DESTRUCTIVE_KEYWORDS)

            # Safety Guard: Never heal a non-destructive action onto a destructive button!
            if cand_is_destructive != base_is_destructive:
                continue

            score = 0.0
            if cand.get("role") == baseline.get("role") and cand.get("tag") == baseline.get("tag"):
                score += 0.25

            score += 0.35 * self._token_jaccard(baseline.get("aria_label", ""), cand.get("aria_label", ""))
            score += 0.25 * self._token_jaccard(baseline.get("text", ""), cand.get("text", ""))

            if cand.get("parent_context") == baseline.get("parent_context"):
                score += 0.15

            score = round(score, 3)
            if score > best_score:
                best_score = score
                best_candidate = cand

        if best_candidate and best_score >= confidence_threshold:
            new_locator = f"page.get_by_role('{best_candidate['role']}', name='{best_candidate['text']}')"
            return {
                "healed": True,
                "confidence": best_score,
                "matched_id": best_candidate["id"],
                "suggested_ast_locator": new_locator,
            }

        return {
            "healed": False,
            "confidence": best_score,
            "matched_id": None,
            "suggested_ast_locator": None,
        }


if __name__ == "__main__":
    sol = Solution()

    baseline_btn = {
        "id": "btn-book-legacy",
        "tag": "button",
        "role": "button",
        "text": "Confirm Flight Booking",
        "aria_label": "Confirm Flight Booking",
        "parent_context": "checkout-form",
    }

    candidates = [
        {
            "id": "btn-cancel-danger",
            "tag": "button",
            "role": "button",
            "text": "Cancel Flight Booking",
            "aria_label": "Cancel Flight Booking",
            "parent_context": "checkout-form",
        },
        {
            "id": "confirm-booking-cta-v2",
            "tag": "button",
            "role": "button",
            "text": "Confirm Flight Booking",
            "aria_label": "Confirm Flight Booking Now",
            "parent_context": "checkout-form",
        },
    ]

    # Case 1: Heals onto renamed CTA button while ignoring the dangerous "Cancel Flight Booking" button
    res1 = sol.heal_broken_locator(baseline_btn, candidates, confidence_threshold=0.75)
    assert res1["healed"] is True, f"Expected successful heal: {res1}"
    assert res1["matched_id"] == "confirm-booking-cta-v2"
    assert res1["confidence"] >= 0.85

    # Case 2: If only the destructive "Cancel" button is on the page, refuse to heal!
    res2 = sol.heal_broken_locator(baseline_btn, [candidates[0]], confidence_threshold=0.75)
    assert res2["healed"] is False, "Must never auto-heal onto a destructive Cancel/Delete button!"

    print("All 2 Python Self-Healing UI Locator & AST Safety Gate test cases passed!")

