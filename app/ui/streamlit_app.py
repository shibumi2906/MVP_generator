import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

from app.core.timeouts import UI_REQUEST_TIMEOUT_SECONDS
from app.ui.components import (
    render_api_spec,
    render_architecture,
    render_assumptions,
    render_erd,
    render_prd,
    render_tasks,
)
from app.ui.help import fill_example, open_help, render_help
from app.ui.i18n import error_message, persist_language, tr

load_dotenv()
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
st.set_page_config(page_title="MVP Generator · Product workspace", page_icon="◈", layout="wide")
st.markdown(
    """
<style>
    .stApp { background: #f5f6fa; color: #19243b; }
    .block-container { max-width: 1280px; padding-top: 2.5rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #e9edf5; }
    h1, h2, h3 { letter-spacing: -.035em; }
    h1 { font-size: clamp(1.8rem, 4vw, 3rem) !important; line-height: 1.12 !important; }
    .st-key-brief_form { background: white; border: 1px solid #dce2ee; border-radius: 16px; padding: 1.5rem; }
    [data-testid="stMetric"] { background: white; border: 1px solid #dce2ee; border-radius: 12px; padding: 1rem; }
    .eyebrow { color: #5b5bd6; letter-spacing: .14em; font-size: .75rem; font-weight: 700; }
    .intro { color: #58657d; font-size: 1.1rem; max-width: 680px; margin-bottom: 2rem; }
    .stButton button[kind="primary"], .stFormSubmitButton button { border-radius: 10px; }
</style>
""",
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs: Any) -> requests.Response | None:
    try:
        response = requests.request(
            method, f"{API_BASE}{path}", timeout=UI_REQUEST_TIMEOUT_SECONDS, **kwargs
        )
        if 200 <= response.status_code < 300:
            return response
        try:
            detail = response.json().get("detail", {})
        except ValueError:
            detail = {}
        if isinstance(detail, dict):
            st.error(error_message(detail.get("code", ""), response.status_code))
            if detail.get("code"):
                st.caption(
                    tr(
                        "{code} · Режим: {mode} · Новый результат не создан",
                        code=detail["code"],
                        mode=detail.get("mode", "unknown"),
                    )
                )
            if detail.get("issues"):
                with st.expander(tr("Детали проверки документов")):
                    for issue in detail["issues"]:
                        st.write(issue)
        else:
            st.error(error_message("", response.status_code))
    except requests.RequestException:
        st.error(
            tr(
                "Сервер недоступен или истекло время ожидания. Проверьте историю перед повторным запуском."
            )
        )
    return None


def show_provenance(data: dict) -> None:
    provenance = data.get("provenance", {})
    status = provenance.get("status", "unverified")
    if status == "demo":
        st.info(tr("Демо · Общий пример документов. Он не адаптирован к вашей идее."))
    elif status == "generated":
        st.success(tr("Создано с OpenAI · Структура и ссылки между документами проверены."))
    else:
        st.warning(
            tr(
                "Происхождение неизвестно · Это старый результат, согласованность документов не проверена."
            )
        )
    st.caption(
        tr(
            "Источник: {source} · Модель: {model} · Сохранено: {created}",
            source=provenance.get("source", "unknown"),
            model=provenance.get("model") or "—",
            created=data.get("created_at", ""),
        )
    )


with st.sidebar:
    st.markdown("## ◈ MVP Generator")
    if "language" not in st.session_state:
        requested_language = st.query_params.get("lang", "ru")
        st.session_state["language"] = (
            requested_language if requested_language in {"ru", "en"} else "ru"
        )
    st.selectbox(
        "Язык / Language",
        ["ru", "en"],
        key="language",
        format_func=lambda value: {"ru": "Русский", "en": "English"}[value],
        on_change=persist_language,
    )
    st.caption(tr("ОТ ИДЕИ К ПЛАНУ РАЗРАБОТКИ"))
    st.button(tr("Как пользоваться"), on_click=open_help, use_container_width=True)
    st.divider()
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=3)
        health_response.raise_for_status()
        health = health_response.json()
        mode = health.get("llm_mode", "unknown")
        st.markdown(
            "**" + tr("Режим: {mode}", mode=tr("Демо") if mode == "mock" else mode.upper()) + "**"
        )
        budget = health.get("token_budget")
        if budget:
            st.caption(
                tr(
                    "Токены за день (расход + резерв): {used:,} / {limit:,}. Сброс в 00:00 по Израилю.",
                    used=budget["used_or_reserved"],
                    limit=budget["limit"],
                )
            )
        if mode == "mock":
            st.info(tr("Деморежим: один общий пример для любой идеи, без вызова OpenAI."))
        elif not health.get("generation_ready"):
            st.warning(tr("Генерация не настроена. Проверьте ключ и настройки сервера."))
        else:
            st.caption(tr("Генерация через OpenAI. Каждый запуск расходует токены."))
    except (requests.RequestException, ValueError):
        st.warning(tr("Сервер недоступен. Нужно запустить API вместе с интерфейсом."))
    st.divider()
    st.markdown("### " + tr("Сохранённые планы"))
    if st.button(tr("Обновить список"), use_container_width=True):
        st.session_state.pop("history", None)
    if "history" not in st.session_state:
        history_response = api_request("GET", "/history?limit=8")
        st.session_state["history"] = (
            history_response.json() if history_response is not None else []
        )
    for item in st.session_state["history"]:
        status_label = {"generated": "OpenAI", "demo": tr("Демо")}.get(
            item.get("provenance", {}).get("status"), tr("Происхождение неизвестно")
        )
        label = f"{status_label} · {item['title']}"
        if st.button(label, key=item["generation_id"], use_container_width=True):
            detail_response = api_request("GET", f"/history/{item['generation_id']}")
            if detail_response is not None:
                st.session_state["last_generation"] = detail_response.json()
                st.session_state.pop("zip_bytes", None)
    if not st.session_state["history"]:
        st.caption(tr("После первой успешной генерации здесь появится ваш план."))
    st.divider()
    st.caption("FastAPI / SQLite / Streamlit")

st.markdown('<div class="eyebrow">MVP GENERATOR</div>', unsafe_allow_html=True)
st.title(tr("Превратите идею в план разработки"))
st.markdown(
    tr(
        '<p class="intro">Опишите, что хотите создать. Вы получите черновик требований, архитектуру и задачи для первой версии. Само приложение нужно будет разработать по этому плану.</p>'
    ),
    unsafe_allow_html=True,
)
st.markdown(
    tr("**1. Опишите идею** → **2. Создайте план** → **3. Проверьте и скачайте документы**")
)
render_help()

# A single form column stays usable inside Codex's narrow browser panel.
left, right = st.container(), st.container()
with left:
    with st.container(border=True, key="brief_form"):
        st.subheader(tr("01 / Опишите будущий продукт"))
        product_idea = st.text_area(
            tr("Идея продукта *"),
            placeholder=tr(
                "Сервис для репетитора: хранить учеников, назначать занятия и видеть расписание на неделю…"
            ),
            help=tr(
                "Обязательное поле, минимум 10 символов. Кто пользователь, какая у него проблема и что он сможет сделать?"
            ),
            key="product_idea",
            height=125,
        )
        target_users = st.text_input(
            tr("Для кого"),
            placeholder=tr("Например, частные репетиторы"),
            help=tr("Необязательно. Укажите конкретную аудиторию и её особенности."),
            key="target_users",
        )
        with st.expander(tr("Дополнительно: сценарий, ограничения и технологии")):
            core_user_flow = st.text_area(
                tr("Сценарий работы"),
                placeholder=tr("Добавить ученика → назначить занятие → открыть расписание"),
                help=tr("Необязательно. Несколько действий пользователя по порядку."),
                key="core_user_flow",
            )
            constraints = st.text_area(
                tr("Ограничения"),
                placeholder=tr("Один разработчик, неделя, без платежей и уведомлений"),
                help=tr(
                    "Необязательно. Срок, ресурсы и функции, которые не нужны в первой версии."
                ),
                key="constraints",
            )
            output_stack = st.text_input(
                tr("Технологии"),
                value="FastAPI + SQLite + Streamlit",
                help=tr(
                    "Набор инструментов для разработки. Если не знаете, оставьте предложенный вариант."
                ),
                key="output_stack",
            )
        submitted = st.button(
            tr("Создать план разработки →"),
            key="generate",
            type="primary",
            use_container_width=True,
        )
with right:
    st.subheader(tr("Первый раз здесь?"))
    st.write(tr("Начните с примера: посмотрите, как описать идею, затем замените текст своим."))
    st.button(
        tr("Заполнить пример"),
        on_click=fill_example,
        use_container_width=True,
        help=tr(
            "Заменит текст во всех полях. Генерация начнётся только по кнопке «Создать план разработки»."
        ),
    )
    st.caption(tr("Обязательно только поле со звёздочкой. Можно писать по-русски."))
    st.markdown(
        tr(
            "**Что вы получите**  \nТребования, архитектуру, данные, API, план работ и список допущений."
        )
    )
    st.markdown(
        tr(
            "**Что делать с результатом**  \nПроверьте требования и допущения, скачайте ZIP с документами и передайте разработчику или используйте для своей работы."
        )
    )
    st.markdown(
        tr(
            "**Уже создавали план?**  \nОткройте его в разделе «Сохранённые планы» слева — это не расходует токены."
        )
    )
    st.caption(
        tr(
            "В режиме OpenAI описание отправляется модели. Не указывайте пароли, API-ключи и реальные данные клиентов."
        )
    )

if submitted:
    # Clear the previous result so a failed request cannot look like a fresh success.
    st.session_state.pop("last_generation", None)
    st.session_state.pop("zip_bytes", None)
    if len(product_idea.strip()) < 10:
        st.error(
            tr("Опишите продукт подробнее: минимум 10 символов после удаления пробелов по краям.")
        )
    else:
        st.caption(
            tr(
                "Подготовка полного плана может занять до трёх минут. Не запускайте повторно, пока идёт генерация."
            )
        )
        with st.spinner(
            tr("Создаём план и проверяем документы. Дождитесь результата…"), show_time=True
        ):
            response = api_request(
                "POST",
                "/generate",
                json={
                    "product_idea": product_idea,
                    "target_users": target_users or None,
                    "core_user_flow": core_user_flow or None,
                    "constraints": constraints or None,
                    "output_stack": output_stack or None,
                },
            )
        if response is not None:
            st.session_state["last_generation"] = response.json()
            st.session_state.pop("history", None)
            st.rerun()

last = st.session_state.get("last_generation")
if last:
    st.divider()
    st.subheader(tr("02 / Ваш план разработки"))
    st.caption(
        tr(
            "Начните с вкладок «Требования» и «Допущения». Затем изучите план работ и скачайте документы ниже."
        )
    )
    show_provenance(last)
    result = last["result"]
    st.markdown(f"### {result['title']}")
    st.write(result["summary"])
    contract = result.get("contract") or {}
    metrics = st.columns(3)
    metrics[0].metric(tr("Сущности данных"), len(contract.get("entities", [])))
    metrics[1].metric(tr("Запросы API"), len(contract.get("endpoints", [])))
    metrics[2].metric(
        tr("Задачи разработки"),
        len([t for t in contract.get("tasks", []) if t["phase"] != "done_checklist"]),
    )
    tabs = st.tabs(
        [
            tr("Требования"),
            tr("Архитектура"),
            tr("Данные"),
            "API",
            tr("План работ"),
            tr("Допущения"),
        ]
    )
    for tab, renderer in zip(
        tabs,
        [
            render_prd,
            render_architecture,
            render_erd,
            render_api_spec,
            render_tasks,
            render_assumptions,
        ],
        strict=True,
    ):
        with tab:
            renderer(result)
    st.divider()
    export_col, info_col = st.columns([1, 2])
    with export_col:
        if st.button(tr("Подготовить ZIP"), key="prepare_zip", use_container_width=True):
            exported = api_request("POST", "/export", json={"generation_id": last["generation_id"]})
            if exported is not None:
                st.session_state["zip_bytes"] = exported.content
        if st.session_state.get("zip_bytes"):
            st.download_button(
                tr("Скачать документы ↓"),
                data=st.session_state["zip_bytes"],
                file_name=f"mvp_bundle_{last['generation_id']}.zip",
                mime="application/zip",
                use_container_width=True,
            )
    with info_col:
        st.caption(
            tr(
                "ZIP с документами Markdown, исходниками схем Mermaid и данными JSON. Скачайте и передайте разработчику."
            )
        )
        st.caption(tr("Идентификатор: {id}", id=last["generation_id"]))
else:
    st.divider()
    st.caption(
        tr(
            "План появится здесь после генерации. Заполните идею выше или нажмите «Заполнить пример»."
        )
    )
