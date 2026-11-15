#!/usr/bin/env python3
"""
Complete Source-of-Truth Catalog for all 128 DSA Problems + 12 5-Minute Muscle-Memory Warmup Drills.

Backed by `hub/data/dsa_specs.json` (token-lean static JSON data outside Python module scan paths):
- Authentic prompt, invariant, complexity targets, and 4-tier Socratic hints
- Anti-Blank-Page "Help Me Start" 1-line nudge + 3-step plain-English outline comments (Python & Java)
- Clean, spoiler-free Python 3 & Java 17 starter signatures (`NotImplementedError` / `UnsupportedOperationException`)
- >= 5 verified structured test cases per problem & warmup drill
- Staff Reference Solution (`refPy` + `refJava`) unlocked only after passing all tests
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_PATH = Path(__file__).resolve().parent / "data" / "dsa_specs.json"

_RAW_CACHE: Dict[str, Any] = json.loads(DATA_PATH.read_text(encoding="utf-8"))
ALL_SPECS: List[Dict[str, Any]] = _RAW_CACHE["problems"]
WARMUP_DRILLS: List[Dict[str, Any]] = _RAW_CACHE["warmups"]
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
    """Lookup problem spec by numeric ID ('8'), exact slug ('longest-consecutive-sequence'), or folder slug."""
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
    out = []
    for d in WARMUP_DRILLS:
        starter = d["starterPy"]
        if starter.rstrip().endswith("pass"):
            starter = starter.rstrip()[:-4] + 'raise NotImplementedError("Write your warmup drill here")\n'
        out.append({
            "id": d["id"],
            "title": d["title"],
            "minutes": d["minutes"],
            "goal": d["goal"],
            "firstLine": d["firstLine"],
            "starterPy": starter,
            "fnName": d["fnName"],
            "cases": d["cases"],
        })
    return out


def get_warmup_drill(drill_id: str) -> Optional[Dict[str, Any]]:
    return WARMUPS_BY_ID.get(str(drill_id or "").strip())


def build_python_starter(spec: Dict[str, Any], meta_row: Optional[Dict[str, Any]] = None) -> str:
    """Generate a clean, spoiler-free Python 3 starter file with authentic signature."""
    title = (meta_row or {}).get("title") or spec["slug"].replace("-", " ").title()
    diff = (meta_row or {}).get("difficulty") or "Medium"

    py_sig = spec["pySig"].strip()
    if spec.get("execMode") == "class_ops" or py_sig.startswith("class "):
        lines = []
        for ln in py_sig.splitlines():
            if ln.strip() == "pass":
                indent = ln[: len(ln) - len(ln.lstrip())]
                lines.append(f'{indent}raise NotImplementedError("Write your solution here")')
            else:
                lines.append(ln)
        body_block = "\n".join(lines)
        if "NotImplementedError" not in body_block:
            body_block += '\n        raise NotImplementedError("Write your solution here")'
    else:
        body_block = (
            "class Solution:\n"
            f"    {py_sig}\n"
            '        raise NotImplementedError("Write your solution here")'
        )

    return (
        f'"""Problem #{spec["id"]}: {title} ({diff})"""\n'
        f"{COMMON_PY_HEADER}\n\n"
        f"{body_block}\n\n\n"
        f'if __name__ == "__main__":\n'
        f"    # Run test cases & Code Coach via Coding Studio (`▶ Run & Coach`) or `./run.sh test {spec['slug']}`\n"
        f'    print("Starter ready for #{spec["id"]} {title}.")\n'
    )


def build_java_starter(spec: Dict[str, Any], meta_row: Optional[Dict[str, Any]] = None) -> str:
    """Generate a clean, compilable, spoiler-free Java 17 starter file that fails until implemented."""
    title = (meta_row or {}).get("title") or spec["slug"].replace("-", " ").title()
    diff = (meta_row or {}).get("difficulty") or "Medium"

    if spec.get("javaClassStub"):
        inner = spec["javaClassStub"].rstrip() + "\n"
    else:
        java_sig = spec["javaSig"].strip()
        cls_name = spec.get("className") or "Solution"
        if cls_name != "Solution":
            inner = (
                f"    public static class {cls_name} {{\n"
                f"        {java_sig} {{\n"
                '            throw new UnsupportedOperationException("Write your solution here");\n'
                "        }\n"
                "    }\n"
            )
        else:
            inner = (
                f"    {java_sig} {{\n"
                '        throw new UnsupportedOperationException("Write your solution here");\n'
                "    }\n"
            )

    return (
        "import java.util.*;\n"
        "import utils.ListNode;\n"
        "import utils.TreeNode;\n"
        "import utils.RandomNode;\n"
        "import utils.GraphNode;\n\n"
        "/**\n"
        f" * Problem #{spec['id']}: {title} ({diff})\n"
        " */\n"
        "public class Solution {\n\n"
        f"{inner}\n"
        "    public static void main(String[] args) {\n"
        f'        System.out.println("Java starter compiled cleanly for {title}.");\n'
        "    }\n"
        "}\n"
    )


def build_python_outline(spec: Dict[str, Any]) -> str:
    """Return 3-step plain-English comment lines for non-destructive injection in Python."""
    steps = spec.get("steps", [])
    return "\n".join(f"# Step {i + 1}: {s}" for i, s in enumerate(steps))


def build_java_outline(spec: Dict[str, Any]) -> str:
    """Return 3-step plain-English comment lines for non-destructive injection in Java."""
    steps = spec.get("steps", [])
    return "\n".join(f"// Step {i + 1}: {s}" for i, s in enumerate(steps))


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
        "javaSig": spec.get("javaSig", ""),
        "timeComplexity": spec["time"],
        "spaceComplexity": spec["space"],
        "visualizerId": row.get("visualizerId", "dsa-group-anagrams"),
        "prompt": spec["prompt"],
        "invariant": spec["invariant"],
        "firstLine": spec["firstLine"],
        "steps": steps,
        "pythonOutlineComments": build_python_outline(spec),
        "javaOutlineComments": build_java_outline(spec),
        "hints": [
            {"tier": 1, "title": "First-Line Nudge", "content": spec["firstLine"]},
            {"tier": 2, "title": "Pattern & Invariant", "content": f"Core invariant: `{spec['invariant']}`"},
            {"tier": 3, "title": "Step-by-Step Plan", "content": " -> ".join(f"Step {i+1}: {s}" for i, s in enumerate(steps))},
            {"tier": 4, "title": "Complexity & Edge Cases", "content": f"Aim for {spec['time']} time and {spec['space']} space. Watch empty inputs, single elements, and duplicates."},
        ],
        "cases": spec["cases"],
    }


def get_reference_solution(slug_or_id: str) -> Optional[Dict[str, str]]:
    """Return Staff reference solution (`python` + optional `java`) unlocked after passing."""
    spec = get_spec(slug_or_id)
    if not spec:
        return None
    res: Dict[str, str] = {
        "python": f"{COMMON_PY_HEADER}\n\n{spec['refPy']}",
        "time": spec["time"],
        "space": spec["space"],
        "invariant": spec["invariant"],
    }
    if spec.get("refJava"):
        res["java"] = spec["refJava"]
    return res
