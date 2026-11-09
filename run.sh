#!/usr/bin/env bash
# Quick launcher for problem testing and management
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -x "$DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/.venv/bin/python3"
else
    PYTHON_BIN="python3"
fi
"$PYTHON_BIN" "$DIR/tools/runner.py" "$@"
