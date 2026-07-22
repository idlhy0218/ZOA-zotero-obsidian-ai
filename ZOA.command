#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ -d ".venv" ]; then
    "./.venv/bin/python" zoa.py
else
    python3 zoa.py
fi
