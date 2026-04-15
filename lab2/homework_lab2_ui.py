"""
Лаконичный UI лабораторной №2 в стиле "оформление для защиты":
только параметры g, k, epsilon и аккуратный LaTeX-вывод ключевых этапов.
"""
import streamlit as st

from homework_lab2 import (
    check_convergence_seidel,
    check_convergence_simple_iteration,
    jacobi_iterative_form,
    norm_inf,
    prepare_system_for_iterations,
    residual,
    seidel_solve,
    simple_iteration_solve,
    solve_gauss_elimination_column_pivot,
    trace_residual_latex,
    build_system,
)


def _fmt(x: float) -> str:
    return f"{x:.10g}"


def matrix_to_latex(A: list[list[float]]) -> str:
    if not A:
        return r"\begin{bmatrix}\end{bmatrix}"
    body = r" \\ ".join(" & ".join(_fmt(v) for v in row) for row in A)
    return rf"\begin{{bmatrix}}{body}\end{{bmatrix}}"


def vector_to_latex(v: list[float]) -> str:
    if not v:
        return r"\begin{bmatrix}\end{bmatrix}"
    body = r" \\ ".join(_fmt(x) for x in v)
    return rf"\begin{{bmatrix}}{body}\end{{bmatrix}}"


def augmented_to_latex(aug: list[list[float]]) -> str:
    n = len(aug)
    spec = "c" * n + "|c"
    rows = []
    for i in range(n):
        left = " & ".join(_fmt(v) for v in aug[i][:-1])
        rows.append(f"{left} & {_fmt(aug[i][-1])}")
    inner = r" \\ ".join(rows)
    return rf"\left[\begin{{array}}{{{spec}}}{inner}\end{{array}}\right]"


def system_cases_latex(A: list[list[float]], b: list[float]) -> str:
    """Система 3x3 в виде { ... } для красивого старта."""
    x_names = ["x", "y", "z"]
    eqs: list[str] = []
    for i in range(3):
        terms = []
        for j in range(3):
            a = A[i][j]
            if abs(a) < 1e-15:
                continue
            sign = "+" if a >= 0 else "-"
            coeff = abs(a)
            if coeff == 1:
                term_core = f"{x_names[j]}"
            else:
                term_core = f"{_fmt(coeff)}{x_names[j]}"
            if not terms:
                terms.append(term_core if a >= 0 else f"-{term_core}")
            else:
                terms.append(f" {sign} {term_core}")
        lhs = "".join(terms) if terms else "0"
        eqs.append(f"{lhs} = {_fmt(b[i])}")
    return r"\begin{cases}" + r"\\ ".join(eqs) + r"\end{cases}"


def iteration_table_latex_3(history: list[dict], epsilon: float) -> str:
    """
    Таблица для 3x3 в формате:
    k | x^k | y^k | z^k | ||x^(k+1)-x^k||_inf | сравнение с epsilon
    """
    rows: list[str] = []
    for i, rec in enumerate(history):
        xk, yk, zk = rec["x"]
        if i + 1 < len(history):
            d = history[i + 1]["delta_inf"]
            d_str = _fmt(d)
            rel = r"< \varepsilon" if d < epsilon else r"> \varepsilon"
        else:
            d_str = "-"
            rel = "-"
        rows.append(
            rf"{rec['k']} & {_fmt(xk)} & {_fmt(yk)} & {_fmt(zk)} & {d_str} & {rel}"
        )
    body = r" \\ ".join(rows)
    return (
        r"\begin{array}{c|c|c|c|c|c}"
        r"k & x^k & y^k & z^k & \|x^{k+1}-x^k\|_\infty & \text{сравнение} \\ \hline "
        + body
        + r"\end{array}"
    )


def render_latex_trace(lines: list[str]) -> None:
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s == "---":
            st.divider()
        else:
            st.markdown(line)


st.set_page_config(page_title="Лабораторная №2", layout="wide")
st.title("Лабораторная работа №2")

c1, c2, c3 = st.columns(3)
with c1:
    g_subgroup = st.number_input("g (номер подгруппы)", value=1, step=1, format="%d")
with c2:
    k_variant = st.number_input("k (номер варианта)", value=3, step=1, format="%d")
with c3:
    epsilon = st.number_input(
        "epsilon (погрешность)",
        min_value=1e-15,
        max_value=1.0,
        value=1e-3,
        format="%.1e",
    )

if not st.button("Рассчитать", type="primary"):
    st.stop()

# В реализации build_system: второй параметр соответствует g, третий - k.
A, b = build_system(3, int(g_subgroup), int(k_variant))

st.subheader("Исходная система")
st.latex(system_cases_latex(A, b))
st.latex(rf"A = {matrix_to_latex(A)},\quad \vec b = {vector_to_latex(b)}")

# ----------------------- Метод Гаусса -----------------------
xg, trace_lines, aug, _ = solve_gauss_elimination_column_pivot(A, b, trace_latex=True)
r = residual(A, b, xg)

st.subheader("Метод Гаусса")
st.markdown("**Последняя матрица перед обратным ходом:**")
st.latex(rf"[U\,|\,c] = {augmented_to_latex(aug)}")
st.latex(rf"\vec x_{{\mathrm{{Гаусс}}}} = {vector_to_latex(xg)}")
st.latex(rf"\vec r = A\vec x - \vec b = {vector_to_latex(r)}")
st.latex(rf"\|\vec r\|_\infty = {_fmt(norm_inf(r))}")

with st.expander("Подробная трассировка Гаусса (LaTeX)", expanded=False):
    render_latex_trace((trace_lines or []) + trace_residual_latex(A, b, xg))

# ----------------------- Подготовка к итерациям -----------------------
st.subheader("Итерационные методы")
try:
    A_it, b_it, row_perm = prepare_system_for_iterations(A, b)
except ValueError as e:
    st.error(f"Систему нельзя привести к удобному для итераций виду: {e}")
    st.stop()

if row_perm != [0, 1, 2]:
    st.markdown(f"Перестановка строк перед итерациями: `{[p + 1 for p in row_perm]}`")
st.latex(rf"A_{{it}} = {matrix_to_latex(A_it)},\quad \vec b_{{it}} = {vector_to_latex(b_it)}")

alpha, beta = jacobi_iterative_form(A_it, b_it)
st.latex(rf"\alpha = {matrix_to_latex(alpha)},\quad \beta = {vector_to_latex(beta)}")

ok_pi, msg_pi, _, _ = check_convergence_simple_iteration(alpha)
ok_sd, msg_sd, _, _, _ = check_convergence_seidel(alpha)

tab1, tab2 = st.tabs(["Метод простой итерации", "Метод Зейделя"])

with tab1:
    (st.success if ok_pi else st.warning)(msg_pi)
    x_pi, hist_pi = simple_iteration_solve(
        A_it, b_it, tol=float(epsilon), max_iter=500, verbose=False
    )
    st.latex(iteration_table_latex_3(hist_pi, float(epsilon)))
    r_pi = residual(A_it, b_it, x_pi)
    st.latex(rf"\vec x^* \approx {vector_to_latex(x_pi)}")
    st.latex(rf"\|\vec r\|_\infty = {_fmt(norm_inf(r_pi))}")

with tab2:
    (st.success if ok_sd else st.warning)(msg_sd)
    x_sd, hist_sd = seidel_solve(
        A_it, b_it, tol=float(epsilon), max_iter=500, verbose=False
    )
    st.latex(iteration_table_latex_3(hist_sd, float(epsilon)))
    r_sd = residual(A_it, b_it, x_sd)
    st.latex(rf"\vec x^* \approx {vector_to_latex(x_sd)}")
    st.latex(rf"\|\vec r\|_\infty = {_fmt(norm_inf(r_sd))}")
