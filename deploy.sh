#!/usr/bin/env bash
set -euo pipefail

# Lightweight deployment/setup script for Unix-like servers
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate

pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Run tests if pytest is available (non-fatal)
if command -v pytest >/dev/null 2>&1; then
  pytest || true
fi

# Prefer gunicorn (production) else fallback to running main.py
if command -v gunicorn >/dev/null 2>&1; then
  exec gunicorn -w 4 -b 0.0.0.0:8000 main:app
else
  exec python main.py
fi
