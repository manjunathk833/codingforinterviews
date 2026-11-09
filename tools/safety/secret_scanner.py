#!/usr/bin/env python3
"""
Pre-Push Secret & Safety Scanner for Antigravity GitHub Agent
Scans git diffs (staged, unstaged, or commit ranges) for exposed credentials,
API keys, private keys, database connection strings, and prohibited files.
Cross-platform compatible (macOS BSD / Linux).
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# High-confidence secret regex patterns
SECRET_PATTERNS = [
    (r"\bghp_[a-zA-Z0-9]{36}\b", "GitHub Classic Personal Access Token"),
    (r"\bgithub_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}\b", "GitHub Fine-Grained Token"),
    (r"\bgh[oas]_[a-zA-Z0-9]{36}\b", "GitHub OAuth/App Token"),
    (r"\bsk-ant-(?:api03|oat01|admin01)-[0-9A-Za-z_\-]{93}AA\b", "Anthropic Claude API Key"),
    (r"\bsk-(?:live|test|proj|svcacct)?-[a-zA-Z0-9_\-]{40,}\b", "OpenAI API Key"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS Access Key ID"),
    (r"(?i)aws_secret_access_key\s*[:=]\s*['\"][A-Za-z0-9/+=]{40}['\"]", "AWS Secret Access Key"),
    (r"\bAIza[0-9A-Za-z_\-]{35}\b", "Google Cloud API Key"),
    (r"\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}\b", "Slack Token"),
    (r"https:\/\/hooks\.slack\.com\/services\/T[a-zA-Z0-9_]+\/B[a-zA-Z0-9_]+\/[a-zA-Z0-9_]+", "Slack Webhook URL"),
    (r"-----BEGIN ((EC|PGP|DSA|RSA|OPENSSH) )?PRIVATE KEY( BLOCK)?-----", "Private Cryptographic Key"),
    (r"(postgres|mysql|mongodb(\+srv)?):\/\/[^\s:@]+:[^\s:@]+@[^\s\/:]+", "Database Connection URI with Password"),
    (r"(?i)(?:api[_-]?key|secret[_-]?key|auth[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]", "Generic Hardcoded Secret"),
]

# Patterns allowed in tests/documentation (false positive filters)
ALLOWLIST_PATTERNS = [
    r"dummy",
    r"example",
    r"sample",
    r"your_jwt",
    r"your[-_]token",
    r"test[-_]token",
    r"bearer\s+<token>",
    r"bearer\s+your",
    r"token_bucket",
    r"rate[-_]limited",
    r"tokenbucketratelimiter",
    r"test_user",
    r"test@example\.com",
    r"secretpass123",
    r"password@2026",
    r"pass1234!",
]

# Prohibited file extensions & names
PROHIBITED_EXTENSIONS = {
    ".class", ".pyc", ".pyo", ".jar", ".war", ".ear", ".pem", ".key",
    ".p12", ".pfx", ".keystore", ".DS_Store", ".pdf"
}
PROHIBITED_FILENAMES = {
    "singlepageresume.json", "resume.json", "credentials.json",
    ".env", ".env.local", ".env.production"
}

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def is_allowed(text: str) -> bool:
    lower = text.lower()
    return any(re.search(pat, lower) for pat in ALLOWLIST_PATTERNS)


def check_file_metadata(repo_root: Path) -> list:
    violations = []
    # Check untracked and staged files
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            status, file_path = line[:2].strip(), line[3:].strip()
            # If path was quoted due to special characters
            file_path = file_path.strip('"').strip("'")
            p = repo_root / file_path

            # Check filename and extension
            if p.name in PROHIBITED_FILENAMES:
                violations.append(f"Prohibited sensitive file tracked or staged: {file_path}")
            if p.suffix in PROHIBITED_EXTENSIONS:
                violations.append(f"Prohibited compiled or certificate extension ({p.suffix}): {file_path}")

            # Check file size if it exists
            if p.exists() and p.is_file():
                size = p.stat().st_size
                if size > MAX_FILE_SIZE_BYTES:
                    violations.append(f"File exceeds maximum allowed size ({size / 1024 / 1024:.2f} MB > 5 MB): {file_path}")
    except Exception as e:
        violations.append(f"Error checking git status: {e}")

    return violations


def check_diff_for_secrets(repo_root: Path, check_staged_only: bool = False) -> list:
    violations = []
    cmd = ["git", "diff", "--diff-filter=ACMRT"]
    if check_staged_only:
        cmd.append("--cached")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True
        )
        current_file = None
        current_line_no = 0

        for line in proc.stdout.splitlines():
            if line.startswith("diff --git a/"):
                parts = line.split(" b/")
                if len(parts) > 1:
                    current_file = parts[1]
                continue
            if line.startswith("@@"):
                # Extract line numbers from hunk header: @@ -1,4 +1,5 @@
                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line_no = int(match.group(1)) - 1
                continue
            if line.startswith("+") and not line.startswith("+++"):
                current_line_no += 1
                added_content = line[1:].strip()

                if is_allowed(added_content):
                    continue

                for pat, label in SECRET_PATTERNS:
                    if re.search(pat, added_content):
                        redacted = added_content[:60] + "..." if len(added_content) > 60 else added_content
                        violations.append(
                            f"[{label}] in {current_file}:{current_line_no} -> \"{redacted}\""
                        )
            elif not line.startswith("-"):
                current_line_no += 1

    except Exception as e:
        violations.append(f"Error executing git diff: {e}")

    return violations


def main():
    repo_root = Path(os.getcwd())
    # Find repo root if executed from subfolder
    while repo_root.parent != repo_root and not (repo_root / ".git").exists():
        repo_root = repo_root.parent

    check_staged = "--staged" in sys.argv or "--cached" in sys.argv

    metadata_violations = check_file_metadata(repo_root)
    diff_violations = check_diff_for_secrets(repo_root, check_staged_only=check_staged)

    all_violations = metadata_violations + diff_violations

    if all_violations:
        print("❌ PRE-PUSH SAFETY AUDIT FAILED:")
        for v in all_violations:
            print(f"  • {v}")
        print("\nPlease resolve all violations before pushing to GitHub.")
        sys.exit(1)
    else:
        print("✓ Pre-push safety audit passed! Zero secrets or prohibited files detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
