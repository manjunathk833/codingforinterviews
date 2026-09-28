#!/usr/bin/env python3
"""Unified Test Runner and Compiler for Java & Python DSA Solutions.

Usage:
    python3 tools/runner.py test <problem-name-or-path> [--lang java|python|all]
    python3 tools/runner.py list
    python3 tools/runner.py test-all
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

REPO_ROOT = Path(__file__).resolve().parent.parent
DSA_ROOT = REPO_ROOT / "dsa"
BIN_DIR = REPO_ROOT / ".build"


def find_all_problems():
    """Discover all problem directories inside dsa/ (excluding utils and hidden folders)."""
    problems = []
    if not DSA_ROOT.exists():
        return problems

    for root, dirs, files in os.walk(DSA_ROOT):
        # Exclude utils and hidden directories
        if "utils" in root or "/." in root:
            continue
        if "Solution.java" in files or "solution.py" in files or "README.md" in files:
            problems.append(Path(root))

    problems.sort()
    return problems


def resolve_problem(target: str) -> Path:
    """Resolve target string to a problem path."""
    target_path = Path(target)
    if target_path.exists() and target_path.is_dir():
        return target_path.resolve()

    # Search by partial name or slug
    all_problems = find_all_problems()
    matched = [p for p in all_problems if target.lower() in p.name.lower() or target.lower() in str(p).lower()]

    if len(matched) == 1:
        return matched[0]
    elif len(matched) > 1:
        exact = [p for p in matched if p.name.lower() == target.lower()]
        if len(exact) == 1:
            return exact[0]
        print(f"{YELLOW}Multiple problems matched '{target}':{RESET}")
        for p in matched:
            print(f"  - {p.relative_to(REPO_ROOT)}")
        sys.exit(1)
    else:
        print(f"{RED}Error: Problem '{target}' not found in dsa/.{RESET}")
        print(f"Run {BOLD}python3 tools/runner.py list{RESET} to see all problems.")
        sys.exit(1)


def compile_and_run_java(problem_dir: Path) -> dict:
    """Compile and execute Solution.java."""
    java_file = problem_dir / "Solution.java"
    if not java_file.exists():
        return {"status": "SKIPPED", "message": "Solution.java does not exist", "time_ms": 0}

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    build_dir = BIN_DIR / "java" / problem_dir.name
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Compile utils first if present
    utils_dir = DSA_ROOT / "utils"
    compile_cmd = ["javac", "-d", str(build_dir), "-cp", f"{DSA_ROOT}:{REPO_ROOT}"]
    if utils_dir.exists():
        utils_sources = list(utils_dir.glob("*.java"))
        if utils_sources:
            compile_cmd.extend([str(f) for f in utils_sources])
    compile_cmd.append(str(java_file))

    start_time = time.perf_counter()
    try:
        compile_proc = subprocess.run(
            compile_cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "message": "Java compilation timed out (15s)", "time_ms": 0}

    if compile_proc.returncode != 0:
        return {
            "status": "COMPILATION_ERROR",
            "message": compile_proc.stderr.strip() or compile_proc.stdout.strip(),
            "time_ms": 0,
        }

    # Execute Solution
    run_cmd = ["java", "-ea", "-cp", f"{build_dir}:{DSA_ROOT}:{REPO_ROOT}", "Solution"]
    try:
        run_proc = subprocess.run(
            run_cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "message": "Java execution timed out (10s)", "time_ms": 10000}

    if run_proc.returncode != 0:
        err_msg = run_proc.stderr.strip() or run_proc.stdout.strip()
        return {"status": "FAILED", "message": err_msg, "time_ms": elapsed_ms}

    return {
        "status": "PASSED",
        "message": run_proc.stdout.strip() or "All assertions passed successfully.",
        "time_ms": elapsed_ms,
    }


def run_python(problem_dir: Path) -> dict:
    """Execute solution.py."""
    py_file = problem_dir / "solution.py"
    if not py_file.exists():
        return {"status": "SKIPPED", "message": "solution.py does not exist", "time_ms": 0}

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{DSA_ROOT}:{DSA_ROOT / 'utils'}:{REPO_ROOT}:{existing_pythonpath}"

    start_time = time.perf_counter()
    try:
        run_proc = subprocess.run(
            ["python3", str(py_file)],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            env=env,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "message": "Python execution timed out (10s)", "time_ms": 10000}

    if run_proc.returncode != 0:
        err_msg = run_proc.stderr.strip() or run_proc.stdout.strip()
        return {"status": "FAILED", "message": err_msg, "time_ms": elapsed_ms}

    return {
        "status": "PASSED",
        "message": run_proc.stdout.strip() or "All assertions passed successfully.",
        "time_ms": elapsed_ms,
    }


def run_test(problem_dir: Path, lang: str):
    """Run tests for a single problem."""
    rel_path = problem_dir.relative_to(REPO_ROOT)
    print(f"\n{BOLD}{CYAN}=== Testing: {rel_path} ==={RESET}\n")

    results = {}
    if lang in ("java", "all"):
        print(f"{BOLD}[Java]{RESET} Compiling & executing Solution.java...")
        results["java"] = compile_and_run_java(problem_dir)
        print_result("Java", results["java"])

    if lang in ("python", "all"):
        print(f"\n{BOLD}[Python]{RESET} Executing solution.py...")
        results["python"] = run_python(problem_dir)
        print_result("Python", results["python"])

    return results


def print_result(label: str, res: dict):
    status = res["status"]
    time_str = f"({res['time_ms']:.1f}ms)" if res["time_ms"] > 0 else ""

    if status == "PASSED":
        print(f"  {GREEN}{BOLD}✓ PASS{RESET} {label} {time_str}")
        if res["message"]:
            for line in res["message"].splitlines()[:5]:
                print(f"    {DIM}{line}{RESET}")
    elif status == "SKIPPED":
        print(f"  {YELLOW}{BOLD}⚠ SKIP{RESET} {label} - {res['message']}")
    else:
        print(f"  {RED}{BOLD}✗ {status}{RESET} {label} {time_str}")
        if res["message"]:
            print(f"    {RED}{res['message']}{RESET}")


def cmd_list():
    """List all problems and their implementation status."""
    problems = find_all_problems()
    if not problems:
        print(f"{YELLOW}No problems found in dsa/.{RESET}")
        return

    print(f"\n{BOLD}{'Problem':<45} {'Java':<12} {'Python':<12}{RESET}")
    print("-" * 72)
    for p in problems:
        rel = str(p.relative_to(DSA_ROOT))
        has_java = f"{GREEN}Yes{RESET}" if (p / "Solution.java").exists() else f"{DIM}No{RESET}"
        has_py = f"{GREEN}Yes{RESET}" if (p / "solution.py").exists() else f"{DIM}No{RESET}"
        print(f"{rel:<45} {has_java:<20} {has_py:<20}")
    print(f"\nTotal: {len(problems)} problems discovered.")


def cmd_test_all(lang: str):
    """Run tests across all problems."""
    problems = find_all_problems()
    passed = 0
    failed = 0
    skipped = 0

    print(f"\n{BOLD}Running test suite across {len(problems)} problems...{RESET}")
    for p in problems:
        res = run_test(p, lang)
        for r in res.values():
            if r["status"] == "PASSED":
                passed += 1
            elif r["status"] == "SKIPPED":
                skipped += 1
            else:
                failed += 1

    print("\n" + "=" * 50)
    print(f"{BOLD}Summary:{RESET} {GREEN}{passed} Passed{RESET} | {RED}{failed} Failed{RESET} | {YELLOW}{skipped} Skipped{RESET}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="DSA Problem Test Runner and Compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    test_parser = subparsers.add_parser("test", help="Test a specific problem")
    test_parser.add_argument("target", help="Problem path, folder name, or search slug (e.g. '001-two-sum')")
    test_parser.add_argument("--lang", choices=["java", "python", "all"], default="all", help="Target language")

    subparsers.add_parser("list", help="List all problems")

    test_all_parser = subparsers.add_parser("test-all", help="Test all problems")
    test_all_parser.add_argument("--lang", choices=["java", "python", "all"], default="all", help="Target language")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "test":
        target_dir = resolve_problem(args.target)
        res = run_test(target_dir, args.lang)
        # Exit with non-zero if any test failed
        has_failure = any(r["status"] not in ("PASSED", "SKIPPED") for r in res.values())
        sys.exit(1 if has_failure else 0)
    elif args.command == "test-all":
        cmd_test_all(args.lang)


if __name__ == "__main__":
    main()
