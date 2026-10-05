#!/usr/bin/env bash
# Read-only, failure-propagating operator/CI entry point; never accesses a cluster.
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$task_root"
if [[ -x .venv/bin/python ]]; then
  task_python=.venv/bin/python
elif [[ -x .venv/Scripts/python.exe ]]; then
  task_python=.venv/Scripts/python.exe
else
  task_python=python
fi
"$task_python" scripts/verify_deployment.py
