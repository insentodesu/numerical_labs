import argparse
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from requests import Response, Session


BASE_URL = "https://openedu.kubsu.ru"


def parse_cookie_string(cookie_string: str) -> Dict[str, str]:
    """
    Parse a raw Cookie header string into a dict suitable for requests.

    Example:
      "MoodleSession=abc; other=xyz" -> {"MoodleSession": "abc", "other": "xyz"}
    """
    cookies: Dict[str, str] = {}
    if not cookie_string:
        return cookies

    parts = cookie_string.split(";")
    for part in parts:
        if not part.strip():
            continue
        if "=" not in part:
            # Skip malformed pieces
            continue
        name, value = part.split("=", 1)
        cookies[name.strip()] = value.strip()
    return cookies


def build_session(cookie_string: str) -> Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) "
                "Gecko/20100101 Firefox/117.0"
            )
        }
    )

    cookies = parse_cookie_string(cookie_string)
    for name, value in cookies.items():
        session.cookies.set(name, value, domain="openedu.kubsu.ru")

    return session


def fetch(session: Session, url: str) -> Optional[Response]:
    try:
        resp = session.get(url, allow_redirects=True, timeout=20)
    except requests.RequestException as exc:
        print(f"[!] Ошибка сети при запросе {url}: {exc}", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(
            f"[!] Неверный код ответа {resp.status_code} для {url} "
            f"(возможно, устаревший cookie или нет доступа)",
            file=sys.stderr,
        )
        return None

    return resp


def make_absolute_url(href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    # Обрабатываем относительные ссылки
    if href.startswith("/"):
        return BASE_URL + href
    return f"{BASE_URL}/{href.lstrip('/')}"


def _section_title_text(section_root) -> str:
    for sel in ("h3.sectionname", ".sectionname", "h2.sectionname"):
        el = section_root.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return ""


def _iter_course_section_roots(soup: BeautifulSoup):
    """Узлы разделов курса в типичной вёрстке Moodle (Boost / совместимые темы)."""
    roots = soup.select('li.section[id^="section-"]')
    if roots:
        return roots
    roots = soup.select("li.section.course-section")
    if roots:
        return roots
    return soup.select("li.section")


def extract_lecture_links(
    course_html: str,
    section_contains: Optional[str] = None,
) -> List[Tuple[str, str]]:
    """
    Возвращает список (url, текст ссылки) для лекций вида /mod/page/view.php.
    Порядок соответствует порядку на странице курса.

    Если задан section_contains (подстрока без учёта регистра), берутся только
    страницы из раздела, в названии которого эта подстрока встречается.
    """
    soup = BeautifulSoup(course_html, "html.parser")
    links: List[Tuple[str, str]] = []
    seen: set[str] = set()

    search_roots = None
    if section_contains:
        needle = section_contains.strip().lower()
        if needle:
            matched = []
            for root in _iter_course_section_roots(soup):
                title = _section_title_text(root)
                if needle in title.lower():
                    matched.append(root)
            if not matched:
                print(
                    f"[!] Раздел с подстрокой «{section_contains}» в заголовке не найден. "
                    "Проверьте название темы на странице курса.",
                    file=sys.stderr,
                )
                return []
            search_roots = matched

    if search_roots is None:
        iterators = [soup]
    else:
        iterators = search_roots

    for container in iterators:
        for a in container.find_all("a", href=True):
            href = a["href"]
            if "/mod/page/view.php" not in href:
                continue
            full_url = make_absolute_url(href)
            if full_url in seen:
                continue
            seen.add(full_url)
            text = a.get_text(strip=True) or ""
            links.append((full_url, text))

    return links


def extract_lecture_title(
    soup: BeautifulSoup,
    fallback_title: str,
    index: int,
) -> str:
    # 1) Заголовок в шапке Moodle
    header_h1 = soup.select_one(".page-header-headings h1")
    if header_h1 and header_h1.get_text(strip=True):
        return header_h1.get_text(strip=True)

    # 2) Любой h1
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    # 3) h2
    h2 = soup.find("h2")
    if h2 and h2.get_text(strip=True):
        return h2.get_text(strip=True)

    # 4) <title>
    if soup.title and soup.title.string and soup.title.string.strip():
        return soup.title.string.strip()

    # 5) Текст ссылки с курса
    if fallback_title.strip():
        return fallback_title.strip()

    # 6) Фолбек по номеру
    return f"lecture_{index}"


def extract_lecture_text(soup: BeautifulSoup) -> str:
    # Основной контент Moodle обычно в #region-main
    container = soup.select_one("div#region-main")
    if not container:
        container = soup.find("div", attrs={"role": "main"})

    if not container:
        # Ищем блок с признаком mod_page
        container = soup.find("div", class_=re.compile(r"mod_page"))

    if container is None:
        # Фолбек: весь body
        if soup.body is not None:
            container = soup.body
        else:
            container = soup

    text = container.get_text("\n", strip=True)
    return text


def slugify_title(title: str, max_length: int = 80) -> str:
    # Убираем опасные символы для файловой системы
    cleaned = re.sub(r'[\\/:*?"<>|]', " ", title)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        cleaned = "lecture"
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
    return cleaned


def save_lecture_text(
    base_dir: str,
    index: int,
    total: int,
    title: str,
    text: str,
    url: str,
) -> str:
    os.makedirs(base_dir, exist_ok=True)

    width = len(str(total)) if total > 0 else 2
    prefix = f"{index:0{width}d}"

    safe_title = slugify_title(title)
    filename = f"{prefix}_{safe_title}.txt"
    path = os.path.join(base_dir, filename)

    header_lines = [
        title,
        "=" * max(len(title), 3),
        f"URL: {url}",
        "",
    ]
    content = "\n".join(header_lines) + text + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Выгрузка всех лекций (mod/page) из курса ОСМДО "
            "в текстовые файлы."
        )
    )
    parser.add_argument(
        "--course-url",
        "-u",
        required=True,
        help="URL страницы курса, например https://openedu.kubsu.ru/course/view.php?id=XXXXX",
    )
    parser.add_argument(
        "--cookie",
        "-c",
        required=True,
        help=(
            "Строка Cookie (как из заголовка браузера), "
            'например: "MoodleSession=...; other=...".'
        ),
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="lectures",
        help="Каталог для сохранения лекций (по умолчанию: lectures).",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Пауза в секундах между запросами к лекциям (по умолчанию: 1.0).",
    )
    parser.add_argument(
        "--section-contains",
        "-s",
        default=None,
        help=(
            "Подстрока в заголовке раздела курса (например: «Задачи вычислительной алгебры» "
            "или «Тема 2»). Если задано, выгружаются только mod/page из этого раздела."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    print("[*] Создаём HTTP-сессию...")
    session = build_session(args.cookie)

    print(f"[*] Загружаем страницу курса: {args.course_url}")
    resp = fetch(session, args.course_url)
    if resp is None:
        print("[!] Не удалось загрузить страницу курса.", file=sys.stderr)
        return 1

    course_html = resp.text
    lecture_links = extract_lecture_links(
        course_html, section_contains=args.section_contains
    )

    if not lecture_links:
        print(
            "[!] Лекции формата /mod/page/view.php не найдены на странице курса.",
            file=sys.stderr,
        )
        return 1

    total = len(lecture_links)
    print(f"[*] Найдено лекций (mod/page): {total}")

    success_count = 0
    fail_count = 0

    for idx, (url, link_text) in enumerate(lecture_links, start=1):
        print(f"[*] [{idx}/{total}] Загружаем лекцию: {url}")

        resp_lecture = fetch(session, url)
        if resp_lecture is None:
            print(f"[!] Пропускаем лекцию {url}", file=sys.stderr)
            fail_count += 1
            continue

        soup = BeautifulSoup(resp_lecture.text, "html.parser")
        title = extract_lecture_title(soup, link_text, idx)
        text = extract_lecture_text(soup)

        if not text.strip():
            print(
                f"[!] Пустой текст лекции, пропускаем сохранение: {url}",
                file=sys.stderr,
            )
            fail_count += 1
            continue

        try:
            saved_path = save_lecture_text(
                base_dir=args.output_dir,
                index=idx,
                total=total,
                title=title,
                text=text,
                url=url,
            )
        except OSError as exc:
            print(
                f"[!] Ошибка записи файла для лекции {url}: {exc}",
                file=sys.stderr,
            )
            fail_count += 1
            continue

        print(f"    -> Сохранено в: {saved_path}")
        success_count += 1

        if args.delay > 0 and idx != total:
            time.sleep(args.delay)

    print()
    print("[*] Готово.")
    print(f"    Успешно сохранено лекций: {success_count}")
    print(f"    Ошибок при обработке:     {fail_count}")

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

