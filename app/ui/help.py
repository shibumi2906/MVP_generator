from pathlib import Path

import streamlit as st

from app.ui.i18n import language, tr

EXAMPLE_BRIEF = {
    "product_idea": "Сервис для частного репетитора: хранить список учеников, записывать их "
    "на занятия и видеть расписание на неделю. Сейчас всё ведётся в блокноте, "
    "из-за чего занятия теряются и пересекаются.",
    "target_users": "Частные репетиторы, которые работают самостоятельно",
    "core_user_flow": "Добавить ученика → назначить дату и длительность занятия → "
    "посмотреть неделю → при необходимости отменить занятие",
    "constraints": "Один разработчик, одна неделя. Локальное приложение для одного пользователя. "
    "Без оплаты, уведомлений и внешних интеграций.",
    "output_stack": "FastAPI + SQLite + Streamlit",
}


EXAMPLE_BRIEF_EN = {
    "product_idea": "A workspace for independent tutors to manage students, schedule lessons "
    "and view a weekly timetable. They currently use a notebook and sometimes lose or double-book lessons.",
    "target_users": "Independent tutors who work on their own",
    "core_user_flow": "Add a student → schedule a lesson with date and duration → "
    "view the week → cancel a lesson if needed",
    "constraints": "One developer, one week. Local single-user application. "
    "No payments, notifications or external integrations.",
    "output_stack": "FastAPI + SQLite + Streamlit",
}


def fill_example() -> None:
    st.session_state.update(EXAMPLE_BRIEF_EN if language() == "en" else EXAMPLE_BRIEF)


def open_help() -> None:
    st.session_state["show_help"] = True


def render_help() -> None:
    with st.expander(
        tr("Помощь: от идеи до готового плана"), expanded=st.session_state.get("show_help", False)
    ):
        st.caption(
            tr(
                "Переключение языка меняет интерфейс. Текст идеи и созданные документы сохраняются на исходном языке."
            )
        )
        st.markdown(Path(__file__).with_name(f"help_{language()}.md").read_text(encoding="utf-8"))
