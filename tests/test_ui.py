from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.storage.models import Generation


def connect_ui(monkeypatch, client):
    def request(method, url, **kwargs):
        path = url.split(":8000", 1)[1]
        kwargs.pop("timeout", None)
        return client.request(method, path, **kwargs)

    monkeypatch.setattr("requests.request", request)
    monkeypatch.setattr("requests.get", lambda url, **kwargs: request("GET", url, **kwargs))


def test_example_fills_form_without_generation_and_help_keeps_input(monkeypatch, client, db):
    from app.ui.help import EXAMPLE_BRIEF

    connect_ui(monkeypatch, client)
    script = Path(__file__).resolve().parents[1] / "app" / "ui" / "streamlit_app.py"
    ui = AppTest.from_file(script).run()
    next(button for button in ui.button if button.label == "Заполнить пример").click().run()
    assert not ui.exception
    assert ui.text_area(key="product_idea").value == EXAMPLE_BRIEF["product_idea"]
    assert ui.text_area(key="constraints").value == EXAMPLE_BRIEF["constraints"]
    assert ui.text_input(key="target_users").value == EXAMPLE_BRIEF["target_users"]
    assert db.query(Generation).count() == 0
    ui.text_area(key="product_idea").set_value("Моя собственная идея продукта")
    next(button for button in ui.button if button.label == "Как пользоваться").click().run()
    assert not ui.exception
    assert ui.session_state["show_help"] is True
    assert ui.text_area(key="product_idea").value == "Моя собственная идея продукта"
    assert db.query(Generation).count() == 0


@pytest.mark.parametrize("language", ["ru", "en"])
def test_ui_demo_and_failure_clear_previous_success(monkeypatch, client, db, language):
    connect_ui(monkeypatch, client)
    script = Path(__file__).resolve().parents[1] / "app" / "ui" / "streamlit_app.py"
    ui = AppTest.from_file(script)
    ui.query_params["lang"] = language
    ui.run()
    assert not ui.exception
    ui.text_area[0].set_value("A booking workspace for independent tutors")
    ui.button(key="generate").click().run()
    assert not ui.exception
    assert any(("Демо" if language == "ru" else "Demo") in message.value for message in ui.info)
    assert not ui.success
    assert db.query(Generation).count() == 1
    ui.button(key="prepare_zip").click().run()
    assert not ui.exception
    assert ui.session_state["zip_bytes"][:2] == b"PK"
    ui.run()
    assert ui.session_state["zip_bytes"][:2] == b"PK"
    # A new request fails: the previous demo must disappear from the workspace.
    from app.utils.config import get_settings

    monkeypatch.setenv("LLM_MODE", "openai")
    get_settings.cache_clear()
    ui.button(key="generate").click().run()
    assert not ui.exception
    expected = "не задан ключ OpenAI" if language == "ru" else "requires OPENAI_API_KEY"
    assert any(expected in error.value for error in ui.error)
    assert "last_generation" not in ui.session_state
    assert "zip_bytes" not in ui.session_state
    assert db.query(Generation).count() == 1


def test_language_switch_keeps_brief_result_and_zip_without_generating(monkeypatch, client, db):
    connect_ui(monkeypatch, client)
    script = Path(__file__).resolve().parents[1] / "app" / "ui" / "streamlit_app.py"
    ui = AppTest.from_file(script).run()
    ui.text_area(key="product_idea").set_value("Моя идея сервиса бронирования")
    ui.text_input(key="target_users").set_value("Частные репетиторы")
    ui.text_area(key="constraints").set_value("Без платежей")
    ui.selectbox(key="language").select("en").run()
    assert not ui.exception
    selected_language = ui.query_params["lang"]
    assert (
        selected_language[-1] if isinstance(selected_language, list) else selected_language
    ) == "en"
    assert ui.title[0].value == "Turn your idea into a development plan"
    assert ui.text_area(key="product_idea").value == "Моя идея сервиса бронирования"
    assert ui.text_input(key="target_users").value == "Частные репетиторы"
    assert ui.text_area(key="constraints").value == "Без платежей"
    assert any("### What you can do here" in md.value for md in ui.markdown)
    assert db.query(Generation).count() == 0
    ui.button(key="generate").click().run()
    assert not ui.exception
    assert any("Demo · Generic" in info.value for info in ui.info)
    assert [tab.label for tab in ui.tabs] == [
        "Requirements",
        "Architecture",
        "Data model",
        "API",
        "Delivery plan",
        "Assumptions",
    ]
    ui.button(key="prepare_zip").click().run()
    result = ui.session_state["last_generation"]
    archive = ui.session_state["zip_bytes"]
    ui.selectbox(key="language").select("ru").run()
    assert not ui.exception
    assert ui.session_state["last_generation"] == result
    assert ui.session_state["zip_bytes"] == archive
    assert ui.text_area(key="product_idea").value == "Моя идея сервиса бронирования"
    assert ui.tabs[0].label == "Требования"
    assert any(header.value == "Проблема" for header in ui.subheader)
    assert db.query(Generation).count() == 1


@pytest.mark.parametrize("requested_language", ["en", "ru", "invalid"])
def test_language_url_and_example(monkeypatch, client, db, requested_language):
    from app.ui.help import EXAMPLE_BRIEF, EXAMPLE_BRIEF_EN

    connect_ui(monkeypatch, client)
    script = Path(__file__).resolve().parents[1] / "app" / "ui" / "streamlit_app.py"
    ui = AppTest.from_file(script)
    ui.query_params["lang"] = requested_language
    ui.run()
    label = "Fill in an example" if requested_language == "en" else "Заполнить пример"
    next(button for button in ui.button if button.label == label).click().run()
    assert not ui.exception
    expected = EXAMPLE_BRIEF_EN if requested_language == "en" else EXAMPLE_BRIEF
    assert ui.text_area(key="product_idea").value == expected["product_idea"]
    assert db.query(Generation).count() == 0
