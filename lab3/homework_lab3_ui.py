"""
Streamlit: лабораторная «Приближение функций» — LaTeX-оформление как в lab2.
"""
from __future__ import annotations

import streamlit as st

from homework_lab3 import (
    build_tables,
    divided_differences_coeffs,
    f_variant,
    lagrange_interpolate,
    linear_spline,
    newton_eval_divided_differences,
    newton_forward_equal_spacing,
    newton_interpolate_general,
    spline_test_points,
    table1_test_points,
    table2_test_points,
)


def _fmt(x: float) -> str:
    return f"{x:.10g}"


def latex_cases_table1(g: int, k: int) -> str:
    base = g - 2 * k
    return (
        rf"\begin{{cases}}"
        rf"x_0={base}-3,\ x_1={base}-1,\ x_2={base},\ x_3={base}+2\\"
        rf"f(x)=\sin x+\dfrac{{{g}}}{{{k}}}"
        rf"\end{{cases}}"
    )


def latex_array_row(vals: list[float]) -> str:
    return " & ".join(_fmt(v) for v in vals)


st.set_page_config(page_title="Лабораторная · интерполяция", layout="wide")
st.title("Лабораторная №3: приближение функций (интерполяция)")
st.caption(
    "В репозитории это отдельная работа (lab3). Узлы и вид f(x) задаются в `homework_lab3.py` — при расхождении с вашей методичкой правьте там."
)

c1, c2 = st.columns(2)
with c1:
    g = st.number_input("g (номер подгруппы)", value=1, step=1, format="%d")
with c2:
    k = st.number_input("k (номер варианта, k≠0)", value=3, step=1, format="%d")

if not st.button("Рассчитать", type="primary"):
    st.stop()

if int(k) == 0:
    st.error("В задании f(x)=sin(x)+g/k требуется k≠0.")
    st.stop()

g_i, k_i = int(g), int(k)
data = build_tables(g_i, k_i)
x1, y1 = data["table1"]
x2, y2 = data["table2"]
h2 = data["h2"]
x0_2 = data["x0_table2"]

st.markdown("### Исходные данные")
st.latex(rf"f(x)=\sin x+\dfrac{{{g_i}}}{{{k_i}}}")
st.latex(latex_cases_table1(g_i, k_i))

st.markdown("### Таблица 1 (неравноотстоящие узлы)")
st.latex(
    rf"\begin{{array}}{{c|cccc}}"
    rf"x & {latex_array_row(x1)} \\ \hline"
    rf"y & {latex_array_row(y1)}"
    rf"\end{{array}}"
)

st.markdown("### Таблица 2 (равноотстоящие узлы, шаг h)")
st.latex(rf"h = x_1-x_0 = {_fmt(h2)}")
st.latex(
    rf"\begin{{array}}{{c|cccc}}"
    rf"x & {latex_array_row(x2)} \\ \hline"
    rf"y & {latex_array_row(y2)}"
    rf"\end{{array}}"
)

# --- Задание 1: Лагранж на равноотстоящих узлах (демонстрация на табл. 2) ---
st.divider()
st.subheader("1. Многочлен Лагранжа (равноотстоящие узлы)")
st.markdown(
    "Лекция 1: постановка интерполяции $P_n(x_i)=y_i$. "
    "Лекция 2: вид $P_n(x)=\\sum y_i\\ell_i(x)$, базис $\\ell_i(x_j)=\\delta_{ij}$. "
    "Для равноотстоящих узлов $x_i=x_0+ih$ (лекция 3) формула Лагранжа та же."
)
demo_x = x0_2 + 0.37 * h2
L_demo = lagrange_interpolate(x2, y2, demo_x)
f_demo = f_variant(demo_x, g_i, k_i)
st.latex(rf"x_{{\mathrm{{demo}}}} = x_0+0{{,}}37h = {_fmt(demo_x)}")
st.latex(rf"P_3(x_{{\mathrm{{demo}}}}) = {_fmt(L_demo)},\quad f(x_{{\mathrm{{demo}}}}) = {_fmt(f_demo)}")

# --- Задание 2 ---
st.divider()
st.subheader("2. Лагранж и Ньютон по таблице 1 (неравноотстоящие узлы)")
st.markdown(
    "Ньютон: лекция 4, разделённые разности (47) и формула (49). "
    "Опционально: перенумерация узлов по $|x-x_i|$ (рекомендация из лекции 4 к вычислению)."
)
pts1 = table1_test_points(g_i, k_i)
rows = []
for xv in pts1:
    f_ex = f_variant(xv, g_i, k_i)
    L = lagrange_interpolate(x1, y1, xv)
    N0 = newton_interpolate_general(x1, y1, xv, reorder=False)
    N1 = newton_interpolate_general(x1, y1, xv, reorder=True)
    rows.append(
        rf"{_fmt(xv)} & {_fmt(f_ex)} & {_fmt(L)} & {_fmt(N0)} & {_fmt(N1)} & {_fmt(abs(L-f_ex))} & {_fmt(abs(N0-f_ex))}"
    )
body = r" \\ ".join(rows)
st.latex(
    r"\begin{array}{c|ccccc|c}"
    r"x & f(x) & L(x) & N(x) & N_{\mathrm{пер}}(x) & |L-f| & |N-f| \\ \hline"
    + body
    + r"\end{array}"
)

# --- Задание 3 ---
st.divider()
st.subheader("3. Ньютон по таблице 2 (равноотстоящие узлы)")
st.markdown(
    "Лекция 3–4: конечные разности и первая формула Ньютона (46) с $q=(x-x_0)/h$."
)
x2_rev = list(reversed(x2))
y2_rev = list(reversed(y2))
pts2 = table2_test_points(g_i, k_i)
rows2 = []
for xv in pts2:
    f_ex = f_variant(xv, g_i, k_i)
    Nf = newton_forward_equal_spacing(x0_2, h2, y2, xv)
    c_rev = divided_differences_coeffs(x2_rev, y2_rev)
    Nr = newton_eval_divided_differences(x2_rev, c_rev, xv)
    rows2.append(
        rf"{_fmt(xv)} & {_fmt(f_ex)} & {_fmt(Nf)} & {_fmt(Nr)} & {_fmt(abs(Nf-Nr))} & {_fmt(abs(Nf-f_ex))}"
    )
body2 = r" \\ ".join(rows2)
st.latex(
    r"\begin{array}{c|ccccc}"
    r"x & f(x) & N_{\rightarrow}(x) & N_{\leftarrow}(x) & |N_\rightarrow-N_\leftarrow| & |N_\rightarrow-f| \\ \hline"
    + body2
    + r"\end{array}"
)
st.caption(
    "Здесь $N_{\\rightarrow}$ — формула (46) в порядке узлов таблицы, "
    "$N_{\\leftarrow}$ — тот же многочлен Ньютона по разделённым разностям для узлов в обратном порядке."
)

# --- Задание 4 ---
st.divider()
st.subheader("4. Линейный сплайн по таблице 1")
st.markdown("Лекция 5: кусочно-линейная функция (50)–(51).")
pts_s = spline_test_points(g_i, k_i)
rows_s = []
for xv in pts_s:
    f_ex = f_variant(xv, g_i, k_i)
    s = linear_spline(x1, y1, xv)
    rows_s.append(rf"{_fmt(xv)} & {_fmt(f_ex)} & {_fmt(s)} & {_fmt(abs(s-f_ex))}")
body_s = r" \\ ".join(rows_s)
st.latex(
    r"\begin{array}{c|ccc}"
    r"x & f(x) & S_{\mathrm{lin}}(x) & |S-f| \\ \hline"
    + body_s
    + r"\end{array}"
)
