#!/usr/bin/env python3
"""
Antigravity Learning Hub — Unified Local Server, Filesystem Bridge & Visualization Engine.
Runs on http://127.0.0.1:8090 (or custom port via HUB_PORT / CLI argument).
"""

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Tuple, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hub import state_manager, storage, visualizer_engine

DEFAULT_PORT = int(os.environ.get("HUB_PORT", 8090))
STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"
PROTOTYPE_HTML = REPO_ROOT / "docs" / "prototypes" / "home-and-dsa-prototype.html"

ALLOWED_TOP_DIRS = {
    "dsa",
    "core-cs",
    "system-design",
    "ai-engineering",
    "frameworks",
    "mock-interviews",
    "knowledgebase",
}
ALLOWED_EXTENSIONS = {".py", ".java", ".md", ".json"}


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _resolve_safe_workspace_file(rel_path: str) -> Optional[Path]:
    """Resolve a workspace-relative path inside allowed curriculum directories, blocking traversal."""
    if not rel_path or not isinstance(rel_path, str):
        return None
    cleaned = rel_path.strip().lstrip("/")
    if not cleaned or ".." in Path(cleaned).parts:
        return None
    parts = Path(cleaned).parts
    if not parts or parts[0] not in ALLOWED_TOP_DIRS:
        return None
    try:
        resolved = (REPO_ROOT / cleaned).resolve()
        repo_resolved = REPO_ROOT.resolve()
        if not resolved.is_relative_to(repo_resolved):
            return None
        if resolved.suffix not in ALLOWED_EXTENSIONS:
            return None
        return resolved
    except Exception:
        return None


def read_workspace_file(rel_path: str) -> Tuple[int, Dict[str, Any]]:
    """Read a workspace source file and return its content + sha256 ETag."""
    target = _resolve_safe_workspace_file(rel_path)
    if target is None:
        return 403, {"error": "Forbidden: path outside allowed workspace directories"}
    if not target.exists() or not target.is_file():
        return 404, {"error": f"File not found: {rel_path}"}

    raw = target.read_bytes()
    sha = _compute_sha256(raw)
    stat = target.stat()
    return 200, {
        "path": str(target.relative_to(REPO_ROOT)),
        "content": raw.decode("utf-8", errors="replace"),
        "sha256": sha,
        "mtimeMs": int(stat.st_mtime * 1000),
    }


def write_workspace_file(
    rel_path: str,
    content: str,
    expected_sha256: Optional[str] = None
) -> Tuple[int, Dict[str, Any]]:
    """
    Atomically write a workspace file with optimistic locking (sha256 If-Match)
    and permission preservation (shutil.copymode + os.replace).
    """
    target = _resolve_safe_workspace_file(rel_path)
    if target is None:
        return 403, {"error": "Forbidden: path outside allowed workspace directories"}
    if not target.exists() or not target.is_file():
        return 404, {"error": f"File not found: {rel_path}"}

    current_bytes = target.read_bytes()
    current_sha = _compute_sha256(current_bytes)

    if expected_sha256:
        clean_expected = expected_sha256.strip().strip('"')
        if clean_expected and clean_expected != current_sha:
            return 412, {
                "error": "Conflict: file was modified externally on disk",
                "path": str(target.relative_to(REPO_ROOT)),
                "diskSha256": current_sha,
                "diskContent": current_bytes.decode("utf-8", errors="replace"),
            }

    new_bytes = content.encode("utf-8")
    fd, tmp_path = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(new_bytes)
            f.flush()
            os.fsync(f.fileno())
        shutil.copymode(str(target), tmp_path)
        os.replace(tmp_path, str(target))
    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return 500, {"error": f"Atomic write failed: {e}"}

    new_sha = _compute_sha256(new_bytes)
    stat = target.stat()
    return 200, {
        "status": "saved",
        "path": str(target.relative_to(REPO_ROOT)),
        "sha256": new_sha,
        "mtimeMs": int(stat.st_mtime * 1000),
    }


def _find_problem_dir(slug: str) -> Optional[Path]:
    """Find a problem or lab directory matching `slug` across curriculum folders."""
    if not slug or not re.match(r"^[a-zA-Z0-9_\-]+$", slug):
        return None
    search_roots = [
        REPO_ROOT / "dsa",
        REPO_ROOT / "core-cs",
        REPO_ROOT / "system-design",
        REPO_ROOT / "ai-engineering",
        REPO_ROOT / "frameworks",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        for dirpath, _, filenames in os.walk(root):
            if "/." in dirpath or "__pycache__" in dirpath:
                continue
            p = Path(dirpath)
            if p.name == slug or p.name.endswith(f"-{slug}"):
                if "solution.py" in filenames or "Solution.java" in filenames:
                    return p
    return None


def _normalize_output(val: Any, compare_mode: str) -> Any:
    if compare_mode == "sorted_int_array" and isinstance(val, (list, tuple)):
        try:
            return sorted(int(x) for x in val)
        except Exception:
            return val
    if compare_mode == "unordered_groups" and isinstance(val, (list, tuple)):
        try:
            norm_groups = [sorted(str(item) for item in grp) for grp in val]
            return sorted(norm_groups, key=lambda g: (len(g), g))
        except Exception:
            return val
    return val


def get_dsa_problem_bundle(slug: str) -> Tuple[int, Dict[str, Any]]:
    """Return full problem metadata, tests.json cases, Socratic hints, and live disk files."""
    prob_dir = _find_problem_dir(slug)
    if prob_dir is None:
        return 404, {"error": f"Problem directory not found for slug: {slug}"}

    tests_path = prob_dir / "tests.json"
    if tests_path.exists():
        meta = json.loads(tests_path.read_text(encoding="utf-8"))
    else:
        readme_text = (prob_dir / "README.md").read_text(encoding="utf-8") if (prob_dir / "README.md").exists() else ""
        meta = {
            "slug": prob_dir.name,
            "title": prob_dir.name.replace("-", " ").title(),
            "chapter": prob_dir.parent.name.replace("-", " ").title(),
            "difficulty": "Medium",
            "methodName": "",
            "compareMode": "exact",
            "timeComplexity": "O(N)",
            "spaceComplexity": "O(N)",
            "visualizerId": "dsa-group-anagrams",
            "prompt": readme_text[:500] or f"Solve {prob_dir.name} in both Python and Java.",
            "invariant": "Verify core invariants across boundary cases.",
            "hints": [
                {"tier": 1, "title": "Mental Model & Intuition", "content": "Identify the bottleneck in the brute-force approach."},
                {"tier": 2, "title": "Pattern Identification", "content": "Consider hash maps, two pointers, or frequency arrays."},
                {"tier": 3, "title": "Algorithmic Invariant", "content": "Maintain your data structure invariant at every loop step."},
                {"tier": 4, "title": "Edge Cases & Scaffolding", "content": "Check empty inputs, single elements, and duplicates."},
            ],
            "cases": [],
        }

    files_bundle = {}
    for lang_key, filename in (("python", "solution.py"), ("java", "Solution.java")):
        fpath = prob_dir / filename
        if fpath.exists():
            rel = str(fpath.relative_to(REPO_ROOT))
            _, fdata = read_workspace_file(rel)
            files_bundle[lang_key] = fdata

    for p in state_manager.get_dsa_overview().get("problems", []):
        if p.get("folderSlug") == prob_dir.name or p.get("slug") == prob_dir.name:
            meta["id"] = int(p["id"])
            meta["roadmapItemId"] = f"dsa-{int(p['id']):03d}"
            break

    return 200, {
        "problem": meta,
        "folderPath": str(prob_dir.relative_to(REPO_ROOT)),
        "files": files_bundle,
    }


def scaffold_dsa_problem(slug_or_id: str) -> Tuple[int, Dict[str, Any]]:
    """Scaffold a new DSA problem directory (`README.md`, `solution.py`, `Solution.java`, `tests.json`) if not yet on disk."""
    existing = _find_problem_dir(str(slug_or_id))
    if existing is not None:
        return get_dsa_problem_bundle(existing.name)

    dsa_overview = state_manager.get_dsa_overview()
    target_prob = None
    for p in dsa_overview["problems"]:
        if (
            str(p["id"]) == str(slug_or_id)
            or p["slug"] == str(slug_or_id).lower()
            or p["folderSlug"] == str(slug_or_id).lower()
        ):
            target_prob = p
            break

    if target_prob is None:
        return 404, {"error": f"Problem '{slug_or_id}' not found in MASTER_SHEET.md"}

    chapter_folder = target_prob["chapterFolder"]
    folder_slug = f"{target_prob['id']:03d}-{target_prob['slug']}"
    prob_dir = REPO_ROOT / "dsa" / chapter_folder / folder_slug
    prob_dir.mkdir(parents=True, exist_ok=True)

    # Convert slug to camelCase method name
    parts = target_prob["slug"].split("-")
    method_name = parts[0] + "".join(w.capitalize() for w in parts[1:]) if parts else "solve"

    readme_path = prob_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            f"# {target_prob['id']:03d}. {target_prob['title']}\n\n"
            f"- **Pattern**: {target_prob['pattern']}\n"
            f"- **Difficulty**: {target_prob['difficulty']}\n"
            f"- **LeetCode URL**: {target_prob['url']}\n"
            f"- **Core Invariant**: `{target_prob['diagramFormula']}`\n",
            encoding="utf-8",
        )

    py_path = prob_dir / "solution.py"
    if not py_path.exists():
        py_path.write_text(
            f'"""Problem: {target_prob["title"]}\n'
            f'Pattern: {target_prob["pattern"]}\n'
            f'Difficulty: {target_prob["difficulty"]}\n'
            f'"""\n'
            f"from typing import List, Optional\n\n\n"
            f"class Solution:\n"
            f"    def {method_name}(self, nums: List[int]) -> bool:\n"
            f"        # TODO: Implement {target_prob['title']} ({target_prob['diagramFormula']})\n"
            f"        return len(nums) != len(set(nums))\n\n\n"
            f'if __name__ == "__main__":\n'
            f"    sol = Solution()\n"
            f"    assert sol.{method_name}([1, 2, 3, 1]) is True\n"
            f"    assert sol.{method_name}([1, 2, 3, 4]) is False\n"
            f'    print("All Python test cases passed!")\n',
            encoding="utf-8",
        )
        os.chmod(py_path, 0o755)

    java_path = prob_dir / "Solution.java"
    if not java_path.exists():
        java_path.write_text(
            f"import java.util.*;\n\n"
            f"/**\n"
            f" * Problem: {target_prob['title']}\n"
            f" * Pattern: {target_prob['pattern']}\n"
            f" * Difficulty: {target_prob['difficulty']}\n"
            f" */\n"
            f"public class Solution {{\n"
            f"    public boolean {method_name}(int[] nums) {{\n"
            f"        Set<Integer> seen = new HashSet<>();\n"
            f"        for (int x : nums) {{\n"
            f"            if (!seen.add(x)) return true;\n"
            f"        }}\n"
            f"        return false;\n"
            f"    }}\n\n"
            f"    public static void main(String[] args) {{\n"
            f"        Solution sol = new Solution();\n"
            f"        assert sol.{method_name}(new int[]{{1, 2, 3, 1}}) == true;\n"
            f"        assert sol.{method_name}(new int[]{{1, 2, 3, 4}}) == false;\n"
            f'        System.out.println("All Java test cases passed!");\n'
            f"    }}\n"
            f"}}\n",
            encoding="utf-8",
        )

    tests_path = prob_dir / "tests.json"
    if not tests_path.exists():
        tests_meta = {
            "slug": folder_slug,
            "title": f"{target_prob['id']:03d}. {target_prob['title']}",
            "chapter": f"Ch {target_prob['chapterNumber']}: {target_prob['pattern']}",
            "difficulty": target_prob["difficulty"],
            "methodName": method_name,
            "compareMode": "exact",
            "timeComplexity": "O(N)",
            "spaceComplexity": "O(N)",
            "visualizerId": target_prob["visualizerId"],
            "prompt": f"Solve {target_prob['title']} ({target_prob['pattern']}) using the core invariant: {target_prob['diagramFormula']}.",
            "invariant": target_prob["diagramFormula"],
            "hints": [
                {"tier": 1, "title": "Mental Model & Intuition", "content": f"Apply the {target_prob['pattern']} mental model: {target_prob['diagramCaption']}."},
                {"tier": 2, "title": "Pattern Identification", "content": f"Core formula: {target_prob['diagramFormula']}."},
                {"tier": 3, "title": "Algorithmic Invariant", "content": "Maintain your data structure invariant at every iteration step."},
                {"tier": 4, "title": "Edge Cases & Scaffolding", "content": "Verify empty inputs, single elements, and duplicate values."},
            ],
            "cases": [
                {"id": "case-1", "label": "Case 1", "input": {"nums": [1, 2, 3, 1]}, "expected": True},
                {"id": "case-2", "label": "Case 2", "input": {"nums": [1, 2, 3, 4]}, "expected": False},
            ],
        }
        tests_path.write_text(json.dumps(tests_meta, indent=2) + "\n", encoding="utf-8")

    return get_dsa_problem_bundle(folder_slug)


def execute_problem_cases(slug: str, lang: str = "python") -> Dict[str, Any]:
    """
    Execute per-case tests from `tests.json` against the candidate's real disk files
    plus run `./run.sh test <slug> --lang <lang>` to verify CLI assertions.
    """
    prob_dir = _find_problem_dir(slug)
    if prob_dir is None:
        return {"status": "ERROR", "error": f"Unknown problem slug: {slug}", "cases": []}

    tests_path = prob_dir / "tests.json"
    cli_res = execute_test_target(prob_dir.name, lang if lang in ("python", "java", "all") else "all")

    if not tests_path.exists():
        return {
            "status": cli_res["status"],
            "slug": prob_dir.name,
            "lang": lang,
            "durationMs": cli_res["durationMs"],
            "output": cli_res["output"],
            "cases": [
                {
                    "id": "case-main",
                    "label": "CLI Assertions",
                    "passed": cli_res["status"] == "PASSED",
                    "input": {"target": prob_dir.name},
                    "expected": "Exit Code 0 (All assertions pass)",
                    "actual": cli_res["output"],
                    "durationMs": cli_res["durationMs"],
                }
            ],
        }

    meta = json.loads(tests_path.read_text(encoding="utf-8"))
    method_name = meta.get("methodName", "")
    compare_mode = meta.get("compareMode", "exact")
    cases_spec = meta.get("cases", [])

    # Evaluate structured cases using Python solution (and verify Java via CLI compilation + assertions)
    py_file = prob_dir / "solution.py"
    case_results = []
    all_cases_passed = (cli_res["status"] == "PASSED")

    if py_file.exists() and method_name:
        try:
            spec = importlib.util.spec_from_file_location(f"sol_{prob_dir.name}", str(py_file))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sol_instance = mod.Solution()
            fn = getattr(sol_instance, method_name)

            for c in cases_spec:
                t0 = time.perf_counter()
                inp = c.get("input", {})
                expected = c.get("expected")
                try:
                    # Copy mutable inputs so in-place mutations don't corrupt display
                    kwargs = json.loads(json.dumps(inp))
                    actual = fn(**kwargs)
                    dt_ms = round((time.perf_counter() - t0) * 1000, 2)
                    passed = (
                        _normalize_output(actual, compare_mode)
                        == _normalize_output(expected, compare_mode)
                    )
                    if lang == "java" and cli_res["status"] != "PASSED":
                        passed = False
                    if not passed:
                        all_cases_passed = False
                    case_results.append({
                        "id": c.get("id", "case"),
                        "label": c.get("label", "Case"),
                        "passed": passed,
                        "input": inp,
                        "expected": expected,
                        "actual": actual,
                        "durationMs": dt_ms,
                    })
                except Exception as exc:
                    all_cases_passed = False
                    case_results.append({
                        "id": c.get("id", "case"),
                        "label": c.get("label", "Case"),
                        "passed": False,
                        "input": inp,
                        "expected": expected,
                        "actual": f"Exception: {exc}",
                        "durationMs": 0.0,
                    })
        except Exception as exc:
            all_cases_passed = False
            case_results.append({
                "id": "case-load-error",
                "label": "Syntax / Import",
                "passed": False,
                "input": {},
                "expected": "Valid Python module",
                "actual": str(exc),
                "durationMs": 0.0,
            })

    return {
        "status": "PASSED" if (all_cases_passed and cli_res["status"] == "PASSED") else "FAILED",
        "slug": prob_dir.name,
        "lang": lang,
        "durationMs": cli_res["durationMs"],
        "output": cli_res["output"],
        "cases": case_results,
    }


def execute_test_target(target: str, lang: str = "all") -> dict:
    """Safely execute `./run.sh test <target> --lang <lang>` and return output."""
    if not target or not re.match(r"^[a-zA-Z0-9_\-/]+$", target):
        return {"status": "ERROR", "exitCode": 1, "output": "Invalid target slug.", "durationMs": 0}
    if lang not in ("all", "java", "python"):
        lang = "all"

    cmd = [sys.executable, str(REPO_ROOT / "tools" / "runner.py"), "test", target, "--lang", lang]
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=25
        )
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        raw_out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        clean_out = re.sub(r"\x1b\[[0-9;]*m", "", raw_out).strip()
        return {
            "status": "PASSED" if proc.returncode == 0 else "FAILED",
            "exitCode": proc.returncode,
            "target": target,
            "lang": lang,
            "durationMs": elapsed_ms,
            "output": clean_out
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "exitCode": 124,
            "target": target,
            "lang": lang,
            "durationMs": 25000,
            "output": "Execution timed out after 25s."
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "exitCode": 1,
            "target": target,
            "lang": lang,
            "durationMs": 0,
            "output": str(e)
        }


_LOCAL_ORIGIN_RE = re.compile(r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$")
_LOCAL_HOST_RE = re.compile(r"^(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$")


class LearningHubHandler(BaseHTTPRequestHandler):

    def _get_validated_origin(self) -> str:
        origin = (self.headers.get("Origin") or "").strip()
        if origin and _LOCAL_ORIGIN_RE.match(origin):
            return origin
        return ""

    def _validate_local_request(self) -> bool:
        """Block cross-origin CSRF requests and DNS rebinding attacks."""
        host = (self.headers.get("Host") or "").strip()
        if host and not _LOCAL_HOST_RE.match(host):
            self._send_json(403, {"error": "Forbidden: invalid Host header"})
            return False

        origin = (self.headers.get("Origin") or "").strip()
        if origin and not _LOCAL_ORIGIN_RE.match(origin):
            self._send_json(403, {"error": "Forbidden: cross-origin request blocked"})
            return False

        return True

    def _apply_cors_headers(self):
        valid_origin = self._get_validated_origin()
        if valid_origin:
            self.send_header("Access-Control-Allow-Origin", valid_origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, If-Match")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")

    def _send_json(self, status_code: int, payload: dict, extra_headers: dict = None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self._apply_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if not self._validate_local_request():
            return
        self.send_response(204)
        self._apply_cors_headers()
        self.end_headers()

    def do_GET(self):
        if not self._validate_local_request():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            if STATIC_INDEX.exists():
                html_bytes = STATIC_INDEX.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
            else:
                self._send_json(404, {"error": "Static UI index.html not found"})
            return

        if path == "/prototype":
            if PROTOTYPE_HTML.exists():
                html_bytes = PROTOTYPE_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
            else:
                self._send_json(404, {"error": "Prototype HTML not found"})
            return

        if path.startswith("/media/"):
            media_root = (REPO_ROOT / "media").resolve()
            rel_media = path[len("/media/") :].lstrip("/")
            target_file = (media_root / rel_media).resolve()
            if not str(target_file).startswith(str(media_root)) or not target_file.is_file():
                self._send_json(404, {"error": "Media asset not found"})
                return
            ext = target_file.suffix.lower()
            mime_map = {
                ".mp4": "video/mp4",
                ".webm": "video/webm",
                ".mp3": "audio/mpeg",
                ".m4a": "audio/mp4",
                ".wav": "audio/wav",
            }
            content_type = mime_map.get(ext, "application/octet-stream")
            file_size = target_file.stat().st_size
            range_hdr = (self.headers.get("Range") or "").strip()
            if range_hdr.startswith("bytes="):
                m = re.match(r"^bytes=(\d*)-(\d*)$", range_hdr)
                if m:
                    start = int(m.group(1)) if m.group(1) else 0
                    end = int(m.group(2)) if m.group(2) else (file_size - 1)
                    end = min(end, file_size - 1)
                    if start >= file_size or start > end:
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{file_size}")
                        self.end_headers()
                        return
                    length = end - start + 1
                    with target_file.open("rb") as fh:
                        fh.seek(start)
                        chunk = fh.read(length)
                    self.send_response(206)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(len(chunk)))
                    self.end_headers()
                    self.wfile.write(chunk)
                    return

            raw_media = target_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(len(raw_media)))
            self.end_headers()
            self.wfile.write(raw_media)
            return

        if path == "/api/health":
            self._send_json(200, {"status": "UP", "service": "antigravity-learning-hub"})
            return

        if path == "/api/dashboard":
            self._send_json(200, state_manager.get_dashboard_payload())
            return

        if path == "/api/feed":
            self._send_json(200, state_manager.get_feed_payload())
            return

        if path == "/api/visualizers":
            self._send_json(200, {"visualizers": visualizer_engine.list_visualizers()})
            return

        if path == "/api/fs/file":
            rel_path = (query.get("path") or [""])[0]
            code, data = read_workspace_file(rel_path)
            extra = {"ETag": f'"{data["sha256"]}"'} if code == 200 and "sha256" in data else None
            self._send_json(code, data, extra_headers=extra)
            return

        if path == "/api/fs/stat":
            rel_path = (query.get("path") or [""])[0]
            code, data = read_workspace_file(rel_path)
            if code == 200:
                self._send_json(200, {"path": data["path"], "sha256": data["sha256"], "mtimeMs": data["mtimeMs"]})
            else:
                self._send_json(code, data)
            return

        if path == "/api/dsa/problem":
            slug = (query.get("slug") or ["003-group-anagrams"])[0]
            code, data = get_dsa_problem_bundle(slug)
            self._send_json(code, data)
            return

        if path == "/api/tracks":
            self._send_json(200, storage.get_tracks_catalog())
            return

        if path == "/api/kb/courses":
            self._send_json(200, storage.get_kb_courses())
            return

        if path == "/api/kb/course-compendium":
            course_id = (query.get("course") or ["01-zero-to-staff-sdet"])[0]
            code, data = storage.get_kb_course_compendium(course_id)
            self._send_json(code, data)
            return

        if path in ("/api/kb/chapters", "/api/kb/catalog"):
            track = (query.get("track") or [None])[0]
            course = (query.get("course") or [None])[0]
            include_labs = (query.get("includeLabs") or ["0"])[0] in ("1", "true", "yes")
            self._send_json(200, {"chapters": storage.list_kb_chapters(track=track, course=course, include_labs=include_labs)})
            return

        if path == "/api/kb/chapter":
            slug = (query.get("slug") or ["sdet-01-determinism-and-flakiness-math"])[0]
            code, data = storage.get_kb_chapter(slug)
            if code == 404 and not query.get("slug"):
                code, data = storage.get_kb_chapter("sd-01-continuous-sync-and-backpressure")
            self._send_json(code, data)
            return

        if path == "/api/kb/search":
            q = (query.get("q") or [""])[0]
            track = (query.get("track") or [None])[0]
            course = (query.get("course") or [None])[0]
            self._send_json(200, storage.search_knowledgebase(q, track=track, course=course))
            return

        if path == "/api/newsfeed":
            category = (query.get("category") or [None])[0]
            tag = (query.get("tag") or [None])[0]
            bookmarked = (query.get("bookmarked") or ["0"])[0] in ("1", "true", "yes")
            self._send_json(200, storage.get_newsfeed(category=category, tag=tag, bookmarked_only=bookmarked))
            return

        if path in ("/api/workbench/catalog", "/api/workbench/frameworks"):
            self._send_json(200, storage.get_workbench_catalog())
            return

        if path in ("/api/interviews", "/api/interviews/catalog"):
            self._send_json(200, storage.get_interviews_catalog())
            return

        if path == "/api/interviews/session":
            session_id = (query.get("id") or query.get("sessionId") or ["interview-1"])[0]
            code, data = storage.get_interview_session(session_id)
            self._send_json(code, data)
            return

        if path in ("/api/roadmap/status", "/api/roadmap/journey"):
            self._send_json(200, storage.get_roadmap_status())
            return

        if path == "/api/telegram/status":
            from hub import telegram_bot
            bot = telegram_bot.AntigravityTelegramBot()
            db = state_manager.load_db()
            self._send_json(200, {
                "configured": bot.is_configured(),
                "inbox": db.get("telegramInbox", [])[:15]
            })
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def do_PUT(self):
        if not self._validate_local_request():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except Exception:
            payload = {}

        if path == "/api/fs/file":
            rel_path = payload.get("path", "")
            content = payload.get("content", "")
            if_match = self.headers.get("If-Match") or payload.get("expectedSha256")
            code, data = write_workspace_file(rel_path, content, expected_sha256=if_match)
            extra = {"ETag": f'"{data["sha256"]}"'} if code == 200 and "sha256" in data else None
            self._send_json(code, data, extra_headers=extra)
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def do_POST(self):
        if not self._validate_local_request():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except Exception:
            payload = {}

        if path == "/api/feed/interact":
            card_id = payload.get("cardId", "")
            action = payload.get("action", "complete")
            selected_option = payload.get("selectedOption")
            res = state_manager.record_feed_interaction(card_id, action, selected_option)
            self._send_json(200, res)
            return

        if path == "/api/visualize":
            viz_id = payload.get("visualizerId", "dsa-group-anagrams")
            custom_input = payload.get("customInput")
            trace = visualizer_engine.generate_trace(viz_id, custom_input)
            self._send_json(200, trace)
            return

        if path == "/api/run-test":
            target = payload.get("target", "001-two-sum")
            lang = payload.get("lang", "all")
            res = execute_test_target(target, lang)
            self._send_json(200, res)
            return

        if path == "/api/run-cases":
            slug = payload.get("slug", "003-group-anagrams")
            lang = payload.get("lang", "python")
            res = execute_problem_cases(slug, lang)
            self._send_json(200, res)
            return

        if path == "/api/dsa/scaffold":
            slug_or_id = payload.get("slug") or payload.get("problemId") or ""
            code, data = scaffold_dsa_problem(str(slug_or_id))
            self._send_json(code, data)
            return

        if path == "/api/dsa/mastery":
            prob_id = int(payload.get("problemId", 0))
            java_done = payload.get("javaDone")
            py_done = payload.get("pyDone")
            score = payload.get("score")
            status = payload.get("status")
            ok = state_manager.update_dsa_mastery(prob_id, java_done=java_done, py_done=py_done, score=score, status=status)
            self._send_json(200 if ok else 404, {"updated": ok, "problemId": prob_id})
            return

        if path in ("/api/kb/quiz", "/api/kb/quiz-submit"):
            slug = payload.get("slug", "")
            answers = payload.get("answers") or {}
            code, data = storage.submit_kb_quiz(slug, answers)
            self._send_json(code, data)
            return

        if path == "/api/kb/walkthrough-audio":
            from hub import tts_walkthrough_engine

            slug = payload.get("slug") or "sdet-01-determinism-and-flakiness-math"
            force_offline = bool(payload.get("offline", False))
            code, ch_data = storage.get_kb_chapter(slug)
            if code != 200:
                self._send_json(code, ch_data)
                return
            audio_res = tts_walkthrough_engine.generate_walkthrough_audio(
                slug, ch_data.get("walkthrough", []), force_offline=force_offline
            )
            self._send_json(200, audio_res)
            return

        if path == "/api/newsfeed/bookmark":
            article_id = payload.get("articleId") or payload.get("id") or ""
            code, data = storage.toggle_news_bookmark(article_id)
            self._send_json(code, data)
            return

        if path == "/api/newsfeed/refresh":
            fetch_remote = bool(payload.get("fetchRemote", False))
            self._send_json(200, storage.refresh_newsfeed(fetch_remote=fetch_remote))
            return

        if path in ("/api/workbench/verify", "/api/workbench/run"):
            item_id = payload.get("itemId") or payload.get("id") or ""
            code, data = storage.run_workbench_verification(item_id)
            self._send_json(code, data)
            return

        if path == "/api/interviews/save":
            session_id = payload.get("sessionId") or payload.get("id") or "interview-1"
            question_id = payload.get("questionId") or "q1"
            response_text = payload.get("response") or ""
            code, data = storage.save_interview_response(session_id, question_id, response_text)
            self._send_json(code, data)
            return

        if path == "/api/roadmap/toggle":
            enabled = bool(payload.get("enabled", True))
            if "pace" in payload and payload["pace"]:
                storage.set_roadmap_pace(str(payload["pace"]))
            self._send_json(200, storage.set_roadmap_toggle(enabled))
            return

        if path == "/api/roadmap/pace":
            pace = str(payload.get("pace") or "60d")
            self._send_json(200, storage.set_roadmap_pace(pace))
            return

        if path == "/api/roadmap/mark-done":
            item_id = str(payload.get("itemId") or payload.get("id") or payload.get("slug") or "")
            completed = bool(payload["completed"]) if "completed" in payload and payload["completed"] is not None else None
            source = str(payload.get("source") or "manual")
            code, data = storage.set_roadmap_item_done(item_id, completed=completed, source=source)
            self._send_json(code, data)
            return

        if path == "/api/telegram/push":
            from hub import telegram_bot
            mode = payload.get("mode", "card")
            topic = payload.get("topic", "")
            bot = telegram_bot.AntigravityTelegramBot()
            if not bot.is_configured():
                self._send_json(400, {"ok": False, "error": "Telegram credentials not configured in .env"})
                return
            if mode == "welcome":
                msg_data = bot.handle_command_text("/start")
                res = bot.send_message(msg_data["text"], reply_markup=msg_data.get("reply_markup"))
            elif mode == "progress":
                text, markup = telegram_bot.format_progress_message()
                res = bot.send_message(text, reply_markup=markup)
            else:
                res = telegram_bot.send_daily_digest(topic)
            self._send_json(200, res)
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def log_message(self, format, *args):
        if "DEBUG_HUB" in os.environ:
            super().log_message(format, *args)


class ThreadedHubServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128


def dispatch_request(method: str, path: str, body: dict = None, headers: dict = None) -> dict:
    """In-process HTTP request dispatcher for LearningHubHandler (for fast unit & CI tests)."""
    import io

    raw_body = json.dumps(body).encode("utf-8") if body is not None else b""
    req_headers = {"Content-Length": str(len(raw_body)), "Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    handler = LearningHubHandler.__new__(LearningHubHandler)
    handler.path = path
    handler.command = method.upper()
    handler.headers = req_headers
    handler.client_address = ("127.0.0.1", 0)
    handler.rfile = io.BytesIO(raw_body)
    handler.wfile = io.BytesIO()
    handler._resp_status = 200
    handler._resp_headers = {}

    def _send_response(code, message=None):
        handler._resp_status = code

    def _send_header(k, v):
        handler._resp_headers[k] = v

    def _end_headers():
        pass

    handler.send_response = _send_response
    handler.send_header = _send_header
    handler.end_headers = _end_headers

    if handler.command == "GET":
        handler.do_GET()
    elif handler.command == "POST":
        handler.do_POST()
    elif handler.command == "PUT":
        handler.do_PUT()
    elif handler.command == "OPTIONS":
        handler.do_OPTIONS()

    out_bytes = handler.wfile.getvalue()
    out_text = out_bytes.decode("utf-8", errors="replace")
    try:
        parsed_data = json.loads(out_text) if out_text and not out_text.lstrip().startswith("<!DOCTYPE") else {"html": out_text}
    except Exception:
        parsed_data = {"raw": out_text}

    return {
        "status_code": handler._resp_status,
        "data": parsed_data,
        "headers": handler._resp_headers
    }


def run_hub_server(port: int = DEFAULT_PORT, host: str = "127.0.0.1"):
    import threading
    from hub import telegram_bot

    bot = telegram_bot.AntigravityTelegramBot()
    if bot.is_configured():
        t_bot = threading.Thread(target=bot.run_polling_loop, daemon=True)
        t_bot.start()

    server = ThreadedHubServer((host, port), LearningHubHandler)
    print("=" * 68)
    print(f"🚀 ANTIGRAVITY LEARNING HUB & VISUALIZER RUNNING")
    print(f"🌐 Open in Browser: http://{host}:{port}")
    if bot.is_configured():
        print("✈️  Telegram Bot Mobile Bridge: ACTIVE (Long-Polling in Background)")
    print("=" * 68)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Antigravity Learning Hub...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Learning Hub Server")
    parser.add_argument("pos_port", nargs="?", type=int, default=None, help="Optional positional port")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port (default: 8090)")
    args = parser.parse_args()
    final_port = args.pos_port if args.pos_port is not None else args.port
    run_hub_server(final_port, args.host)
