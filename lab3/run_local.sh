#!/usr/bin/env bash
# Лабораторная №3 на порту 8503 (как в portal/run_local.sh).
set -euo pipefail
cd "$(dirname "$0")"
if [[ -f venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  . venv/bin/activate
fi
exec streamlit run homework_lab3_ui.py --server.port 8503 "$@"
