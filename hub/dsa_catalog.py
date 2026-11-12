#!/usr/bin/env python3
"""
Complete Source-of-Truth Catalog for all 128 DSA Problems + 12 5-Minute Muscle-Memory Warmup Drills.

Eliminates placeholder/hardcoded scaffolding by providing every problem with:
- Authentic prompt, invariant, complexity targets, and 4-tier Socratic hints
- Anti-Blank-Page "Help Me Start" 1-line nudge + 3-step plain-English outline comments
- Clean empty Python 3 & Java 17 starter signatures (never pre-solved)
- Real structured test cases (including ListNode, TreeNode, RandomNode, GraphNode, Codec, OOP classes)
- Staff Reference Solution (`refPy`) unlocked only after passing all tests
"""
import json
from typing import Dict, Any, List, Optional

from hub.dsa_specs_g1 import SPECS_G1
from hub.dsa_specs_g2 import SPECS_G2
from hub.dsa_specs_g3 import SPECS_G3
from hub.dsa_specs_g4 import SPECS_G4, WARMUP_DRILLS

ALL_SPECS: List[Dict[str, Any]] = SPECS_G1 + SPECS_G2 + SPECS_G3 + SPECS_G4
assert len(ALL_SPECS) == 128, f"Expected 128 DSA problem specs, found {len(ALL_SPECS)}"

BY_ID: Dict[int, Dict[str, Any]] = {int(s["id"]): s for s in ALL_SPECS}
BY_SLUG: Dict[str, Dict[str, Any]] = {s["slug"].lower(): s for s in ALL_SPECS}
WARMUPS_BY_ID: Dict[str, Dict[str, Any]] = {d["id"]: d for d in WARMUP_DRILLS}

COMMON_PY_HEADER = (
    "from typing import List, Optional, Dict\n"
    "from collections import Counter, defaultdict, deque, OrderedDict\n"
    "from bisect import bisect_left\n"
    "import heapq\n"
    "import threading\n"
    "from utils.dsa_helpers import ListNode, TreeNode, RandomNode, GraphNode\n"
)


def get_spec(slug_or_id: str) -> Optional[Dict[str, Any]]:
    """Lookup problem spec by numeric ID ('8'), exact slug ('longest-consecutive-sequence'), or folder slug ('008-longest-consecutive-sequence')."""
    if slug_or_id is None:
        return None
    raw = str(slug_or_id).strip().lower()
    if raw.isdigit():
        return BY_ID.get(int(raw))
    if raw in BY_SLUG:
        return BY_SLUG[raw]
    if len(raw) > 4 and raw[:3].isdigit() and raw[3] == "-":
        tail = raw[4:]
        if tail in BY_SLUG:
            return BY_SLUG[tail]
        for s_slug, spec in BY_SLUG.items():
            if s_slug.startswith(tail) or tail.startswith(s_slug[:18]):
                return spec
    for s_slug, spec in BY_SLUG.items():
        if raw == s_slug or raw.endswith("-" + s_slug):
            return spec
    return None


def get_warmup_drills() -> List[Dict[str, Any]]:
    return [
        {
            "id": d["id"],
            "title": d["title"],
            "minutes": d["minutes"],
            "goal": d["goal"],
            "firstLine": d["firstLine"],
            "starterPy": d["starterPy"],
            "fnName": d["fnName"],
            "cases": d["cases"],
        }
        for d in WARMUP_DRILLS
    ]


def get_warmup_drill(drill_id: str) -> Optional[Dict[str, Any]]:
    return WARMUPS_BY_ID.get(str(drill_id or "").strip())


def build_python_starter(spec: Dict[str, Any], meta_row: Optional[Dict[str, Any]] = None) -> str:
    """Generate a clean, un-spoiled Python 3 starter file with authentic signature and outline comments."""
    title = (meta_row or {}).get("title") or spec["slug"].replace("-", " ").title()
    pattern = (meta_row or {}).get("pattern") or "DSA Pattern"
    diff = (meta_row or {}).get("difficulty") or "Medium"

    py_sig = spec["pySig"].strip()
    if spec.get("execMode") == "class_ops" or py_sig.startswith("class "):
        body_block = py_sig
        if not body_block.rstrip().endswith("pass"):
            body_block += "\n        pass"
    else:
        body_block = (
            "class Solution:\n"
            f"    {py_sig}\n"
            f"        # First-line idea: {spec['firstLine']}\n"
            "        pass"
        )

    return (
        f'"""Problem #{spec["id"]}: {title}\n'
        f"Pattern: {pattern} | Difficulty: {diff}\n"
        f"Target: {spec['time']} Time · {spec['space']} Space\n"
        f'"""\n'
        f"{COMMON_PY_HEADER}\n\n"
        f"{body_block}\n\n\n"
        f'if __name__ == "__main__":\n'
        f"    # Run full test cases & Code Coach via the Hub (`▶ Run & Coach`) or `./run.sh test {spec['slug']}`\n"
        f'    print("Starter ready for #{spec["id"]} {title}. Implement your solution above!")\n'
    )


def build_java_starter(spec: Dict[str, Any], meta_row: Optional[Dict[str, Any]] = None) -> str:
    """Generate a clean, compilable Java 17 starter file with matching signature and zero spoilers."""
    title = (meta_row or {}).get("title") or spec["slug"].replace("-", " ").title()
    pattern = (meta_row or {}).get("pattern") or "DSA Pattern"
    diff = (meta_row or {}).get("difficulty") or "Medium"
    java_sig = spec["javaSig"].strip()
    ret_stmt = spec.get("javaRet", "").strip()
    steps = spec.get("steps", [])
    step_comments = "\n        ".join(f"// Step {i + 1}: {st}" for i, st in enumerate(steps))
    body_lines = step_comments
    if ret_stmt:
        body_lines += f"\n        {ret_stmt}"

    cls_name = spec.get("className") or "Solution"
    if cls_name != "Solution":
        inner = (
            f"    public static class {cls_name} {{\n"
            f"        {java_sig} {{\n"
            f"        {body_lines}\n"
            f"        }}\n"
            f"    }}\n"
        )
    else:
        inner = (
            f"    {java_sig} {{\n"
            f"        {body_lines}\n"
            f"    }}\n"
        )

    return (
        "import java.util.*;\n"
        "import utils.ListNode;\n"
        "import utils.TreeNode;\n\n"
        "/**\n"
        f" * Problem #{spec['id']}: {title}\n"
        f" * Pattern: {pattern} | Difficulty: {diff}\n"
        " */\n"
        "public class Solution {\n\n"
        f"{inner}\n"
        "    public static void main(String[] args) {\n"
        f'        System.out.println("Java starter compiled cleanly for {title}.");\n'
        "    }\n"
        "}\n"
    )


def build_python_outline(spec: Dict[str, Any]) -> str:
    """Return the exact 3-step plain-English outline body (`Help Me Start` Click 2)."""
    steps = spec.get("steps", [])
    comments = "\n        ".join(f"# Step {i + 1}: {s}" for i, s in enumerate(steps))
    py_sig = spec["pySig"].strip()
    if py_sig.startswith("class "):
        return f"{COMMON_PY_HEADER}\n\n# 3-Step Blueprint:\n" + "\n".join(f"# Step {i + 1}: {s}" for i, s in enumerate(steps)) + f"\n\n{py_sig}\n        pass\n"
    return (
        f"{COMMON_PY_HEADER}\n\n"
        "class Solution:\n"
        f"    {py_sig}\n"
        f"        {comments}\n"
        "        pass\n"
    )


def build_tests_meta(spec: Dict[str, Any], folder_slug: str, meta_row: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build complete `tests.json` metadata dictionary for any of the 128 problems."""
    row = meta_row or {}
    title = row.get("title") or spec["slug"].replace("-", " ").title()
    ch_num = row.get("chapterNumber", 1)
    pattern = row.get("pattern") or "DSA"
    diff = row.get("difficulty") or "Medium"
    steps = spec.get("steps", [])

    return {
        "id": int(spec["id"]),
        "slug": folder_slug,
        "problemSlug": spec["slug"],
        "title": f"{int(spec['id']):03d}. {title}",
        "chapter": f"Ch {ch_num}: {pattern}",
        "difficulty": diff,
        "methodName": spec["method"],
        "className": spec.get("className", "Solution"),
        "execMode": spec.get("execMode", "solution_method"),
        "compareMode": spec.get("compareMode", "exact"),
        "argTypes": spec.get("argTypes", {}),
        "returnType": spec.get("returnType"),
        "timeComplexity": spec["time"],
        "spaceComplexity": spec["space"],
        "visualizerId": row.get("visualizerId", "dsa-group-anagrams"),
        "prompt": spec["prompt"],
        "invariant": spec["invariant"],
        "firstLine": spec["firstLine"],
        "steps": steps,
        "hints": [
            {"tier": 1, "title": "First-Line Nudge", "content": spec["firstLine"]},
            {"tier": 2, "title": "Pattern & Invariant", "content": f"Core invariant: `{spec['invariant']}`"},
            {"tier": 3, "title": "Step-by-Step Plan", "content": " -> ".join(f"Step {i+1}: {s}" for i, s in enumerate(steps))},
            {"tier": 4, "title": "Complexity & Edge Cases", "content": f"Aim for {spec['time']} time and {spec['space']} space. Watch empty inputs, single elements, and duplicates."},
        ],
        "cases": spec["cases"],
    }


def get_reference_solution(slug_or_id: str) -> Optional[Dict[str, str]]:
    """Return full import-ready Staff reference Python snippet for side-by-side review."""
    spec = get_spec(slug_or_id)
    if not spec:
        return None
    return {
        "python": f"{COMMON_PY_HEADER}\n\n{spec['refPy']}",
        "time": spec["time"],
        "space": spec["space"],
        "invariant": spec["invariant"],
    }
