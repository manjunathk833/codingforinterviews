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
from typing import Any, Dict, List, Optional, Tuple

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


# ==============================================================================
# WAVE 3A: 90-SECOND BLIND PATTERN-TRIAGE & FIRST-LINES IGNITION ARENA
# ==============================================================================
_ALL_TRIAGE_PATTERNS: List[str] = [
    "Arrays & Hashing",
    "Two Pointers",
    "Sliding Window",
    "Stack & Queue",
    "Binary Search",
    "Linked List",
    "Trees & BST",
    "Heaps & Priority Queue",
    "Backtracking",
    "Graphs",
    "1D Dynamic Programming",
    "2D Dynamic Programming",
    "Greedy & Intervals",
    "Design & Concurrency",
    "Bit Manipulation",
]

_ALL_TRIAGE_TIMES: List[str] = [
    "O(1)",
    "O(log N)",
    "O(N)",
    "O(N log N)",
    "O(N * K)",
    "O(N log K)",
    "O(V + E)",
    "O(M * N)",
    "O(N^2)",
    "O(2^N)",
]

_ALL_TRIAGE_STATES: List[str] = [
    "HashMap / Frequency Counter",
    "HashSet / Seen Lookup",
    "Two Pointers (l, r)",
    "Monotonic Stack / Deque",
    "Min / Max Priority Heap",
    "BFS Queue / Graph Frontier",
    "DP Table / Memoization",
    "In-Place Pointers / Tree / Bit State",
]


def infer_canonical_state(spec: Dict[str, Any], pattern: str) -> str:
    """Deterministically infer the primary state container for any of the 128 DSA problems."""
    hint = f"{spec.get('firstLine', '')} {spec.get('invariant', '')}".lower()
    pat = (pattern or "").lower()

    if any(k in hint for k in ("heap", "priority", "heapq")):
        return "Min / Max Priority Heap"
    if any(k in hint for k in ("deque", "stack")) or "stack" in pat:
        return "Monotonic Stack / Deque"
    if "dp" in pat or "dynamic programming" in pat or any(k in hint for k in ("dp =", "dp[", "memo")):
        return "DP Table / Memoization"
    if "two pointers" in pat or "sliding window" in pat or any(k in hint for k in ("l, r =", "left =", "l = 0")):
        if "counter" in hint or "freq" in hint or "window_counts" in hint:
            return "HashMap / Frequency Counter"
        return "Two Pointers (l, r)"
    if any(k in hint for k in ("queue", "deque([", "indegree", "adj", "visited")) and ("graph" in pat or "bfs" in hint):
        return "BFS Queue / Graph Frontier"
    if any(k in hint for k in ("set(", "seen = set", "num_set")):
        return "HashSet / Seen Lookup"
    if any(k in hint for k in ("dict", "counter", "{}", "map", "freq", "buckets")):
        return "HashMap / Frequency Counter"
    if "heap" in pat:
        return "Min / Max Priority Heap"
    if "graph" in pat:
        return "BFS Queue / Graph Frontier"
    return "In-Place Pointers / Tree / Bit State"


def _pick_four_options(canonical: str, pool: List[str], seed_int: int) -> List[str]:
    import random

    rng = random.Random(seed_int)
    distractors = [x for x in pool if x != canonical]
    chosen = [canonical] + rng.sample(distractors, k=min(3, len(distractors)))
    rng.shuffle(chosen)
    return chosen


def _scrub_blind_prompt(prompt: str) -> str:
    import re

    # Strip explicit Big-O / pattern hints embedded in prompt sentences so blind triage stays spoiler-free
    cleaned = re.sub(r"\s*(?:Achieve|in)\s+`?O\([^)]+\)`?\s+time[^.]*\.", ".", prompt or "")
    return cleaned.strip()


def _problem_sheet_lookup() -> Dict[int, Dict[str, Any]]:
    from hub import state_manager

    probs = state_manager.get_dashboard_payload().get("dsa", {}).get("problems", [])
    return {int(p["id"]): p for p in probs}


def build_blind_triage_round(
    difficulty: str = "all",
    exclude_slugs: Optional[List[str]] = None,
    target_slug: Optional[str] = None,
) -> Dict[str, Any]:
    """Select a DSA problem and return a 100% spoiler-free 90s Blind Triage round."""
    import random
    import time as _time

    sheet_by_id = _problem_sheet_lookup()
    excluded = {s.strip().lower() for s in (exclude_slugs or []) if s}

    candidates: List[Dict[str, Any]] = []
    if target_slug:
        sp = get_spec(target_slug)
        if sp:
            candidates = [sp]

    if not candidates:
        diff_norm = (difficulty or "all").strip().lower()
        for sp in ALL_SPECS:
            row = sheet_by_id.get(int(sp["id"]), {})
            row_diff = str(row.get("difficulty") or "Medium")
            if diff_norm not in ("all", "") and row_diff.lower() != diff_norm:
                continue
            if sp["slug"].lower() in excluded:
                continue
            candidates.append(sp)
        if not candidates:
            candidates = list(ALL_SPECS)

    chosen_spec = random.choice(candidates)
    pid = int(chosen_spec["id"])
    row = sheet_by_id.get(pid, {})
    pattern = str(row.get("pattern") or "Arrays & Hashing")
    diff_label = str(row.get("difficulty") or "Medium")
    title_clean = str(row.get("title") or chosen_spec["slug"].replace("-", " ").title())
    folder_slug = str(row.get("folderSlug") or f"{pid:03d}-{chosen_spec['slug']}")
    canon_time = str(chosen_spec["time"])
    canon_state = infer_canonical_state(chosen_spec, pattern)

    seed = int(_time.time() * 1000) ^ (pid * 7919)
    time_pool = list(dict.fromkeys([canon_time] + _ALL_TRIAGE_TIMES))

    return {
        "problemId": pid,
        "slug": chosen_spec["slug"],
        "folderSlug": folder_slug,
        "hasLocalFiles": bool(row.get("hasLocalFiles")),
        "title": title_clean,
        "difficulty": diff_label,
        "blindPrompt": _scrub_blind_prompt(chosen_spec["prompt"]),
        "durationSeconds": 90,
        "patternOptions": _pick_four_options(pattern, _ALL_TRIAGE_PATTERNS, seed + 1),
        "timeOptions": _pick_four_options(canon_time, time_pool, seed + 2),
        "stateOptions": _pick_four_options(canon_state, _ALL_TRIAGE_STATES, seed + 3),
        "pythonStarter": build_python_starter(chosen_spec, row),
        "javaStarter": build_java_starter(chosen_spec, row),
    }


def _score_setup_code(spec: Dict[str, Any], row: Dict[str, Any], lang: str, setup_code: str) -> Tuple[int, str]:
    import ast as _ast
    import re as _re

    code = (setup_code or "").strip()
    if not code:
        return 0, "Editor is empty — write your first 2–5 guard & state-initialization lines."

    if (lang or "python").lower() == "java":
        blank_j = build_java_starter(spec, row).strip()
        if code == blank_j:
            return 0, "Starter Java file was unchanged — replace `UnsupportedOperationException` with your initial state."
        if code.count("{") != code.count("}") or code.count("{") < 2:
            return 0, "Java braces `{ ... }` are unbalanced."
        # Strip main() and comments before checking user statements
        no_comments = _re.sub(r"//.*?$|/\*[\s\S]*?\*/", "", code, flags=_re.MULTILINE)
        no_main = _re.sub(r"public\s+static\s+void\s+main\s*\([^)]*\)\s*\{[^}]*\}", "", no_comments)
        has_real_stmt = bool(
            _re.search(
                r"\b(?:Map<|HashMap|Set<|HashSet|List<|ArrayList|Deque<|ArrayDeque|Stack<|Queue<|PriorityQueue<|int\s+\w+\s*=|int\[\]|long\s+\w+|boolean\s+\w+|Arrays\.sort|Collections\.|if\s*\(|for\s*\(|while\s*\()",
                no_main,
            )
        )
        if not has_real_stmt:
            if "UnsupportedOperationException" in no_main:
                return 0, "Method still only throws `UnsupportedOperationException` — declare your primary Java data structure."
            return 10, "Method signature compiles structurally; add your initial state container (`Map`, `Deque`, pointers, or guard)."
        return 25, "Clean Java first-lines state & guard structure verified."

    # Python AST inspection
    blank_py = build_python_starter(spec, row).strip()
    if code == blank_py:
        return 0, "Starter Python file was unchanged — replace `NotImplementedError` with your initial state."

    try:
        tree = _ast.parse(code)
    except SyntaxError as exc:
        return 0, f"Python SyntaxError on line {exc.lineno}: {exc.msg}"

    real_stmts = 0
    only_not_impl = True
    for node in _ast.walk(tree):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            for stmt in node.body:
                if isinstance(stmt, _ast.Pass):
                    continue
                if isinstance(stmt, _ast.Expr) and isinstance(stmt.value, _ast.Constant) and isinstance(stmt.value.value, str):
                    continue
                if isinstance(stmt, _ast.Raise):
                    dump = _ast.dump(stmt)
                    if "NotImplementedError" in dump:
                        continue
                only_not_impl = False
                if isinstance(
                    stmt,
                    (_ast.Assign, _ast.AnnAssign, _ast.AugAssign, _ast.If, _ast.For, _ast.While, _ast.With, _ast.Try),
                ):
                    real_stmts += 1
                elif isinstance(stmt, _ast.Return) and stmt.value is not None:
                    if not (isinstance(stmt.value, _ast.Constant) and stmt.value.value is None):
                        real_stmts += 1

    if only_not_impl or real_stmts == 0:
        return 0, "No setup statements found inside the method — add a base-case guard or initialize your primary state container."
    if real_stmts == 1:
        return 20, "Valid Python AST with initial statement — add a base-case guard or loop skeleton for full 25/25 ignition points."
    return 25, f"Verified {real_stmts} valid Python AST setup/guard statements."


def grade_blind_triage_submission(
    slug_or_id: str,
    lang: str,
    selected_pattern: str,
    selected_time: str,
    selected_state: str,
    setup_code: str,
    elapsed_sec: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """Deterministically score a 90s Blind Pattern-Triage + First-Lines submission (`0-100`)."""
    spec = get_spec(slug_or_id)
    if not spec:
        return None
    pid = int(spec["id"])
    row = _problem_sheet_lookup().get(pid, {})
    canon_pattern = str(row.get("pattern") or "Arrays & Hashing")
    canon_time = str(spec["time"])
    canon_state = infer_canonical_state(spec, canon_pattern)

    pat_ok = (selected_pattern or "").strip() == canon_pattern
    time_ok = (selected_time or "").strip() == canon_time
    state_ok = (selected_state or "").strip() == canon_state

    pat_pts = 35 if pat_ok else 0
    time_pts = 25 if time_ok else 0
    state_pts = 15 if state_ok else 0
    code_pts, code_note = _score_setup_code(spec, row, lang, setup_code)

    total = pat_pts + time_pts + state_pts + code_pts
    bullets: List[str] = []
    bullets.append(
        f"✓ Pattern `{canon_pattern}` identified!" if pat_ok else f"✗ Pattern is `{canon_pattern}` (you picked `{selected_pattern or 'none'}`)."
    )
    bullets.append(
        f"✓ Optimal Time `{canon_time}` matched!" if time_ok else f"✗ Optimal Time is `{canon_time}` (you picked `{selected_time or 'none'}`)."
    )
    bullets.append(
        f"✓ Primary State `{canon_state}` matched!" if state_ok else f"✗ Primary State is `{canon_state}` (first-line cue: `{spec['firstLine']}`)."
    )
    bullets.append(code_note)

    folder_slug = str(row.get("folderSlug") or f"{pid:03d}-{spec['slug']}")
    return {
        "problemId": pid,
        "slug": spec["slug"],
        "folderSlug": folder_slug,
        "hasLocalFiles": bool(row.get("hasLocalFiles")),
        "score": total,
        "passed": total >= 75,
        "elapsedSeconds": round(float(elapsed_sec or 0.0), 1),
        "breakdown": {
            "patternPts": pat_pts,
            "timePts": time_pts,
            "statePts": state_pts,
            "codePts": code_pts,
            "patternOk": pat_ok,
            "timeOk": time_ok,
            "stateOk": state_ok,
        },
        "canonical": {
            "chapter": f"Ch {row.get('chapterNumber', '01')}: {canon_pattern}",
            "pattern": canon_pattern,
            "time": canon_time,
            "space": spec["space"],
            "state": canon_state,
            "invariant": spec["invariant"],
            "firstLine": spec["firstLine"],
        },
        "feedback": bullets,
    }
