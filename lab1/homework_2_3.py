import math
G = 1
K = 22
EPS = 0.05  
EPS_SYS = 0.1  
MAX_ITER = 200  
def find_bracket(
    f,
    x_start: float = 0,
    step: float = 0.5,
    max_steps: int = 200,
) -> tuple[float, float]:
    eps = 1e-12
    fc = f(x_start)
    if abs(fc) < eps:
        x_start = x_start + step * 0.5
        fc = f(x_start)
    x = x_start
    fa = fc
    for _ in range(max_steps):
        x += step
        fb = f(x)
        if fa * fb < 0:
            return (x - step, x)
        if abs(fb) >= eps:
            fa = fb
    x = x_start
    fa = fc
    for _ in range(max_steps):
        x -= step
        fb = f(x)
        if fa * fb < 0:
            return (x, x + step)
        if abs(fb) >= eps:
            fa = fb
    raise ValueError(f"Не найден отрезок с переменой знака (x_start={x_start}, step={step})")
def f2(x: float, k: float = K, g: int = G) -> float:
    t = x - g * k
    return t * t + math.sin(t)
def f2_prime(x: float, k: float = K, g: int = G) -> float:
    t = x - g * k
    return 2 * t + math.cos(t)
def f2_prime2(x: float, k: float = K, g: int = G) -> float:
    return 2 - math.sin(x - g * k)
def f3(x: float, k: float = K, g: int = G) -> float:
    return (k * x - 10 * g) - math.sin(x - 10 * g / k)
def f3_prime(x: float, k: float = K, g: int = G) -> float:
    return k - math.cos(x - 10 * g / k)
def _u6(x: float, y: float, k: float, g: int) -> float:
    return k * x + y - 4 * g
def f6_1(x: float, y: float, k: float = 22, g: int = 1) -> float:
    return k * x - 4 * g + math.sin(_u6(x, y, k, g)) / 10
def f6_2(x: float, y: float, k: float = 22, g: int = 1) -> float:
    return y - math.sin(_u6(x, y, k, g)) / (10 * g)
def phi6_1(x: float, y: float, k: float, g: int) -> float:
    return (4 * g - math.sin(_u6(x, y, k, g)) / 10) / k
def phi6_2(x: float, y: float, k: float, g: int) -> float:
    return math.sin(_u6(x, y, k, g)) / (10 * g)


def method_iteration_system(
    x0: float, y0: float, eps: float, k: float = 22, g: int = 1, trace_latex: bool = False
) -> tuple[tuple[float, float], list, list | None]:
    latex_out = [] if trace_latex else None
    if trace_latex:
        latex_out.extend([
            r"**Лекция 5 темы «Системы нелинейных уравнений» (метод итераций).** Обобщение формулы (28) на систему. Формула (36): $(x,y)_{n+1} = (\varphi_1(x_n,y_n), \varphi_2(x_n,y_n))$.",
            r"**Система двух уравнений:**",
            rf"$f_1(x,y) = k \cdot x - 4g + \frac{{\sin(kx + y - 4g)}}{{10}} = 0$",
            rf"$f_2(x,y) = y - \frac{{\sin(kx + y - 4g)}}{{10g}} = 0$",
            rf"При $k = {k}$, $g = {g}$.",
            r"**Вывод итерационных функций $\varphi_1$, $\varphi_2$:**",
            r"Введём $u = kx + y - 4g$. Тогда:",
            r"Из $f_1 = 0$: $kx - 4g + \frac{\sin(u)}{10} = 0$ $\Rightarrow$ $kx = 4g - \frac{\sin(u)}{10}$ $\Rightarrow$ $\boxed{x = \varphi_1(x,y) = \frac{4g - \sin(u)/10}{k}}$",
            r"Из $f_2 = 0$: $y - \frac{\sin(u)}{10g} = 0$ $\Rightarrow$ $\boxed{y = \varphi_2(x,y) = \frac{\sin(u)}{10g}}$",
            r"**Метод итераций:** $x_{n+1} = \varphi_1(x_n, y_n)$, $y_{n+1} = \varphi_2(x_n, y_n)$",
            rf"**Начальное приближение:** $x_0 = {x0:.6f}$, $y_0 = {y0:.6f}$",
            "---",
        ])
    rows = [(0, x0, y0, f6_1(x0, y0, k, g), f6_2(x0, y0, k, g), None)]
    x, y = x0, y0
    for n in range(1, MAX_ITER + 1):
        u_val = _u6(x, y, k, g)
        su = math.sin(u_val)
        x_new = phi6_1(x, y, k, g)
        y_new = phi6_2(x, y, k, g)
        dx, dy = abs(x_new - x), abs(y_new - y)
        diff = max(dx, dy)
        if trace_latex:
            eps_mark = r"$< \varepsilon$ ✓" if diff < eps else ""
            phi1_num = 4 * g - su / 10
            phi2_val = su / (10 * g)
            kx_plus_y = k * x + y
            kx_plus_y_minus_4g = kx_plus_y - 4 * g
            su_div_10 = su / 10
            if n > 1:
                latex_out.append("---")
            latex_out.extend([
                f"**Итерация {n}**",
                rf"**Шаг 1.** Текущее приближение: $x_{{{n-1}}} = {x:.6f}$, $y_{{{n-1}}} = {y:.6f}$",
                rf"**Шаг 2.** $u = k \cdot x_{{{n-1}}} + y_{{{n-1}}} - 4g = {k} \cdot {x:.6f} + {y:.6f} - 4 \cdot {g} = {kx_plus_y:.6f} - {4*g} = {u_val:.6f}$",
                rf"**Шаг 3.** $\sin(u) = \sin({u_val:.6f}) = {su:.6f}$",
                rf"**Шаг 4.** Числитель $\varphi_1$: $4g - \frac{{\sin(u)}}{{10}} = 4 \cdot {g} - \frac{{{su:.6f}}}{{10}} = {4*g:.6f} - {su_div_10:.6f} = {phi1_num:.6f}$",
                rf"**Шаг 5.** $x_{{{n}}} = \varphi_1 = \frac{{4g - \sin(u)/10}}{{k}} = \frac{{{phi1_num:.6f}}}{{{k}}} = {x_new:.6f}$",
                rf"**Шаг 6.** $y_{{{n}}} = \varphi_2 = \frac{{\sin(u)}}{{10g}} = \frac{{{su:.6f}}}{{10 \cdot {g}}} = {phi2_val:.6f}$",
                rf"**Шаг 7.** Проверка: $f_1(x_{{{n}}}, y_{{{n}}}) = {f6_1(x_new, y_new, k, g):.6f}$, $f_2(x_{{{n}}}, y_{{{n}}}) = {f6_2(x_new, y_new, k, g):.6f}$",
                rf"**Шаг 8.** $\max(|\Delta x|, |\Delta y|) = \max({dx:.6f}, {dy:.6f}) = {diff:.6f}$ {eps_mark}",
            ])
        rows.append((n, x_new, y_new, f6_1(x_new, y_new, k, g), f6_2(x_new, y_new, k, g), diff))
        x, y = x_new, y_new  
        if diff < eps:  
            break
    return (x, y), rows, latex_out  
def method_newton_system(
    x0: float, y0: float, eps: float, k: float = 22, g: int = 1, trace_latex: bool = False
) -> tuple[tuple[float, float], list, list | None]:
    latex_out = [] if trace_latex else None  
    if trace_latex:
        latex_out.extend([
            r"**Лекция 4 темы «Системы нелинейных уравнений» (метод Ньютона).** Формула (33): $(x,y)_{k+1} = (x,y)_k + h_k$, где $J \cdot h = -F$ (формула (32)). Условие окончания (34): $\max|\Delta| < \varepsilon$.",
            r"**Система:** $f_1 = kx - 4g + \frac{\sin(kx+y-4g)}{10} = 0$, $f_2 = y - \frac{\sin(kx+y-4g)}{10g} = 0$",
            r"**Матрица Якоби** $J$ (элементы — частные производные). Пусть $u = kx + y - 4g$:",
            r"$\frac{\partial f_1}{\partial x} = k + \frac{\cos(u)}{10} \cdot k = k\left(1 + \frac{\cos(u)}{10}\right)$",
            r"$\frac{\partial f_1}{\partial y} = \frac{\cos(u)}{10} \cdot 1 = \frac{\cos(u)}{10}$",
            r"$\frac{\partial f_2}{\partial x} = -\frac{\cos(u)}{10g} \cdot k = -\frac{k\cos(u)}{10g}$",
            r"$\frac{\partial f_2}{\partial y} = 1 - \frac{\cos(u)}{10g}$",
            r"**Система Ньютона:** $J \cdot \Delta = -F$, где $F = (f_1, f_2)^T$, $\Delta = (\Delta x, \Delta y)^T$",
            r"**Обратная матрица:** $J^{-1} = \frac{1}{\det J} \begin{pmatrix} j_{22} & -j_{12} \\ -j_{21} & j_{11} \end{pmatrix}$, $\det J = j_{11}j_{22} - j_{12}j_{21}$",
            r"$\Delta x = \frac{-(j_{22}f_1 - j_{12}f_2)}{\det J}$, $\Delta y = \frac{j_{21}f_1 - j_{11}f_2}{\det J}$",
            rf"**Начальное приближение:** $x_0 = {x0:.6f}$, $y_0 = {y0:.6f}$",
            "---",
        ])
    rows = [(0, x0, y0, f6_1(x0, y0, k, g), f6_2(x0, y0, k, g), None)]
    x, y = x0, y0
    for n in range(1, MAX_ITER + 1):
        u = _u6(x, y, k, g)
        f1, f2 = f6_1(x, y, k, g), f6_2(x, y, k, g)
        cu = math.cos(u)
        j11 = k * (1 + cu / 10)
        j12 = cu / 10
        j21 = -k * cu / (10 * g)
        j22 = 1 - cu / (10 * g)
        det = j11 * j22 - j12 * j21
        if abs(det) < 1e-15:
            raise ValueError("Якобиан вырожден, метод неприменим.")
        num_dx = -(j22 * f1 - j12 * f2)
        num_dy = -(-j21 * f1 + j11 * f2)
        dx_val = num_dx / det
        dy_val = num_dy / det
        x_new, y_new = x + dx_val, y + dy_val
        diff = max(abs(dx_val), abs(dy_val))
        if trace_latex:
            eps_mark = r"$< \varepsilon$ ✓" if diff < eps else ""
            j11_j22 = j11 * j22
            j12_j21 = j12 * j21
            num_dx_val = -(j22 * f1 - j12 * f2)
            num_dy_val = j21 * f1 - j11 * f2
            j22_f1 = j22 * f1
            j12_f2 = j12 * f2
            j21_f1 = j21 * f1
            j11_f2 = j11 * f2
            kx_plus_y = k * x + y
            if n > 1:
                latex_out.append("---")
            latex_out.extend([
                f"**Итерация {n}**",
                rf"**Шаг 1.** Текущее приближение: $x_{{{n-1}}} = {x:.6f}$, $y_{{{n-1}}} = {y:.6f}$",
                rf"**Шаг 2.** $u = kx + y - 4g = {k} \cdot {x:.6f} + {y:.6f} - 4 \cdot {g} = {kx_plus_y:.6f} - {4*g} = {u:.6f}$, $\cos(u) = {cu:.6f}$",
                rf"**Шаг 3.** Вектор невязки: $f_1 = {f1:.6f}$, $f_2 = {f2:.6f}$",
                rf"**Шаг 4.** Элементы Якоби: $j_{{11}} = k(1 + \cos(u)/10) = {j11:.6f}$, $j_{{12}} = \cos(u)/10 = {j12:.6f}$",
                rf"$j_{{21}} = -k\cos(u)/(10g) = {j21:.6f}$, $j_{{22}} = 1 - \cos(u)/(10g) = {j22:.6f}$",
                rf"**Шаг 5.** $J = \begin{{pmatrix}} {j11:.6f} & {j12:.6f} \\\\ {j21:.6f} & {j22:.6f} \end{{pmatrix}}$",
                rf"**Шаг 6.** $\det J = j_{{11}}j_{{22}} - j_{{12}}j_{{21}} = {j11:.6f} \cdot {j22:.6f} - {j12:.6f} \cdot {j21:.6f} = {j11_j22:.6f} - {j12_j21:.6f} = {det:.6f}$",
                rf"**Шаг 7.** Числитель $\Delta x$: $-(j_{{22}}f_1 - j_{{12}}f_2) = -({j22:.6f} \cdot {f1:.6f} - {j12:.6f} \cdot {f2:.6f}) = -({j22_f1:.6f} - {j12_f2:.6f}) = {num_dx_val:.6f}$",
                rf"$\Delta x = \frac{{{num_dx_val:.6f}}}{{{det:.6f}}} = {dx_val:.6f}$",
                rf"**Шаг 8.** Числитель $\Delta y$: $j_{{21}}f_1 - j_{{11}}f_2 = {j21:.6f} \cdot {f1:.6f} - {j11:.6f} \cdot {f2:.6f} = {j21_f1:.6f} - {j11_f2:.6f} = {num_dy_val:.6f}$",
                rf"$\Delta y = \frac{{{num_dy_val:.6f}}}{{{det:.6f}}} = {dy_val:.6f}$",
                rf"**Шаг 9.** $x_{{{n}}} = x_{{{n-1}}} + \Delta x = {x:.6f} + {dx_val:.6f} = {x_new:.6f}$",
                rf"$y_{{{n}}} = y_{{{n-1}}} + \Delta y = {y:.6f} + {dy_val:.6f} = {y_new:.6f}$",
                rf"**Шаг 10.** Проверка: $f_1(x_{{{n}}}, y_{{{n}}}) = {f6_1(x_new, y_new, k, g):.6f}$, $f_2(x_{{{n}}}, y_{{{n}}}) = {f6_2(x_new, y_new, k, g):.6f}$",
                rf"**Шаг 11.** $\max(|\Delta x|, |\Delta y|) = \max({abs(dx_val):.6f}, {abs(dy_val):.6f}) = {diff:.6f}$ {eps_mark}",
            ])
        rows.append((n, x_new, y_new, f6_1(x_new, y_new, k, g), f6_2(x_new, y_new, k, g), diff))
        x, y = x_new, y_new
        if diff < eps:  
            break
    return (x, y), rows, latex_out
def method_secant(f, f_prime2, a: float, b: float, eps: float, trace_latex: bool = False):
    fa, fb = f(a), f(b)  
    if fa * fb >= 0:  
        raise ValueError("f(a) и f(b) должны иметь разные знаки (корень на [a,b]).")  
    if fa * f_prime2(a) > 0:  
        c = a                 
    else:
        c = b                 
    fc = f(c)                 
    x = b if c == a else a # сначала выбираем неподвижный конец C по условию f(c) * f''(c) > 0 если у нас произведение функции на двойную производную больше нуля то с = a, иначе c = b. x0 (x) - это второй конец отрезка, то есть тот, который не равен c. если с = a => x0 = b, если c = b => x0 = a  
    latex_out = [] if trace_latex else None
    if trace_latex:
        fa_val, fb_val = f(a), f(b)
        f2a, f2b = f_prime2(a), f_prime2(b)
        prod_a = fa_val * f2a
        prod_b = fb_val * f2b
        latex_out.extend([
            r"**Лекция 1 темы «Нелинейные уравнения» (метод хорд/секущих).**",
            r"**Формула (19):** $x_1 = a - \frac{f(a)(b-a)}{f(b)-f(a)}$ (первое приближение)",
            r"**Формула (24):** $x_{n+1} = x_n - \frac{f(x_n)(x_n - c)}{f(x_n) - f(c)}$ (при $n \geq 1$)",
            r"**Выбор неподвижного конца $c$ по формуле (23):** $c$ — тот конец отрезка, для которого $f(c) \cdot f''(c) > 0$.",
            r"Имеем $a$ и $b$: $f(a)$ и $f(b)$ разных знаков (корень на $[a,b]$).",
            rf"**Точка $a = {a:.6f}$:** $f(a) = {fa_val:.6f}$, $f''(a) = {f2a:.6f}$ $\Rightarrow$ $f(a) \cdot f''(a) = {fa_val:.6f} \cdot {f2a:.6f} = {prod_a:.6f}$ {'$> 0$ ✓' if prod_a > 0 else '$< 0$'}",
            rf"**Точка $b = {b:.6f}$:** $f(b) = {fb_val:.6f}$, $f''(b) = {f2b:.6f}$ $\Rightarrow$ $f(b) \cdot f''(b) = {fb_val:.6f} \cdot {f2b:.6f} = {prod_b:.6f}$ {'$> 0$ ✓' if prod_b > 0 else '$< 0$'}",
            rf"Произведение $f \cdot f''$ больше нуля у точки {'$a$' if prod_a > 0 else '$b$'}, поэтому $c = {'a' if prod_a > 0 else 'b'} = {c:.6f}$ (неподвижный конец).",
            rf"Начальное приближение $x_0$ — второй конец (подвижный): $x_0 = {'b' if c == a else 'a'} = {x:.6f}$",
            rf"$f(c) = f({c:.6f}) = {fc:.6f}$, $f(x_0) = f({x:.6f}) = {f(x):.6f}$",
            "---",
        ])
    rows = []
    rows.append((0, x, f(x), None))
    denom_ab = fb - fa
    for n in range(1, MAX_ITER + 1):
        if n == 1:
            num_val = fa * (b - a)
            denom = denom_ab
            if abs(denom) < 1e-15:
                break
            x_new = a - num_val / denom
        else:
            fx = f(x)
            denom = fx - fc
            if abs(denom) < 1e-15:
                break
            num_val = fx * (x - c)
            x_new = x - num_val / denom
        diff = abs(x_new - x)
        if trace_latex:
            eps_mark = r"$< \varepsilon$ ✓" if diff < eps else ""
            if n > 1:
                latex_out.append("---")
            if n == 1:
                quot = num_val / denom
                latex_out.extend([
                    f"**Итерация {n}**",
                    r"**Формула (19):** $x_1 = a - \frac{f(a)(b-a)}{f(b)-f(a)}$",
                    rf"**Шаг 1.** Числитель: $f(a)(b-a) = {fa:.6f} \cdot ({b:.6f} - {a:.6f}) = {fa:.6f} \cdot {b-a:.6f} = {num_val:.6f}$",
                    rf"**Шаг 2.** Знаменатель: $f(b) - f(a) = {fb:.6f} - ({fa:.6f}) = {denom:.6f}$",
                    rf"**Шаг 3.** Дробь: $\frac{{{num_val:.6f}}}{{{denom:.6f}}} = {quot:.6f}$",
                    rf"**Шаг 4.** $x_1 = a - \frac{{f(a)(b-a)}}{{f(b)-f(a)}} = {a:.6f} - {quot:.6f} = {x_new:.6f}$",
                    rf"**Шаг 5.** Проверка: $f(x_1) = f({x_new:.6f}) = {f(x_new):.6f}$",
                    rf"**Шаг 6.** Критерий окончания: $|\Delta x| = |x_1 - x_0| = {diff:.6f}$ {eps_mark}",
                ])
            else:
                fx = f(x)
                quot = num_val / denom
                x_minus_c = x - c
                latex_out.extend([
                    f"**Итерация {n}**",
                    rf"**Шаг 1.** Текущее приближение: $x_{{{n-1}}} = {x:.6f}$",
                    rf"**Шаг 2.** Значение функции: $f(x_{{{n-1}}}) = f({x:.6f}) = {fx:.6f}$",
                    rf"**Шаг 3.** Числитель: $f(x_{{{n-1}}})(x_{{{n-1}}} - c) = {fx:.6f} \cdot ({x:.6f} - {c:.6f}) = {fx:.6f} \cdot {x_minus_c:.6f} = {num_val:.6f}$",
                    rf"**Шаг 4.** Знаменатель: $f(x_{{{n-1}}}) - f(c) = {fx:.6f} - {fc:.6f} = {denom:.6f}$",
                    rf"**Шаг 5.** Дробь: $\frac{{{num_val:.6f}}}{{{denom:.6f}}} = {quot:.6f}$",
                    rf"**Шаг 6.** Новое приближение: $x_{{{n}}} = x_{{{n-1}}} - \frac{{f(x)(x-c)}}{{f(x)-f(c)}} = {x:.6f} - {quot:.6f} = {x_new:.6f}$",
                    rf"**Шаг 7.** Проверка: $f(x_{{{n}}}) = f({x_new:.6f}) = {f(x_new):.6f}$",
                    rf"**Шаг 8.** Критерий окончания (25): $|\Delta x| = |x_{{{n}}} - x_{{{n-1}}}| = {diff:.6f}$ {eps_mark}",
                ])
        rows.append((n, x_new, f(x_new), diff))
        x = x_new
        if diff < eps:
            break
    return (x, rows, latex_out) if trace_latex else (x, rows)


def method_newton(f, f_prime, f_prime2, a: float, b: float, eps: float, trace_latex: bool = False):
    fa, fb = f(a), f(b)                               
    if fa * fb >= 0:                                   
        raise ValueError("f(a) и f(b) должны иметь разные знаки.")  
    if fa * f_prime2(a) > 0:                           
        x = a                                          
    else:
        x = b                                          
    latex_out = [] if trace_latex else None
    if trace_latex:
        def add(*lines):
            latex_out.extend(lines)
        fa_val, fb_val = f(a), f(b)
        f2a, f2b = f_prime2(a), f_prime2(b)
        prod_a = fa_val * f2a
        prod_b = fb_val * f2b
        add(
            r"**Лекция 2 темы «Нелинейные уравнения» (метод Ньютона/касательных).**",
            r"**Формула (26):** $x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$",
            r"**Выбор $x_0$ по формуле (27):** $x_0$ — тот конец $[a,b]$, для которого $f(x_0) \cdot f''(x_0) > 0$.",
            r"Имеем $a$ и $b$: $f(a)$ и $f(b)$ разных знаков (корень между ними).",
            rf"**Точка $a = {a:.6f}$:** $f(a) = {fa_val:.6f}$, $f''(a) = {f2a:.6f}$ $\Rightarrow$ $f(a) \cdot f''(a) = {fa_val:.6f} \cdot {f2a:.6f} = {prod_a:.6f}$ {'$> 0$ ✓' if prod_a > 0 else '$< 0$'}",
            rf"**Точка $b = {b:.6f}$:** $f(b) = {fb_val:.6f}$, $f''(b) = {f2b:.6f}$ $\Rightarrow$ $f(b) \cdot f''(b) = {fb_val:.6f} \cdot {f2b:.6f} = {prod_b:.6f}$ {'$> 0$ ✓' if prod_b > 0 else '$< 0$'}",
            rf"Произведение $f \cdot f''$ больше нуля у точки {'$a$' if prod_a > 0 else '$b$'}, поэтому $x_0 = {'a' if prod_a > 0 else 'b'} = {x:.6f}$",
            rf"$f(x_0) = {f(x):.6f}$, $f'(x_0) = {f_prime(x):.6f}$",
            "---",
        )
    rows = []
    rows.append((0, x, f(x), None))
    for n in range(1, MAX_ITER + 1):
        fx = f(x)
        dfx = f_prime(x)
        if abs(dfx) < 1e-15:
            raise ValueError("f'(x) ≈ 0, метод неприменим.")
        fx_div_dfx = fx / dfx
        x_new = x - fx_div_dfx
        diff = abs(x_new - x)
        if trace_latex:
            eps_mark = r"$< \varepsilon$ ✓" if diff < eps else ""
            if n > 1:
                add("---")
            add(
                f"**Итерация {n}**",
                rf"**Шаг 1.** $x_{{{n-1}}} = {x:.6f}$",
                rf"**Шаг 2.** $f(x_{{{n-1}}}) = f({x:.6f}) = {fx:.6f}$",
                rf"**Шаг 3.** $f'(x_{{{n-1}}}) = f'({x:.6f}) = {dfx:.6f}$",
                rf"**Шаг 4.** $\frac{{f(x_{{{n-1}}})}}{{f'(x_{{{n-1}}})}} = \frac{{{fx:.6f}}}{{{dfx:.6f}}} = {fx_div_dfx:.6f}$",
                rf"**Шаг 5.** $x_{{{n}}} = x_{{{n-1}}} - \frac{{f(x_{{{n-1}}})}}{{f'(x_{{{n-1}}})}} = {x:.6f} - {fx_div_dfx:.6f} = {x_new:.6f}$",
                rf"**Шаг 6.** Проверка: $f(x_{{{n}}}) = f({x_new:.6f}) = {f(x_new):.6f}$",
                rf"**Шаг 7.** $|\Delta x| = |{x_new:.6f} - {x:.6f}| = {diff:.6f}$ {eps_mark}",
            )
        rows.append((n, x_new, f(x_new), diff))
        x = x_new
        if diff < eps:
            break
    return (x, rows, latex_out) if trace_latex else (x, rows)


def method_iteration(f, f_prime, a: float, b: float, eps: float, trace_latex: bool = False, trace_k: float | None = None, trace_g: int | None = None):
    """
    trace_k, trace_g — для подробной трассировки задания 3: f(x) = kx - 10g - sin(x - 10g/k)
    """
    n_points = 500
    max_fp = 0.0 # максимум на f'(x) на отрезке [a, b]
    for i in range(n_points + 1):
        t = a + (b - a) * i / n_points
        max_fp = max(max_fp, abs(f_prime(t)))
    if max_fp < 1e-15:
        raise ValueError("f'(x) ≈ 0 на отрезке, метод неприменим.")
    C = 1.0 / max_fp # тут мы находим C (по условию сходимости)
    x = (a + b) / 2.0
    latex_out = [] if trace_latex else None
    use_full_formula = trace_latex and trace_k is not None and trace_g is not None
    if trace_latex:
        def add(*lines):
            latex_out.extend(lines)
        if use_full_formula:
            arg_10gk = 10 * trace_g / trace_k
            add(
                r"**Лекция 3 (метод итераций).** Формула (28): $x_{n+1} = \varphi(x_n)$, $\varphi(x) = x - C \cdot f(x)$.",
                rf"**Функция задания 3:** $f(x) = kx - 10g - \sin\left(x - \frac{{10g}}{{k}}\right)$",
                rf"При $k = {trace_k}$, $g = {trace_g}$:",
                rf"$f(x) = {trace_k} \cdot x - {10*trace_g} - \sin\left(x - \frac{{10 \cdot {trace_g}}}{{{trace_k}}}\right) = {trace_k}x - {10*trace_g} - \sin(x - {arg_10gk:.6f})$",
                rf"Производная: $f'(x) = k - \cos\left(x - \frac{{10g}}{{k}}\right) = {trace_k} - \cos(x - {arg_10gk:.6f})$",
                r"**Метод простых итераций:** $\varphi(x) = x - C \cdot f(x)$, $x_{n+1} = \varphi(x_n)$",
                r"**Условие сходимости:** $C = \frac{1}{\max_{x \in [a,b]}|f'(x)|}$",
                rf"На отрезке $[a, b] = [{a:.6f}, {b:.6f}]$ найдено $\max|f'(x)| = {max_fp:.6f}$",
                rf"$C = \frac{{1}}{{{max_fp:.6f}}} = {C:.6f}$",
                rf"**Начальное приближение:** $x_0 = \frac{{a+b}}{{2}} = \frac{{{a:.6f} + {b:.6f}}}{{2}} = \frac{{{a+b:.6f}}}{{2}} = {x:.6f}$",
                "---",
            )
        else:
            add(
                r"**Лекция 3 темы «Нелинейные уравнения» (метод итераций).**",
                r"**Формула (28):** $x_{n+1} = \varphi(x_n)$, где $\varphi(x) = x - C \cdot f(x)$.",
                r"**Условие сходимости:** $C = \frac{1}{\max_{[a,b]}|f'(x)|}$ (лекция 3).",
                rf"$C = {C:.6f}$, $x_0 = \frac{{a+b}}{{2}} = {x:.6f}$",
                "---",
            )
    rows = []
    rows.append((0, x, f(x), None))
    for n in range(1, MAX_ITER + 1):
        fx = f(x) # тут мы фи находим (следующие три строки)
        C_fx = C * fx
        x_new = x - C_fx # это и есть фи от х (результат применения фи к текущему приближению)
        diff = abs(x_new - x)
        if trace_latex:
            eps_mark = r"$< \varepsilon$ ✓" if diff < eps else ""
            if n > 1:
                add("---")
            if use_full_formula:
                arg_sin = x - 10 * trace_g / trace_k
                sin_val = math.sin(arg_sin)
                kx = trace_k * x
                kx_minus_10g = kx - 10 * trace_g
                add(
                    f"**Итерация {n}**",
                    rf"**Шаг 1.** Текущее приближение: $x_{{{n-1}}} = {x:.6f}$",
                    rf"**Шаг 2.** Аргумент синуса: $x_{{{n-1}}} - \frac{{10g}}{{k}} = {x:.6f} - \frac{{10 \cdot {trace_g}}}{{{trace_k}}} = {x:.6f} - {10*trace_g/trace_k:.6f} = {arg_sin:.6f}$",
                    rf"**Шаг 3.** $\sin\left(x_{{{n-1}}} - \frac{{10g}}{{k}}\right) = \sin({arg_sin:.6f}) = {sin_val:.6f}$",
                    rf"**Шаг 4.** $k \cdot x_{{{n-1}}} = {trace_k} \cdot {x:.6f} = {kx:.6f}$",
                    rf"**Шаг 5.** $k \cdot x_{{{n-1}}} - 10g = {kx:.6f} - {10*trace_g} = {kx_minus_10g:.6f}$",
                    rf"**Шаг 6.** $f(x_{{{n-1}}}) = (kx - 10g) - \sin(x - 10g/k) = {kx_minus_10g:.6f} - {sin_val:.6f} = {fx:.6f}$",
                    rf"**Шаг 7.** $C \cdot f(x_{{{n-1}}}) = {C:.6f} \cdot {fx:.6f} = {C_fx:.6f}$",
                    rf"**Шаг 8.** $x_{{{n}}} = x_{{{n-1}}} - C \cdot f(x_{{{n-1}}}) = {x:.6f} - {C_fx:.6f} = {x_new:.6f}$",
                    rf"**Шаг 9.** Проверка: $f(x_{{{n}}}) = f({x_new:.6f}) = {f(x_new):.6f}$",
                    rf"**Шаг 10.** $|\Delta x| = |x_{{{n}}} - x_{{{n-1}}}| = |{x_new:.6f} - {x:.6f}| = {diff:.6f}$ {eps_mark}",
                )
            else:
                add(
                    f"**Итерация {n}**",
                    rf"$x_{{{n-1}}} = {x:.6f}$, $f(x_{{{n-1}}}) = {fx:.6f}$",
                    rf"$C \cdot f(x_{{{n-1}}}) = {C:.6f} \cdot {fx:.6f} = {C_fx:.6f}$",
                    rf"$x_{{{n}}} = x_{{{n-1}}} - C \cdot f(x_{{{n-1}}}) = {x:.6f} - {C_fx:.6f} = {x_new:.6f}$",
                    rf"$|\Delta x| = {diff:.6f}$ {eps_mark}",
                )
        rows.append((n, x_new, f(x_new), diff))
        x = x_new
        if diff < eps:
            break
    return (x, rows, latex_out) if trace_latex else (x, rows)