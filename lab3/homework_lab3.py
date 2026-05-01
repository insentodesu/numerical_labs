"""
Лабораторная: приближение функций (интерполяция Лагранжа, Ньютона, линейный сплайн).

В docstring у ключевых функций указаны ссылки на лекции и номера формул из методички,
как в курсе (полиномиальная интерполяция, Лагранж, Ньютон, сплайны).
"""
from __future__ import annotations

import math
from typing import Sequence


def f_variant(x: float, g: int, k: int) -> float:
    """Табличная функция по заданию: f(x) = sin(x) + g/k."""
    return math.sin(x) + float(g) / float(k)


def lagrange_basis(
    x_nodes: Sequence[float], i: int, x: float
) -> float:
    """
    Базисный многочлен Лагранжа l_i(x).

    Лекция 2: l_i(x) = Π_{j≠i} (x - x_j) / (x_i - x_j), свойство l_i(x_j)=δ_ij (после (3.9)).
    """
    xi = x_nodes[i]
    num, den = 1.0, 1.0
    for j, xj in enumerate(x_nodes):
        if j == i:
            continue
        num *= x - xj
        den *= xi - xj
    return num / den


def lagrange_interpolate(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x: float
) -> float:
    """
    Интерполяционный многочлен Лагранжа P_n(x) = Σ y_i l_i(x).

    Лекция 2: формула (3.8) с C_i = y_i и явный вид l_i после (3.9).
    Для равноотстоящих узлов шаг h постоянен (Лекция 3), сама формула P_n та же.
    """
    n = len(x_nodes)
    if len(y_nodes) != n:
        raise ValueError("Размеры x_nodes и y_nodes должны совпадать.")
    return sum(y_nodes[i] * lagrange_basis(x_nodes, i, x) for i in range(n))


def divided_differences_coeffs(x: Sequence[float], y: Sequence[float]) -> list[float]:
    """
    Первая строка таблицы разделённых разностей: f[x0], f[x0,x1], …, f[x0,…,xn].

    Лекция 4: рекуррентное определение (47), итоговая формула Ньютона (49).
    """
    n = len(x)
    if len(y) != n:
        raise ValueError("Размеры x и y должны совпадать.")
    # table[i][k] = f[x_i, …, x_{i+k}], k = 0..n-1-i
    table: list[list[float]] = [[float(y[i])] for i in range(n)]
    for k in range(1, n):
        for i in range(n - k):
            num = table[i + 1][k - 1] - table[i][k - 1]
            den = x[i + k] - x[i]
            table[i].append(num / den)
    return [table[0][k] for k in range(n)]


def newton_eval_divided_differences(
    x_nodes: Sequence[float], coeffs: Sequence[float], x: float
) -> float:
    """
    Значение интерполяционного многочлена Ньютона по разделённым разностям.

    Лекция 4: N_n(x) из (49) — сумма с накоплением произведений (x-x0)…(x-x_{j-1}).
    """
    s = 0.0
    prod = 1.0
    for j in range(len(coeffs)):
        if j == 0:
            prod = 1.0
        else:
            prod *= x - x_nodes[j - 1]
        s += coeffs[j] * prod
    return s


def newton_interpolate_general(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x: float, *, reorder: bool
) -> float:
    """
    Ньютон для неравноотстоящих узлов.

    reorder=False — узлы в исходном порядке таблицы.
    reorder=True — перед построением разностей узлы перенумерованы по возрастанию
    |x - x_i| (практическая рекомендация из лекции 4 к остаточному члену / устойчивости).
    """
    xs = list(x_nodes)
    ys = list(y_nodes)
    if reorder:
        order = sorted(range(len(xs)), key=lambda i: abs(x - xs[i]))
        xs = [xs[i] for i in order]
        ys = [ys[i] for i in order]
    c = divided_differences_coeffs(xs, ys)
    return newton_eval_divided_differences(xs, c, x)


def finite_differences_forward(y: Sequence[float]) -> list[list[float]]:
    """
    Таблица прямых конечных разностей Δ^k y_i.

    Лекция 3: Δ y_i = y_{i+1}-y_i, Δ^k y_i = Δ^{k-1} y_{i+1} - Δ^{k-1} y_i.
    """
    table: list[list[float]] = [list(map(float, y))]
    row = table[0]
    while len(row) > 1:
        row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
        table.append(row)
    return table


def newton_forward_equal_spacing(
    x0: float, h: float, y: Sequence[float], x: float
) -> float:
    """
    Первая интерполяционная формула Ньютона для равноотстоящих узлов.

    Лекция 3–4: ввод q = (x-x0)/h и разложение (46):
    N(x0+qh) = y0 + qΔy0 + [q(q-1)/2!] Δ^2 y0 + … + [q…(q-n+1)/n!] Δ^n y0.
    """
    q = (x - x0) / h
    fd = finite_differences_forward(y)
    s = float(y[0])
    for k in range(1, len(y)):
        dky0 = fd[k][0]
        prod = 1.0
        for t in range(k):
            prod *= q - t
        s += (prod / math.factorial(k)) * dky0
    return s


def linear_spline(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x: float
) -> float:
    """
    Линейный сплайн (кусочно-линейная интерполяция).

    Лекция 5: на [x_{i-1}, x_i] отрезок φ(x)=a_i x + b_i, коэффициенты из (51).
    """
    xs, ys = list(x_nodes), list(y_nodes)
    if x <= xs[0]:
        x0, y0, x1, y1 = xs[0], ys[0], xs[1], ys[1]
    elif x >= xs[-1]:
        x0, y0, x1, y1 = xs[-2], ys[-2], xs[-1], ys[-1]
    else:
        for i in range(1, len(xs)):
            if xs[i - 1] <= x <= xs[i]:
                x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]
                break
        else:
            raise ValueError("x вне объединения отрезков узлов.")
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    return (1.0 - t) * y0 + t * y1


# --- Постановка из лабораторного задания (узлы и контрольные точки) ---


def table1_nodes(g: int, k: int) -> list[float]:
    base = float(g) - 2.0 * float(k)
    return [base - 3.0, base - 1.0, base, base + 2.0]


def table1_test_points(g: int, k: int) -> list[float]:
    base = float(g) - 2.0 * float(k)
    return [base - 2.7, base - 0.5, base + 2.3]


def table2_nodes(g: int, k: int) -> list[float]:
    base = float(g) - 2.0 * float(k)
    return [base - 2.0, base - 1.0, base, base + 1.0]


def table2_test_points(g: int, k: int) -> list[float]:
    base = float(g) - 2.0 * float(k)
    return [base - 1.7, base + 0.6, base + 1.9]


def spline_test_points(g: int, k: int) -> list[float]:
    """Контрольные точки для линейного сплайна по таблице 1 (из задания)."""
    base = float(g) - 2.0 * float(k)
    return [base - 2.7, base - 0.5, base + 0.8]


def build_tables(g: int, k: int) -> dict:
    """Собирает узлы и значения f для пунктов 2–4."""
    if k == 0:
        raise ValueError("k должно быть ненулевым (деление g/k в f(x)).")
    x1 = table1_nodes(g, k)
    y1 = [f_variant(t, g, k) for t in x1]
    x2 = table2_nodes(g, k)
    y2 = [f_variant(t, g, k) for t in x2]
    h2 = x2[1] - x2[0]
    return {
        "table1": (x1, y1),
        "table2": (x2, y2),
        "h2": h2,
        "x0_table2": x2[0],
    }
