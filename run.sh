#!/usr/bin/env bash
# Quick launcher for problem testing and management
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 "$DIR/tools/runner.py" "$@"
