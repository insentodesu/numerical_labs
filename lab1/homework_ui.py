from functools import partial
import matplotlib
matplotlib.use("Agg")  
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from homework_2_3 import EPS, EPS_SYS, f2, f2_prime, f2_prime2, f3, f3_prime
from homework_2_3 import f6_1, f6_2, find_bracket
from homework_2_3 import method_iteration, method_newton, method_secant
from homework_2_3 import method_iteration_system, method_newton_system
st.set_page_config("Лабораторная работа №1", layout="centered")
st.write("# Лабораторная работа №1. Решение нелинейных уравнений и систем")
st.markdown("""
<style>
    .stApp { background-color: #000; }
    h1, h2, h3, p, label { color: #FAFAFA !important; }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; }
    .stButton > button { background: #FFD700 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)
tab6, tab1, tab2 = st.tabs(["Задание 6", "Задание 2", "Задание 3"])
def param_inputs(key_prefix, default_k=22, default_g=1):
    c1, c2 = st.columns(2)
    with c1:
        try:
            k = int(st.text_input("k", value=str(default_k), key=f"{key_prefix}_k") or str(default_k))
        except ValueError:
            k = default_k
    with c2:
        try:
            g = int(st.text_input("g", value=str(default_g), key=f"{key_prefix}_g") or str(default_g))
        except ValueError:
            g = default_g
    return k, g
def eps_input(key, default=0.05):
    return st.number_input("ε (точность)", value=float(default), min_value=1e-6, format="%.6f", step=0.01, key=key)
def render_latex_trace(lines: list) -> None:
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s == "---":
            st.divider()
        else:
            st.markdown(line)
def plot_single_graph(f, a: float, b: float, margin: float = 0.3):
    x_min = min(a, b) - margin
    x_max = max(a, b) + margin
    x = np.linspace(x_min, x_max, 200)
    y = np.vectorize(f)(x)
    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#000000")
    ax.set_facecolor("#000000")
    ax.plot(x, y, color="#FFD700", linewidth=2, label="$f(x)$")
    ax.axvline(a, color="#FFA500", linestyle="--", linewidth=2, label=f"$a = {a:.4f}$")
    ax.axvline(b, color="#FFA500", linestyle="--", linewidth=2, label=f"$b = {b:.4f}$")
    ax.axhline(0, color="#666666", linestyle="-", linewidth=0.5)
    y_lo, y_hi = y.min() - 0.5, y.max() + 0.5
    ax.fill_betweenx([y_lo, y_hi], a, b, alpha=0.15, color="#FFD700")
    ax.set_xlabel("x", color="#FAFAFA")
    ax.set_ylabel("f(x)", color="#FAFAFA")
    ax.set_title("Отрезок [a, b] с переменой знака", color="#FAFAFA")
    ax.legend(facecolor="#1A1A1A", edgecolor="#FFD700", labelcolor="#FAFAFA")
    ax.tick_params(colors="#FAFAFA")
    ax.spines["bottom"].set_color("#FFD700")
    ax.spines["top"].set_color("#FFD700")
    ax.spines["left"].set_color("#FFD700")
    ax.spines["right"].set_color("#FFD700")
    ax.grid(True, alpha=0.3, color="#FFD700")
    plt.tight_layout()
    return fig
def plot_system_graph(x_range, y_range, k, g, resolution=150):
    x_min, x_max = x_range
    y_min, y_max = y_range
    x = np.linspace(x_min, x_max, resolution)
    y = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(x, y)
    f1 = lambda xi, yi: f6_1(xi, yi, k, g)
    f2 = lambda xi, yi: f6_2(xi, yi, k, g)
    Z1 = np.vectorize(f1)(X, Y)
    Z2 = np.vectorize(f2)(X, Y)
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#000000")
    ax.set_facecolor("#000000")
    ax.contour(X, Y, Z1, levels=[0], colors="#FFD700", linewidths=2)
    ax.contour(X, Y, Z2, levels=[0], colors="#FFA500", linewidths=2)
    legend_handles = [
        Line2D([0], [0], color="#FFD700", linewidth=2, label="f₁(x,y)=0"),
        Line2D([0], [0], color="#FFA500", linewidth=2, label="f₂(x,y)=0"),
    ]
    ax.legend(handles=legend_handles, facecolor="#1A1A1A", edgecolor="#FFD700", labelcolor="#FAFAFA")
    ax.set_xlabel("x", color="#FAFAFA")
    ax.set_ylabel("y", color="#FAFAFA")
    ax.set_title("Поиск начальных приближений: пересечения кривых — решения системы", color="#FAFAFA")
    ax.tick_params(colors="#FAFAFA")
    ax.spines["bottom"].set_color("#FFD700")
    ax.spines["top"].set_color("#FFD700")
    ax.spines["left"].set_color("#FFD700")
    ax.spines["right"].set_color("#FFD700")
    ax.grid(True, alpha=0.3, color="#FFD700")
    ax.set_aspect("equal")
    plt.tight_layout()
    return fig
with tab6:
    st.subheader("Параметры")
    k6, g6 = param_inputs("t6", 22, 1)
    eps6 = eps_input("eps6", EPS_SYS)
    method6 = st.radio("Метод", ["Итераций", "Ньютона"], horizontal=True, key="m6")
    st.subheader("Уравнение")
    st.latex(rf"\begin{{cases}} {k6} \cdot x - 4 \cdot {g6} + \frac{{\sin({k6}x + y - 4 \cdot {g6})}}{{10}} = 0 \\\\ y - \frac{{\sin({k6}x + y - 4 \cdot {g6})}}{{10 \cdot {g6}}} = 0 \end{{cases}} \quad (k={k6},\, g={g6})")
    with st.expander("📊 График для поиска начальных приближений", expanded=True):
        x_center = 4 * g6 / k6
        fig = plot_system_graph((x_center - 0.5, x_center + 1.0), (-0.5, 0.5), k6, g6)
        st.pyplot(fig)
        plt.close()
    st.subheader("Начальное приближение")
    x0_default = 4 * g6 / k6  
    y0_default = 0.0          
    st.caption(f"По умолчанию: x₀ = 4g/k = {x0_default:.4f}, y₀ = 0 (можно изменить)")
    c6a, c6b = st.columns(2)
    with c6a:
        x0_6 = st.number_input("x₀", value=float(x0_default), format="%.4f", key="x06")
    with c6b:
        y0_6 = st.number_input("y₀", value=float(y0_default), format="%.4f", key="y06")
    st.divider()
    if st.button("Рассчитать", key="btn6", type="primary"):
        try:
            if method6 == "Итераций":
                (x_root, y_root), rows, trace = method_iteration_system(x0_6, y0_6, eps6, k=k6, g=g6, trace_latex=True)
            else:
                (x_root, y_root), rows, trace = method_newton_system(x0_6, y0_6, eps6, k=k6, g=g6, trace_latex=True)
            st.subheader("Результат")
            st.dataframe(pd.DataFrame(rows, columns=["n", "x_n", "y_n", "f₁(x,y)", "f₂(x,y)", "max|Δ|"]))
            st.success(f"x ≈ {x_root:.6f},  y ≈ {y_root:.6f}")
            if trace:
                with st.expander("Трассировка", expanded=True):
                    render_latex_trace(trace)
        except ValueError as e:
            st.error(str(e))
with tab1:
    st.subheader("Параметры")
    k2, g2 = param_inputs("t2", 22, 1)
    eps2 = eps_input("eps2", EPS)
    method2 = st.radio("Метод", ["Секущих", "Ньютона"], horizontal=True, key="m2")
    st.subheader("Отрезок [a, b]")
    manual_ab2 = st.checkbox("Задать a и b вручную", key="manual2")
    if manual_ab2:
        ca2, cb2 = st.columns(2)
        with ca2:
            a2 = st.number_input("a", value=21.5, format="%.4f", key="a2")
        with cb2:
            b2 = st.number_input("b", value=23.0, format="%.4f", key="b2")
    st.subheader("Уравнение")
    st.latex(rf"f(x) = (x - {g2} \cdot {k2})^2 + \sin(x - {g2} \cdot {k2}) = 0 \quad (g={g2},\, k={k2})")
    st.divider()
    if st.button("Рассчитать", key="btn2", type="primary"):
        try:
            f2_k = partial(f2, k=k2, g=g2)
            f2p_k = partial(f2_prime, k=k2, g=g2)
            f2p2_k = partial(f2_prime2, k=k2, g=g2)
            if not manual_ab2:
                a2, b2 = find_bracket(f2_k, x_start=g2 * k2, step=0.3)
                st.subheader("Найденный отрезок [a, b]")
                st.info(rf"$a = {a2:.4f}$, $b = {b2:.4f}$ (автоматический поиск по перемене знака $f(a) \cdot f(b) < 0$)")
            else:
                a2, b2 = min(a2, b2), max(a2, b2)
                st.subheader("Отрезок [a, b]")
                st.info(rf"$a = {a2:.4f}$, $b = {b2:.4f}$ (задано вручную)")
            fig2 = plot_single_graph(f2_k, a2, b2)
            st.pyplot(fig2)
            plt.close()
            if method2 == "Секущих":
                root, rows, trace = method_secant(f2_k, f2p2_k, a2, b2, eps2, trace_latex=True)
            else:
                root, rows, trace = method_newton(f2_k, f2p_k, f2p2_k, a2, b2, eps2, trace_latex=True)
            st.subheader("Результат")
            st.dataframe(pd.DataFrame(rows, columns=["n", "x_n", "f(x_n)", "|Δx|"]))
            st.success(f"x ≈ {root:.6f}")
            if trace:
                with st.expander("Трассировка", expanded=True):
                    render_latex_trace(trace)
        except ValueError as e:
            st.error(str(e))
with tab2:
    st.subheader("Параметры")
    k3, g3 = param_inputs("t3", 22, 1)
    eps3 = eps_input("eps3", EPS)
    st.subheader("Отрезок [a, b]")
    manual_ab3 = st.checkbox("Задать a и b вручную", key="manual3")
    if manual_ab3:
        ca3, cb3 = st.columns(2)
        with ca3:
            a3 = st.number_input("a", value=0.4, format="%.4f", key="a3")
        with cb3:
            b3 = st.number_input("b", value=0.5, format="%.4f", key="b3")
    st.subheader("Уравнение")
    st.latex(rf"f(x) = {k3}x - {10*g3} - \sin\left(x - \frac{{10 \cdot {g3}}}{{{k3}}}\right) = 0 \quad (g={g3},\, k={k3})")
    st.divider()
    if st.button("Рассчитать", key="btn3", type="primary"):
        try:
            f3_k = partial(f3, k=k3, g=g3)
            f3p_k = partial(f3_prime, k=k3, g=g3)
            if not manual_ab3:
                x_start = 10 * g3 / k3
                a3, b3 = find_bracket(f3_k, x_start=x_start, step=0.05)
                st.subheader("Найденный отрезок [a, b]")
                st.info(rf"$a = {a3:.4f}$, $b = {b3:.4f}$ (автоматический поиск по перемене знака $f(a) \cdot f(b) < 0$)")
            else:
                a3, b3 = min(a3, b3), max(a3, b3)
                st.subheader("Отрезок [a, b]")
                st.info(rf"$a = {a3:.4f}$, $b = {b3:.4f}$ (задано вручную)")
            fig3 = plot_single_graph(f3_k, a3, b3)
            st.pyplot(fig3)
            plt.close()
            root, rows, trace = method_iteration(f3_k, f3p_k, a3, b3, eps3, trace_latex=True, trace_k=k3, trace_g=g3)
            st.subheader("Результат")
            st.dataframe(pd.DataFrame(rows, columns=["n", "x_n", "f(x_n)", "|Δx|"]))
            st.success(f"x ≈ {root:.6f}")
            if trace:
                with st.expander("Трассировка", expanded=True):
                    render_latex_trace(trace)
        except ValueError as e:
            st.error(str(e))