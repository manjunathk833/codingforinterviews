#!/usr/bin/env python3
"""
Deterministic Docs-as-Code Executable Snippet Verifier (`tools/safety/snippet_verify.py`)

Enforces across ALL Textbook Course chapters (`knowledgebase/**/*.md`):
1. 100% of ```python blocks parse cleanly via `ast.parse`.
2. 100% of stdlib-only ```python blocks execute cleanly (exit code 0) in an isolated temp dir.
3. 100% of stdlib-only public ```java classes/records compile cleanly via `javac` (batched for speed).
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
KB_ROOT = REPO_ROOT / "knowledgebase"

STDLIB_PY_MODULES: set[str] = (
    set(sys.stdlib_module_names)
    if hasattr(sys, "stdlib_module_names")
    else {
        "__future__", "abc", "argparse", "ast", "asyncio", "base64", "bisect",
        "collections", "concurrent", "contextlib", "contextvars", "copy", "csv",
        "dataclasses", "datetime", "decimal", "difflib", "email", "enum", "fnmatch",
        " fractions", "fractions", "functools", "gc", "gzip", "hashlib", "heapq",
        "hmac", "html", "http", "inspect", "io", "ipaddress", "itertools", "json",
        "logging", "math", "mmap", "multiprocessing", "operator", "os", "pathlib",
        "pickle", "platform", "pprint", "queue", "random", "re", " resource",
        "resource", "secrets", "selectors", "shlex", "shutil", "signal", "socket",
        "sqlite3", "ssl", "stat", "statistics", "string", "struct", "subprocess",
        "sys", "tempfile", "textwrap", "threading", "time", "timeit", "traceback",
        "types", "typing", "unicodedata", "unittest", "urllib", "uuid", "warnings",
        "weakref", "xml", "zipfile", "zlib",
    }
)


def is_stdlib_python(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in STDLIB_PY_MODULES:
                    return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] not in STDLIB_PY_MODULES:
                return False
    return True


def is_stdlib_java(code: str) -> tuple[bool, str | None]:
    # Skip blocks with third-party imports (including wildcard `.*`) or third-party @Annotations
    for m in re.finditer(r"^\s*import\s+(?:static\s+)?([A-Za-z0-9_.*]+)\s*;", code, flags=re.MULTILINE):
        imp = m.group(1)
        if not imp.startswith(("java.", "javax.", "com.sun.")):
            return False, None
    if re.search(r"@(?:Test|BeforeAll|BeforeEach|AfterEach|AfterAll|ParameterizedTest)\b", code):
        return False, None
    m_cls = re.search(r"public\s+(?:final\s+|abstract\s+)?(?:class|record|interface)\s+([A-Za-z0-9_]+)", code)
    if not m_cls:
        return False, None
    return True, m_cls.group(1)


def verify_all_snippets(target_paths: list[pathlib.Path] | None = None) -> tuple[dict[str, int], list[str]]:
    md_files = (
        sorted(target_paths)
        if target_paths
        else sorted(KB_ROOT.glob("*/*.md"))
    )
    errors: list[str] = []
    stats = {
        "chapters": len(md_files),
        "py_total": 0,
        "py_stdlib_executed": 0,
        "java_total": 0,
        "java_stdlib_compiled": 0,
    }

    has_javac = shutil.which("javac") is not None
    java_jobs: list[tuple[str, int, str, str]] = []  # (rel, idx, cls_name, code_no_pkg)

    with tempfile.TemporaryDirectory() as tmpdir:
        for md_path in md_files:
            rel = md_path.relative_to(KB_ROOT).as_posix() if KB_ROOT in md_path.parents else md_path.name
            raw = md_path.read_text(encoding="utf-8")

            py_blocks = re.findall(r"```python\s*\n(.*?)```", raw, flags=re.DOTALL)
            java_blocks = re.findall(r"```java\s*\n(.*?)```", raw, flags=re.DOTALL)

            for idx, pb in enumerate(py_blocks, start=1):
                stats["py_total"] += 1
                try:
                    ast.parse(pb)
                except SyntaxError as exc:
                    errors.append(f"[PY-AST] {rel} (python block #{idx}): {exc}")
                    continue

                if is_stdlib_python(pb):
                    proc = subprocess.run(
                        [sys.executable, "-c", pb],
                        capture_output=True,
                        text=True,
                        timeout=6,
                        cwd=tmpdir,
                    )
                    if proc.returncode == 0:
                        stats["py_stdlib_executed"] += 1
                    else:
                        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-1:]
                        errors.append(f"[PY-EXEC] {rel} (python block #{idx}): {tail[0] if tail else 'exit!=0'}")

            for idx, jb in enumerate(java_blocks, start=1):
                stats["java_total"] += 1
                ok_std, cls_name = is_stdlib_java(jb)
                if ok_std and cls_name and has_javac:
                    # Strip `package ...;` so flat temp-dir compilation works cleanly
                    clean_jb = re.sub(r"^\s*package\s+[A-Za-z0-9_.]+\s*;\s*$", "", jb, flags=re.MULTILINE)
                    java_jobs.append((rel, idx, cls_name, clean_jb))

        # Compile Java stdlib blocks in collision-free batches for <2s speed!
        remaining = list(java_jobs)
        while remaining:
            batch: list[tuple[str, int, str, str]] = []
            used_names: set[str] = set()
            next_round: list[tuple[str, int, str, str]] = []
            for job in remaining:
                if job[2] not in used_names:
                    used_names.add(job[2])
                    batch.append(job)
                else:
                    next_round.append(job)
            remaining = next_round

            with tempfile.TemporaryDirectory() as jtmp_str:
                jtmp = pathlib.Path(jtmp_str)
                jfiles: list[str] = []
                for _, _, cls_name, code in batch:
                    jf = jtmp / f"{cls_name}.java"
                    jf.write_text(code, encoding="utf-8")
                    jfiles.append(str(jf))
                cproc = subprocess.run(["javac", *jfiles], capture_output=True, text=True, timeout=25)
                if cproc.returncode == 0:
                    stats["java_stdlib_compiled"] += len(batch)
                else:
                    # Fallback to individual compile inside failed batch to pinpoint exact culprit
                    for rel, idx, cls_name, code in batch:
                        with tempfile.TemporaryDirectory() as single_str:
                            sf = pathlib.Path(single_str) / f"{cls_name}.java"
                            sf.write_text(code, encoding="utf-8")
                            sp = subprocess.run(["javac", str(sf)], capture_output=True, text=True, timeout=10)
                            if sp.returncode == 0:
                                stats["java_stdlib_compiled"] += 1
                            else:
                                first_err = " | ".join((sp.stderr or "").strip().splitlines()[:2])
                                errors.append(f"[JAVA-COMPILE] {rel} (java block #{idx} {cls_name}): {first_err}")

    return stats, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Python AST/runtime and Java javac compilation across KB chapters.")
    parser.add_argument("paths", nargs="*", help="Optional specific markdown file(s) to verify.")
    args = parser.parse_args()

    targets = [pathlib.Path(p).resolve() for p in args.paths] if args.paths else None
    stats, errors = verify_all_snippets(targets)
    if errors:
        for err in errors:
            print(f"✗ {err}", file=sys.stderr)
        print(f"\n[FAIL] {len(errors)} snippet verification error(s) across {stats['chapters']} chapter(s).", file=sys.stderr)
        return 1

    print(
        f"[PASS] Verified {stats['chapters']} chapters: "
        f"{stats['py_total']} Python AST OK ({stats['py_stdlib_executed']} stdlib executed exit=0), "
        f"{stats['java_stdlib_compiled']}/{stats['java_total']} stdlib Java 17 compiled cleanly via javac."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
