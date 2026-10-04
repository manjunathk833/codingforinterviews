#!/usr/bin/env python3
"""
Session Manager CLI for Antigravity Mock Interview Simulation Agent.
Handles interview session indexing, folder initialization, answer validation,
and updating the master session tracker.
"""

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MOCK_ROOT = REPO_ROOT / "mock-interviews"


def get_all_sessions():
    """Returns sorted list of (session_num, Path) for existing interviews."""
    if not MOCK_ROOT.exists():
        return []
    sessions = []
    for item in MOCK_ROOT.iterdir():
        if item.is_dir() and item.name.startswith("interview-"):
            match = re.match(r"interview-(\d+)", item.name)
            if match:
                sessions.append((int(match.group(1)), item))
    sessions.sort(key=lambda x: x[0])
    return sessions


def get_next_session_info():
    """Determines the next session number and folder path."""
    sessions = get_all_sessions()
    next_num = sessions[-1][0] + 1 if sessions else 1
    folder_name = f"interview-{next_num}"
    return next_num, MOCK_ROOT / folder_name


def get_latest_session_info():
    """Returns the latest existing session info or None."""
    sessions = get_all_sessions()
    if not sessions:
        return None
    return sessions[-1]


def cmd_next(args):
    """Outputs next session folder path."""
    num, path = get_next_session_info()
    if args.create:
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created session folder: {path}")
    else:
        print(str(path))


def cmd_latest(args):
    """Outputs latest session folder path."""
    session = get_latest_session_info()
    if not session:
        print("No sessions found.")
        sys.exit(1)
    print(str(session[1]))


def cmd_validate_answers(args):
    """Checks if candidate answers are filled in interviewquestions.md."""
    target = Path(args.path) if args.path else None
    if not target:
        latest = get_latest_session_info()
        if not latest:
            print("No active session found.")
            sys.exit(1)
        target = latest[1] / "interviewquestions.md"
    elif target.is_dir():
        target = target / "interviewquestions.md"

    if not target.exists():
        print(f"Error: {target} does not exist.")
        sys.exit(1)

    content = target.read_text(encoding="utf-8")
    
    # Check for placeholder comments
    placeholder_count = content.count("<!-- Type your answer below this line -->")
    
    # Simple check for filled answers
    sections = re.findall(r"^#### ✍️ Candidate Answer:\s*(.*?)(?=^### Question|\Z)", content, re.DOTALL | re.MULTILINE)
    unfilled = 0
    for idx, s in enumerate(sections, 1):
        clean_text = s.replace("<!-- Type your answer below this line -->", "").strip()
        if len(clean_text) < 15:
            unfilled += 1

    print(f"Session questions: {len(sections)}")
    print(f"Unanswered or empty: {unfilled}")

    if unfilled > 0:
        print(f"⚠️  {unfilled} question(s) appear unanswered or very brief.")
        sys.exit(2)
    else:
        print("✓ All questions have candidate answers provided!")
        sys.exit(0)


def cmd_update_tracker(args):
    """Updates the master tracker table in mock-interviews/README.md."""
    readme_path = MOCK_ROOT / "README.md"
    if not readme_path.exists():
        print("README.md not found in mock-interviews.")
        sys.exit(1)

    content = readme_path.read_text(encoding="utf-8")
    session_num = f"{int(args.id):02d}"
    
    # Pattern to match table row
    pattern = rf"(\|\s*\*\*{session_num}\*\*\s*\|[^|]+\|[^|]+\|[^|]+\|)[^|]+(\|)[^|]+(\|[^\n]+)"
    
    replacement = rf"\g<1> {args.score} \g<2> {args.status} \g<3>"
    
    new_content, count = re.subn(pattern, replacement, content)
    if count == 0:
        # Append new row if not matched
        row = f"| **{session_num}** | {args.focus} | {args.level} | {args.questions} | {args.score} | `{args.status}` | {args.date} |\n"
        # Find where table ends
        marker = "## 📚 Core Knowledge Domains Evaluated"
        if marker in new_content:
            parts = new_content.split(marker)
            new_content = parts[0] + row + "\n---\n\n" + marker + parts[1]
        else:
            new_content += "\n" + row

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"✓ Updated session #{session_num} in mock-interviews/README.md")


def main():
    parser = argparse.ArgumentParser(description="Mock Interview Session Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # next
    p_next = subparsers.add_parser("next", help="Get next session info")
    p_next.add_argument("--create", action="store_true", help="Create folder if missing")
    p_next.set_defaults(func=cmd_next)

    # latest
    p_latest = subparsers.add_parser("latest", help="Get latest session folder")
    p_latest.set_defaults(func=cmd_latest)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate submitted answers")
    p_validate.add_argument("path", nargs="?", help="Path to folder or interviewquestions.md")
    p_validate.set_defaults(func=cmd_validate_answers)

    # update-tracker
    p_tracker = subparsers.add_parser("update-tracker", help="Update master README table")
    p_tracker.add_argument("id", help="Session ID (e.g. 1)")
    p_tracker.add_argument("--score", default="90/100", help="Score string")
    p_tracker.add_argument("--status", default="Completed", help="Status string")
    p_tracker.add_argument("--focus", default="Microservice QE & AI Testing", help="Session focus")
    p_tracker.add_argument("--level", default="Senior / Lead SDET", help="Target level")
    p_tracker.add_argument("--questions", default="5 Topics", help="Question count")
    p_tracker.add_argument("--date", default="2026-10-04", help="Date")
    p_tracker.set_defaults(func=cmd_update_tracker)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
