"""
Лабораторная работа No.2: метод Гаусса с частичным выбором главного элемента по столбцу,
вычисление определителя тем же ходом, невязка r = Ax - b, методы простой итерации и Зейделя
(лекции 3-4, 8-9), подробная LaTeX-трассировка для Гаусса.
"""
import math  # модуль math: произведение диагонали (prod), isnan и т.д.


# Порог "практически ноль" при сравнении с опорным элементом (вырожденность / шум).
_EPS = 1e-15
# При n больше этого числа в трассировку не вставляем полные матрицы в LaTeX (слишком громоздко).
_LATEX_MAX_N = 6


def build_system(n: int, g: int, k: int) -> tuple[list[list[float]], list[float]]:
    """
    Собирает матрицу A и вектор b по параметрам задания.

    g - номер варианта (входит в коэффициенты A), k - подгруппа (правая часть b).
    Для n == 3 используется каноническая 3x3 система из методички; для больших n -
    вспомогательная регулярная схема заполнения (для отладки и произвольного размера).
    """
    # Целые g, k приводим к float, чтобы матрица была вещественной.
    gf, kf = float(g), float(k)
    if n == 3:
        # Три уравнения с параметром g в коэффициентах и k, k+1, k+2 в b.
        # Первая строка A и далее - фиксированный шаблон из задания.
        A = [
            [gf, gf + 1, gf + 2],
            [2 * gf, gf + 5, gf - 6],
            [3 * gf, gf - 1, -3.0],
        ]
        # Правая часть: k, k+1, k+2.
        return A, [kf, kf + 1, kf + 2]
    # Общий случай: диагональ "крупная", внедиагональные - смешанные g, k.
    # Вспомогательная величина для масштаба диагонали.
    base = abs(gf) + abs(kf) + 1.0
    # Нулевая матрица nxn.
    A = [[0.0] * n for _ in range(n)]
    # Заполняем все элементы по формулам (диагональ / внедиагональ).
    for i in range(n):
        for j in range(n):
            # На диагонали - крупное значение; иначе - дробное от g,k.
            A[i][j] = (
                base * n + abs(g + k) * (i + 1) if i == j else (gf * (i - j) + kf) / (n + 1)
            )
    # b_i = k + i для i = 0..n-1.
    return A, [kf + float(i) for i in range(n)]


def Ax(A: list[list[float]], x: list[float]) -> list[float]:
    """Умножение матрицы A на вектор x: результат - список длины n (строки A)."""
    # i-я компонента: скалярное произведение i-й строки A на x.
    return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]


def residual(A: list[list[float]], b: list[float], x: list[float]) -> list[float]:
    """Невязка при подстановке решения: r = Ax - b (покомпонентно)."""
    # (Ax)_i минус b_i для каждого i.
    return [v - b[i] for i, v in enumerate(Ax(A, x))]


def norm_inf(v: list[float]) -> float:
    """Норма ||v||_inf = max_i |v_i|; для пустого вектора возвращает 0."""
    # Максимум из модулей компонент; пустой список даёт 0.
    return max(abs(t) for t in v) if v else 0.0


def norm_1_vec(v: list[float]) -> float:
    """Норма ||v||_1 = sum_i |v_i|."""
    # Сумма модулей всех компонент.
    return sum(abs(t) for t in v)


def matrix_norm_inf(A: list[list[float]]) -> float:
    """Норма матрицы, согласованная с ||*||_inf: ||A||_inf = max_i sum_j |a_ij| (макс. сумма по строке)."""
    # Пустая матрица - норма 0.
    if not A:
        return 0.0
    # Берём максимум по строкам от суммы |a_ij| по столбцам j.
    return max(sum(abs(A[i][j]) for j in range(len(A[0]))) for i in range(len(A)))


def matrix_norm_1(A: list[list[float]]) -> float:
    """Норма матрицы, согласованная с ||*||_1: ||A||_1 = max_j sum_i |a_ij| (макс. сумма по столбцу)."""
    # Нет строк или нет столбцов - норма 0.
    if not A or not A[0]:
        return 0.0
    # Размеры: n строк, m столбцов.
    n, m = len(A), len(A[0])
    # Максимум по j от суммы |a_ij| по строкам i.
    return max(sum(abs(A[i][j]) for i in range(n)) for j in range(m))


def vec_sub(a: list[float], b: list[float]) -> list[float]:
    """Покомпонентная разность a - b (длины векторов должны совпадать)."""
    return [a[i] - b[i] for i in range(len(a))]


def jacobi_iterative_form(
    A: list[list[float]], b: list[float]
) -> tuple[list[list[float]], list[float]]:
    """
    Приведение Ax = b к виду x = alpha*x + beta (лекция 8): beta_i = b_i/a_ii, alpha_ij = -a_ij/a_ii (i!=j), alpha_ii = 0.
    Требуются ненулевые диагональные элементы.
    """
    # Порядок системы (число неизвестных).
    n = len(A)
    # Матрица итераций alpha (сначала нули).
    alpha = [[0.0] * n for _ in range(n)]
    # Вектор свободных членов в форме x = alpha*x + beta.
    beta = [0.0] * n
    # Построчно выражаем x_i через остальные неизвестные.
    for i in range(n):
        # Деление на диагональ возможно только если a_ii != 0.
        if abs(A[i][i]) < _EPS:
            raise ValueError(f"Нулевой диагональный элемент a[{i},{i}] - нельзя построить итерационную форму.")
        for j in range(n):
            # Внедиагональные коэффициенты переносятся с минусом и делятся на a_ii.
            if i != j:
                alpha[i][j] = -A[i][j] / A[i][i]
        # Постоянная часть i-го уравнения в итерационной форме.
        beta[i] = b[i] / A[i][i]
    return alpha, beta


def split_alpha_seidel(alpha: list[list[float]]) -> tuple[list[list[float]], list[list[float]]]:
    """
    alpha = alpha_1 + alpha_2 (лекция 9): alpha_1 - строго нижнетреугольная, alpha_2 - верхнетреугольная с диагональю.
    """
    n = len(alpha)
    # Нижняя часть alpha (строго под главной диагональю).
    a1 = [[0.0] * n for _ in range(n)]
    # Верхняя часть включая диагональ.
    a2 = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            # j < i - относится к уже "новым" компонентам в шаге Зейделя.
            if j < i:
                a1[i][j] = alpha[i][j]
            else:
                # j >= i - используются значения с предыдущей итерации (или текущие на диагонали в alpha).
                a2[i][j] = alpha[i][j]
    return a1, a2


def check_convergence_simple_iteration(
    alpha: list[list[float]],
) -> tuple[bool, str, float, float]:
    """
    Достаточное условие (лекция 8, теорема 2): если ||alpha|| < 1 в какой-либо матричной норме,
    процесс сходится при любом начальном приближении. Проверяем ||alpha||_inf и ||alpha||_1.
    """
    # Матричная норма "максимум сумм по строкам".
    n_inf = matrix_norm_inf(alpha)
    # Матричная норма "максимум сумм по столбцам".
    n_1 = matrix_norm_1(alpha)
    # Достаточно, чтобы хотя бы одна из проверяемых норм была строго меньше 1.
    ok = n_inf < 1.0 - _EPS or n_1 < 1.0 - _EPS
    # Фрагменты текста для отчёта пользователю.
    parts = [
        f"||alpha||_inf = {n_inf:.6g}",
        f"||alpha||_1 = {n_1:.6g}",
    ]
    if ok:
        msg = "Достаточное условие сходимости выполняется: " + ", ".join(parts) + " (хотя бы одна норма < 1)."
    else:
        msg = (
            "**Ни** в норме ||*||_inf, **ни** в ||*||_1 матрица alpha не имеет нормы < 1: "
            + ", ".join(parts)
            + ". Достаточное условие из лекции (хотя бы одна из этих норм < 1) **не** выполняется; "
            "сходимость не гарантирована (возможна при rho(alpha) < 1)."
        )
    return ok, msg, n_inf, n_1


def check_convergence_seidel(
    alpha: list[list[float]],
) -> tuple[bool, str, float, float, float]:
    """
    Достаточное условие (лекция 9): q = ||alpha_2||/(1 - ||alpha_1||) < 1 при ||alpha_1|| < 1 (используем ||*||_inf).
    """
    # Раскладываем alpha на нижнюю и верхнюю (с диагональю) части.
    a1, a2 = split_alpha_seidel(alpha)
    # Норма ||alpha_1||_inf.
    na1 = matrix_norm_inf(a1)
    # Норма ||alpha_2||_inf.
    na2 = matrix_norm_inf(a2)
    if na1 >= 1.0 - _EPS:
        # Знаменатель 1 - ||alpha_1|| неположителен - формула для q из лекции неприменима.
        ok = False
        q = float("inf")
        msg = (
            f"||alpha_1||_inf = {na1:.6g} >= 1 - условие из лекции (знаменатель 1-||alpha_1||) не выполняется. "
            f"||alpha_2||_inf = {na2:.6g}."
        )
    else:
        # Вычисляем q по лекции; при q < 1 даётся достаточное условие сходимости Зейделя.
        q = na2 / (1.0 - na1)
        ok = q < 1.0 - _EPS
        msg = f"||alpha_1||_inf = {na1:.6g}, ||alpha_2||_inf = {na2:.6g}, q = ||alpha_2||_inf/(1-||alpha_1||_inf) = {q:.6g}."
        if ok:
            msg = "Достаточное условие сходимости Зейделя: q < 1. " + msg
        else:
            msg = "Достаточное условие q < 1 **не** выполняется. " + msg
    return ok, msg, na1, na2, q


def _iter_print_header(title: str, conv_ok: bool, conv_msg: str, *, verbose: bool = True) -> None:
    if not verbose:
        return
    # Визуальный разделитель и заголовок метода в консоли.
    print(f"\n{'='*60}\n{title}\n{'='*60}")
    # Подпись первого этапа: теоретическая проверка сходимости.
    print("Этап 1 - проверка сходимости:")
    # Текст с численными нормами и выводом.
    print(conv_msg)
    # Краткий итог: "ок" или предупреждение.
    print(f"Итог проверки: {'условия достаточной сходимости выполняются' if conv_ok else 'предупреждение / условие не выполнено'}")
    # Подпись второго этапа: сами итерации.
    print("\nЭтап 2 - итерации (вектор приближения и точность):")


def simple_iteration_solve(
    A: list[list[float]],
    b: list[float],
    *,
    tol: float = 1e-8,
    max_iter: int = 500,
    x0: list[float] | None = None,
    verbose: bool = True,
) -> tuple[list[float], list[dict]]:
    """
    Метод простой итерации: x^(k) = alpha x^(k-1) + beta, x^(0) = beta (лекция 8).
    При verbose=True печатает этап проверки сходимости и каждую итерацию; иначе только заполняет history.
    В history первая строка - k=0 (начальное приближение), далее k>=1.
    """
    # Строим alpha и beta из исходной системы (деление на диагональ).
    alpha, beta = jacobi_iterative_form(A, b)
    # Этап 1: проверка ||alpha||_inf и ||alpha||_1.
    conv_ok, conv_msg, n_inf, n_1 = check_convergence_simple_iteration(alpha)
    # Апостериорная оценка ||x-x^(k)|| <= (nu/(1-nu))||x^(k)-x^(k-1)|| строго согласована с ||·||_inf,
    # если nu = ||alpha||_inf < 1. Если nu берётся из ||alpha||_1, а приращение считаем в ||·||_inf,
    # оценка может быть не из той же теоремы — для надёжности в отчёте опирайтесь на случай ||alpha||_inf < 1.
    nu_for_est = n_inf if n_inf < 1.0 - _EPS else (n_1 if n_1 < 1.0 - _EPS else None)

    _iter_print_header("Метод простой итерации (Якоби в форме x = alpha*x + beta)", conv_ok, conv_msg, verbose=verbose)

    # Начальное приближение: по умолчанию beta, иначе переданный x0.
    x = list(beta if x0 is None else x0)
    n = len(x)
    # Журнал шагов (Streamlit и т.п.): с нулевой итерации.
    history: list[dict] = [
        {
            "k": 0,
            "x": x[:],
            "delta_inf": float("nan"),
            "accuracy_est": float("nan"),
            "residual_inf": norm_inf(residual(A, b, x)),
        }
    ]

    if verbose:
        print(f"k = 0  x^(0) = {[round(t, 8) for t in x]}  (начальное приближение)")

    # Копия предыдущего приближения для сравнения и формулы x^(k) = alpha x^(k-1) + beta.
    x_prev = x[:]
    for k in range(1, max_iter + 1):
        # Новое приближение: целиком из старого вектора (метод Якоби).
        x_new = [sum(alpha[i][j] * x_prev[j] for j in range(n)) + beta[i] for i in range(n)]
        # Приращение по норме inf - критерий остановки и "точность" шага.
        diff = norm_inf(vec_sub(x_new, x_prev))
        if nu_for_est is not None:
            # Оценка погрешности решения через разность двух итераций (лекция 8).
            accuracy_est = (nu_for_est / (1.0 - nu_for_est)) * diff
        else:
            # Нормы alpha >= 1 - классическая оценка через ||alpha||/(1-||alpha||) не задаётся.
            accuracy_est = float("nan")
        # Невязка ||Ax - b||_inf показывает, насколько текущий x удовлетворяет системе.
        res_n = norm_inf(residual(A, b, x_new))

        rec = {
            "k": k,
            "x": x_new[:],
            "delta_inf": diff,
            "accuracy_est": accuracy_est,
            "residual_inf": res_n,
        }
        history.append(rec)

        acc_str = f"оценка ||x-x^(k)||_inf <= {accuracy_est:.6g}" if nu_for_est is not None else "оценка по ||alpha||<1 недоступна"
        if verbose:
            print(
                f"k = {k}  x^({k}) = {[round(t, 8) for t in x_new]}  "
                f"||x^({k})-x^({k-1})||_inf = {diff:.6g}  {acc_str}  ||r||_inf = {res_n:.6g}"
            )

        if diff < tol:
            if verbose:
                print(f"Останов: ||x^({k})-x^({k-1})||_inf < tol = {tol}.")
            return x_new, history

        # Сдвигаем "предыдущий" вектор для следующего шага.
        x_prev = x_new

    if verbose:
        print(f"Достигнуто max_iter = {max_iter}.")
    return x_prev, history


def seidel_solve(
    A: list[list[float]],
    b: list[float],
    *,
    tol: float = 1e-8,
    max_iter: int = 500,
    x0: list[float] | None = None,
    verbose: bool = True,
) -> tuple[list[float], list[dict]]:
    """
    Метод Зейделя: x_i^(k+1) = sum_{j<i} alpha_ij x_j^(k+1) + sum_{j>=i} alpha_ij x_j^(k) + beta_i (лекция 9).
    verbose: печать в консоль; при False удобно вызывать из Streamlit и разбирать history.
    В history есть строка k=0, затем шаги k>=1 (поле q повторяется в каждой записи для отладки).
    """
    # Та же alpha, beta, что и для простой итерации; отличается только порядок обновления компонент.
    alpha, beta = jacobi_iterative_form(A, b)
    # Этап 1: проверка q = ||alpha_2||_inf/(1-||alpha_1||_inf).
    conv_ok, conv_msg, na1, na2, q = check_convergence_seidel(alpha)

    _iter_print_header("Метод Зейделя", conv_ok, conv_msg, verbose=verbose)

    n = len(beta)
    # Старт: beta или пользовательский x0.
    x = list(beta) if x0 is None else list(x0)

    history: list[dict] = [
        {
            "k": 0,
            "x": x[:],
            "delta_inf": float("nan"),
            "accuracy_est": float("nan"),
            "residual_inf": norm_inf(residual(A, b, x)),
            "q": q,
        }
    ]
    if verbose:
        print(f"k = 0  x^(0) = {[round(t, 8) for t in x]}")

    x_prev = x[:]
    for k in range(1, max_iter + 1):
        # Копия предыдущего шага; будем перезаписывать x по компонентам "на лету".
        x = x_prev[:]
        for i in range(n):
            # Начинаем с beta_i, добавляем вклад всех x_j с уже обновлёнными j < i.
            s = beta[i]
            for j in range(n):
                if j == i:
                    # alpha_ii в нашей форме всегда 0 - пропуск.
                    continue
                s += alpha[i][j] * x[j]
            # Для j > i в x[j] ещё лежат значения с предыдущей итерации - это и есть Зейдель.
            x[i] = s
        diff = norm_inf(vec_sub(x, x_prev))
        if conv_ok and q < 1.0 - _EPS:
            # Апостериорная оценка по параметру q из лекции (аналогично виду с ||alpha||/(1-||alpha||)).
            accuracy_est = (q / (1.0 - q)) * diff
        else:
            accuracy_est = float("nan")
        res_n = norm_inf(residual(A, b, x))

        history.append(
            {
                "k": k,
                "x": x[:],
                "delta_inf": diff,
                "accuracy_est": accuracy_est,
                "residual_inf": res_n,
                "q": q,
            }
        )

        acc_str = (
            f"оценка (по q) ||x-x^(k)||_inf <= {accuracy_est:.6g}"
            if not math.isnan(accuracy_est)
            else "оценка по q недоступна"
        )
        if verbose:
            print(
                f"k = {k}  x^({k}) = {[round(t, 8) for t in x]}  "
                f"||x^({k})-x^({k-1})||_inf = {diff:.6g}  {acc_str}  ||r||_inf = {res_n:.6g}"
            )

        if diff < tol:
            if verbose:
                print(f"Останов: ||x^({k})-x^({k-1})||_inf < tol = {tol}.")
            return x, history

        x_prev = x[:]

    if verbose:
        print(f"Достигнуто max_iter = {max_iter}.")
    return x, history



def _copy_mat(A: list[list[float]]) -> list[list[float]]:
    """Глубокая копия матрицы (списки строк), чтобы не портить исходные данные."""
    # Каждая строка копируется отдельно (неглубокая копия строки = новый список чисел).
    return [r[:] for r in A]


def _fmt(x: float) -> str:
    """Формат числа для вывода в трассировке и LaTeX (компактно, ~6 значащих цифр)."""
    # .6g - до 6 значащих цифр, компактная запись больших/малых чисел.
    return f"{x:.6g}"


def _augmented_tex(M: list[list[float]], rhs: list[float]) -> str:
    """
    Строка LaTeX: расширенная матрица [M | rhs] в виде array с вертикальной чертой.

    Используется в markdown-трассировке (Streamlit рендерит как часть формулы).
    """
    n = len(M)
    # Спецификация столбцов: n раз "центр", черта, ещё один столбец для b.
    spec = "c" * n + "|c"  # n столбцов A + разделитель + столбец правой части
    body_rows = []
    for i in range(n):
        # Левая часть строки: коэффициенты уравнения.
        left = r" & ".join(_fmt(M[i][j]) for j in range(n))
        # Правая часть b_i в той же строке LaTeX.
        body_rows.append(rf"{left} & {_fmt(rhs[i])}")
    # Строки матрицы разделяются \\ в LaTeX.
    inner = r" \\".join(body_rows)  # конец строки в LaTeX array
    # Обёртка в квадратные скобки как принято в LaTeX.
    return rf"\left[\begin{{array}}{{{spec}}} {inner} \end{{array}}\right]"


def determinant_gauss_pivot(A: list[list[float]]) -> float:
    """
    det A через приведение к верхнетреугольному виду с тем же правилом pivot по столбцу.

    Каждая перестановка двух строк меняет знак определителя; det равен произведению
    диагонали треугольника с учётом знака. Если опорный элемент обнулился - det = 0.
    """
    # Размер квадратной матрицы.
    n = len(A)
    # Работаем с копией, исходную A не меняем.
    M = _copy_mat(A)
    # Знак определителя: каждая перестановка строк умножает det на -1.
    sign = 1  # (-1)^(число перестановок)
    for k in range(n):
        # Индекс строки с максимальным |a_ik| в столбце k снизу от диагонали.
        p = max(range(k, n), key=lambda r: abs(M[r][k]))
        if abs(M[p][k]) < _EPS:
            # Столбец вырожден - треугольный вид даст ноль на диагонали, det = 0.
            return 0.0
        if p != k:
            # Меняем строки местами (как в методе Гаусса с выбором главного).
            M[k], M[p] = M[p], M[k]
            sign = -sign
        # Опорный элемент на диагонали после перестановки.
        t = M[k][k]
        # Исключение: обнуляем поддиагональ в столбце k (без хранения правой части).
        for i in range(k + 1, n):
            # Множитель исключения для строки i.
            c = M[i][k] / t
            for j in range(k, n):
                # Элементарное преобразование: строка_i - c*строка_k.
                M[i][j] -= c * M[k][j]
    # det = знак x произведение диагонали верхнетреугольной матрицы.
    return sign * math.prod(M[i][i] for i in range(n))


def solve_gauss_elimination_column_pivot(
    A: list[list[float]],
    b: list[float],
    trace_latex: bool = False,
) -> tuple[list[float], list[str] | None, list[list[float]], dict]:
    """
    Решение Ax = b методом Гаусса с выбором главного элемента по столбцу.

    Возвращает:
        x - решение;
        latex - список строк markdown/LaTeX для пошагового отчёта или None;
        aug - расширенная матрица [U|c] после прямого хода;
        stats - счётчики перестановок и операций обновления коэффициентов.
    """
    # --- Инициализация прямого хода Гаусса с выбором главного элемента по столбцу ---
    # Порядок системы.
    n = len(A)
    M = _copy_mat(A)  # рабочая копия A
    r = list(b)  # правая часть синхронно переставляется с строками M
    # Список строк отчёта в LaTeX/markdown или None, если трассировка выключена.
    latex: list[str] | None = [] if trace_latex else None
    swaps = 0  # число перестановок строк
    ops = 0  # число обновлений элементов M[i][j] при исключении + обновлений r[i]

    def L(*lines: str) -> None:
        """Добавить строки в буфер трассировки (если она включена)."""
        if latex is not None:
            latex.extend(lines)

    # Вступление и начальное состояние [A|b] в трассировке.
    if trace_latex:
        assert latex is not None
        L(
            r'**Лекция 3, тема 2 "Задачи вычислительной алгебры".** Метод Гаусса **с выбором главного элемента по столбцу** (частичный pivot).',
            r"На шаге $k$ ($k=1,\ldots,n$) в **столбце $k$** среди строк $k,\ldots,n$ ищем элемент с **максимальным модулем** $|a_{ik}|$, меняем строки местами, затем обнуляем столбец $k$ под диагональю: из строки $i$ вычитаем $\alpha_{ik}$ умноженную на опорную строку $k$, где $\alpha_{ik} = a_{ik}^{(k-1)}/a_{kk}^{(k-1)}$.",
            r"**Обратный ход:** из верхнетреугольной системы находим $x_n, x_{n-1}, \ldots, x_1$.",
            "---",
            r"**Исходная система** $A\vec{x}=\vec{b}$.",
        )
        if n <= _LATEX_MAX_N:
            # Вставляем полную расширенную матрицу в отчёт (малый n).
            L(rf"Расширенная матрица $[A\,|\,\vec b]$: ${_augmented_tex(M, r)}$")
        else:
            # Для больших n матрицу в LaTeX не разворачиваем - слишком длинно.
            L(f"*(Размер $n={n}$: матрицу см. таблицу на экране; ниже - численные шаги.)*")

    # ---------- Прямой ход: для каждого k - pivot, перестановка, исключение ----------
    for k in range(n):
        if trace_latex:
            L("---", f"### Прямой ход: столбец {k + 1} (исключаем $x_{{{k + 1}}}$)")

        # Пары (номер строки, элемент) в текущем столбце k от диагонали вниз - для подписи в отчёте.
        col_vals = [(i, M[i][k]) for i in range(k, n)]
        # Номер строки, где в столбце k максимум по модулю (частичный pivot по столбцу).
        p = max(range(k, n), key=lambda i: abs(M[i][k]))
        if abs(M[p][k]) < _EPS:
            raise ValueError("Нулевой опорный элемент - система вырождена или неустойчива.")

        if trace_latex:
            cand = ", ".join(
                rf"строка ${i + 1}$: $|a_{{{i + 1},{k + 1}}}| = {_fmt(abs(v))}$"
                for i, v in col_vals
            )
            L(rf"**Шаг 1.** В столбце ${k + 1}$ среди строк ${k + 1}\ldots{n}$: {cand}.")
            L(
                rf"**Шаг 2.** Максимум по модулю - в **строке ${p + 1}$**: "
                rf"$|a_{{{p + 1},{k + 1}}}| = {_fmt(abs(M[p][k]))}$."
            )

        if p != k:
            # Учёт перестановки для статистики.
            swaps += 1
            # Меняем местами строки матрицы и соответствующие компоненты b.
            M[k], M[p] = M[p], M[k]
            r[k], r[p] = r[p], r[k]
            if trace_latex:
                L(
                    rf"**Шаг 3.** **Перестановка строк** ${k + 1} \leftrightarrow {p + 1}$ "
                    rf"(меняем местами уравнения, чтобы главный элемент стал на позицию $({k + 1},{k + 1})$)."
                )
        elif trace_latex:
            L(rf"**Шаг 3.** Перестановка не нужна: главный элемент уже в строке ${k + 1}$.")

        piv = M[k][k]  # ведущий элемент на диагонали после возможной перестановки
        if trace_latex:
            L(rf"**Шаг 4.** Опорный (ведущий) элемент после выбора: $a_{{{k + 1},{k + 1}}} = {_fmt(piv)}$.")

        # Обнуляем элементы под диагональю в столбце k для строк i > k.
        for i in range(k + 1, n):
            alpha = M[i][k] / piv  # множитель: строка_i -= alpha * строка_k
            if trace_latex:
                L(
                    rf"**Строка ${i + 1}$.** Множитель исключения: "
                    rf"$\alpha = a_{{{i + 1},{k + 1}}}/a_{{{k + 1},{k + 1}}} = {_fmt(M[i][k])}/{_fmt(piv)} = {_fmt(alpha)}$."
                )
                L(rf"Операция: $(\text{{стр. }}{i + 1}) := (\text{{стр. }}{i + 1}) - \alpha\cdot(\text{{стр. }}{k + 1})$.")
            row_old = M[i][:]  # снимок строки до изменений - для подписей в трассировке
            b_old = r[i]
            # Обновляем коэффициенты от столбца k до конца (слева уже нули в столбце k у строки i).
            for j in range(k, n):
                new_v = M[i][j] - alpha * M[k][j]
                if trace_latex:
                    L(
                        rf"$a_{{{i + 1},{j + 1}}} := {_fmt(row_old[j])} - {_fmt(alpha)}\cdot {_fmt(M[k][j])} = {_fmt(new_v)}$"
                    )
                M[i][j] = new_v
                ops += 1
            # Та же операция для правой части (вектор b).
            r_new = r[i] - alpha * r[k]
            if trace_latex:
                L(rf"$b_{{{i + 1}}} := {_fmt(b_old)} - {_fmt(alpha)}\cdot {_fmt(r[k])} = {_fmt(r_new)}$")
            r[i] = r_new
            ops += 1

        if trace_latex and n <= _LATEX_MAX_N:
            L(rf"**Матрица после исключения в столбце ${k + 1}$:** ${_augmented_tex(M, r)}$")

    # Расширенная матрица для отображения в UI: верхнетреугольная U и преобразованная c.
    aug = [M[i] + [r[i]] for i in range(n)]
    # Решение; заполняется с конца при обратном ходе.
    x = [0.0] * n

    # ---------- Обратный ход: x_n, x_{n-1}, ... ----------
    if trace_latex:
        L(
            "---",
            "### Обратный ход",
            r"Система верхнетреугольная: последнее уравнение даёт $x_n$, подстановка выше - $x_{n-1},\ldots$",
        )

    for i in range(n - 1, -1, -1):
        # Сумма a_ij * x_j для j > i (эти x уже найдены на предыдущих шагах цикла).
        ssum = sum(M[i][j] * x[j] for j in range(i + 1, n))  # уже известные x_{i+1}..x_n
        # Правая часть после переноса известных слагаемых в левую сторону.
        rhs_rest = r[i] - ssum
        # x_i = (обновлённая правая часть) / a_ii.
        x[i] = rhs_rest / M[i][i]
        if trace_latex:
            if i == n - 1:
                L(
                    rf"**Шаг 1.** $x_{{{i + 1}}} = b_{{{i + 1}}}^{{(тр)}}/a_{{{i + 1},{i + 1}}} = {_fmt(r[i])}/{_fmt(M[i][i])} = {_fmt(x[i])}$."
                )
            else:
                # LaTeX-строка с символами суммы для отчёта.
                tail = " + ".join(
                    rf"a_{{{i + 1},{j + 1}}}x_{{{j + 1}}}"
                    for j in range(i + 1, n)
                )
                # Численные слагаемые для той же суммы.
                sum_part = " + ".join(_fmt(M[i][j] * x[j]) for j in range(i + 1, n))
                L(
                    rf"**$x_{{{i + 1}}}$.** $x_{{{i + 1}}} = (b_{{{i + 1}}} - ({tail}))/a_{{{i + 1},{i + 1}}}$.",
                    rf"Численно: $({_fmt(r[i])} - ({sum_part}))/{_fmt(M[i][i])} = {_fmt(rhs_rest)}/{_fmt(M[i][i])} = {_fmt(x[i])}$.",
                )

    if trace_latex:
        # Итоговый вектор решения одной строкой в LaTeX.
        xv = ", ".join(_fmt(v) for v in x)
        L("---", "**Вектор решения (метод Гаусса):**", rf"$\vec x^T \approx ({xv})$.")

    # Сводка для интерфейса: сколько раз меняли строки и сколько раз обновляли элементы.
    stats = {"row_swaps": swaps, "elimination_ops": ops, "forward_pass_outer_iterations": n}
    return x, latex, aug, stats


# Короткий синоним имени функции (удобно в отчётах / импортах).
solve_gauss_column_pivot = solve_gauss_elimination_column_pivot


def trace_residual_latex(A: list[list[float]], b: list[float], x: list[float]) -> list[str]:
    """
    Строит текстовую трассировку проверки: каждая компонента r_i = (Ax)_i - b_i и ||r||_inf.

    Предназначено для вывода в Streamlit после получения решения x.
    """
    n = len(x)
    # Заголовок раздела и определение невязки в LaTeX.
    lines: list[str] = [
        "---",
        "### Невязка $\\vec r = A\\vec x - \\vec b$",
        r"По определению: $r_i = (A\vec x)_i - b_i = \sum_{j=1}^n a_{ij}x_j - b_i$.",
    ]
    # Вектор Ax для подстановки в формулы (один раз считаем).
    ax = Ax(A, x)
    for i in range(n):
        # Символьная сумма и численное развёртывание скалярного произведения i-й строки на x.
        terms = " + ".join(rf"a_{{{i + 1},{j + 1}}}x_{{{j + 1}}}" for j in range(n))
        num = " + ".join(_fmt(A[i][j] * x[j]) for j in range(n))
        ri = ax[i] - b[i]
        lines.append(
            rf"**$r_{{{i + 1}}}$.** $(A\vec x)_{{{i + 1}}} = {terms} = {num} = {_fmt(ax[i])}$; "
            rf"$r_{{{i + 1}}} = {_fmt(ax[i])} - {_fmt(b[i])} = {_fmt(ri)}$."
        )
    # Финальная строка: норма невязки по максимуму модулей.
    lines.append(rf"$\|\vec r\|_\infty = \max_i |r_i| = {_fmt(norm_inf(residual(A, b, x)))}$.")
    return lines


if __name__ == "__main__":
    # Параметры демо: размер 3, вариант g=5, подгруппа k=1 (как в типовом задании).
    n, g, k_par = 3, 5, 1
    A0, b0 = build_system(n, g, k_par)
    print("Система из методички (пример): A, b заданы.")
    # Решение прямым методом без LaTeX-трассировки (только числа).
    xg, _, _, _ = solve_gauss_elimination_column_pivot(A0, b0, trace_latex=False)
    print("Гаусс (главный элемент по столбцу):", [round(t, 8) for t in xg])
    print("||r||_inf после Гаусса:", norm_inf(residual(A0, b0, xg)))

    # Для итерационных методов - строго диагонально доминирующая 3x3 (сходимость ||alpha||_inf < 1).
    A_dd = [[4.0, 1.0, 0.0], [1.0, 4.0, 1.0], [0.0, 1.0, 4.0]]
    b_dd = [1.0, 2.0, 3.0]
    print("\n--- Итерации на диагонально доминирующей системе (демонстрация сходимости) ---")
    simple_iteration_solve(A_dd, b_dd, tol=1e-8, max_iter=100)
    seidel_solve(A_dd, b_dd, tol=1e-8, max_iter=100)
