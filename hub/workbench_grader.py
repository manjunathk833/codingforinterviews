#!/usr/bin/env python3
"""
Multi-File & Blank-Canvas Architecture Workbench Grader (Wave 2 Option B).

- Supports all 17 Workbench Builds:
  - 4-Layer Multi-File `AeroCart` Quality Capstone (`frameworks/aerocart-quality-suite/`)
  - 13 Blank-Canvas SDET & Framework Architecture Labs (`frameworks/.../workspace.py`)
- Executes 4 isolated black-box checkpoints per challenge in a 4.0s subprocess.
- Computes 0-100 AST Architecture Score (strictly gated at 0/100 when 0 checkpoints pass):
  - Checkpoints (60 pts): 15 pts per passing black-box checkpoint
  - Contract & Type Discipline (20 pts): required classes/functions + type annotations
  - Architectural Cleanliness (20 pts): flat control flow, zero `time.sleep(>0.2)` anti-patterns,
    zero mutable default arguments, zero bare `except:` blocks
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_PATH = Path(__file__).resolve().parent / "data" / "workbench_specs.json"

_CACHE: Optional[List[Dict[str, Any]]] = None


def _load_challenges() -> List[Dict[str, Any]]:
    global _CACHE
    if _CACHE is None:
        raw = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
        _CACHE = raw["challenges"]
    return _CACHE


def list_challenges() -> List[Dict[str, Any]]:
    items = []
    for ch in _load_challenges():
        ws_path = REPO_ROOT / ch["workspacePath"]
        exists = ws_path.exists()
        content = ws_path.read_text(encoding="utf-8") if exists else ch["starterPy"]
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        items.append({
            "id": ch["id"],
            "order": ch["order"],
            "title": ch["title"],
            "category": ch["category"],
            "group": ch["group"],
            "stack": ch["stack"],
            "folderPath": ch["folderPath"],
            "workspacePath": ch["workspacePath"],
            "absWorkspacePath": str(ws_path),
            "vscodeUri": f"vscode://file/{ws_path}",
            "relatedChapter": ch["relatedChapter"],
            "roadmapItemId": ch.get("roadmapItemId"),
            "prompt": ch["prompt"],
            "invariant": ch["invariant"],
            "contractSymbols": ch["contractSymbols"],
            "outlineSteps": ch["outlineSteps"],
            "checkpointLabels": [
                {"id": cp["id"], "title": cp["title"], "description": cp["description"]}
                for cp in ch["checkpoints"]
            ],
            "sha256": sha,
            "code": content,
        })
    return items


def get_challenge(challenge_id: str) -> Optional[Dict[str, Any]]:
    cid = str(challenge_id or "").strip()
    for ch in _load_challenges():
        if ch["id"] == cid:
            return ch
    return None


def reset_challenge_workspace(challenge_id: str) -> Optional[Dict[str, Any]]:
    ch = get_challenge(challenge_id)
    if not ch:
        return None
    ws_path = REPO_ROOT / ch["workspacePath"]
    ws_path.parent.mkdir(parents=True, exist_ok=True)
    ws_path.write_text(ch["starterPy"], encoding="utf-8")
    sha = hashlib.sha256(ch["starterPy"].encode("utf-8")).hexdigest()
    return {
        "id": ch["id"],
        "workspacePath": ch["workspacePath"],
        "code": ch["starterPy"],
        "sha256": sha,
    }


_SUBPROCESS_HARNESS = r'''
import importlib.util, json, sys, time
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
ws_file = payload["workspaceFile"]
code_override = payload.get("codeOverride")
checkpoints = payload["checkpoints"]

mod_ns = {"__name__": "user_workbench_module", "__file__": ws_file}
if code_override is not None:
    exec(compile(code_override, ws_file, "exec"), mod_ns)
else:
    src = Path(ws_file).read_text(encoding="utf-8")
    exec(compile(src, ws_file, "exec"), mod_ns)

out = []
all_ok = True
for cp in checkpoints:
    t0 = time.perf_counter()
    probe_ns = {"mod": type("ModProxy", (), mod_ns), "ns": mod_ns}
    try:
        exec(compile(cp["probeCode"], f"<{cp['id']}>", "exec"), probe_ns)
        detail = str(probe_ns.get("RESULT_DETAIL", "Passed deterministic verification"))
        dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        out.append({
            "id": cp["id"],
            "title": cp["title"],
            "description": cp["description"],
            "passed": True,
            "detail": detail,
            "durationMs": dt_ms,
        })
    except Exception as exc:
        all_ok = False
        dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        out.append({
            "id": cp["id"],
            "title": cp["title"],
            "description": cp["description"],
            "passed": False,
            "detail": f"{type(exc).__name__}: {exc}",
            "durationMs": dt_ms,
        })

print(json.dumps({"status": "PASSED" if all_ok else "FAILED", "checkpoints": out}))
'''


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    branch = (ast.For, ast.While, ast.If, ast.Try, ast.With)
    nd = depth + (1 if isinstance(node, branch) else 0)
    mx = nd
    for ch in ast.iter_child_nodes(node):
        mx = max(mx, _max_nesting(ch, nd))
    return mx


def analyze_architecture_ast(
    code_text: str,
    required_symbols: List[str],
    passed_count: int,
    total_count: int,
    timed_out: bool = False,
) -> Dict[str, Any]:
    """Compute 0-100 AST Architecture Reviewer score strictly gated at 0/100 when 0 checkpoints pass."""
    if timed_out:
        return {
            "score": 0,
            "checkpointPts": 0,
            "contractPts": 0,
            "cleanlinessPts": 0,
            "verdict": "Timed Out (>4s)",
            "tips": ["Execution exceeded 4.0s — check polling deadlines or thread joins."],
        }

    try:
        tree = ast.parse(code_text)
    except SyntaxError as syn:
        return {
            "score": 0,
            "checkpointPts": 0,
            "contractPts": 0,
            "cleanlinessPts": 0,
            "verdict": f"Syntax Error (Line {syn.lineno})",
            "tips": [f"Fix Python syntax near line {syn.lineno}: {syn.msg}."],
        }

    if passed_count == 0:
        has_not_impl = "NotImplementedError" in code_text
        return {
            "score": 0,
            "checkpointPts": 0,
            "contractPts": 0,
            "cleanlinessPts": 0,
            "verdict": "Unimplemented Contract" if has_not_impl else "0 Checkpoints Passing",
            "tips": [
                "Blank contract raises NotImplementedError. Click `⚡ 3-Step Architecture Outline` or open in VS Code to implement Checkpoint 1 first!"
                if has_not_impl else
                "0/4 checkpoints passed. Inspect Checkpoint 1's failure message below and fix the contract behavior."
            ],
        }

    total_safe = max(1, total_count)
    cp_pts = round(60.0 * passed_count / total_safe)

    defined_names = {
        n.name for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    present_syms = sum(1 for sym in required_symbols if sym.split(".")[0] in defined_names)
    sym_ratio = present_syms / max(1, len(required_symbols))

    fn_nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    typed_fns = sum(
        1 for fn in fn_nodes
        if fn.returns is not None or any(a.annotation is not None for a in fn.args.args if a.arg != "self")
    )
    type_ratio = (typed_fns / len(fn_nodes)) if fn_nodes else 1.0
    contract_pts = round(12.0 * sym_ratio + 8.0 * min(1.0, type_ratio + 0.25))

    clean_pts = 20
    tips: List[str] = []
    nesting = _max_nesting(tree)
    if nesting > 4:
        clean_pts -= 6
        tips.append(f"Deep control-flow nesting ({nesting} levels). Extract helper methods or early guard clauses.")

    for n in ast.walk(tree):
        if isinstance(n, ast.ExceptHandler) and n.type is None:
            clean_pts -= 6
            tips.append("Avoid bare `except:` blocks in test infrastructure — catch explicit fault classes.")
            break

    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            if any(isinstance(d, (ast.List, ast.Dict, ast.Set)) for d in n.args.defaults):
                clean_pts -= 6
                tips.append("Avoid mutable default arguments (`[]` / `{}`) across parallel workers.")
                break

    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "sleep":
            if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, (int, float)):
                if float(n.args[0].value) >= 0.25:
                    clean_pts -= 6
                    tips.append("Hardcoded long `time.sleep()` spotted — prefer deadline-bounded polling intervals.")
                    break

    clean_pts = max(0, min(20, clean_pts))
    total_score = int(cp_pts + contract_pts + clean_pts)

    if passed_count == total_count and total_score >= 92:
        verdict = "Staff Architecture Verified"
        if not tips:
            tips.append("All 4 black-box checkpoints green with typed contracts and deterministic concurrency hygiene!")
    elif passed_count == total_count:
        verdict = "Checkpoints Green — Polish Types/Cleanliness"
    else:
        verdict = f"{passed_count}/{total_count} Checkpoints Passing"
        if not tips:
            tips.append("Inspect the first red checkpoint card below and implement its contract requirement.")

    return {
        "score": total_score,
        "checkpointPts": int(cp_pts),
        "contractPts": int(contract_pts),
        "cleanlinessPts": int(clean_pts),
        "verdict": verdict,
        "tips": tips,
    }


def run_challenge(
    challenge_id: str,
    code_override: Optional[str] = None,
    persist_to_disk: bool = False,
    timeout_s: float = 4.0,
) -> Optional[Dict[str, Any]]:
    ch = get_challenge(challenge_id)
    if not ch:
        return None

    ws_path = REPO_ROOT / ch["workspacePath"]
    ws_path.parent.mkdir(parents=True, exist_ok=True)
    if persist_to_disk and code_override is not None:
        ws_path.write_text(code_override, encoding="utf-8")
    elif not ws_path.exists():
        ws_path.write_text(ch["starterPy"], encoding="utf-8")

    code_for_ast = code_override if code_override is not None else ws_path.read_text(encoding="utf-8")

    payload = {
        "workspaceFile": str(ws_path),
        "codeOverride": code_override,
        "checkpoints": ch["checkpoints"],
    }
    env = os.environ.copy()
    suite_dir = REPO_ROOT / "frameworks" / "aerocart-quality-suite"
    lab_dir = ws_path.parent
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{lab_dir}:{suite_dir}:{REPO_ROOT}:{existing_pp}"

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        tf.write(json.dumps(payload))
        p_path = tf.name

    t0 = time.perf_counter()
    timed_out = False
    raw_out = ""
    raw_err = ""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _SUBPROCESS_HARNESS, p_path],
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
            os.unlink(p_path)
        except OSError:
            pass

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    if timed_out:
        review = analyze_architecture_ast(
            code_for_ast, ch["contractSymbols"], 0, len(ch["checkpoints"]), timed_out=True
        )
        return {
            "id": ch["id"],
            "status": "TIMEOUT",
            "durationMs": elapsed_ms,
            "checkpoints": [
                {
                    "id": cp["id"],
                    "title": cp["title"],
                    "description": cp["description"],
                    "passed": False,
                    "detail": f"TimeoutError: Exceeded {timeout_s:.0f}s limit",
                    "durationMs": elapsed_ms,
                }
                for cp in ch["checkpoints"]
            ],
            "architectureReview": review,
        }

    parsed: Dict[str, Any] = {}
    if raw_out:
        try:
            parsed = json.loads(raw_out.splitlines()[-1])
        except Exception:
            parsed = {}

    if not parsed or "checkpoints" not in parsed:
        err_line = (raw_err or raw_out or "Import/Execution error").splitlines()[-1]
        review = analyze_architecture_ast(code_for_ast, ch["contractSymbols"], 0, len(ch["checkpoints"]))
        return {
            "id": ch["id"],
            "status": "FAILED",
            "durationMs": elapsed_ms,
            "checkpoints": [
                {
                    "id": cp["id"],
                    "title": cp["title"],
                    "description": cp["description"],
                    "passed": False,
                    "detail": err_line,
                    "durationMs": elapsed_ms,
                }
                for cp in ch["checkpoints"]
            ],
            "architectureReview": review,
        }

    cp_list = parsed["checkpoints"]
    passed_cnt = sum(1 for cp in cp_list if cp.get("passed"))
    review = analyze_architecture_ast(code_for_ast, ch["contractSymbols"], passed_cnt, len(cp_list))
    sha = hashlib.sha256(ws_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()

    result: Dict[str, Any] = {
        "id": ch["id"],
        "status": parsed["status"],
        "durationMs": elapsed_ms,
        "passedCount": passed_cnt,
        "totalCount": len(cp_list),
        "checkpoints": cp_list,
        "architectureReview": review,
        "sha256": sha,
    }
    if passed_cnt == len(cp_list) and len(cp_list) > 0:
        result["referenceSolution"] = ch["referencePy"]
    return result
