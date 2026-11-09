#!/usr/bin/env bash
# ==============================================================================
# Pre-Push Safety Audit Entrypoint for Antigravity GitHub Agent
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"

cd "$REPO_ROOT"

echo "============================================================"
echo "      🛡️  ANTIGRAVITY PRE-PUSH SAFETY AUDIT"
echo "============================================================"

# 1. Branch Protection Check
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "▶ Checking active branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "⚠️  WARNING: Direct commits to 'main' are discouraged!"
    echo "   Best practice is to work on 'develop' (or feature branch) and merge to 'main' via Pull Request."
    echo "   To switch to develop: git checkout -b develop"
fi

# 2. Gitignore Integrity
echo "▶ Verifying .gitignore integrity..."
if [ ! -f ".gitignore" ]; then
    echo "❌ Error: .gitignore file is missing at repository root!"
    exit 1
fi

REQUIRED_PATTERNS=(".env" "*.class" ".build/" "__pycache__" "allure-results/" "*resume*")
for pat in "${REQUIRED_PATTERNS[@]}"; do
    if ! grep -q "$pat" .gitignore; then
        echo "❌ Warning: Critical ignore pattern '$pat' not found in .gitignore!"
        exit 1
    fi
done
echo "  ✓ .gitignore contains all required security and build exclusions."

# 3. Secret & Prohibited File Scanning
echo "▶ Executing secret and file metadata scan..."
python3 "$SCRIPT_DIR/secret_scanner.py" "$@"

# 4. Git Porcelain Status
echo "▶ Checking git status..."
MODIFIED_COUNT="$(git status --porcelain | wc -l | tr -d ' ')"
echo "  Found $MODIFIED_COUNT pending change(s) in working tree."

echo "============================================================"
echo "  ✅ Pre-push safety check COMPLETED SUCCESSFULLY!"
echo "============================================================"
exit 0
