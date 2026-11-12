#!/usr/bin/env python3
"""
100% Local Subprocess Test Runner & Instant 0-100 Code Coach for The Hub of Learning.

- Zero external AI API required.
- Executes user Python code inside an isolated subprocess with a strict 4.0s timeout guard
  (so infinite while loops fail gracefully without freezing hub/server.py).
- Supports all 128 DSA problem shapes (arrays, matrices, ListNode, TreeNode, RandomNode,
  GraphNode, Codec, OOP classes via `class_ops`, cycle lists, BST LCA) and all 12 Warmup Drills.
- Computes 0-100 Code Coach Score:
  - Correctness (50 pts): structured case pass ratio
  - Speed (25 pts): runtime + empirical 8x scaling probe on O(N)/O(N log N) problems
  - Clean Code (25 pts): AST control-flow nesting, guard clauses, mutable defaults, clarity
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DSA_ROOT = REPO_ROOT / "dsa"

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

# Load target module from code_text or disk file
mod_ns = {}
if code_text is not None:
    exec(compile(code_text, "<warmup>", "exec"), mod_ns)
else:
    spec = importlib.util.spec_from_file_location("user_submission", file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod_ns = mod.__dict__

# Ensure helpers are present if code omitted imports
def _normalize(val, cmode):
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
        norm_items = [_normalize(x, "unordered") if isinstance(x, list) else x for x in val]
        try:
            return sorted(norm_items, key=lambda item: json.dumps(item, sort_keys=True))
        except Exception:
            return norm_items
    if cmode == "anagram_groups" and isinstance(val, list):
        return sorted([sorted(g) if isinstance(g, list) else g for g in val])
    return val

def _match_case(actual, expected, cmode):
    if cmode == "float_1e5":
        if isinstance(actual, list) and isinstance(expected, list):
            return len(actual) == len(expected) and all(_match_case(a, e, "float_1e5") for a, e in zip(actual, expected))
        if actual is None or expected is None:
            return actual is expected
        try:
            return abs(float(actual) - float(expected)) <= 1e-5
        except Exception:
            return False
    if cmode == "any_of" and isinstance(expected, list):
        return actual in expected
    return _normalize(actual, cmode) == _normalize(expected, cmode)

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
        passed = _match_case(actual, expected, compare_mode)
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
        def _run_bench(n):
            if kind == "single_int_array":
                arr = list(range(n))
                t_a = time.perf_counter()
                fn(arr)
                return time.perf_counter() - t_a
            if kind == "two_sum_array":
                arr = list(range(n))
                tgt = (n - 2) + (n - 1)
                t_a = time.perf_counter()
                fn(arr, tgt)
                return time.perf_counter() - t_a
            if kind == "unique_str":
                s = "".join(chr(97 + (i % 26)) for i in range(n))
                t_a = time.perf_counter()
                fn(s)
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
    if not spec:
        return None
    slug = spec.get("slug", "")
    if slug == "two-sum":
        return {"kind": "two_sum_array"}
    if slug in (
        "contains-duplicate",
        "product-of-array-except-self",
        "longest-consecutive-sequence",
        "best-time-to-buy-and-sell-stock",
        "maximum-subarray",
        "house-robber",
        "single-number",
    ):
        return {"kind": "single_int_array"}
    if slug in ("longest-substring-without-repeating-characters",):
        return {"kind": "unique_str"}
    return None


def analyze_python_code_coach(
    code_text: str,
    passed_count: int,
    total_count: int,
    target_time: str = "O(N)",
    scaling_ratio: Optional[float] = None,
    timed_out: bool = False,
    duration_ms: float = 0.0,
) -> Dict[str, Any]:
    """Compute 0-100 Instant Code Coach scorecard & plain-English tips strictly locally via Python AST."""
    if timed_out:
        return {
            "score": 0,
            "correctnessPts": 0,
            "speedPts": 0,
            "cleanCodePts": 10,
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
        # Exclude `__main__` test runner block when scoring solution quality
        sol_section = code_text.split('if __name__ == "__main__"')[0]
        tree = ast.parse(sol_section)
        nesting = _max_ast_nesting(tree)
        loops = _max_loop_depth(tree)

        fn_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith("__")]
        if fn_defs:
            non_trivial = [
                stmt for fn in fn_defs for stmt in fn.body
                if not isinstance(stmt, (ast.Pass, ast.Expr))
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
            "cleanCodePts": 5,
            "verdict": f"Syntax Error (Line {syn.lineno})",
            "empiricalScaling": "Did not run",
            "nestingDepth": 0,
            "loopDepth": 0,
            "tips": [
                f"Fix the Python syntax issue near line {syn.lineno}: {syn.msg}.",
            ],
        }

    # Speed score (25 pts)
    speed_pts = 25
    scaling_label = f"Fast ({duration_ms:.1f}ms) · Target {target_time}"
    if passed_count == 0:
        speed_pts = 0 if is_pass_stub else 10
        scaling_label = "Waiting for passing tests"
    elif scaling_ratio is not None:
        if target_time in ("O(N)", "O(N log N)") and scaling_ratio > 24.0:
            speed_pts = 10
            scaling_label = f"Slowdown detected: {scaling_ratio:.1f}x slower for 8x input (~O(N²))"
            tips.append(
                f"Your code slowed down {scaling_ratio:.1f}x when the input grew 8x. Look for a hidden `in list` scan or nested loop and swap it for a `set()` or `dict`."
            )
        else:
            scaling_label = f"Matches {target_time} ({scaling_ratio:.1f}x on 8x input)"
    elif loops >= 2 and target_time in ("O(N)", "O(N) Time") and scaling_ratio is None:
        # Careful: only soft hint unless obviously quadratic and slow
        if duration_ms > 45.0:
            speed_pts = 14
            tips.append(f"Nested loop spotted on an {target_time} problem — check if a hash map or sliding window removes the inner loop.")

    # Clean Code score (25 pts)
    if is_pass_stub:
        style_pts = 8
        tips.append("Starter stub still has only `pass`. Click `⚡ Help Me Start` to insert the 3-step outline and write 2 lines under each step.")
    else:
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
    cli_res: Dict[str, Any],
    target_time: str = "O(N)",
) -> Dict[str, Any]:
    """Compute 0-100 Code Coach score for Java 17 submissions alongside CLI javac/java assertion output."""
    passed = cli_res.get("status") == "PASSED"
    comp_err = cli_res.get("status") == "COMPILATION_ERROR"
    timed_out = cli_res.get("status") == "TIMEOUT"
    duration_ms = float(cli_res.get("durationMs") or 0.0)

    if timed_out:
        return {
            "score": 0, "correctnessPts": 0, "speedPts": 0, "cleanCodePts": 10,
            "verdict": "Timed Out (>10s)",
            "empiricalScaling": "Java execution timed out",
            "tips": ["Java execution timed out — check loop termination conditions."],
        }
    if comp_err:
        msg = (cli_res.get("output") or "").splitlines()[:2]
        return {
            "score": 5, "correctnessPts": 0, "speedPts": 0, "cleanCodePts": 5,
            "verdict": "Java Compile Error",
            "empiricalScaling": "Did not compile",
            "tips": [f"Compiler message: {' '.join(msg)}"],
        }

    # Count max brace depth inside class body as proxy for nesting
    depth = 0
    max_depth = 0
    for ch in code_text:
        if ch == "{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == "}":
            depth = max(0, depth - 1)

    correctness_pts = 50 if passed else 10
    speed_pts = 25 if passed else 10
    clean_pts = 25
    tips: List[str] = []
    if max_depth > 5:
        clean_pts -= 5
        tips.append(f"Deep Java brace nesting ({max_depth} levels). Add early `return` checks to simplify control flow.")
    if passed and not tips:
        tips.append(f"Java 17 compiled & passed assertions in {duration_ms:.0f}ms. Great job typing strongly-typed Java!")
    elif not passed and not tips:
        tips.append("Check the assertion message below and trace your base cases.")

    return {
        "score": correctness_pts + speed_pts + max(0, clean_pts),
        "correctnessPts": correctness_pts,
        "speedPts": speed_pts,
        "cleanCodePts": max(0, clean_pts),
        "verdict": "Java Passing" if passed else "Java Assertion Failed",
        "empiricalScaling": f"Compiled + JVM executed ({duration_ms:.0f}ms · Target {target_time})",
        "tips": tips,
    }


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
