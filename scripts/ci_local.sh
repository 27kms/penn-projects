#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python3 scripts/check_archive.py
python3 -m unittest discover -s scripts -p 'test_*.py'
