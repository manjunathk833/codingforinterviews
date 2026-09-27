#!/usr/bin/env python3
"""Master Sheet Progress Tracker and Summary Utility.

Usage:
    python3 tools/tracker.py summary
    python3 tools/tracker.py update <problem_id> [--java-done] [--py-done] [--score SCORE] [--status STATUS]
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_SHEET = REPO_ROOT / "dsa" / "MASTER_SHEET.md"


def parse_master_sheet():
    """Parse the Master Sheet markdown table to extract problems and status."""
    if not MASTER_SHEET.exists():
        print(f"Error: {MASTER_SHEET} not found.")
        sys.exit(1)

    content = MASTER_SHEET.read_text(encoding="utf-8")
    lines = content.splitlines()

    problems = []
    # Match markdown table row: | # | Title | Pattern | Difficulty | Java | Python | Score | Status |
    row_pattern = re.compile(
        r"^\|\s*(\d+)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*\[([ xX])\]\s*\|\s*\[([ xX])\]\s*\|\s*([^|]+)\|\s*([^|]+)\|"
    )

    for line in lines:
        m = row_pattern.match(line)
        if m:
            prob_id = int(m.group(1))
            title = m.group(2).strip()
            link = m.group(3).strip()
            pattern = m.group(4).strip()
            difficulty = m.group(5).strip()
            java_done = m.group(6).lower() == "x"
            py_done = m.group(7).lower() == "x"
            score = m.group(8).strip()
            status = m.group(9).strip()
            problems.append({
                "id": prob_id,
                "title": title,
                "link": link,
                "pattern": pattern,
                "difficulty": difficulty,
                "java_done": java_done,
                "py_done": py_done,
                "score": score,
                "status": status,
                "raw_line": line,
            })

    return problems, content


def cmd_summary():
    """Print overall curriculum and readiness metrics."""
    problems, _ = parse_master_sheet()
    if not problems:
        print("No problems found in Master Sheet.")
        return

    total = len(problems)
    java_count = sum(1 for p in problems if p["java_done"])
    py_count = sum(1 for p in problems if p["py_done"])
    both_count = sum(1 for p in problems if p["java_done"] and p["py_done"])
    passed_count = sum(1 for p in problems if "Passed" in p["status"] or "Completed" in p["status"])

    by_diff = {"Easy": [0, 0], "Medium": [0, 0], "Hard": [0, 0]}
    for p in problems:
        d = p["difficulty"]
        if d in by_diff:
            by_diff[d][0] += 1
            if p["java_done"] and p["py_done"]:
                by_diff[d][1] += 1

    by_pattern = {}
    for p in problems:
        pat = p["pattern"]
        if pat not in by_pattern:
            by_pattern[pat] = [0, 0]
        by_pattern[pat][0] += 1
        if p["java_done"] and p["py_done"]:
            by_pattern[pat][1] += 1

    print("\n" + "=" * 60)
    print("      🎯 MAANG CODING PREPARATION: MASTER SUMMARY")
    print("=" * 60)
    print(f"Total Questions Tracked : {total}")
    print(f"Java Implemented        : {java_count}/{total} ({java_count*100//total}%)")
    print(f"Python Implemented      : {py_count}/{total} ({py_count*100//total}%)")
    print(f"Both Solved (Dual Stack): {both_count}/{total} ({both_count*100//total}%)")
    print(f"Interviewer Passed (≥80): {passed_count}/{total} ({passed_count*100//total}%)")
    print("-" * 60)

    print("📊 Difficulty Breakdown:")
    for diff, (tot, done) in by_diff.items():
        pct = (done * 100 // tot) if tot > 0 else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"  {diff:<8} : {done:>2}/{tot:<2} [{bar}] {pct}%")

    print("\n🧩 Pattern Completion Breakdown:")
    for pat, (tot, done) in by_pattern.items():
        pct = (done * 100 // tot) if tot > 0 else 0
        print(f"  {pat:<32} : {done:>2}/{tot:<2} ({pct}%)")
    print("=" * 60 + "\n")


def cmd_update(prob_id: int, java_done: bool, py_done: bool, score: str, status: str):
    """Update a specific row in MASTER_SHEET.md."""
    if not MASTER_SHEET.exists():
        print(f"Error: {MASTER_SHEET} not found.")
        sys.exit(1)

    content = MASTER_SHEET.read_text(encoding="utf-8")
    lines = content.splitlines()
    updated = False

    row_pattern = re.compile(rf"^\|\s*{prob_id}\s*\|")

    new_lines = []
    for line in lines:
        if row_pattern.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 8:
                if java_done is not None:
                    cells[4] = "[x]" if java_done else "[ ]"
                if py_done is not None:
                    cells[5] = "[x]" if py_done else "[ ]"
                if score is not None:
                    cells[6] = score
                if status is not None:
                    cells[7] = status
                line = f"| {' | '.join(cells)} |"
                updated = True
        new_lines.append(line)

    if updated:
        MASTER_SHEET.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"✓ Successfully updated problem #{prob_id} in {MASTER_SHEET.name}")
    else:
        print(f"Error: Problem ID #{prob_id} not found in {MASTER_SHEET.name}")


def main():
    parser = argparse.ArgumentParser(description="Master Sheet Tracker Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("summary", help="Print preparation summary and metrics")

    up_parser = subparsers.add_parser("update", help="Update problem status in Master Sheet")
    up_parser.add_argument("id", type=int, help="Problem ID (e.g. 1)")
    up_parser.add_argument("--java-done", dest="java_done", action="store_true", default=None)
    up_parser.add_argument("--py-done", dest="py_done", action="store_true", default=None)
    up_parser.add_argument("--score", type=str, default=None, help="Assigned score (e.g. '92/100')")
    up_parser.add_argument("--status", type=str, default=None, help="Status (e.g. 'Passed', 'Needs Revision')")

    args = parser.parse_args()

    if args.command == "summary":
        cmd_summary()
    elif args.command == "update":
        cmd_update(args.id, args.java_done, args.py_done, args.score, args.status)


if __name__ == "__main__":
    main()
