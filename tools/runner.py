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
SEARCH_ROOTS = [
    REPO_ROOT / "dsa",
    REPO_ROOT / "core-cs",
    REPO_ROOT / "system-design",
    REPO_ROOT / "ai-engineering",
    REPO_ROOT / "frameworks" / "design-challenges",
    REPO_ROOT / "frameworks" / "sdet-system-design",
]


def find_all_problems(dsa_only: bool = False):
    """Discover all runnable problem/lab directories across curriculum pillars."""
    problems = []
    roots = [DSA_ROOT] if dsa_only else SEARCH_ROOTS

    for search_root in roots:
        if not search_root.exists():
            continue
        for root, dirs, files in os.walk(search_root):
            if "utils" in root or "/." in root or "__pycache__" in root:
                continue
            if "Solution.java" in files or "solution.py" in files:
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
    normalized_target = target.lower().strip().replace(" ", "-").replace("_", "-")
    matched = [
        p for p in all_problems 
        if target.lower() in p.name.lower() 
        or normalized_target in p.name.lower() 
        or target.lower() in str(p).lower()
    ]

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
            [sys.executable, str(py_file)],
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
        rel = str(p.relative_to(REPO_ROOT))
        has_java = f"{GREEN}Yes{RESET}" if (p / "Solution.java").exists() else f"{DIM}No{RESET}"
        has_py = f"{GREEN}Yes{RESET}" if (p / "solution.py").exists() else f"{DIM}No{RESET}"
        print(f"{rel:<55} {has_java:<20} {has_py:<20}")
    print(f"\nTotal: {len(problems)} problems/labs discovered.")


def find_completed_problems():
    """Discover all problems marked as completed in dsa/MASTER_SHEET.md."""
    import re
    master_sheet = DSA_ROOT / "MASTER_SHEET.md"
    if not master_sheet.exists():
        return []

    content = master_sheet.read_text(encoding="utf-8")
    row_pattern = re.compile(
        r"^\|\s*\d+\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|[^|]+\|[^|]+\|\s*\[([ xX])\]\s*\|\s*\[([ xX])\]"
    )
    all_problems = find_all_problems(dsa_only=True)
    completed = []
    for line in content.splitlines():
        m = row_pattern.match(line)
        if m:
            _, url, java_chk, py_chk = m.groups()
            java_done = java_chk.lower() == "x"
            py_done = py_chk.lower() == "x"
            if java_done or py_done:
                slug = url.strip("/").split("/")[-1].lower()
                matched = [p for p in all_problems if slug in p.name.lower()]
                if matched and matched[0] not in completed:
                    completed.append(matched[0])
    return completed


def cmd_test_completed(lang: str):
    """Run tests across all completed problems in MASTER_SHEET.md."""
    problems = find_completed_problems()
    if not problems:
        print(f"{YELLOW}No completed problems marked in dsa/MASTER_SHEET.md.{RESET}")
        return

    passed = 0
    failed = 0
    skipped = 0

    print(f"\n{BOLD}Running test suite across {len(problems)} completed problems...{RESET}")
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
    if failed > 0:
        sys.exit(1)


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
    if failed > 0:
        sys.exit(1)


def cmd_ci():
    """Execute the full local CI suite mirroring .github/workflows/ci.yml."""
    steps = [
        ("🛡️ Stage 1/5: Pre-Push & Secret Safety Audit", [str(REPO_ROOT / "tools/safety/safety_check.sh")]),
        ("📐 Stage 2/5: Pedagogy, Manifest DAG & Executable Snippet Gate", [
            sys.executable, "-c",
            "import subprocess, sys; "
            "r1 = subprocess.run([sys.executable, 'tools/safety/pedagogy_lint.py']).returncode; "
            "r2 = subprocess.run([sys.executable, 'tools/safety/snippet_verify.py']).returncode; "
            "sys.exit(r1 or r2)"
        ]),
        ("🧩 Stage 3/5: Completed DSA Solutions (Java 17 & Python 3)", [sys.executable, str(REPO_ROOT / "tools/runner.py"), "test-completed"]),
        ("🏗️ Stage 4/5: SDET System Design, Concurrency & SQL Data-QA Labs", [
            sys.executable, "-c",
            "import subprocess, sys; "
            "r1 = subprocess.run([sys.executable, 'frameworks/sdet-system-design/01-distributed-concurrency-isolation/reference_solution.py']).returncode; "
            "r2 = subprocess.run([sys.executable, 'frameworks/data-validation/01-sql-reconciliation-and-isolation/reference_solution.py']).returncode; "
            "sys.exit(r1 or r2)"
        ]),
        ("🌐 Stage 5/5: Learning Hub, Visualizer & AeroCart Suite CI", [sys.executable, str(REPO_ROOT / "hub/tests/test_hub_phase1.py")]),
    ]
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}   🚀 EXECUTING FULL LOCAL CI VERIFICATION PIPELINE (5 STAGES){RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    for label, cmd in steps:
        print(f"\n{BOLD}{YELLOW}▶ {label}{RESET}")
        res = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            print(f"\n{RED}{BOLD}✗ CI FAILED at stage: {label}{RESET}")
            sys.exit(res.returncode)
    print(f"\n{BOLD}{GREEN}======================================================================{RESET}")
    print(f"{BOLD}{GREEN}   ✅ ALL 5 CI STAGES PASSED SUCCESSFULLY! READY FOR RELEASE.{RESET}")
    print(f"{BOLD}{GREEN}======================================================================{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="DSA Problem Test Runner and Compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    test_parser = subparsers.add_parser("test", help="Test a specific problem")
    test_parser.add_argument("target", help="Problem path, folder name, or search slug (e.g. '001-two-sum')")
    test_parser.add_argument("--lang", choices=["java", "python", "all"], default="all", help="Target language")

    subparsers.add_parser("list", help="List all problems")

    test_completed_parser = subparsers.add_parser("test-completed", help="Test all completed problems from MASTER_SHEET.md")
    test_completed_parser.add_argument("--lang", choices=["java", "python", "all"], default="all", help="Target language")

    test_all_parser = subparsers.add_parser("test-all", help="Test all problems")
    test_all_parser.add_argument("--lang", choices=["java", "python", "all"], default="all", help="Target language")

    cycle_parser = subparsers.add_parser("cycle", help="Inspect or advance active practice cycle")
    cycle_parser.add_argument("subaction", nargs="?", default="status", choices=["status", "next", "advance", "init"], help="Cycle subaction")
    cycle_parser.add_argument("--stage", type=int, default=None, help="Stage number to advance")

    hub_parser = subparsers.add_parser("hub", help="Launch the MAANG Learning Hub & Step-by-Step Visualizer Web UI")
    hub_parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    hub_parser.add_argument("--port", type=int, default=8090, help="Bind port (default: 8090)")

    tg_parser = subparsers.add_parser("telegram", help="Manage the Antigravity Telegram Bot & Mobile Learning Bridge")
    tg_parser.add_argument("tg_action", nargs="?", default="status", choices=["status", "push", "poll", "poll-once"], help="Telegram action")
    tg_parser.add_argument("--mode", default="card", choices=["card", "progress", "welcome"], help="Push mode")
    tg_parser.add_argument("--topic", default="", help="Optional topic keyword")

    subparsers.add_parser("ci", help="Run the full local CI verification suite (Safety, DSA, Frameworks, AeroCart & Hub)")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "ci":
        cmd_ci()
    elif args.command == "telegram":
        tg_script = REPO_ROOT / "hub" / "telegram_bot.py"
        cmd = [sys.executable, str(tg_script), args.tg_action]
        if args.tg_action == "push":
            cmd.extend(["--mode", args.mode, "--topic", args.topic])
        subprocess.run(cmd)
    elif args.command == "hub":
        hub_script = REPO_ROOT / "hub" / "server.py"
        cmd = [sys.executable, str(hub_script), "--host", args.host, "--port", str(args.port)]
        subprocess.run(cmd)
    elif args.command == "cycle":
        cycle_script = REPO_ROOT / "tools" / "cycle.py"
        cmd = [sys.executable, str(cycle_script), args.subaction]
        if args.stage is not None:
            cmd.extend(["--stage", str(args.stage)])
        subprocess.run(cmd)
    elif args.command == "test":
        target_dir = resolve_problem(args.target)
        res = run_test(target_dir, args.lang)
        # Exit with non-zero if any test failed
        has_failure = any(r["status"] not in ("PASSED", "SKIPPED") for r in res.values())
        sys.exit(1 if has_failure else 0)
    elif args.command == "test-completed":
        cmd_test_completed(args.lang)
    elif args.command == "test-all":
        cmd_test_all(args.lang)


if __name__ == "__main__":
    main()
