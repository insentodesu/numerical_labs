# numerical_labs

Лабораторные по численным методам: Streamlit-портал и три работы.

| Каталог   | Содержимое |
|-----------|------------|
| `portal/` | Портал [labs.inst.rest](https://labs.inst.rest): переходы в лаб. №1–№3 |
| `lab1/`   | Лабораторная №1 — нелинейные уравнения и системы (`homework_ui.py`) |
| `lab2/`   | Лабораторная №2 — Гаусс, простая итерация, Зейдель (`homework_lab2_ui.py`) |
| `lab3/`   | Лабораторная №3 — интерполяция Лагранжа/Ньютона, линейный сплайн (`homework_lab3_ui.py`) |

## Локальный запуск

```bash
cd portal && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && cd ..
# то же для lab1, lab2 и lab3 (отдельный venv в каждой папке)
./portal/run_local.sh
```

Открыть [http://127.0.0.1:8500](http://127.0.0.1:8500).

## Деплой на VPS

Пошаговая инструкция (Nginx, systemd, HTTPS): [`portal/deploy/README.md`](portal/deploy/README.md).

Кратко: клонировать репозиторий в `/opt/labs/numerical_labs`, создать `venv` в `portal`, `lab1`, `lab2`, `lab3`, подставить production-конфиги Streamlit из `portal/deploy/configs/`, включить юниты из `portal/deploy/systemd/`.

## Репозиторий

Исходники: [github.com/insentodesu/numerical_labs](https://github.com/insentodesu/numerical_labs).
