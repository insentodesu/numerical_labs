"""
Портал лабораторных для домена labs.inst.rest.

Лабораторные №1–№3 — отдельные процессы Streamlit (у каждой свой set_page_config).
Здесь только выбор ссылки; адреса задаются переменными окружения LAB1_URL, LAB2_URL и LAB3_URL.

Локально из корня репозитория numerical_labs:
  ./portal/run_local.sh
  (или четыре процесса: lab1 :8501, lab2 :8502, lab3 :8503, portal :8500)

Продакшен (схема): Nginx на 443, location / → этот app; /lab1/, /lab2/, /lab3/ — proxy_pass на
три внутренних порта. У каждого дочернего Streamlit в .streamlit/config.toml:
  [server]
  baseUrlPath = "lab1"
  enableCORS = false
  enableXsrfProtection = true
(для lab2 — baseUrlPath = "lab2", для lab3 — baseUrlPath = "lab3"). Тогда:
  LAB1_URL=https://labs.inst.rest/lab1/
  LAB2_URL=https://labs.inst.rest/lab2/
  LAB3_URL=https://labs.inst.rest/lab3/
"""
from __future__ import annotations

import os

import streamlit as st

# Продакшен: задайте в окружении хоста или в Streamlit Cloud secrets.
def _with_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else url + "/"


LAB1_URL = _with_trailing_slash(os.environ.get("LAB1_URL", "http://127.0.0.1:8501"))
LAB2_URL = _with_trailing_slash(os.environ.get("LAB2_URL", "http://127.0.0.1:8502"))
LAB3_URL = _with_trailing_slash(os.environ.get("LAB3_URL", "http://127.0.0.1:8503"))

st.set_page_config(
    page_title="Лабораторные · численные методы",
    page_icon="📐",
    layout="centered",
)

st.title("Лабораторные работы")
st.caption("Численные методы — выберите работу (откроется в той же вкладке).")

st.markdown(
    """
<style>
div[data-testid="stLinkButton"] a {
    display: block;
    text-align: center;
    padding: 0.85rem 1rem;
    font-weight: 600;
    border-radius: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Лабораторная №1")
    st.caption("Нелинейные уравнения и системы")
    st.link_button("Открыть лабораторную №1", LAB1_URL, use_container_width=True)
with c2:
    st.subheader("Лабораторная №2")
    st.caption("Гаусс, простая итерация, Зейдель")
    st.link_button("Открыть лабораторную №2", LAB2_URL, use_container_width=True)
with c3:
    st.subheader("Лабораторная №3")
    st.caption("Интерполяция и линейный сплайн")
    st.link_button("Открыть лабораторную №3", LAB3_URL, use_container_width=True)

with st.expander("Куда ведут кнопки (отладка)"):
    st.code(f"LAB1_URL = {LAB1_URL}\nLAB2_URL = {LAB2_URL}\nLAB3_URL = {LAB3_URL}", language="text")

st.divider()
st.markdown(
    "Если ссылка не открывается, убедитесь, что соответствующий Streamlit уже запущен "
    "на сервере, и что в DNS для **labs.inst.rest** указан ваш хост."
)
