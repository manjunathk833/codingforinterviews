#!/usr/bin/env python3
"""Staff Reference Architecture — AI Build 3/4: Self-Healing Locator Agent & AST Selector Patcher."""
import ast
from dataclasses import dataclass
from html.parser import HTMLParser
import re
from typing import Any, Dict, List, Optional, Set, Tuple


def _tokens(text: str) -> Set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t}


@dataclass(frozen=True)
class AccessibleNode:
    element_id: str
    tag: str
    role: str
    name: str
    test_id: str
    disabled: bool


@dataclass(frozen=True)
class BrokenLocatorIntent:
    old_selector: str
    expected_role: str
    expected_name: str


class _A11yParser(HTMLParser):
    _IMPLICIT_ROLES = {"button": "button", "a": "link", "input": "textbox", "select": "combobox"}

    def __init__(self) -> None:
        super().__init__()
        self.nodes: List[Dict[str, Any]] = []
        self._open_idx: Optional[int] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        amap = {k: (v or "") for k, v in attrs}
        role = amap.get("role") or self._IMPLICIT_ROLES.get(tag, "")
        if not role:
            return
        hidden = "hidden" in amap or amap.get("aria-hidden") == "true"
        if hidden:
            return
        entry = {
            "element_id": amap.get("id", ""),
            "tag": tag,
            "role": role.lower(),
            "name": (amap.get("aria-label") or amap.get("placeholder") or "").strip(),
            "test_id": amap.get("data-testid", ""),
            "disabled": "disabled" in amap,
        }
        self.nodes.append(entry)
        self._open_idx = len(self.nodes) - 1

    def handle_data(self, data: str) -> None:
        if self._open_idx is not None:
            txt = data.strip()
            if txt and not self.nodes[self._open_idx]["name"]:
                self.nodes[self._open_idx]["name"] = txt

    def handle_endtag(self, tag: str) -> None:
        self._open_idx = None


class AccessibilitySnapshotter:
    """Extracts interactive AccessibleNode descriptors from raw HTML."""

    def extract_nodes(self, html_source: str) -> List[AccessibleNode]:
        parser = _A11yParser()
        parser.feed(html_source or "")
        return [
            AccessibleNode(
                element_id=n["element_id"],
                tag=n["tag"],
                role=n["role"],
                name=n["name"],
                test_id=n["test_id"],
                disabled=bool(n["disabled"]),
            )
            for n in parser.nodes
        ]


class SemanticLocatorHealer:
    """Matches a BrokenLocatorIntent to candidate AccessibleNodes with strict anti-hallucination bounds."""

    def __init__(self, min_confidence: float = 0.78, min_margin: float = 0.10) -> None:
        self.min_confidence = min_confidence
        self.min_margin = min_margin

    def _score_candidate(self, intent: BrokenLocatorIntent, node: AccessibleNode) -> float:
        if node.disabled:
            return 0.0
        role_match = 1.0 if node.role == intent.expected_role.lower() else 0.0
        if role_match == 0.0:
            return 0.0

        exp_toks = _tokens(intent.expected_name)
        cand_toks = _tokens(node.name) | _tokens(node.test_id) | _tokens(node.element_id)
        if not exp_toks or not cand_toks:
            return 0.0

        name_toks = _tokens(node.name)
        exact_name = 1.0 if node.name.strip().lower() == intent.expected_name.strip().lower() else 0.0
        jacc_name = (len(exp_toks & name_toks) / len(exp_toks | name_toks)) if name_toks else 0.0
        recall_all = len(exp_toks & cand_toks) / len(exp_toks)

        score = 0.35 * role_match + 0.35 * max(exact_name, jacc_name) + 0.30 * recall_all
        return round(min(1.0, score), 4)

    def heal(self, intent: BrokenLocatorIntent, candidates: List[AccessibleNode]) -> Dict[str, Any]:
        if not candidates:
            return {"healed": False, "confidence": 0.0, "newSelector": None, "reason": "empty_dom"}

        scored: List[Tuple[float, AccessibleNode]] = [
            (self._score_candidate(intent, c), c) for c in candidates
        ]
        scored.sort(key=lambda pair: -pair[0])
        best_score, best_node = scored[0]
        second_score = scored[1][0] if len(scored) > 1 else 0.0
        margin = round(best_score - second_score, 4)

        if best_score < self.min_confidence:
            return {
                "healed": False,
                "confidence": best_score,
                "newSelector": None,
                "reason": "below_confidence_threshold_genuine_regression",
            }
        if margin < self.min_margin:
            return {
                "healed": False,
                "confidence": best_score,
                "newSelector": None,
                "reason": "ambiguous_candidates_refusing_unsafe_heal",
            }

        if best_node.test_id:
            new_sel = f"[data-testid='{best_node.test_id}']"
        elif best_node.element_id:
            new_sel = f"#{best_node.element_id}"
        else:
            new_sel = f"role={best_node.role}[name='{best_node.name}']"

        return {
            "healed": True,
            "confidence": best_score,
            "margin": margin,
            "newSelector": new_sel,
            "matchedNode": best_node,
            "reason": "verified_semantic_match",
        }


class ASTSelectorPatcher:
    """Uses Python stdlib `ast` to locate and rewrite an obsolete selector literal inside Page Object code."""

    def patch_selector(self, source_code: str, old_selector: str, new_selector: str) -> str:
        tree = ast.parse(source_code)
        lines = source_code.splitlines(keepends=True)
        replacements: List[Tuple[int, int, int, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == old_selector:
                if node.lineno is not None and node.end_lineno == node.lineno:
                    replacements.append((node.lineno - 1, node.col_offset, node.end_col_offset or 0, 1))

        if not replacements:
            raise LookupError(f"Selector literal {old_selector!r} not found in AST")

        for line_idx, col_start, col_end, _ in sorted(replacements, reverse=True):
            raw_line = lines[line_idx]
            quote_char = raw_line[col_start] if raw_line[col_start] in ('"', "'") else '"'
            escaped = new_selector.replace(quote_char, "\\" + quote_char)
            lines[line_idx] = raw_line[:col_start] + f"{quote_char}{escaped}{quote_char}" + raw_line[col_end:]

        patched = "".join(lines)
        ast.parse(patched)
        return patched


def _self_test() -> None:
    mutated_html = """
    <main>
      <button id="cancel-flight-btn" data-testid="cta-cancel">Cancel Reservation</button>
      <button id="checkout-submit-v2" data-testid="cta-confirm-booking">Confirm Booking</button>
    </main>
    """
    snap = AccessibilitySnapshotter()
    nodes = snap.extract_nodes(mutated_html)
    healer = SemanticLocatorHealer(min_confidence=0.78, min_margin=0.10)
    res = healer.heal(BrokenLocatorIntent("#confirm-booking-btn", "button", "Confirm Booking"), nodes)
    assert res["healed"] is True and res["confidence"] >= 0.85, res

    reg_html = "<main><button id='cancel-btn'>Cancel Reservation</button></main>"
    reg_res = healer.heal(BrokenLocatorIntent("#confirm-booking-btn", "button", "Confirm Booking"), snap.extract_nodes(reg_html))
    assert reg_res["healed"] is False

    po_src = 'class BookingPage:\n    SUBMIT_BTN = "#confirm-booking-btn"\n    CANCEL_BTN = "#cancel-flight-btn"\n'
    patched = ASTSelectorPatcher().patch_selector(po_src, "#confirm-booking-btn", res["newSelector"])
    assert res["newSelector"] in patched and "#cancel-flight-btn" in patched
    print("[PASS] AI-03 Self-Healing Accessibility Locator Agent & AST Patcher verified.")


if __name__ == "__main__":
    _self_test()
