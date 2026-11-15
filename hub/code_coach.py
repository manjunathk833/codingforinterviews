#!/usr/bin/env python3
"""
100% Local Subprocess Test Runner & Instant 0-100 Code Coach for The Hub of Learning.

- Zero external AI API required.
- Executes both Python 3 and Java 17 user code inside isolated subprocesses with strict timeout guards.
- Supports all 128 DSA problem shapes (arrays, matrices, ListNode, TreeNode, RandomNode,
  GraphNode, Codec, OOP classes via `class_ops`, cycle lists, BST LCA) and all 12 Warmup Drills.
- Computes 0-100 Code Coach Score (strictly gated at 0/100 when 0 test cases pass):
  - Correctness (50 pts): structured case pass ratio
  - Speed (25 pts): runtime + generalized empirical 8x scaling probe on O(N)/O(N log N) problems
  - Clean Code (25 pts): AST / brace control-flow nesting, guard clauses, mutable defaults
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DSA_ROOT = REPO_ROOT / "dsa"


def normalize_case_value(val: Any, cmode: str) -> Any:
    if cmode == "sorted_int_array" and isinstance(val, (list, tuple)):
        try:
            return sorted(int(x) for x in val)
        except Exception:
            return val
    if cmode == "unordered_groups" and isinstance(val, (list, tuple)):
        try:
            norm_groups = [sorted(str(item) for item in grp) for grp in val]
            return sorted(norm_groups, key=lambda g: (len(g), g))
        except Exception:
            return val
    if cmode == "unordered" and isinstance(val, list):
        norm_items = [normalize_case_value(x, "unordered") if isinstance(x, list) else x for x in val]
        try:
            return sorted(norm_items, key=lambda item: json.dumps(item, sort_keys=True))
        except Exception:
            return norm_items
    if cmode == "anagram_groups" and isinstance(val, list):
        return sorted([sorted(g) if isinstance(g, list) else g for g in val])
    return val


def match_case_output(actual: Any, expected: Any, cmode: str) -> bool:
    if cmode == "float_1e5":
        if isinstance(actual, list) and isinstance(expected, list):
            return len(actual) == len(expected) and all(
                match_case_output(a, e, "float_1e5") for a, e in zip(actual, expected)
            )
        if actual is None or expected is None:
            return actual is expected
        try:
            return abs(float(actual) - float(expected)) <= 1e-5
        except Exception:
            return False
    if cmode == "any_of" and isinstance(expected, list):
        return actual in expected
    return normalize_case_value(actual, cmode) == normalize_case_value(expected, cmode)


_PYTHON_RUNNER_SCRIPT = r'''
import json, sys, time, importlib.util

payload_path = sys.argv[1]
payload = json.loads(open(payload_path, "r", encoding="utf-8").read())
mode = payload["mode"]
file_path = payload.get("filePath")
code_text = payload.get("codeText")
method_name = payload.get("methodName", "")
class_name = payload.get("className", "Solution")
exec_mode = payload.get("execMode", "solution_method")
compare_mode = payload.get("compareMode", "exact")
arg_types = payload.get("argTypes", {})
return_type = payload.get("returnType")
cases = payload.get("cases", [])
scaling_cfg = payload.get("scalingProbe")

from utils.dsa_helpers import ListNode, TreeNode, RandomNode, GraphNode
from hub.code_coach import match_case_output

mod_ns = {}
if code_text is not None:
    exec(compile(code_text, "<warmup>", "exec"), mod_ns)
else:
    spec = importlib.util.spec_from_file_location("user_submission", file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod_ns = mod.__dict__

def _convert_arg(name, val):
    t = arg_types.get(name)
    if t == "ListNode":
        return ListNode.from_list(val)
    if t == "ListOfListNode":
        return [ListNode.from_list(x) for x in val]
    if t == "TreeNode":
        return TreeNode.from_list(val)
    if t == "RandomNode":
        return RandomNode.from_pairs(val)
    if t == "GraphNode":
        return GraphNode.from_adj_list(val)
    return json.loads(json.dumps(val))

def _convert_ret(ret):
    if return_type == "ListNode":
        return ret.to_list() if ret is not None else []
    if return_type == "TreeNode":
        return ret.to_list() if ret is not None else []
    if return_type == "RandomNode":
        return ret.to_pairs() if ret is not None else []
    if return_type == "GraphNode":
        return ret.to_adj_list() if ret is not None else []
    return ret

def _find_bst_node(root, target_val):
    curr = root
    while curr:
        if curr.val == target_val:
            return curr
        curr = curr.left if target_val < curr.val else curr.right
    return None

results = []
all_ok = True

for idx, c in enumerate(cases):
    t0 = time.perf_counter()
    inp = c.get("input", {})
    expected = c.get("expected")
    label = c.get("label") or f"Case {idx + 1}"
    cid = c.get("id") or f"case-{idx + 1}"
    try:
        if mode == "warmup":
            fn = mod_ns[payload["fnName"]]
            kwargs = {k: _convert_arg(k, v) for k, v in inp.items()}
            if "graph" in kwargs and isinstance(kwargs["graph"], dict):
                kwargs["graph"] = {int(k): v for k, v in kwargs["graph"].items()}
            actual = _convert_ret(fn(**kwargs))
        elif exec_mode == "class_ops":
            ops = inp["ops"]
            args = inp["args"]
            cls = mod_ns[class_name]
            obj = cls(*args[0])
            out = [None]
            for op, arg in zip(ops[1:], args[1:]):
                out.append(getattr(obj, op)(*arg))
            actual = out
        elif exec_mode == "codec_strings":
            cls = mod_ns.get(class_name) or mod_ns["Solution"]
            obj = cls()
            encoded = obj.encode(list(inp["strs"]))
            actual = obj.decode(encoded)
        elif exec_mode == "codec_tree":
            cls = mod_ns.get(class_name) or mod_ns["Solution"]
            obj = cls()
            tree_in = TreeNode.from_list(inp["root"])
            ser = obj.serialize(tree_in)
            des = obj.deserialize(ser)
            actual = des.to_list() if des is not None else []
        elif exec_mode == "list_cycle":
            vals = inp["values"]
            pos = inp["pos"]
            nodes = [ListNode(v) for v in vals]
            for i in range(len(nodes) - 1):
                nodes[i].next = nodes[i + 1]
            if nodes and 0 <= pos < len(nodes):
                nodes[-1].next = nodes[pos]
            head = nodes[0] if nodes else None
            sol = mod_ns["Solution"]()
            actual = getattr(sol, method_name)(head)
        elif exec_mode == "bst_lca":
            root = TreeNode.from_list(inp["root"])
            p_n = _find_bst_node(root, inp["p"])
            q_n = _find_bst_node(root, inp["q"])
            sol = mod_ns["Solution"]()
            ans_node = getattr(sol, method_name)(root, p_n, q_n)
            actual = ans_node.val if ans_node is not None else None
        else:
            sol = mod_ns["Solution"]()
            fn = getattr(sol, method_name)
            kwargs = {k: _convert_arg(k, v) for k, v in inp.items()}
            ret = fn(**kwargs)
            if return_type == "InPlaceHead":
                head_obj = kwargs["head"]
                actual = head_obj.to_list() if head_obj is not None else []
            elif return_type == "InPlaceArg0":
                first_k = next(iter(kwargs))
                actual = kwargs[first_k]
            else:
                actual = _convert_ret(ret)
        dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        passed = match_case_output(actual, expected, compare_mode)
        if not passed:
            all_ok = False
        results.append({
            "id": cid, "label": label, "passed": bool(passed),
            "input": inp, "expected": expected, "actual": actual, "durationMs": dt_ms,
        })
    except Exception as exc:
        all_ok = False
        dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        results.append({
            "id": cid, "label": label, "passed": False,
            "input": inp, "expected": expected, "actual": f"{type(exc).__name__}: {exc}", "durationMs": dt_ms,
        })

scaling_ratio = None
if all_ok and scaling_cfg and exec_mode == "solution_method":
    try:
        sol = mod_ns["Solution"]()
        fn = getattr(sol, method_name)
        kind = scaling_cfg.get("kind")

        def _build_bst(lo, hi):
            if lo > hi:
                return None
            mid = (lo + hi) // 2
            node = TreeNode(mid)
            node.left = _build_bst(lo, mid - 1)
            node.right = _build_bst(mid + 1, hi)
            return node

        def _run_bench(n):
            if kind == "single_int_array":
                arr = [((i * 37) % 97) + 1 for i in range(n)]
                t_a = time.perf_counter()
                fn(arr)
                return time.perf_counter() - t_a
            if kind == "unit_product_array":
                arr = [2 if i % 64 == 0 else (-1 if i % 2 else 1) for i in range(n)]
                t_a = time.perf_counter()
                fn(arr)
                return time.perf_counter() - t_a
            if kind == "two_sum_array":
                arr = list(range(1, n + 1))
                tgt = (n - 1) + n
                t_a = time.perf_counter()
                fn(arr, tgt)
                return time.perf_counter() - t_a
            if kind == "sorted_nums_target":
                arr = [i * 2 for i in range(n)]
                tgt = (n - 2) * 2
                t_a = time.perf_counter()
                fn(arr, tgt)
                return time.perf_counter() - t_a
            if kind == "nums_and_k":
                arr = [((i * 31) % 53) + 1 for i in range(n)]
                t_a = time.perf_counter()
                fn(arr, 5)
                return time.perf_counter() - t_a
            if kind == "unique_str":
                s = "".join(chr(97 + (i % 26)) for i in range(n))
                t_a = time.perf_counter()
                fn(s)
                return time.perf_counter() - t_a
            if kind == "parens_str":
                s = "()" * max(1, n // 2)
                t_a = time.perf_counter()
                fn(s)
                return time.perf_counter() - t_a
            if kind == "linked_list":
                head = ListNode.from_list(list(range(1, n + 1)))
                t_a = time.perf_counter()
                fn(head)
                return time.perf_counter() - t_a
            if kind == "balanced_bst":
                root = _build_bst(1, n)
                t_a = time.perf_counter()
                fn(root)
                return time.perf_counter() - t_a
            if kind == "intervals_array":
                ivs = [[i * 2, i * 2 + 3] for i in range(n)]
                t_a = time.perf_counter()
                fn(ivs)
                return time.perf_counter() - t_a
            return None

        dt_small = _run_bench(120)
        dt_large = _run_bench(960)
        if dt_small is not None and dt_large is not None:
            dt_s = sum(_run_bench(120) for _ in range(3)) / 3.0
            dt_l = sum(_run_bench(960) for _ in range(3)) / 3.0
            scaling_ratio = round(dt_l / max(1e-6, dt_s), 1)
    except Exception:
        scaling_ratio = None

print(json.dumps({
    "status": "PASSED" if all_ok else "FAILED",
    "cases": results,
    "scalingRatio": scaling_ratio,
}))
'''


def _max_ast_nesting(node: ast.AST, depth: int = 0) -> int:
    branch_nodes = (ast.For, ast.While, ast.If, ast.Try, ast.With)
    next_d = depth + (1 if isinstance(node, branch_nodes) else 0)
    child_max = next_d
    for ch in ast.iter_child_nodes(node):
        child_max = max(child_max, _max_ast_nesting(ch, next_d))
    return child_max


def _max_loop_depth(node: ast.AST, depth: int = 0) -> int:
    loop_nodes = (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
    next_d = depth + (1 if isinstance(node, loop_nodes) else 0)
    child_max = next_d
    for ch in ast.iter_child_nodes(node):
        child_max = max(child_max, _max_loop_depth(ch, next_d))
    return child_max


def _detect_scaling_probe(spec: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
    """Generalized empirical 8x scaling detector across arrays, strings, linked lists, trees, and intervals."""
    if not spec or spec.get("execMode", "solution_method") != "solution_method":
        return None
    target_t = spec.get("time", "")
    if target_t not in ("O(N)", "O(N log N)"):
        return None
    slug = spec.get("slug", "")
    if slug in ("two-sum", "two-sum-ii-input-array-is-sorted"):
        return {"kind": "two_sum_array"}
    if slug == "product-of-array-except-self":
        return {"kind": "unit_product_array"}
    if slug == "valid-parentheses":
        return {"kind": "parens_str"}

    cases = spec.get("cases") or []
    if not cases:
        return None
    inp = cases[0].get("input") or {}
    arg_t = spec.get("argTypes") or {}
    keys = list(inp.keys())

    if len(keys) == 1:
        k0 = keys[0]
        v0 = inp[k0]
        if arg_t.get(k0) == "ListNode":
            return {"kind": "linked_list"}
        if arg_t.get(k0) == "TreeNode":
            return {"kind": "balanced_bst"}
        if isinstance(v0, str) and slug not in ("decode-ways", "palindrome-partitioning"):
            return {"kind": "unique_str"}
        if isinstance(v0, list) and v0:
            if all(isinstance(x, int) and not isinstance(x, bool) for x in v0):
                return {"kind": "single_int_array"}
            if all(isinstance(x, list) and len(x) == 2 and all(isinstance(y, int) for y in x) for x in v0):
                return {"kind": "intervals_array"}
    elif len(keys) == 2:
        k0, k1 = keys[0], keys[1]
        v0, v1 = inp[k0], inp[k1]
        if isinstance(v0, list) and v0 and all(isinstance(x, int) for x in v0) and isinstance(v1, int):
            if k1 == "target":
                return {"kind": "sorted_nums_target"}
            if k1 == "k":
                return {"kind": "nums_and_k"}
    return None


def _is_unimplemented_stmt(stmt: ast.stmt) -> bool:
    if isinstance(stmt, (ast.Pass, ast.Expr)):
        return True
    if isinstance(stmt, ast.Raise) and stmt.exc is not None:
        exc = stmt.exc
        fn = exc.func if isinstance(exc, ast.Call) else exc
        if isinstance(fn, ast.Name) and fn.id == "NotImplementedError":
            return True
    return False


def analyze_python_code_coach(
    code_text: str,
    passed_count: int,
    total_count: int,
    target_time: str = "O(N)",
    scaling_ratio: Optional[float] = None,
    timed_out: bool = False,
    duration_ms: float = 0.0,
) -> Dict[str, Any]:
    """Compute 0-100 Instant Code Coach scorecard strictly gated at 0/100 when 0 cases pass."""
    if timed_out:
        return {
            "score": 0,
            "correctnessPts": 0,
            "speedPts": 0,
            "cleanCodePts": 0,
            "verdict": "Timed Out (>4s) — Likely Infinite Loop",
            "empiricalScaling": "Stopped after 4.0s safety limit",
            "nestingDepth": 0,
            "loopDepth": 0,
            "tips": [
                "Your loop did not finish within 4 seconds. Check that `left`, `right`, or `curr` advances inside every branch of your `while` loop!"
            ],
        }

    total_safe = max(1, total_count)
    correctness_pts = round(50.0 * passed_count / total_safe)

    tips: List[str] = []
    nesting = 0
    loops = 0
    style_pts = 25
    has_mutable_default = False
    is_pass_stub = False

    try:
        sol_section = code_text.split('if __name__ == "__main__"')[0]
        tree = ast.parse(sol_section)
        nesting = _max_ast_nesting(tree)
        loops = _max_loop_depth(tree)

        fn_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith("__")]
        if fn_defs:
            non_trivial = [
                stmt for fn in fn_defs for stmt in fn.body
                if not _is_unimplemented_stmt(stmt)
            ]
            if not non_trivial:
                is_pass_stub = True

        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef):
                for d in n.args.defaults:
                    if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                        has_mutable_default = True
                        break
    except SyntaxError as syn:
        return {
            "score": 0,
            "correctnessPts": 0,
            "speedPts": 0,
            "cleanCodePts": 0,
            "verdict": f"Syntax Error (Line {syn.lineno})",
            "empiricalScaling": "Did not run",
            "nestingDepth": 0,
            "loopDepth": 0,
            "tips": [f"Fix the Python syntax issue near line {syn.lineno}: {syn.msg}."],
        }

    # Strict Carbon Gate: 0 passed cases -> 0/100 score (no free Speed or Clean Code points!)
    if passed_count == 0 or is_pass_stub:
        if is_pass_stub:
            tips.append(
                "Starter is still unimplemented. Click `⚡ Help Me Start` to inject the 3-step outline comments without overwriting your file."
            )
        else:
            tips.append("0 test cases passed yet. Click Case 1 below to compare Expected vs. Actual output.")
        return {
            "score": 0,
            "correctnessPts": 0,
            "speedPts": 0,
            "cleanCodePts": 0,
            "verdict": "Unimplemented Starter" if is_pass_stub else "Keep Iterating (0 Cases Passed)",
            "empiricalScaling": "Waiting for passing tests",
            "nestingDepth": nesting,
            "loopDepth": loops,
            "tips": tips,
        }

    speed_pts = 25
    scaling_label = f"Fast ({duration_ms:.1f}ms) · Target {target_time}"
    if scaling_ratio is not None:
        if target_time in ("O(N)", "O(N log N)") and scaling_ratio > 24.0:
            speed_pts = 10
            scaling_label = f"Slowdown detected: {scaling_ratio:.1f}x slower for 8x input (~O(N²))"
            tips.append(
                f"Your code slowed down {scaling_ratio:.1f}x when the input grew 8x. Look for a hidden `in list` scan or nested loop and swap it for a `set()` or `dict`."
            )
        else:
            scaling_label = f"Matches {target_time} ({scaling_ratio:.1f}x on 8x input)"
    elif loops >= 2 and target_time in ("O(N)", "O(N) Time") and duration_ms > 45.0:
        speed_pts = 14
        tips.append(f"Nested loop spotted on an {target_time} problem — check if a hash map or sliding window removes the inner loop.")

    if nesting > 3:
        style_pts -= 6
        tips.append(
            f"Deep nesting ({nesting} levels). Add an early guard `if not ...: return ...` at the top of your function to keep indentation flat."
        )
    if has_mutable_default:
        style_pts -= 7
        tips.append("Avoid mutable defaults like `cache={}` in function arguments; use `None` and initialize inside.")
    if passed_count == total_count and style_pts >= 22 and not tips:
        tips.append("Clean control flow, flat nesting, and optimal algorithmic speed. Ready for Staff review!")
    elif passed_count < total_count and not tips:
        tips.append("Click the failing red test pill below to compare Expected vs. Actual output line by line.")

    style_pts = max(0, min(25, style_pts))
    total_score = correctness_pts + speed_pts + style_pts
    if passed_count == total_count and total_score >= 90:
        verdict = "Staff Ready"
    elif passed_count == total_count:
        verdict = "Passing — Can Optimize Further"
    else:
        verdict = "Keep Iterating"

    return {
        "score": int(total_score),
        "correctnessPts": int(correctness_pts),
        "speedPts": int(speed_pts),
        "cleanCodePts": int(style_pts),
        "verdict": verdict,
        "empiricalScaling": scaling_label,
        "nestingDepth": nesting,
        "loopDepth": loops,
        "tips": tips,
    }


def analyze_java_code_coach(
    code_text: str,
    passed_count: int = 0,
    total_count: int = 1,
    target_time: str = "O(N)",
    duration_ms: float = 0.0,
    comp_err: Optional[str] = None,
    timed_out: bool = False,
) -> Dict[str, Any]:
    """Compute 0-100 Code Coach score for Java 17 submissions strictly gated at 0/100 on 0 passed cases."""
    if timed_out:
        return {
            "score": 0, "correctnessPts": 0, "speedPts": 0, "cleanCodePts": 0,
            "verdict": "Timed Out (>6s)",
            "empiricalScaling": "Java execution timed out",
            "tips": ["Java execution timed out — check loop termination conditions."],
        }
    if comp_err:
        msg = [ln.strip() for ln in comp_err.splitlines() if ln.strip()][:2]
        return {
            "score": 0, "correctnessPts": 0, "speedPts": 0, "cleanCodePts": 0,
            "verdict": "Java Compile Error",
            "empiricalScaling": "Did not compile",
            "tips": [f"Compiler message: {' '.join(msg)}"],
        }

    is_stub = 'UnsupportedOperationException("Write your solution here")' in code_text
    if passed_count == 0 or is_stub:
        return {
            "score": 0, "correctnessPts": 0, "speedPts": 0, "cleanCodePts": 0,
            "verdict": "Unimplemented Starter" if is_stub else "Keep Iterating (0 Cases Passed)",
            "empiricalScaling": "Waiting for passing tests",
            "tips": [
                "Java starter is still unimplemented. Click `⚡ Help Me Start` to inject `// Step 1..3` comments."
                if is_stub else
                "0 Java test cases passed. Click Case 1 below to inspect Expected vs. Actual output."
            ],
        }

    depth = 0
    max_depth = 0
    for ch in code_text:
        if ch == "{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == "}":
            depth = max(0, depth - 1)

    total_safe = max(1, total_count)
    correctness_pts = round(50.0 * passed_count / total_safe)
    speed_pts = 25
    clean_pts = 25
    tips: List[str] = []
    if max_depth > 5:
        clean_pts -= 5
        tips.append(f"Deep Java brace nesting ({max_depth} levels). Add early `return` guard clauses.")
    if passed_count == total_count and not tips:
        tips.append(f"Java 17 compiled & passed all {total_count} cases ({duration_ms:.1f}ms). Staff Ready!")
    elif passed_count < total_count and not tips:
        tips.append("Click the failing red test pill below to inspect Expected vs. Actual output.")

    total_score = int(correctness_pts + speed_pts + max(0, clean_pts))
    return {
        "score": total_score,
        "correctnessPts": int(correctness_pts),
        "speedPts": speed_pts,
        "cleanCodePts": max(0, clean_pts),
        "verdict": "Staff Ready" if (passed_count == total_count and total_score >= 90) else "Keep Iterating",
        "empiricalScaling": f"JVM case runner ({duration_ms:.1f}ms · Target {target_time})",
        "tips": tips,
    }


def _py_val_to_java_expr(val: Any) -> str:
    """Emit any JSON value as a valid Java Object expression (`List<Object>`, `String`, `Integer`, `Double`, `Boolean`, `null`)."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "Boolean.TRUE" if val else "Boolean.FALSE"
    if isinstance(val, int):
        if -2147483648 <= val <= 2147483647:
            return f"Integer.valueOf({val})"
        return f"Long.valueOf({val}L)"
    if isinstance(val, float):
        return f"Double.valueOf({repr(val)})"
    if isinstance(val, str):
        esc = (
            val.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
        return f'"{esc}"'
    if isinstance(val, list):
        if not val:
            return "new ArrayList<>()"
        items = ", ".join(_py_val_to_java_expr(x) for x in val)
        return f"new ArrayList<>(Arrays.asList({items}))"
    if isinstance(val, dict):
        entries = []
        for k, v in val.items():
            entries.append(f"m.put({_py_val_to_java_expr(str(k))}, {_py_val_to_java_expr(v)});")
        return f"new Object() {{ Map<String, Object> build() {{ Map<String, Object> m = new LinkedHashMap<>(); {' '.join(entries)} return m; }} }}.build()"
    return "null"


_JAVA_HARNESS_TEMPLATE = r'''
import java.lang.reflect.*;
import java.util.*;
import utils.ListNode;
import utils.TreeNode;
import utils.RandomNode;
import utils.GraphNode;

public class CoachJavaHarness {

    private static int toInt(Object o) {
        if (o instanceof Number) return ((Number) o).intValue();
        return Integer.parseInt(String.valueOf(o));
    }

    @SuppressWarnings("unchecked")
    private static Object adaptArg(Object raw, Class<?> paramType, Type genericType, String hint) {
        if (raw == null) return null;
        if ("ListNode".equals(hint) || paramType == ListNode.class) {
            List<?> lst = (List<?>) raw;
            int[] arr = new int[lst.size()];
            for (int i = 0; i < lst.size(); i++) arr[i] = toInt(lst.get(i));
            return ListNode.fromArray(arr);
        }
        if ("ListOfListNode".equals(hint) || paramType == ListNode[].class) {
            List<?> outer = (List<?>) raw;
            ListNode[] arr = new ListNode[outer.size()];
            for (int i = 0; i < outer.size(); i++) {
                arr[i] = (ListNode) adaptArg(outer.get(i), ListNode.class, ListNode.class, "ListNode");
            }
            if (paramType == List.class) return new ArrayList<>(Arrays.asList(arr));
            return arr;
        }
        if ("TreeNode".equals(hint) || paramType == TreeNode.class) {
            List<?> lst = (List<?>) raw;
            Integer[] vals = new Integer[lst.size()];
            for (int i = 0; i < lst.size(); i++) {
                vals[i] = lst.get(i) == null ? null : toInt(lst.get(i));
            }
            return TreeNode.fromLevelOrder(vals);
        }
        if ("RandomNode".equals(hint) || paramType == RandomNode.class) {
            List<?> outer = (List<?>) raw;
            List<List<Integer>> pairs = new ArrayList<>();
            for (Object item : outer) {
                List<?> row = (List<?>) item;
                List<Integer> p = new ArrayList<>();
                p.add(toInt(row.get(0)));
                p.add(row.get(1) == null ? null : toInt(row.get(1)));
                pairs.add(p);
            }
            return RandomNode.fromPairs(pairs);
        }
        if ("GraphNode".equals(hint) || paramType == GraphNode.class) {
            List<?> outer = (List<?>) raw;
            List<List<Integer>> adj = new ArrayList<>();
            for (Object item : outer) {
                List<?> row = (List<?>) item;
                List<Integer> r = new ArrayList<>();
                for (Object x : row) r.add(toInt(x));
                adj.add(r);
            }
            return GraphNode.fromAdjList(adj);
        }
        if (paramType == int.class || paramType == Integer.class) return toInt(raw);
        if (paramType == long.class || paramType == Long.class) return ((Number) raw).longValue();
        if (paramType == double.class || paramType == Double.class) return ((Number) raw).doubleValue();
        if (paramType == boolean.class || paramType == Boolean.class) return (Boolean) raw;
        if (paramType == char.class || paramType == Character.class) return String.valueOf(raw).charAt(0);
        if (paramType == String.class) return String.valueOf(raw);
        if (paramType == int[].class) {
            List<?> lst = (List<?>) raw;
            int[] a = new int[lst.size()];
            for (int i = 0; i < lst.size(); i++) a[i] = toInt(lst.get(i));
            return a;
        }
        if (paramType == String[].class) {
            List<?> lst = (List<?>) raw;
            String[] a = new String[lst.size()];
            for (int i = 0; i < lst.size(); i++) a[i] = String.valueOf(lst.get(i));
            return a;
        }
        if (paramType == char[].class) {
            List<?> lst = (List<?>) raw;
            char[] a = new char[lst.size()];
            for (int i = 0; i < lst.size(); i++) a[i] = String.valueOf(lst.get(i)).charAt(0);
            return a;
        }
        if (paramType == int[][].class) {
            List<?> outer = (List<?>) raw;
            int[][] m = new int[outer.size()][];
            for (int i = 0; i < outer.size(); i++) {
                m[i] = (int[]) adaptArg(outer.get(i), int[].class, int[].class, null);
            }
            return m;
        }
        if (paramType == char[][].class) {
            List<?> outer = (List<?>) raw;
            char[][] m = new char[outer.size()][];
            for (int i = 0; i < outer.size(); i++) {
                List<?> row = (List<?>) outer.get(i);
                m[i] = new char[row.size()];
                for (int j = 0; j < row.size(); j++) m[i][j] = String.valueOf(row.get(j)).charAt(0);
            }
            return m;
        }
        if (List.class.isAssignableFrom(paramType) && raw instanceof List<?>) {
            List<?> src = (List<?>) raw;
            if (genericType instanceof ParameterizedType) {
                Type elemT = ((ParameterizedType) genericType).getActualTypeArguments()[0];
                if (elemT == Integer.class) {
                    List<Integer> out = new ArrayList<>();
                    for (Object x : src) out.add(x == null ? null : toInt(x));
                    return out;
                }
                if (elemT == String.class) {
                    List<String> out = new ArrayList<>();
                    for (Object x : src) out.add(x == null ? null : String.valueOf(x));
                    return out;
                }
                if (elemT instanceof ParameterizedType) {
                    List<Object> out = new ArrayList<>();
                    for (Object x : src) out.add(adaptArg(x, List.class, elemT, null));
                    return out;
                }
            }
            return new ArrayList<>(src);
        }
        return raw;
    }

    private static Class<?> resolveClass(String clsName) throws ClassNotFoundException {
        if (clsName == null || clsName.isEmpty() || "Solution".equals(clsName)) {
            return Class.forName("Solution");
        }
        try {
            return Class.forName("Solution$" + clsName);
        } catch (ClassNotFoundException e) {
            try {
                return Class.forName(clsName);
            } catch (ClassNotFoundException e2) {
                return Class.forName("Solution");
            }
        }
    }

    private static TreeNode findBst(TreeNode root, int target) {
        TreeNode curr = root;
        while (curr != null) {
            if (curr.val == target) return curr;
            curr = target < curr.val ? curr.left : curr.right;
        }
        return null;
    }

    private static String escJson(String s) {
        StringBuilder sb = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\\') sb.append("\\\\");
            else if (c == '"') sb.append("\\\"");
            else if (c == '\n') sb.append("\\n");
            else if (c == '\r') sb.append("\\r");
            else if (c == '\t') sb.append("\\t");
            else sb.append(c);
        }
        sb.append('"');
        return sb.toString();
    }

    private static String toJson(Object val, String retHint) {
        if ("ListNode".equals(retHint) && val == null) return "[]";
        if ("TreeNode".equals(retHint) && val == null) return "[]";
        if ("RandomNode".equals(retHint) && val == null) return "[]";
        if ("GraphNode".equals(retHint) && val == null) return "[]";
        if (val == null) return "null";
        if (val instanceof ListNode) return toJson(ListNode.toArray((ListNode) val), null);
        if (val instanceof TreeNode) return toJson(TreeNode.toLevelOrder((TreeNode) val), null);
        if (val instanceof RandomNode) return toJson(RandomNode.toPairs((RandomNode) val), null);
        if (val instanceof GraphNode) return toJson(GraphNode.toAdjList((GraphNode) val), null);
        if (val instanceof Boolean || val instanceof Integer || val instanceof Long) return String.valueOf(val);
        if (val instanceof Number) {
            double d = ((Number) val).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) return "null";
            return String.valueOf(d);
        }
        if (val instanceof Character || val instanceof String) return escJson(String.valueOf(val));
        if (val.getClass().isArray()) {
            int n = Array.getLength(val);
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < n; i++) {
                if (i > 0) sb.append(',');
                sb.append(toJson(Array.get(val, i), null));
            }
            sb.append(']');
            return sb.toString();
        }
        if (val instanceof Collection<?>) {
            StringBuilder sb = new StringBuilder("[");
            boolean first = true;
            for (Object item : (Collection<?>) val) {
                if (!first) sb.append(',');
                first = false;
                sb.append(toJson(item, null));
            }
            sb.append(']');
            return sb.toString();
        }
        return escJson(String.valueOf(val));
    }

    private static Object runSingleCase(
        String execMode,
        String clsName,
        String methodName,
        String retHint,
        Map<String, String> argHints,
        List<String> argNames,
        List<Object> rawArgs,
        Map<String, Object> fullInput
    ) throws Throwable {
        try {
            if ("class_ops".equals(execMode)) {
                Class<?> cls = resolveClass(clsName);
                List<?> ops = (List<?>) fullInput.get("ops");
                List<?> argsList = (List<?>) fullInput.get("args");
                List<?> ctorRaw = (List<?>) argsList.get(0);
                Constructor<?> chosenCtor = null;
                for (Constructor<?> c : cls.getDeclaredConstructors()) {
                    if (c.getParameterCount() == ctorRaw.size()) {
                        chosenCtor = c;
                        break;
                    }
                }
                if (chosenCtor == null) throw new NoSuchMethodException("Constructor not found for " + clsName);
                chosenCtor.setAccessible(true);
                Class<?>[] cp = chosenCtor.getParameterTypes();
                Type[] cg = chosenCtor.getGenericParameterTypes();
                Object[] cArgs = new Object[cp.length];
                for (int i = 0; i < cp.length; i++) {
                    cArgs[i] = adaptArg(ctorRaw.get(i), cp[i], cg[i], null);
                }
                Object inst = chosenCtor.newInstance(cArgs);
                List<Object> out = new ArrayList<>();
                out.add(null);
                for (int step = 1; step < ops.size(); step++) {
                    String opName = String.valueOf(ops.get(step));
                    List<?> callRaw = (List<?>) argsList.get(step);
                    Method m = null;
                    for (Method cand : cls.getDeclaredMethods()) {
                        if (cand.getName().equals(opName) && cand.getParameterCount() == callRaw.size()) {
                            m = cand;
                            break;
                        }
                    }
                    if (m == null) throw new NoSuchMethodException(clsName + "." + opName);
                    m.setAccessible(true);
                    Class<?>[] mp = m.getParameterTypes();
                    Type[] mg = m.getGenericParameterTypes();
                    Object[] mArgs = new Object[mp.length];
                    for (int j = 0; j < mp.length; j++) {
                        mArgs[j] = adaptArg(callRaw.get(j), mp[j], mg[j], null);
                    }
                    Object r = m.invoke(inst, mArgs);
                    out.add(m.getReturnType() == void.class ? null : r);
                }
                return out;
            }
            if ("codec_strings".equals(execMode)) {
                Class<?> cls = resolveClass(clsName);
                Constructor<?> ctor = cls.getDeclaredConstructor();
                ctor.setAccessible(true);
                Object codec = ctor.newInstance();
                Method enc = null, dec = null;
                for (Method m : cls.getDeclaredMethods()) {
                    if ("encode".equals(m.getName())) enc = m;
                    if ("decode".equals(m.getName())) dec = m;
                }
                enc.setAccessible(true);
                dec.setAccessible(true);
                Object arg0 = adaptArg(fullInput.get("strs"), enc.getParameterTypes()[0], enc.getGenericParameterTypes()[0], null);
                Object encoded = enc.invoke(codec, arg0);
                return dec.invoke(codec, encoded);
            }
            if ("codec_tree".equals(execMode)) {
                Class<?> cls = resolveClass(clsName);
                Constructor<?> ctor = cls.getDeclaredConstructor();
                ctor.setAccessible(true);
                Object codec = ctor.newInstance();
                Method ser = null, des = null;
                for (Method m : cls.getDeclaredMethods()) {
                    if ("serialize".equals(m.getName())) ser = m;
                    if ("deserialize".equals(m.getName())) des = m;
                }
                ser.setAccessible(true);
                des.setAccessible(true);
                TreeNode tree = (TreeNode) adaptArg(fullInput.get("root"), TreeNode.class, TreeNode.class, "TreeNode");
                Object s = ser.invoke(codec, tree);
                return des.invoke(codec, s);
            }
            Class<?> solCls = Class.forName("Solution");
            Constructor<?> sCtor = solCls.getDeclaredConstructor();
            sCtor.setAccessible(true);
            Object sol = sCtor.newInstance();

            if ("list_cycle".equals(execMode)) {
                List<?> vals = (List<?>) fullInput.get("values");
                int pos = toInt(fullInput.get("pos"));
                ListNode[] nodes = new ListNode[vals.size()];
                for (int i = 0; i < vals.size(); i++) nodes[i] = new ListNode(toInt(vals.get(i)));
                for (int i = 0; i < vals.size() - 1; i++) nodes[i].next = nodes[i + 1];
                if (vals.size() > 0 && pos >= 0 && pos < vals.size()) nodes[vals.size() - 1].next = nodes[pos];
                Method m = solCls.getDeclaredMethod(methodName, ListNode.class);
                m.setAccessible(true);
                return m.invoke(sol, vals.size() > 0 ? nodes[0] : null);
            }
            if ("bst_lca".equals(execMode)) {
                TreeNode root = (TreeNode) adaptArg(fullInput.get("root"), TreeNode.class, TreeNode.class, "TreeNode");
                TreeNode p = findBst(root, toInt(fullInput.get("p")));
                TreeNode q = findBst(root, toInt(fullInput.get("q")));
                Method m = solCls.getDeclaredMethod(methodName, TreeNode.class, TreeNode.class, TreeNode.class);
                m.setAccessible(true);
                TreeNode ans = (TreeNode) m.invoke(sol, root, p, q);
                return ans == null ? null : ans.val;
            }

            Method targetM = null;
            for (Method cand : solCls.getDeclaredMethods()) {
                if (cand.getName().equals(methodName) && cand.getParameterCount() == rawArgs.size()) {
                    targetM = cand;
                    break;
                }
            }
            if (targetM == null) throw new NoSuchMethodException("Solution." + methodName);
            targetM.setAccessible(true);
            Class<?>[] pt = targetM.getParameterTypes();
            Type[] gt = targetM.getGenericParameterTypes();
            Object[] callArgs = new Object[pt.length];
            for (int i = 0; i < pt.length; i++) {
                String hint = argHints.get(argNames.get(i));
                callArgs[i] = adaptArg(rawArgs.get(i), pt[i], gt[i], hint);
            }
            Object ret = targetM.invoke(sol, callArgs);
            if ("InPlaceHead".equals(retHint)) return callArgs[0];
            if ("InPlaceArg0".equals(retHint)) return callArgs[0];
            return ret;
        } catch (InvocationTargetException ite) {
            throw ite.getTargetException();
        }
    }

    public static void main(String[] args) {
__CASE_CALLS__
    }
}
'''


def run_java_cases_sandboxed(
    prob_dir: Optional[Path],
    meta: Dict[str, Any],
    spec: Optional[Dict[str, Any]] = None,
    code_text: Optional[str] = None,
    timeout_s: float = 6.0,
) -> Dict[str, Any]:
    """Compile and execute Solution.java against structured test cases in an isolated temp directory."""
    java_src = code_text
    if java_src is None and prob_dir is not None and (prob_dir / "Solution.java").exists():
        java_src = (prob_dir / "Solution.java").read_text(encoding="utf-8")
    java_src = java_src or ""

    cases = meta.get("cases", [])
    exec_mode = meta.get("execMode") or (spec or {}).get("execMode", "solution_method")
    cls_name = meta.get("className") or (spec or {}).get("className", "Solution")
    method_name = meta.get("methodName") or (spec or {}).get("method", "")
    compare_mode = meta.get("compareMode") or (spec or {}).get("compareMode", "exact")
    arg_types = meta.get("argTypes") or (spec or {}).get("argTypes", {})
    ret_type = meta.get("returnType") or (spec or {}).get("returnType") or ""
    target_time = meta.get("timeComplexity") or (spec or {}).get("time", "O(N)")

    hint_entries = " ".join(f'argHints.put("{k}", "{v}");' for k, v in arg_types.items())
    case_blocks: List[str] = [
        "        Map<String, String> argHints = new HashMap<>();",
        f"        {hint_entries}",
    ]
    for idx, c in enumerate(cases):
        inp = c.get("input", {})
        keys_expr = ", ".join(f'"{k}"' for k in inp.keys())
        vals_expr = ", ".join(_py_val_to_java_expr(v) for v in inp.values())
        full_expr = _py_val_to_java_expr(inp)
        case_blocks.append(
            f"""        {{
            long t0 = System.nanoTime();
            try {{
                List<String> aNames = Arrays.asList({keys_expr});
                List<Object> rArgs = Arrays.asList({vals_expr});
                @SuppressWarnings("unchecked")
                Map<String, Object> fIn = (Map<String, Object>) ({full_expr});
                Object actual = runSingleCase("{exec_mode}", "{cls_name}", "{method_name}", "{ret_type}", argHints, aNames, rArgs, fIn);
                double ms = Math.round(((System.nanoTime() - t0) / 1_000_000.0) * 100.0) / 100.0;
                System.out.println("CASE_OK\\t{idx}\\t" + ms + "\\t" + toJson(actual, "{ret_type}"));
            }} catch (Throwable err) {{
                double ms = Math.round(((System.nanoTime() - t0) / 1_000_000.0) * 100.0) / 100.0;
                String msg = err.getClass().getSimpleName() + ": " + (err.getMessage() == null ? "" : err.getMessage());
                System.out.println("CASE_ERR\\t{idx}\\t" + ms + "\\t" + escJson(msg));
            }}
        }}"""
        )

    harness_code = _JAVA_HARNESS_TEMPLATE.replace("__CASE_CALLS__", "\n".join(case_blocks))
    tmp_dir = Path(tempfile.mkdtemp(prefix="hub_java_coach_"))
    t_total0 = time.perf_counter()
    try:
        (tmp_dir / "Solution.java").write_text(java_src, encoding="utf-8")
        (tmp_dir / "CoachJavaHarness.java").write_text(harness_code, encoding="utf-8")

        cp = f"{tmp_dir}:{DSA_ROOT}"
        util_sources = [str(p) for p in sorted((DSA_ROOT / "utils").glob("*.java"))]
        comp = subprocess.run(
            ["javac", "-cp", cp, "-d", str(tmp_dir), str(tmp_dir / "Solution.java"), str(tmp_dir / "CoachJavaHarness.java")] + util_sources,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s,
        )
        if comp.returncode != 0:
            elapsed = round((time.perf_counter() - t_total0) * 1000.0, 2)
            err_txt = comp.stderr.strip() or comp.stdout.strip()
            coach = analyze_java_code_coach(
                java_src, 0, len(cases), target_time=target_time, duration_ms=elapsed, comp_err=err_txt
            )
            return {
                "status": "COMPILATION_ERROR",
                "durationMs": elapsed,
                "cases": [
                    {
                        "id": c.get("id") or f"case-{i+1}",
                        "label": c.get("label") or f"Case {i+1}",
                        "passed": False,
                        "input": c.get("input", {}),
                        "expected": c.get("expected"),
                        "actual": f"CompileError: {err_txt.splitlines()[0] if err_txt else 'javac failed'}",
                        "durationMs": 0.0,
                    }
                    for i, c in enumerate(cases)
                ],
                "codeCoach": coach,
                "output": err_txt,
            }

        try:
            run_p = subprocess.run(
                ["java", "-cp", str(tmp_dir), "CoachJavaHarness"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            elapsed = round((time.perf_counter() - t_total0) * 1000.0, 2)
            coach = analyze_java_code_coach(java_src, 0, len(cases), target_time=target_time, timed_out=True)
            return {
                "status": "TIMEOUT",
                "durationMs": elapsed,
                "cases": [
                    {
                        "id": c.get("id") or f"case-{i+1}",
                        "label": c.get("label") or f"Case {i+1}",
                        "passed": False,
                        "input": c.get("input", {}),
                        "expected": c.get("expected"),
                        "actual": f"TimeoutError: Exceeded {timeout_s:.0f}s",
                        "durationMs": elapsed,
                    }
                    for i, c in enumerate(cases)
                ],
                "codeCoach": coach,
            }

        elapsed = round((time.perf_counter() - t_total0) * 1000.0, 2)
        by_idx: Dict[int, Dict[str, Any]] = {}
        for ln in run_p.stdout.splitlines():
            parts = ln.split("\t", 3)
            if len(parts) == 4 and parts[0] in ("CASE_OK", "CASE_ERR"):
                idx = int(parts[1])
                dt_ms = float(parts[2])
                val = json.loads(parts[3])
                by_idx[idx] = {"ok": parts[0] == "CASE_OK", "durationMs": dt_ms, "val": val}

        results = []
        all_ok = True
        for i, c in enumerate(cases):
            expected = c.get("expected")
            rec = by_idx.get(i)
            if not rec:
                all_ok = False
                results.append({
                    "id": c.get("id") or f"case-{i+1}",
                    "label": c.get("label") or f"Case {i+1}",
                    "passed": False,
                    "input": c.get("input", {}),
                    "expected": expected,
                    "actual": run_p.stderr.strip() or "No output captured",
                    "durationMs": 0.0,
                })
                continue
            if not rec["ok"]:
                all_ok = False
                results.append({
                    "id": c.get("id") or f"case-{i+1}",
                    "label": c.get("label") or f"Case {i+1}",
                    "passed": False,
                    "input": c.get("input", {}),
                    "expected": expected,
                    "actual": rec["val"],
                    "durationMs": rec["durationMs"],
                })
            else:
                passed = match_case_output(rec["val"], expected, compare_mode)
                if not passed:
                    all_ok = False
                results.append({
                    "id": c.get("id") or f"case-{i+1}",
                    "label": c.get("label") or f"Case {i+1}",
                    "passed": bool(passed),
                    "input": c.get("input", {}),
                    "expected": expected,
                    "actual": rec["val"],
                    "durationMs": rec["durationMs"],
                })

        passed_cnt = sum(1 for r in results if r["passed"])
        coach = analyze_java_code_coach(
            java_src, passed_cnt, len(results), target_time=target_time, duration_ms=elapsed
        )
        return {
            "status": "PASSED" if (all_ok and len(results) > 0) else "FAILED",
            "durationMs": elapsed,
            "cases": results,
            "codeCoach": coach,
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_python_cases_sandboxed(
    py_file: Optional[Path],
    meta: Dict[str, Any],
    spec: Optional[Dict[str, Any]] = None,
    code_text: Optional[str] = None,
    mode: str = "dsa",
    fn_name: str = "",
    timeout_s: float = 4.0,
) -> Dict[str, Any]:
    """Execute Python cases in an isolated subprocess with strict timeout protection."""
    payload = {
        "mode": mode,
        "filePath": str(py_file) if py_file else None,
        "codeText": code_text,
        "fnName": fn_name,
        "methodName": meta.get("methodName") or (spec or {}).get("method", ""),
        "className": meta.get("className") or (spec or {}).get("className", "Solution"),
        "execMode": meta.get("execMode") or (spec or {}).get("execMode", "solution_method"),
        "compareMode": meta.get("compareMode") or (spec or {}).get("compareMode", "exact"),
        "argTypes": meta.get("argTypes") or (spec or {}).get("argTypes", {}),
        "returnType": meta.get("returnType") or (spec or {}).get("returnType"),
        "cases": meta.get("cases", []),
        "scalingProbe": _detect_scaling_probe(spec),
    }

    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{DSA_ROOT}:{DSA_ROOT / 'utils'}:{REPO_ROOT}:{existing_pp}"

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        tf.write(json.dumps(payload))
        payload_path = tf.name

    t0 = time.perf_counter()
    timed_out = False
    raw_out = ""
    raw_err = ""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _PYTHON_RUNNER_SCRIPT, payload_path],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s,
            env=env,
        )
        raw_out = proc.stdout.strip()
        raw_err = proc.stderr.strip()
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        try:
            os.unlink(payload_path)
        except OSError:
            pass

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    disk_or_text = code_text if code_text is not None else (
        py_file.read_text(encoding="utf-8") if py_file and py_file.exists() else ""
    )

    if timed_out:
        coach = analyze_python_code_coach(
            disk_or_text, 0, len(payload["cases"]),
            target_time=meta.get("timeComplexity", "O(N)"),
            timed_out=True,
            duration_ms=elapsed_ms,
        )
        timeout_cases = [
            {
                "id": c.get("id") or f"case-{i+1}",
                "label": c.get("label") or f"Case {i+1}",
                "passed": False,
                "input": c.get("input", {}),
                "expected": c.get("expected"),
                "actual": f"TimeoutError: Exceeded {timeout_s:.0f}s (infinite loop?)",
                "durationMs": elapsed_ms,
            }
            for i, c in enumerate(payload["cases"])
        ]
        return {
            "status": "TIMEOUT",
            "durationMs": elapsed_ms,
            "cases": timeout_cases,
            "codeCoach": coach,
        }

    parsed: Dict[str, Any] = {}
    if raw_out:
        try:
            parsed = json.loads(raw_out.splitlines()[-1])
        except Exception:
            parsed = {}

    if not parsed or "cases" not in parsed:
        err_msg = raw_err or raw_out or "Execution failed"
        err_cases = [
            {
                "id": c.get("id") or f"case-{i+1}",
                "label": c.get("label") or f"Case {i+1}",
                "passed": False,
                "input": c.get("input", {}),
                "expected": c.get("expected"),
                "actual": err_msg.splitlines()[-1],
                "durationMs": elapsed_ms,
            }
            for i, c in enumerate(payload["cases"])
        ]
        coach = analyze_python_code_coach(
            disk_or_text, 0, len(payload["cases"]),
            target_time=meta.get("timeComplexity", "O(N)"),
            duration_ms=elapsed_ms,
        )
        return {
            "status": "FAILED",
            "durationMs": elapsed_ms,
            "cases": err_cases,
            "codeCoach": coach,
            "output": err_msg,
        }

    cases_res = parsed["cases"]
    passed_cnt = sum(1 for c in cases_res if c.get("passed"))
    coach = analyze_python_code_coach(
        disk_or_text,
        passed_cnt,
        len(cases_res),
        target_time=meta.get("timeComplexity", "O(N)"),
        scaling_ratio=parsed.get("scalingRatio"),
        duration_ms=elapsed_ms,
    )
    return {
        "status": parsed["status"],
        "durationMs": elapsed_ms,
        "cases": cases_res,
        "codeCoach": coach,
    }
