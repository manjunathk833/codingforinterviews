#!/usr/bin/env python3
"""Practice Cycle Manager for MAANG Coding & SDET Preparation.

Manages holistic multi-discipline practice cycles tracking:
  - Stage 1: Core Algorithmic Mastery (DSA - Java + Python)
  - Stage 2: SDET Framework & Concurrency Architecture
  - Stage 3: System Design & Conceptual Drill (Mock Interview / Architecture)
  - Stage 4: Bar-Raiser Quality Gate & Release Sync

Usage:
    python3 tools/cycle.py status
    python3 tools/cycle.py next
    python3 tools/cycle.py advance [--stage STAGE_NUM]
    python3 tools/cycle.py complete
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CYCLE_FILE = REPO_ROOT / "PRACTICE_CYCLE.md"

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def read_cycle_file():
    if not CYCLE_FILE.exists():
        print(f"{YELLOW}Warning: {CYCLE_FILE} not found. Initializing default cycle...{RESET}")
        init_default_cycle()
    return CYCLE_FILE.read_text(encoding="utf-8")


def write_cycle_file(content: str):
    CYCLE_FILE.write_text(content, encoding="utf-8")


def init_default_cycle():
    template = """# 🔄 MAANG Preparation: Active Practice Cycle

**Current Cycle:** `Cycle #1: Distributed Concurrency, Data Isolation & Hash Invariants`  
**Target Completion:** `In Progress`  
**Last Updated:** `{date}`  

---

## 🎯 Cycle Progression & Active HUD

```text
[Stage 1: DSA]  ➔  [Stage 2: Architecture]  ➔  [Stage 3: Concept/Mock]  ➔  [Stage 4: Bar-Raiser Sync]
    [✓]                     [▶ IN PROGRESS]                 [ ]                         [ ]
```

| Stage | Focus Area | Target Item / Path | Verification Command | Status |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **DSA Algorithmic Mastery** | `Group Anagrams` (Arrays & Hashing) | `./run.sh test 003-group-anagrams` | `In Progress` |
| **2** | **Framework / Concurrency** | `01-distributed-concurrency-isolation` | `python3 frameworks/sdet-system-design/01-distributed-concurrency-isolation/solution.py` | `In Progress` |
| **3** | **System Design & AI Drill** | `mock-interviews/interview-1/` | Review `conceptual-mastery-guide.md` | `Pending` |
| **4** | **Bar-Raiser Gate & Release** | Full Suite Audit & PR Sync | `tools/safety/safety_check.sh` | `Pending` |

---

## 🚀 Active Step Guidance

### Currently Active: **Stage 2: Framework & Distributed Concurrency**
- **Objective**: Implement tenant-isolated concurrent test data manager and Kafka eventual-consistency poller.
- **Working Files**:
  - `frameworks/sdet-system-design/01-distributed-concurrency-isolation/solution.py`
  - `frameworks/sdet-system-design/01-distributed-concurrency-isolation/Solution.java`
- **Verification**: Run `python3 frameworks/sdet-system-design/01-distributed-concurrency-isolation/solution.py`
- **When Complete**: Run `/cycle advance` or have `/interviewer` verify.

---

## 📜 Completed Cycles Archive

*No cycles archived yet. Complete Cycle #1 to log your first milestone!*
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
    write_cycle_file(template)


def parse_stages(content: str):
    """Parse table rows for stages flexibly."""
    stages = []
    lines = content.splitlines()
    for line in lines:
        line_s = line.strip()
        if not line_s.startswith("|") or ":---" in line_s or "Focus Area" in line_s:
            continue
        cells = [c.strip() for c in line_s.strip("|").split("|")]
        if len(cells) >= 5:
            m_num = re.search(r"\d+", cells[0])
            if m_num:
                num = int(m_num.group(0))
                focus = cells[1].replace("*", "").strip()
                target = cells[2].replace("`", "").strip()
                cmd = cells[3].replace("`", "").strip()
                status = cells[4].replace("`", "").strip()
                stages.append({
                    "num": num,
                    "focus": focus,
                    "target": target,
                    "cmd": cmd,
                    "status": status,
                    "raw_line": line
                })
    return stages


def cmd_status():
    content = read_cycle_file()
    print("\n" + "=" * 68)
    print(f"{BOLD}{CYAN}      🔄 ACTIVE MAANG PRACTICE CYCLE STATUS{RESET}")
    print("=" * 68)
    
    # Extract Current Cycle
    m_cycle = re.search(r"\*\*Current Cycle:\*\*\s*`([^`]+)`", content)
    cycle_name = m_cycle.group(1) if m_cycle else "Active Cycle"
    print(f"\n{BOLD}Cycle:{RESET} {cycle_name}")
    
    stages = parse_stages(content)
    if stages:
        print("\n" + "-" * 68)
        print(f"{'Stg':<4} | {'Focus Area':<28} | {'Status':<13} | {'Target'}")
        print("-" * 68)
        for s in stages:
            status = s["status"]
            status_color = GREEN if any(w in status for w in ["Passed", "Completed", "Done"]) else (
                YELLOW if any(w in status for w in ["Progress", "Active"]) else DIM
            )
            print(f"{s['num']:<4} | {s['focus']:<28} | {status_color}{status:<13}{RESET} | {s['target']}")
        print("-" * 68)
    
    # Extract Active Step Guidance if present
    m_active = re.search(r"### Currently Active:\s*\*\*([^*]+)\*\*", content)
    if m_active:
        print(f"\n{BOLD}🎯 Immediate Next Action:{RESET} {m_active.group(1).strip()}")
    print("=" * 68 + "\n")


def cmd_next():
    content = read_cycle_file()
    m_active = re.search(r"### Currently Active:\s*\*\*([^*]+)\*\*", content)
    active_title = m_active.group(1).strip() if m_active else "Current Stage"
    
    print(f"\n{BOLD}{CYAN}🎯 NEXT STEP IN ACTIVE PRACTICE CYCLE:{RESET} {active_title}\n")
    # Extract objective and verification
    m_obj = re.search(r"-\s*\*\*Objective\*\*:\s*([^\n]+)", content)
    m_files = re.search(r"-\s*\*\*Working Files\*\*:\n((?:\s*-\s*`[^`]+`\n?)+)", content)
    m_cmd = re.search(r"-\s*\*\*Verification\*\*:\s*([^\n]+)", content)
    
    if m_obj:
        print(f"  • {BOLD}Objective:{RESET} {m_obj.group(1).strip()}")
    if m_files:
        print(f"  • {BOLD}Files:{RESET}\n{m_files.group(1)}")
    if m_cmd:
        print(f"  • {BOLD}Run Command:{RESET} {m_cmd.group(1).strip()}")
    print(f"\n{DIM}Run `tools/cycle.py advance` or ask `/cycle advance` when this step is verified.{RESET}\n")


def cmd_advance(stage_num: int = None):
    content = read_cycle_file()
    lines = content.splitlines()
    
    # Extract stages flexibly
    stage_regex = re.compile(r"^\|\s*\*\*(\d+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|")
    updated_lines = []
    current_active_found = False
    next_stage_to_activate = None
    
    for line in lines:
        m = stage_regex.match(line.strip())
        if m:
            num = int(m.group(1))
            focus = m.group(2).strip()
            target = m.group(3).strip()
            cmd = m.group(4).strip()
            status = m.group(5).strip()
            
            # Determine if this stage should be marked completed
            should_complete = False
            if stage_num is not None:
                if num == stage_num:
                    should_complete = True
            elif ("In Progress" in status or "Active" in status) and not current_active_found:
                should_complete = True
                current_active_found = True
                next_stage_to_activate = num + 1
            
            if should_complete:
                new_status = "`Completed`"
                line = f"| **{num}** | {focus} | {target} | {cmd} | {new_status} |"
            elif next_stage_to_activate and num == next_stage_to_activate:
                new_status = "`In Progress`"
                line = f"| **{num}** | {focus} | {target} | {cmd} | {new_status} |"
        
        updated_lines.append(line)
    
    new_content = "\n".join(updated_lines)
    write_cycle_file(new_content)
    print(f"{GREEN}✓ Active Practice Cycle successfully advanced!{RESET}")
    cmd_status()


def main():
    parser = argparse.ArgumentParser(description="Practice Cycle Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("status", help="Print active practice cycle HUD")
    subparsers.add_parser("next", help="Show instructions for immediate next task")
    
    adv_parser = subparsers.add_parser("advance", help="Mark current stage completed and advance")
    adv_parser.add_argument("--stage", type=int, default=None, help="Stage number to mark complete")
    
    subparsers.add_parser("init", help="Initialize or reset default cycle")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status()
    elif args.command == "next":
        cmd_next()
    elif args.command == "advance":
        cmd_advance(args.stage)
    elif args.command == "init":
        init_default_cycle()
        print(f"{GREEN}✓ Initialized default practice cycle in {CYCLE_FILE.name}{RESET}")


if __name__ == "__main__":
    main()
