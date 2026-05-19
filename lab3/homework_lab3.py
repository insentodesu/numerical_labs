"""
Лабораторная №3: приближение функций (интерполяция).

Содержание файла (для защиты — где искать):
  f_variant, table*_nodes, build_tables     — исходная f(x) и узлы по g, k
  lagrange_*                                  — задание 1 (Лагранж, табл. 2 в UI)
  divided_differences_*, newton_interpolate_* — задание 2 (Ньютон, табл. 1)
  finite_differences_*, newton_forward/backward_* — задание 3 (равные узлы, табл. 2)
  linear_spline*                              — задание 4 (сплайн, табл. 1)

В docstring функций — ссылки на лекции и номера формул.
"""
from __future__ import annotations  # отложенная аннотация типов (list[float] и т.п.)

import math  # sin, factorial для формул Ньютона
from typing import Sequence  # общий тип для списков узлов/значений


# =============================================================================
# ИСХОДНАЯ ФУНКЦИЯ f(x) = sin(x) + x  (заполнение таблиц y_i = f(x_i))
# =============================================================================

def f_variant(x: float) -> float:
    """Табличная функция по заданию: f(x) = sin(x) + x."""
    return math.sin(x) + x


# =============================================================================
# ЛАГРАНЖ — лекция 2, формулы (3.8)–(3.9); в UI: задание 1 (таблица 2)
# =============================================================================

def lagrange_basis(
    x_nodes: Sequence[float], i: int, x: float
) -> float:
    """Базисный многочлен ℓ_i(x): произведение (x-x_j)/(x_i-x_j) по j≠i."""
    xi = x_nodes[i]  # i-й узел — «свой» знаменатель
    num, den = 1.0, 1.0  # числитель и знаменатель произведения
    for j, xj in enumerate[float](x_nodes):  # перебор всех узлов
        if j == i:  # в произведении j=i не участвует
            continue
        num *= x - xj  # множитель числителя
        den *= xi - xj  # множитель знаменателя
    return num / den  # ℓ_i(x)


def lagrange_interpolate(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x: float
) -> float:
    """P_n(x) = Σ y_i · ℓ_i(x) — интерполяционный многочлен Лагранжа."""
    n = len(x_nodes)  # число узлов
    if len(y_nodes) != n:  # защита от разной длины таблиц
        raise ValueError("Размеры x_nodes и y_nodes должны совпадать.")
    return sum(y_nodes[i] * lagrange_basis(x_nodes, i, x) for i in range(n))  # сумма вкладов


def lagrange_trace_at(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x_val: float
) -> tuple[float, list[dict[str, float]]]:
    """То же, что lagrange_interpolate, но с разбором каждого слагаемого для отчёта."""
    details: list[dict[str, float]] = []  # список вкладов y_i·ℓ_i
    total = 0.0  # накопленная сумма P(x)
    for i in range(len(x_nodes)):  # по каждому базисному многочлену
        ell = lagrange_basis(x_nodes, i, x_val)  # ℓ_i в контрольной точке
        c = float(y_nodes[i]) * ell  # слагаемое y_i·ℓ_i
        total += c  # прибавляем к сумме
        details.append({"i": float(i), "ell_i": ell, "y_i": float(y_nodes[i]), "term": c})
    return total, details  # значение P и пошаговый разбор


# =============================================================================
# РАЗДЕЛЁННЫЕ РАЗНОСТИ И НЬЮТОН (неравные узлы) — лекция 4, (47)–(49); задание 2
# =============================================================================

def divided_differences_coeffs(x: Sequence[float], y: Sequence[float]) -> list[float]:
    """
    Первая строка треугольника: c_k = f[x_0,…,x_k] — коэффициенты формулы (49).
    """
    n = len(x)
    if len(y) != n:
        raise ValueError("Размеры x и y должны совпадать.")
    # table[i][k] = f[x_i, …, x_{i+k}]
    table: list[list[float]] = [[float(y[i])] for i in range(n)]  # нулевой столбец — сами y_i
    for k in range(1, n):  # порядок разности 1, 2, …, n-1
        for i in range(n - k):  # сколько элементов в строке k
            num = table[i + 1][k - 1] - table[i][k - 1]  # числитель (47)
            den = x[i + k] - x[i]  # знаменатель x_{i+k} - x_i
            table[i].append(num / den)  # новая разделённая разность
    return [table[0][k] for k in range(n)]  # только первая строка — для (49)


def divided_differences_triangle(
    x: Sequence[float], y: Sequence[float]
) -> list[list[float | None]]:
    """Полный треугольник разностей — для вывода в Streamlit (все f[x_i,…,x_{i+k}])."""
    n = len(x)
    table: list[list[float | None]] = [[None] * n for _ in range(n)]  # пустая матрица n×n
    for i in range(n):
        table[i][0] = float(y[i])  # диагональ «нуля»: значения в узлах
    for k in range(1, n):
        for i in range(n - k):
            num = float(table[i + 1][k - 1]) - float(table[i][k - 1])
            den = x[i + k] - x[i]
            table[i][k] = num / den
    return table


def newton_eval_divided_differences(
    x_nodes: Sequence[float], coeffs: Sequence[float], x: float
) -> float:
    """Вычисление N(x) по коэффициентам c_j и узлам — формула (49)."""
    s = 0.0  # сумма слагаемых
    prod = 1.0  # накопленное произведение (x-x_0)…(x-x_{j-1})
    for j in range(len(coeffs)):
        if j == 0:
            prod = 1.0  # при j=0 множитель пустой → 1
        else:
            prod *= x - x_nodes[j - 1]  # домножаем (x - x_{j-1})
        s += coeffs[j] * prod  # c_j · произведение
    return s


def newton_eval_divided_differences_trace(
    x_nodes: Sequence[float], coeffs: Sequence[float], x_val: float
) -> tuple[float, list[dict[str, float]]]:
    """newton_eval_divided_differences + пошаговые partial_sum для expander в UI."""
    s = 0.0
    prod = 1.0
    steps: list[dict[str, float]] = []
    for j in range(len(coeffs)):
        if j == 0:
            prod = 1.0
        else:
            prod *= x_val - x_nodes[j - 1]
        addend = float(coeffs[j]) * prod  # j-е слагаемое
        s += addend
        steps.append(
            {
                "j": float(j),
                "prod": prod,
                "c_j": float(coeffs[j]),
                "addend": addend,
                "partial_sum": s,
            }
        )
    return s, steps


def newton_interpolate_general(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x: float, *, reorder: bool
) -> float:
    """
    Ньютон по неравным узлам.
    reorder=False — порядок как в таблице.
    reorder=True — узлы переставлены по возрастанию |x-x_i| (рекомендация лекции 4).
    Полином тот же; меняется только численная устойчивость построения разностей.
    """
    xs = list(x_nodes)  # копия, чтобы не портить исходные списки
    ys = list(y_nodes)
    if reorder:
        order = sorted(range(len(xs)), key=lambda i: abs(x - xs[i]))  # ближайший узел первым
        xs = [xs[i] for i in order]  # переставленные x
        ys = [ys[i] for i in order]  # y едут вместе с узлами
    c = divided_differences_coeffs(xs, ys)  # коэффициенты c_j в новом порядке
    return newton_eval_divided_differences(xs, c, x)  # значение N(x)


# =============================================================================
# КОНЕЧНЫЕ РАЗНОСТИ, ПРЯМАЯ И ОБРАТНАЯ ФОРМУЛЫ НЬЮТОНА — лекция 3–4, (46); задание 3
# =============================================================================

def finite_differences_forward(y: Sequence[float]) -> list[list[float]]:
    """
    Таблица прямых разностей Δ^k y_i: строка k — все Δ^k y_i на сетке.
    """
    table: list[list[float]] = [list(map(float, y))]  # k=0: исходные y_i
    row = table[0]
    while len(row) > 1:  # пока есть что разностить
        row = [row[i + 1] - row[i] for i in range(len(row) - 1)]  # Δ по строке
        table.append(row)  # следующий порядок разности
    return table


def finite_differences_backward_at_last(y: Sequence[float]) -> list[float]:
    """
    ∇^k y_n у последнего узла — для второй формулы Ньютона (опора x_n).
    Берём последний элемент каждой строки обратных разностей.
    """
    row = [float(t) for t in y]  # текущая строка таблицы
    out: list[float] = []  # [y_n, ∇y_n, ∇²y_n, …]
    while row:
        out.append(row[-1])  # значение у правого конца
        if len(row) == 1:
            break
        row = [row[i] - row[i - 1] for i in range(1, len(row))]  # ∇: y_i - y_{i-1}
    return out


def newton_forward_trace(
    x0: float, h: float, y: Sequence[float], x_val: float
) -> tuple[float, list[dict[str, float]], float]:
    """
    Первая формула Ньютона: q=(x-x0)/h, N = y0 + Σ C(q,k)·Δ^k y0 / k!.
    Возвращает (N, слагаемые, q).
    """
    q = (x_val - x0) / h  # безразмерный аргумент
    fd = finite_differences_forward(y)  # таблица Δ^k
    s = float(y[0])  # k=0: первое слагаемое y0
    terms: list[dict[str, float]] = [
        {"k": 0.0, "binom_part": 1.0, "delta": float(y[0]), "addend": float(y[0])}
    ]
    for k in range(1, len(y)):  # k=1..n
        dky0 = fd[k][0]  # Δ^k y_0 — первый элемент k-й строки
        prod = 1.0
        for t in range(k):
            prod *= q - t  # q(q-1)…(q-k+1)
        add = (prod / math.factorial(k)) * dky0  # слагаемое k-й степени
        s += add
        terms.append(
            {
                "k": float(k),
                "binom_part": prod / math.factorial(k),
                "delta": dky0,
                "addend": add,
            }
        )
    return s, terms, q


def newton_forward_equal_spacing(
    x0: float, h: float, y: Sequence[float], x: float
) -> float:
    """Обёртка: только значение N(x) по первой формуле."""
    s, _, _ = newton_forward_trace(x0, h, y, x)
    return s


def newton_backward_trace(
    xn: float, h: float, y: Sequence[float], x_val: float
) -> tuple[float, list[dict[str, float]], float]:
    """
    Вторая формула Ньютона: q=(x-x_n)/h, N = y_n + Σ C(q+k-1,k)·∇^k y_n / k!.
    Тот же интерполяционный многочлен, что и прямая формула.
    """
    q = (x_val - xn) / h
    nabla_at_n = finite_differences_backward_at_last(y)  # ∇^k y_n
    s = float(nabla_at_n[0])  # k=0 → y_n
    terms: list[dict[str, float]] = [
        {"k": 0.0, "binom_part": 1.0, "nabla": nabla_at_n[0], "addend": float(nabla_at_n[0])}
    ]
    for k in range(1, len(y)):
        nabla_k = nabla_at_n[k]
        prod = 1.0
        for t in range(k):
            prod *= q + t  # q(q+1)…(q+k-1) — знак «плюс» у обратной формулы
        add = (prod / math.factorial(k)) * nabla_k
        s += add
        terms.append(
            {
                "k": float(k),
                "binom_part": prod / math.factorial(k),
                "nabla": nabla_k,
                "addend": add,
            }
        )
    return s, terms, q


def newton_backward_equal_spacing(
    xn: float, h: float, y: Sequence[float], x: float
) -> float:
    """Обёртка: только значение N(x) по второй формуле."""
    s, _, _ = newton_backward_trace(xn, h, y, x)
    return s


# =============================================================================
# ЛИНЕЙНЫЙ СПЛАЙН — лекция 5, (50)–(51); задание 4
# =============================================================================

def linear_spline_segments(
    x_nodes: Sequence[float], y_nodes: Sequence[float],
) -> list[dict[str, float]]:
    """
    Коэффициенты a_i, b_i на каждом отрезке [x_{i-1}, x_i]: φ(x)=a_i·x+b_i.
    """
    xs, ys = list(x_nodes), list(y_nodes)
    segs: list[dict[str, float]] = []
    for i in range(1, len(xs)):  # по каждому интервалу между соседними узлами
        x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]  # концы отрезка
        if x1 == x0:  # вырожденный отрезок (не должно быть при разных узлах)
            a, b = 0.0, y0
        else:
            a = (y1 - y0) / (x1 - x0)  # наклон прямой
            b = y0 - a * x0  # свободный член из y0 = a·x0 + b
        segs.append(
            {
                "segment": float(i),
                "x_lo": x0,
                "x_hi": x1,
                "y_lo": y0,
                "y_hi": y1,
                "a": a,
                "b": b,
            }
        )
    return segs


def linear_spline(
    x_nodes: Sequence[float], y_nodes: Sequence[float], x: float
) -> float:
    """
    Значение кусочно-линейного сплайна в точке x (линейная интерполяция на отрезке).
    На узлах совпадает с y_i; между узлами — отрезок прямой.
    """
    xs, ys = list(x_nodes), list(y_nodes)
    if x <= xs[0]:  # левее всех узлов — экстраполяция первым отрезком
        x0, y0, x1, y1 = xs[0], ys[0], xs[1], ys[1]
    elif x >= xs[-1]:  # правее — последним отрезком
        x0, y0, x1, y1 = xs[-2], ys[-2], xs[-1], ys[-1]
    else:
        for i in range(1, len(xs)):  # ищем отрезок, куда попадает x
            if xs[i - 1] <= x <= xs[i]:
                x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]
                break
        else:
            raise ValueError("x вне объединения отрезков узлов.")
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)  # параметр 0..1 вдоль отрезка
    return (1.0 - t) * y0 + t * y1  # выпуклая комбинация y0 и y1


# =============================================================================
# УЗЛЫ И КОНТРОЛЬНЫЕ ТОЧКИ по варианту (g, k) — формулы из методички
# base = g - 2k; дальше сдвиги ±3, ±1, 0, +2 и т.д.
# =============================================================================

def table1_nodes(g: int, k: int) -> list[float]:
    """Таблица 1: неравноотстоящие узлы x0..x3."""
    base = float(g) - 2.0 * float(k)
    return [base - 3.0, base - 1.0, base, base + 2.0]


def table1_test_points(g: int, k: int) -> list[float]:
    """Контрольные x для задания 2 (Лагранж/Ньютон по табл. 1)."""
    base = float(g) - 2.0 * float(k)
    return [base - 2.7, base - 0.5, base + 2.8]


def table2_nodes(g: int, k: int) -> list[float]:
    """Таблица 2: равноотстоящие узлы, шаг h=1."""
    base = float(g) - 2.0 * float(k)
    return [base - 2.0, base - 1.0, base, base + 1.0]


def table2_test_points(g: int, k: int) -> list[float]:
    """Контрольные x для задания 3 (прямая/обратная формула Ньютона)."""
    base = float(g) - 2.0 * float(k)
    return [base - 1.7, base - 0.3, base + 1.6]


def spline_test_points(g: int, k: int) -> list[float]:
    """Контрольные x для задания 4 (линейный сплайн)."""
    base = float(g) - 2.0 * float(k)
    return [base - 1.7, base - 0.3, base + 0.8]


def build_tables(g: int, k: int) -> dict:
    """
    Собирает обе таблицы и служебные величины для UI.
    Возвращает table1, table2, h2, x0_table2.
    """
    x1 = table1_nodes(g, k)
    y1 = [f_variant(t) for t in x1]  # y_i = f(x_i)
    x2 = table2_nodes(g, k)
    y2 = [f_variant(t) for t in x2]
    h2 = x2[1] - x2[0]  # шаг равномерной сетки (должен быть постоянным)
    return {
        "table1": (x1, y1),
        "table2": (x2, y2),
        "h2": h2,
        "x0_table2": x2[0],  # левый узел для q=(x-x0)/h
    }
