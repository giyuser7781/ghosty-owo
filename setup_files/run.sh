#!/usr/bin/env bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

if command -v python3 >/dev/null 2>&1; then
    python3 main.py "$@"
elif command -v python >/dev/null 2>&1; then
    python main.py "$@"
else
    echo "[!] Python is not installed or not in PATH."
    exit 1
fi
