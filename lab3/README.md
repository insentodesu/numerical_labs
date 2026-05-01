# Лабораторная №3 — приближение функций

Интерполяция (Лагранж, Ньютон для равных и неравных узлов) и кусочно-линейный сплайн. Подробный пошаговый вывод в Streamlit и графики (`matplotlib`). В коде `homework_lab3.py` — ссылки на лекции и формулы.

## Запуск

```bash
cd lab3
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
streamlit run homework_lab3_ui.py --server.port 8503
```

Параметры `g`, `k` — как в задании; при необходимости измените узлы и `f(x)` в `homework_lab3.py` (функции `table*_…` и `f_variant`).
