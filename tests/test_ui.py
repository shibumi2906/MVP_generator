from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.storage.models import Generation


def connect_ui(monkeypatch, client):
    def request(method, url, **kwargs):
        path = url.split(":8000", 1)[1]
        kwargs.pop("timeout", None)
        return client.request(method, path, **kwargs)

    monkeypatch.setattr("requests.request", request)
    monkeypatch.setattr("requests.get", lambda url, **kwargs: request("GET", url, **kwargs))


def test_ui_demo_and_failure_clear_previous_success(monkeypatch, client, db):
    connect_ui(monkeypatch, client)
    script = Path(__file__).resolve().parents[1] / "app" / "ui" / "streamlit_app.py"
    ui = AppTest.from_file(script).run()
    assert not ui.exception
    ui.text_area[0].set_value("A booking workspace for independent tutors")
    ui.button(key="FormSubmitter:mvp_form-Build starter pack →").click().run()
    assert not ui.exception
    assert any("Demo template" in message.value for message in ui.info)
    assert not ui.success
    assert db.query(Generation).count() == 1
    prepare = next(button for button in ui.button if button.label == "Prepare ZIP download")
    prepare.click().run()
    assert not ui.exception
    assert ui.session_state["zip_bytes"][:2] == b"PK"
    ui.run()
    assert ui.session_state["zip_bytes"][:2] == b"PK"
    # A new request fails: the previous demo must disappear from the workspace.
    from app.utils.config import get_settings

    monkeypatch.setenv("LLM_MODE", "openai")
    get_settings.cache_clear()
    ui.button(key="FormSubmitter:mvp_form-Build starter pack →").click().run()
    assert not ui.exception
    assert any("requires OPENAI_API_KEY" in error.value for error in ui.error)
    assert not ui.session_state.filtered_state.get("last_generation")
    assert not ui.session_state.filtered_state.get("zip_bytes")
    assert db.query(Generation).count() == 1
