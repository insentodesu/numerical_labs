"""
Streamlit: лабораторная «Приближение функций» — подробные шаги, ссылки на лекции, графики.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from homework_lab3 import (
    build_tables,
    divided_differences_coeffs,
    divided_differences_triangle,
    f_variant,
    finite_differences_backward_at_last,
    finite_differences_forward,
    lagrange_interpolate,
    lagrange_trace_at,
    linear_spline,
    linear_spline_segments,
    newton_backward_equal_spacing,
    newton_backward_trace,
    newton_eval_divided_differences,
    newton_eval_divided_differences_trace,
    newton_forward_equal_spacing,
    newton_forward_trace,
    newton_interpolate_general,
    spline_test_points,
    table1_test_points,
    table2_test_points,
)

# Как в лабораторной №1 (homework_ui): тёмный фон, золотой акцент, полупрозрачные заливки
_PLOT_FACE = "#000000"
_ACCENT = "#FFD700"
_ACCENT2 = "#FFA500"
_TEXT = "#FAFAFA"
_MUTED = "#666666"
_LEGEND_FACE = "#1A1A1A"


def _style_plot_axes(fig: plt.Figure, ax: plt.Axes) -> None:
    fig.patch.set_facecolor(_PLOT_FACE)
    ax.set_facecolor(_PLOT_FACE)
    ax.tick_params(colors=_TEXT)
    for spine in ax.spines.values():
        spine.set_color(_ACCENT)
    ax.grid(True, alpha=0.3, color=_ACCENT)
    ax.xaxis.label.set_color(_TEXT)
    ax.yaxis.label.set_color(_TEXT)
    t = ax.title
    if t.get_text():
        t.set_color(_TEXT)


def _fmt(x: float) -> str:
    return f"{x:.10g}"


def _linspace(a: float, b: float, n: int) -> list[float]:
    if n < 2:
        return [a]
    return [a + i * (b - a) / (n - 1) for i in range(n)]


def latex_cases_table1(g: int, k: int) -> str:
    base = g - 2 * k
    return (
        rf"\begin{{cases}}"
        rf"x_0={base}-3,\ x_1={base}-1,\ x_2={base},\ x_3={base}+2\\"
        rf"f(x)=\dfrac{{\sin x}}{{x}}\ (\text{{при }}x=0:\ f(0)=1)"
        rf"\end{{cases}}"
    )


def latex_array_row(vals: list[float]) -> str:
    return " & ".join(_fmt(v) for v in vals)


def latex_finite_diff_table(fd: list[list[float]]) -> str:
    """Таблица конечных разностей (лекция 3)."""
    rows = []
    for k, row in enumerate(fd):
        rows.append(rf"\Delta^{{{k}}} y & " + " & ".join(_fmt(v) for v in row))
    return r"\begin{array}{l}" + r" \\ ".join(rows) + r"\end{array}"


def latex_divided_differences_aligned(x: list[float], tri: list[list[float | None]]) -> str:
    """Разделённые разности построчно (лекция 4, (47))."""
    n = len(x)
    parts = [r"\begin{aligned}"]
    for k in range(n):
        for i in range(n - k):
            v = tri[i][k]
            assert v is not None
            parts.append(rf"f[x_{i},\ldots,x_{{{i + k}}}] &= {_fmt(float(v))} \\")
    parts.append(r"\end{aligned}")
    return "".join(parts)


def fig_interpolation_overview(
    x1: list[float],
    y1: list[float],
    x2: list[float],
    y2: list[float],
    *,
    n_plot: int = 250,
) -> plt.Figure:
    """График f, интерполянта по табл.1, сплайна и узлов."""
    lo = min(min(x1), min(x2)) - 0.4
    hi = max(max(x1), max(x2)) + 0.4
    xs = _linspace(lo, hi, n_plot)
    fy = [f_variant(t) for t in xs]
    Ly = [lagrange_interpolate(x1, y1, t) for t in xs]
    Sy = [linear_spline(x1, y1, t) for t in xs]

    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=_PLOT_FACE)
    _style_plot_axes(fig, ax)

    y_all = fy + Ly + Sy
    span = max(y_all) - min(y_all)
    y_bot = min(y_all) - (0.12 * span if span > 0 else 0.5)
    ax.fill_between(xs, y_bot, fy, alpha=0.12, color=_ACCENT, linewidth=0, zorder=0)

    ax.plot(xs, fy, color=_ACCENT, linewidth=2.2, label=r"$f(x)=\sin x/x$", zorder=2)
    ax.plot(
        xs,
        Ly,
        color=_ACCENT2,
        linestyle="--",
        linewidth=1.65,
        alpha=0.92,
        label=r"$P_L(x)$ Лагранж, узлы табл.1",
        zorder=2,
    )
    ax.plot(
        xs,
        Sy,
        color="#FFEC8B",
        linewidth=1.55,
        alpha=0.88,
        label=r"$S_{\mathrm{lin}}(x)$ линейный сплайн, табл.1",
        zorder=2,
    )
    ax.scatter(
        x1,
        y1,
        s=72,
        zorder=5,
        facecolors=(1.0, 0.84, 0.0, 0.42),
        edgecolors=_ACCENT,
        linewidths=1.2,
        label="узлы табл.1",
    )
    ax.scatter(
        x2,
        y2,
        s=58,
        zorder=5,
        marker="s",
        facecolors=(1.0, 0.65, 0.0, 0.42),
        edgecolors=_ACCENT2,
        linewidths=1.2,
        label="узлы табл.2",
    )
    ax.axhline(0, color=_MUTED, linewidth=0.5, zorder=1)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"значение")
    ax.legend(loc="best", facecolor=_LEGEND_FACE, edgecolor=_ACCENT, labelcolor=_TEXT)
    ax.set_title(
        "Интуиция: сплайн — это ломаная, соединяющая узлы отрезками прямых "
        "(лекция 5); многочлен Лагранжа — одна гладкая кривая через все узлы (лекции 1–2)."
    )
    fig.tight_layout()
    return fig


st.set_page_config(page_title="Лабораторная · интерполяция", layout="wide")
st.title("Лабораторная №3: приближение функций (интерполяция)")
st.markdown(
    """
**Как читать отчёт.** В каждом пункте указано: **лекция** и **номер формулы** из курса.
В конце — **графики** (как в лаб. №1: тёмный фон, золотой акцент): яркая золотая линия — $f(x)$,
пунктир оранжевый — многочлен Лагранжа по таблице 1, светло-жёлтая — **линейный сплайн**
(кусочно прямые между узлами; на узлах $y_i$, между узлами — линейная связь).
"""
)

c1, c2 = st.columns(2)
with c1:
    g = st.number_input("g (номер подгруппы)", value=1, step=1, format="%d")
with c2:
    k = st.number_input("k (номер группы)", value=3, step=1, format="%d")

if not st.button("Рассчитать", type="primary"):
    st.stop()

g_i, k_i = int(g), int(k)
data = build_tables(g_i, k_i)
x1, y1 = data["table1"]
x2, y2 = data["table2"]
h2 = data["h2"]
x0_2 = data["x0_table2"]

st.markdown("### Исходные данные")
st.markdown(
    "**Лекция 1:** постановка задачи полиномиальной интерполяции — ищем $P_n$ такой, что "
    r"$P_n(x_i)=y_i=f(x_i)$ на узлах."
)
st.latex(r"f(x)=\dfrac{\sin x}{x},\quad x\neq 0;\quad f(0)=1.")
st.latex(latex_cases_table1(g_i, k_i))

st.markdown("### Таблица 1 (неравноотстоящие узлы)")
st.latex(
    rf"\begin{{array}}{{c|cccc}}"
    rf"x & {latex_array_row(x1)} \\ \hline "
    rf"y & {latex_array_row(y1)}"
    rf"\end{{array}}"
)

st.markdown("### Таблица 2 (равноотстоящие узлы, шаг h)")
st.markdown("**Лекция 3:** узлы $x_i=x_0+i h$, одинаковый шаг $h$.")
st.latex(rf"h = x_1-x_0 = {_fmt(h2)}")
st.latex(
    rf"\begin{{array}}{{c|cccc}}"
    rf"x & {latex_array_row(x2)} \\ \hline "
    rf"y & {latex_array_row(y2)}"
    rf"\end{{array}}"
)

# --- Общий график ---
st.divider()
st.subheader("Наглядно: график $f(x)$, многочлен Лагранжа (табл.1) и линейный сплайн")
fig0 = fig_interpolation_overview(x1, y1, x2, y2)
st.pyplot(fig0, width="stretch")
plt.close(fig0)

# --- Задание 1 ---
st.divider()
st.subheader("1. Многочлен Лагранжа (равноотстоящие узлы, таблица 2)")
st.markdown(
    r"**Лекция 2:** $P_n(x)=\sum_{i=0}^n y_i\,\ell_i(x)$, базис $\ell_i(x_j)=\delta_{ij}$ (после формулы (3.9)); "
    r"явный вид $\ell_i(x)=\prod_{j\neq i}\frac{x-x_j}{x_i-x_j}$. "
    "**Лекция 3:** равноотстоящие узлы $x_i=x_0+i h$ — **формула Лагранжа та же**, меняется только расположение узлов."
)
demo_x = x0_2 + 0.37 * h2
st.latex(rf"x_{{\mathrm{{demo}}}} = x_0+0{{,}}37h = {_fmt(demo_x)}")
with st.expander(
    r"Пошагово: вклад каждого $\ell_i(x)\cdot y_i$ в точке $x_{\mathrm{demo}}$",
    expanded=True,
):
    tot, details = lagrange_trace_at(x2, y2, demo_x)
    for d in details:
        i = int(d["i"])
        st.latex(
            rf"\ell_{{{i}}}({{_fmt(demo_x)}})={_fmt(d['ell_i'])},\quad "
            rf"y_{{{i}}}\,\ell_{{{i}}}={_fmt(d['y_i'])}\cdot{_fmt(d['ell_i'])}={_fmt(d['term'])}"
        )
    st.latex(rf"P_3(x_{{\mathrm{{demo}}}})=\sum_i y_i\ell_i={_fmt(tot)}")
f_demo = f_variant(demo_x)
st.latex(rf"f(x_{{\mathrm{{demo}}}})={_fmt(f_demo)},\quad |P-f|={_fmt(abs(tot-f_demo))}")

# --- Задание 2 ---
st.divider()
st.subheader("2. Лагранж и Ньютон по таблице 1 (неравноотстоящие узлы)")
st.markdown(
    "**Лекция 4:** разделённые разности (47), интерполяционный многочлен Ньютона (49). "
    "Рекомендация к вычислению: перенумеровать узлы по возрастанию $|x-x_i|$ перед таблицей разностей."
)
tri1 = divided_differences_triangle(x1, y1)
st.markdown("**Таблица разделённых разностей** (исходный порядок узлов), лекция 4, (47):")
st.latex(latex_divided_differences_aligned(x1, tri1))
coeffs1 = divided_differences_coeffs(x1, y1)
st.latex(
    r"\text{Коэффициенты в формуле (49): }"
    rf"c_0=f[x_0]={_fmt(coeffs1[0])},\ c_1=f[x_0,x_1]={_fmt(coeffs1[1])},\ "
    rf"c_2=f[x_0,x_1,x_2]={_fmt(coeffs1[2])},\ c_3=f[x_0,\ldots,x_3]={_fmt(coeffs1[3])}"
)

pts1 = table1_test_points(g_i, k_i)
for xv in pts1:
    with st.expander(f"Контрольная точка $x={_fmt(xv)}$", expanded=False):
        f_ex = f_variant(xv)
        L, ldet = lagrange_trace_at(x1, y1, xv)
        st.markdown(f"**Точное** $f(x)={_fmt(f_ex)}$.")
        st.markdown("**Лагранж (лекция 2, (3.8)–(3.9)):**")
        for d in ldet:
            i = int(d["i"])
            st.latex(
                rf"\ell_{{{i}}}={_fmt(d['ell_i'])},\ y_{{{i}}}\ell_{{{i}}}={_fmt(d['term'])}"
            )
        st.latex(rf"P_L(x)={_fmt(L)},\quad |P_L-f|={_fmt(abs(L-f_ex))}")
        st.markdown("**Ньютон, порядок узлов как в таблице (лекция 4, (49)):**")
        _, nsteps = newton_eval_divided_differences_trace(x1, coeffs1, xv)
        for stp in nsteps:
            j = int(stp["j"])
            st.latex(
                rf"j={j}:\ \prod_{{m<j}}(x-x_m)={_fmt(stp['prod'])},\ "
                rf"c_{{{j}}}={_fmt(stp['c_j'])},\ \text{{слагаемое}}={_fmt(stp['addend'])},\ "
                rf"\text{{частичная сумма}}={_fmt(stp['partial_sum'])}"
            )
        N0 = newton_interpolate_general(x1, y1, xv, reorder=False)
        st.latex(rf"N(x)={_fmt(N0)},\quad |N-f|={_fmt(abs(N0-f_ex))}")
        st.markdown("**Ньютон с перенумерацией узлов по $|x-x_i|$ (лекция 4, практическая рекомендация):**")
        order = sorted(range(len(x1)), key=lambda i: abs(xv - x1[i]))
        x_ord = [x1[i] for i in order]
        st.latex(r"\text{Порядок индексов узлов: }" + ", ".join(str(i) for i in order))
        N1 = newton_interpolate_general(x1, y1, xv, reorder=True)
        st.latex(rf"N_{{\mathrm{{пер}}}}(x)={_fmt(N1)},\quad |N_{{\mathrm{{пер}}}}-f|={_fmt(abs(N1-f_ex))}")

rows = []
for xv in pts1:
    f_ex = f_variant(xv)
    L = lagrange_interpolate(x1, y1, xv)
    N0 = newton_interpolate_general(x1, y1, xv, reorder=False)
    N1 = newton_interpolate_general(x1, y1, xv, reorder=True)
    rows.append(
        rf"{_fmt(xv)} & {_fmt(f_ex)} & {_fmt(L)} & {_fmt(N0)} & {_fmt(N1)} & {_fmt(abs(L-f_ex))} & {_fmt(abs(N0-f_ex))}"
    )
body = r" \\ ".join(rows)
st.markdown("**Сводная таблица по всем контрольным точкам:**")
st.latex(
    r"\begin{array}{c|ccccc|c}"
    r"x & f(x) & L(x) & N(x) & N_{\mathrm{пер}}(x) & |L-f| & |N-f| \\ \hline"
    + body
    + r"\end{array}"
)

# --- Задание 3 ---
st.divider()
st.subheader("3. Ньютон по таблице 2 (равноотстоящие узлы)")
xn_2 = float(x2[-1])
st.markdown(
    "**Лекция 3:** прямые разности $\\Delta^k y_i$ и обратные $\\nabla^k y_i$. "
    "**Первая формула Ньютона (лекция 3–4, (46)):** $q=(x-x_0)/h$, "
    r"$N(x)=y_0+\sum_{k=1}^n \frac{q(q-1)\cdots(q-k+1)}{k!}\,\Delta^k y_0$. "
    "**Вторая формула Ньютона:** $q=(x-x_n)/h$, "
    r"$N(x)=y_n+\sum_{k=1}^n \frac{q(q+1)\cdots(q+k-1)}{k!}\,\nabla^k y_n$ "
    "(те же узлы и тот же интерполяционный многочлен $P_3$, другая запись)."
)
fd2 = finite_differences_forward(y2)
st.markdown(r"Таблица прямых конечных разностей $\Delta^k y$ (по строкам $k=0,1,\ldots$):")
st.latex(latex_finite_diff_table(fd2))
nb_list = finite_differences_backward_at_last(y2)
st.markdown(
    r"Коэффициенты второй формулы: $y_n,\nabla y_n,\nabla^2 y_n,\ldots$ "
    r"(последние элементы строк обратных разностей, лекция 3)."
)
st.latex(
    r"\big[y_n,\ \nabla y_n,\ \nabla^2 y_n,\ \nabla^3 y_n\big] = \big["
    + ", ".join(_fmt(v) for v in nb_list)
    + r"\big]"
)

x2_rev = list(reversed(x2))
y2_rev = list(reversed(y2))
coeffs_rev = divided_differences_coeffs(x2_rev, y2_rev)
pts2 = table2_test_points(g_i, k_i)

for xv in pts2:
    with st.expander(
        rf"Точка $x={_fmt(xv)}$: первая и вторая формулы Ньютона",
        expanded=False,
    ):
        f_ex = f_variant(xv)
        s_tr, terms, qv = newton_forward_trace(x0_2, h2, y2, xv)
        st.markdown("**Первая формула** ((46), разности $\\Delta^k y_0$):")
        st.latex(rf"q=\dfrac{{x-x_0}}{{h}}=\dfrac{{{_fmt(xv)}-{_fmt(x0_2)}}}{{{_fmt(h2)}}}={_fmt(qv)}")
        for t in terms:
            kk = int(t["k"])
            st.latex(
                rf"k={kk}:\ \frac{{q(q-1)\cdots}}{{k!}}={_fmt(t['binom_part'])},\ "
                rf"\Delta^{{{kk}}} y_0={_fmt(t['delta'])},\ \text{{слагаемое}}={_fmt(t['addend'])}"
            )
        st.latex(rf"N_{{\rightarrow}}(x)={_fmt(s_tr)},\quad |N_{{\rightarrow}}-f|={_fmt(abs(s_tr-f_ex))}")
        s_b, terms_b, qb = newton_backward_trace(xn_2, h2, y2, xv)
        st.markdown("**Вторая формула** (разности $\\nabla^k y_n$, опорный узел $x_n$):")
        st.latex(rf"q=\dfrac{{x-x_n}}{{h}}=\dfrac{{{_fmt(xv)}-{_fmt(xn_2)}}}{{{_fmt(h2)}}}={_fmt(qb)}")
        for t in terms_b:
            kk = int(t["k"])
            st.latex(
                rf"k={kk}:\ \frac{{q(q+1)\cdots}}{{k!}}={_fmt(t['binom_part'])},\ "
                rf"\nabla^{{{kk}}} y_n={_fmt(t['nabla'])},\ \text{{слагаемое}}={_fmt(t['addend'])}"
            )
        st.latex(rf"N_{{\nabla}}(x)={_fmt(s_b)},\quad |N_{{\nabla}}-f|={_fmt(abs(s_b-f_ex))}")
        st.latex(
            rf"|N_{{\rightarrow}}-N_{{\nabla}}|={_fmt(abs(s_tr-s_b))}\ \text{{(должно быть порядка машинного }}\varepsilon\text{{)}}"
        )
        st.markdown(
            "**Тот же многочлен**, запись (49) с узлами в обратном порядке (разделённые разности) — для контроля:"
        )
        _, nst = newton_eval_divided_differences_trace(x2_rev, coeffs_rev, xv)
        for stp in nst:
            st.latex(
                rf"j={int(stp['j'])}:\ \text{{слагаемое}}={_fmt(stp['addend'])},\ "
                rf"\Sigma={_fmt(stp['partial_sum'])}"
            )
        Nrev = newton_eval_divided_differences(x2_rev, coeffs_rev, xv)
        st.latex(rf"N_{{\mathrm{{обр}}}}(x)={_fmt(Nrev)},\quad |N_{{\rightarrow}}-N_{{\mathrm{{обр}}}}|={_fmt(abs(s_tr-Nrev))}")

rows2 = []
for xv in pts2:
    f_ex = f_variant(xv)
    Nf = newton_forward_equal_spacing(x0_2, h2, y2, xv)
    Nb = newton_backward_equal_spacing(xn_2, h2, y2, xv)
    Nrev = newton_eval_divided_differences(x2_rev, coeffs_rev, xv)
    rows2.append(
        rf"{_fmt(xv)} & {_fmt(f_ex)} & {_fmt(Nf)} & {_fmt(Nb)} & {_fmt(Nrev)} & {_fmt(abs(Nf-Nb))} & {_fmt(abs(Nf-f_ex))} & {_fmt(abs(Nb-f_ex))}"
    )
body2 = r" \\ ".join(rows2)
st.latex(
    r"\begin{array}{c|ccccccc}"
    r"x & f(x) & N_{\rightarrow} & N_{\nabla} & N_{\mathrm{обр}} & |N_\rightarrow-N_{\nabla}| & |N_\rightarrow-f| & |N_{\nabla}-f| \\ \hline"
    + body2
    + r"\end{array}"
)
st.caption(
    r"$N_{\rightarrow}$ — первая формула (46); $N_{\nabla}$ — вторая формула с $\nabla^k y_n$; "
    r"$N_{\mathrm{обр}}$ — (49) при переставленных узлах (тот же $P_3$)."
)

# --- Задание 4 + график сплайна крупно ---
st.divider()
st.subheader("4. Линейный сплайн по таблице 1")
st.markdown(
    "**Лекция 5, (50)–(51):** на каждом отрезке $[x_{i-1},x_i]$ функция $\\varphi(x)=a_i x+b_i$; "
    "коэффициенты из условий прохождения через $(x_{i-1},y_{i-1})$ и $(x_i,y_i)$. "
    "Глобально получается **непрерывная ломаная** (углы в узлах — производная скачет, "
    "но значения совпадают с таблицей)."
)
segs = linear_spline_segments(x1, y1)
for sg in segs:
    sn = int(sg["segment"])
    st.latex(
        rf"\text{{Отрезок }}[{_fmt(sg['x_lo'])},{_fmt(sg['x_hi'])}]:\ "
        rf"a_{{{sn}}}={_fmt(sg['a'])},\ b_{{{sn}}}={_fmt(sg['b'])},\ "
        rf"\varphi(x)=a_{{{sn}}}x+b_{{{sn}}}"
    )

pts_s = spline_test_points(g_i, k_i)


def _segment_for_point(x_nodes: list[float], segs: list[dict[str, float]], xv: float) -> dict[str, float]:
    if xv <= x_nodes[0]:
        return segs[0]
    if xv >= x_nodes[-1]:
        return segs[-1]
    for sg in segs:
        if sg["x_lo"] <= xv <= sg["x_hi"]:
            return sg
    return segs[-1]


for xv in pts_s:
    with st.expander(f"Сплайн в точке $x={_fmt(xv)}$", expanded=False):
        f_ex = f_variant(xv)
        s = linear_spline(x1, y1, xv)
        sg = _segment_for_point(x1, segs, xv)
        st.latex(
            rf"x\in[{_fmt(sg['x_lo'])},{_fmt(sg['x_hi'])}]:\ "
            rf"\varphi(x)={_fmt(sg['a'])}\cdot x + {_fmt(sg['b'])},\ "
            rf"\varphi({_fmt(xv)})={_fmt(s)}"
        )
        st.latex(rf"f(x)={_fmt(f_ex)},\quad |S-f|={_fmt(abs(s-f_ex))}")

rows_s = []
for xv in pts_s:
    f_ex = f_variant(xv)
    s = linear_spline(x1, y1, xv)
    rows_s.append(rf"{_fmt(xv)} & {_fmt(f_ex)} & {_fmt(s)} & {_fmt(abs(s-f_ex))}")
body_s = r" \\ ".join(rows_s)
st.latex(
    r"\begin{array}{c|ccc}"
    r"x & f(x) & S_{\mathrm{lin}}(x) & |S-f| \\ \hline"
    + body_s
    + r"\end{array}"
)

fig2, ax2 = plt.subplots(figsize=(10, 4.5), facecolor=_PLOT_FACE)
_style_plot_axes(fig2, ax2)
lo, hi = min(x1) - 0.35, max(x1) + 0.35
xs2 = _linspace(lo, hi, 200)
fy2 = [f_variant(t) for t in xs2]
sy2 = [linear_spline(x1, y1, t) for t in xs2]
span2 = max(fy2 + sy2) - min(fy2 + sy2)
y_bot2 = min(fy2 + sy2) - (0.1 * span2 if span2 > 0 else 0.4)
ax2.fill_between(xs2, y_bot2, fy2, alpha=0.1, color=_ACCENT, linewidth=0, zorder=0)
ax2.plot(xs2, fy2, color=_ACCENT, linewidth=2.1, label=r"$f(x)$", zorder=2)
ax2.plot(
    xs2,
    sy2,
    color=_ACCENT2,
    linewidth=2.0,
    alpha=0.9,
    label="линейный сплайн",
    zorder=2,
)
for xv in pts_s:
    ax2.axvline(xv, color=_ACCENT2, linestyle=":", linewidth=0.9, alpha=0.55)
    ax2.scatter(
        [xv],
        [linear_spline(x1, y1, xv)],
        s=48,
        zorder=6,
        facecolors=(0.75, 0.55, 1.0, 0.45),
        edgecolors=_ACCENT2,
        linewidths=1.0,
    )
ax2.scatter(
    x1,
    y1,
    s=68,
    zorder=5,
    facecolors=(1.0, 0.84, 0.0, 0.42),
    edgecolors=_ACCENT,
    linewidths=1.2,
    label="узлы",
)
ax2.set_title("Линейный сплайн: «соединили точки отрезками» (лекция 5)")
ax2.legend(loc="best", facecolor=_LEGEND_FACE, edgecolor=_ACCENT, labelcolor=_TEXT)
fig2.tight_layout()
st.pyplot(fig2, width="stretch")
plt.close(fig2)
