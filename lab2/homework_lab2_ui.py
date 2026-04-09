"""
Веб-интерфейс лабораторной №2 на Streamlit: ввод A и b, расчёт Гаусса,
определитель, невязка, трассировка; методы простой итерации и Зейделя
с проверкой сходимости и таблицей по каждой итерации (k, x, ||dx||, оценка, ||r||).
"""
import math

import pandas as pd
import streamlit as st

from homework_lab2 import (
    build_system,
    check_convergence_seidel,
    check_convergence_simple_iteration,
    determinant_gauss_pivot,
    jacobi_iterative_form,
    norm_inf,
    residual,
    seidel_solve,
    simple_iteration_solve,
    solve_gauss_elimination_column_pivot,
    trace_residual_latex,
)

# Допустимый размер системы в интерфейсе (квадратная матрица n×n).
N_MIN, N_MAX = 2, 16


def render_latex_trace(lines: list[str]) -> None:
    """
    Выводит список строк трассировки в Streamlit.

    Маркер "---" превращается в горизонтальный разделитель; остальное — markdown
    (в т.ч. встроенный LaTeX в $...$).
    """
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s == "---":
            st.divider()
        else:
            st.markdown(line)


def add_x_cols(row: dict, x: list[float]) -> dict:
    """Добавляет в словарь строки таблицы поля x_1, x_2, ... из вектора решения."""
    for i, v in enumerate(x):
        row[f"x_{i + 1}"] = v
    return row


def iteration_history_to_dataframe(history: list[dict], n: int) -> pd.DataFrame:
    """Таблица шагов: k, x_1..x_n, ||dx||_inf, оценка, ||r||_inf; для Зейделя — ещё q из лекции 9."""
    has_q = any("q" in rec for rec in history)
    rows: list[dict] = []
    for rec in history:
        row: dict = {
            "k": rec["k"],
            "||dx||_inf": rec.get("delta_inf"),
            "оценка": rec.get("accuracy_est"),
            "||r||_inf": rec.get("residual_inf"),
        }
        if has_q:
            row["q"] = rec.get("q")
        for i in range(n):
            row[f"x_{i + 1}"] = rec["x"][i]
        rows.append(row)
    return pd.DataFrame(rows)


def _df_blank_nan(df: pd.DataFrame) -> pd.DataFrame:
    """Пустые ячейки вместо NaN (удобнее читать k=0 без шага dx)."""
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].apply(
            lambda v: "" if isinstance(v, float) and math.isnan(v) else v
        )
    return out


def shape_ok(A: list[list[float]], b: list[float], n: int) -> bool:
    """Проверка: A квадратная n×n, длина b равна n."""
    if len(A) != n or len(b) != n:
        return False
    return all(len(row) == n for row in A)


# --- Оформление страницы ---
st.set_page_config("Лабораторная №2", layout="wide")
st.markdown(
    "<style>.stButton>button{background:#FFD700!important;color:#111!important;font-weight:600!important}</style>",
    unsafe_allow_html=True,
)

st.title("Лабораторная №2: Гаусс, простая итерация, Зейдель")
st.caption(r"Решение $Ax=b$ · $\det A$ · невязка · итерации с проверкой сходимости")

# --- Параметры: размер n и режим задания матрицы ---
r1 = st.columns([1, 2])
with r1[0]:
    n = st.number_input("n", min_value=N_MIN, max_value=N_MAX, value=3, key="n_dim")
with r1[1]:
    mode = st.selectbox(
        "Матрица A и вектор b",
        ["lab", "manual"],
        format_func=lambda m: "По заданию (g, k)" if m == "lab" else "Вручную",
        key="mode",
    )

# В режиме «lab» ждём целые g и k; пока не введены — дальше показываем подсказку / ручной ввод.
g = k = None
if mode == "lab":
    c1, c2 = st.columns(2)
    with c1:
        gs = st.text_input("g (вариант, коэффициенты A)", "", key="g_in")
    with c2:
        ks = st.text_input("k (подгруппа, правая часть b)", "", key="k_in")
    bad = False
    if gs.strip():
        try:
            g = int(gs.strip())
        except ValueError:
            st.error("g — целое число.")
            bad = True
    if ks.strip():
        try:
            k = int(ks.strip())
        except ValueError:
            st.error("k — целое число.")
            bad = True
    if bad:
        st.stop()

st.subheader("A и b")

# --- Формирование A_list, b_list: из build_system или из редакторов ---
if mode == "lab" and g is not None and k is not None:
    A_list, b_list = build_system(int(n), g, k)
    st.success(f"**g**={g} в A, **k**={k} в b, **n**={n}.")
    if n == 3:
        # Система в виде, совпадающем с записью в задании (LaTeX cases).
        st.latex(
            rf"\begin{{cases}}{g}x+({g}+1)y+({g}+2)z={k}\\"
            rf"2\cdot{g}x+({g}+5)y+({g}-6)z={k}+1\\"
            rf"3\cdot{g}x+({g}-1)y-3z={k}+2\end{{cases}}"
        )
else:
    if mode == "lab":
        st.info("Введите **g** и **k** или переключитесь на ввод вручную.")
    # Заготовки под data_editor; пользователь правит ячейки.
    A_list = [[0.0] * n for _ in range(n)]
    b_list = [0.0] * n
    an = [f"a{j + 1}" for j in range(n)]
    ed_a = st.data_editor(
        pd.DataFrame(A_list, columns=an, index=[f"{i + 1}" for i in range(n)]),
        key=f"ea{n}",
        num_rows="fixed",
        use_container_width=True,
    )
    ed_b = st.data_editor(
        pd.DataFrame({"b": b_list}, index=[f"{i + 1}" for i in range(n)]),
        key=f"eb{n}",
        num_rows="fixed",
        use_container_width=True,
    )
    try:
        A_list = ed_a.iloc[:n, :n].astype(float).values.tolist()
        b_list = ed_b.iloc[:n, 0].astype(float).tolist()
    except Exception:
        pass

# Предпросмотр текущих A и b (и для lab, и после ручного ввода).
st.dataframe(
    pd.DataFrame(A_list, columns=[f"a_{j + 1}" for j in range(n)], index=range(1, n + 1)),
    use_container_width=True,
)
st.text("b = " + ", ".join(f"{v:.6g}" for v in b_list))

st.divider()

# До нажатия кнопки тяжёлые расчёты не выполняем.
if not st.button("Рассчитать", type="primary"):
    st.stop()

if mode == "lab" and (g is None or k is None):
    st.error("Введите g и k.")
    st.stop()
if not shape_ok(A_list, b_list, int(n)):
    st.error("Нужна квадратная A размера n×n и длина b равна n.")
    st.stop()

# --- Определитель (отдельный проход Гаусса по копии A) ---
try:
    det_a = determinant_gauss_pivot(A_list)
except Exception as e:
    st.error(f"det A: {e}")
    st.stop()

# --- Решение с полной трассировкой; aug — [U|c] для таблицы ---
x_g, trace_lines = [0.0] * int(n), []
aug = [list(A_list[i]) + [float(b_list[i])] for i in range(int(n))]
gstat = {"forward_pass_outer_iterations": int(n), "row_swaps": 0, "elimination_ops": 0}
try:
    x_g, trace_lines, aug, gstat = solve_gauss_elimination_column_pivot(
        A_list, b_list, trace_latex=True
    )
except ValueError as e:
    st.error(str(e))
    st.stop()

# Невязка и объединённая трассировка: Гаусс + пошаговый разбор r = Ax − b.
r_vec = residual(A_list, b_list, x_g)
full_trace = (trace_lines or []) + trace_residual_latex(A_list, b_list, x_g)
xc = [f"x_{i + 1}" for i in range(int(n))]

# --- Результаты: решение, норма невязки, det, верхнетреугольная форма ---
st.subheader("Решение и невязка")
st.dataframe(
    pd.DataFrame(
        [
            add_x_cols(
                {
                    "||r||_inf": norm_inf(r_vec),
                    "компоненты r": ", ".join(f"{v:.6g}" for v in r_vec),
                },
                x_g,
            )
        ]
    )[["||r||_inf", "компоненты r"] + xc],
    use_container_width=True,
)
st.markdown(rf"$\vec r^T = ({', '.join(f'{v:.6g}' for v in r_vec)})$")

st.subheader(f"det A = {det_a:.10g}")

st.subheader("Прямой ход")
st.write(
    f"Столбцов: **{gstat['forward_pass_outer_iterations']}**, "
    f"перестановок строк: **{gstat['row_swaps']}**, "
    f"обновлений a_ij: **{gstat['elimination_ops']}**."
)
st.markdown("**[U | c]** после прямого хода:")
st.dataframe(
    pd.DataFrame(
        aug,
        columns=[f"a_{j + 1}" for j in range(int(n))] + ["b"],
        index=range(1, int(n) + 1),
    ),
    use_container_width=True,
)

with st.expander("Подробная трассировка (как в лаб. №1)", expanded=True):
    render_latex_trace(full_trace)

# --- Итерационные методы: та же A, b; этап 1 - проверка сходимости, этап 2 - таблица итераций ---
st.divider()
st.subheader("Итерационные методы (лекции 8-9)")
it_col1, it_col2 = st.columns(2)
with it_col1:
    it_tol = st.number_input(
        "tol (останов при ||x^(k)-x^(k-1)||_inf < tol)",
        min_value=1e-15,
        max_value=1.0,
        value=1e-8,
        format="%.1e",
        key="it_tol",
    )
with it_col2:
    it_max = st.number_input("max_iter", min_value=1, max_value=5000, value=500, key="it_max")

try:
    _alpha_chk, _beta_chk = jacobi_iterative_form(A_list, b_list)
except ValueError as e:
    st.warning(f"Итерации недоступны (нужны ненулевые диагонали a_ii): {e}")
else:
    ok_pi, msg_pi, _, _ = check_convergence_simple_iteration(_alpha_chk)
    ok_sd, msg_sd, _, _, _ = check_convergence_seidel(_alpha_chk)

    tab_pi, tab_sd = st.tabs(["Простая итерация", "Зейдель"])

    with tab_pi:
        st.markdown("**Этап 1 - проверка сходимости**")
        if ok_pi:
            st.success(msg_pi)
        else:
            st.warning(msg_pi)
        try:
            x_pi, hist_pi = simple_iteration_solve(
                A_list,
                b_list,
                tol=float(it_tol),
                max_iter=int(it_max),
                verbose=False,
            )
        except ValueError as e:
            st.error(str(e))
        else:
            st.markdown("**Этап 2 - приближения по шагам**")
            df_pi = iteration_history_to_dataframe(hist_pi, int(n))
            st.dataframe(
                _df_blank_nan(df_pi),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                f"Итоговое x (последняя итерация): {', '.join(f'{v:.10g}' for v in x_pi)}"
            )

    with tab_sd:
        st.markdown("**Этап 1 - проверка сходимости**")
        if ok_sd:
            st.success(msg_sd)
        else:
            st.warning(msg_sd)
        try:
            x_sd, hist_sd = seidel_solve(
                A_list,
                b_list,
                tol=float(it_tol),
                max_iter=int(it_max),
                verbose=False,
            )
        except ValueError as e:
            st.error(str(e))
        else:
            st.markdown("**Этап 2 - приближения по шагам**")
            df_sd = iteration_history_to_dataframe(hist_sd, int(n))
            st.dataframe(
                _df_blank_nan(df_sd),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                f"Итоговое x: {', '.join(f'{v:.10g}' for v in x_sd)}. "
                f"Параметр q см. в тексте этапа 1 (лекция 9: сходимость при q < 1)."
            )
