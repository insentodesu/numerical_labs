#!/usr/bin/env bash
# Портал на 8500 + лаб. №1 (8501) + лаб. №2 (8502). Останов: Ctrl+C.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
LAB1="$ROOT/lab1"
LAB2="$ROOT/lab2"

cleanup() {
  for pid in $(jobs -p 2>/dev/null || true); do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

if [[ -f "$LAB1/venv/bin/activate" ]]; then
  (cd "$LAB1" && . venv/bin/activate && streamlit run homework_ui.py --server.port 8501 --server.headless true) &
else
  echo "Нет venv в лаб. №1 — запустите вручную: streamlit run homework_ui.py --server.port 8501" >&2
fi

if [[ -f "$LAB2/venv/bin/activate" ]]; then
  (cd "$LAB2" && . venv/bin/activate && streamlit run homework_lab2_ui.py --server.port 8502 --server.headless true) &
else
  echo "Нет venv в лаб. №2 — запустите вручную." >&2
fi

sleep 2
export LAB1_URL="${LAB1_URL:-http://127.0.0.1:8501/}"
export LAB2_URL="${LAB2_URL:-http://127.0.0.1:8502/}"
cd "$HERE"
if [[ -f "$HERE/venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  . "$HERE/venv/bin/activate"
elif [[ -f "$LAB2/venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  . "$LAB2/venv/bin/activate"
fi
streamlit run app.py --server.port 8500
