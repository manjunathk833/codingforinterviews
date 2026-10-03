#!/usr/bin/env bash
# ==============================================================================
# Automated Pull Request Creator for Antigravity GitHub Agent
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"

cd "$REPO_ROOT"

# Run safety check first
bash "$SCRIPT_DIR/safety_check.sh"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
TARGET_BASE="${1:-main}"
TITLE="${2:-Sync $CURRENT_BRANCH into $TARGET_BASE}"
BODY_FILE="${3:-}"

echo "============================================================"
echo "      🚀 PREPARING PULL REQUEST"
echo "============================================================"
echo "Source Branch : $CURRENT_BRANCH"
echo "Target Base   : $TARGET_BASE"
echo "PR Title      : $TITLE"

# Push branch to remote
echo "▶ Pushing $CURRENT_BRANCH to origin..."
git push -u origin "$CURRENT_BRANCH"

# Check GitHub CLI authentication
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    echo "▶ Creating PR via GitHub CLI (gh)..."
    CMD=("gh" "pr" "create" "--base" "$TARGET_BASE" "--head" "$CURRENT_BRANCH" "--title" "$TITLE")
    if [ -n "$BODY_FILE" ] && [ -f "$BODY_FILE" ]; then
        CMD+=("--body-file" "$BODY_FILE")
    else
        CMD+=("--body" "Automated PR created by Antigravity GitHub Agent.")
    fi
    "${CMD[@]}"
else
    # Fallback to browser URL
    REMOTE_URL="$(git remote get-url origin | sed -e 's/\.git$//' -e 's/git@github.com:/https:\/\/github.com\//')"
    COMPARE_URL="$REMOTE_URL/compare/$TARGET_BASE...$CURRENT_BRANCH?expand=1"
    echo "ℹ️  GitHub CLI is not authenticated. Review and open your PR in the browser:"
    echo "👉 $COMPARE_URL"
fi

exit 0
