import io
import json
import zipfile
from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.core.assumptions import build_demo_draft
from app.services import llm_client
from app.storage import repository
from app.storage.models import Generation
from app.utils.config import get_settings

PAYLOAD = {"product_idea": "A booking workspace for independent tutors"}


def fake_provider(monkeypatch, response=None, error=None):
    calls = []

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            self.responses = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def create(self, **kwargs):
            calls.append(kwargs)
            if error:
                raise error
            return response

    monkeypatch.setenv("LLM_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()
    monkeypatch.setattr(llm_client, "OpenAI", FakeOpenAI)
    return calls


def test_health(client):
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert data["llm_mode"] == "mock"
    assert data["generation_ready"] is True


def test_demo_history_detail_and_export_keep_provenance(client):
    response = client.post("/generate", json=PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    provenance = data["provenance"]
    assert provenance == {
        "mode": "mock",
        "source": "demo_template",
        "status": "demo",
        "model": None,
        "used_fallback": False,
        "consistency_checked": True,
    }
    history = client.get("/history").json()
    assert history[0]["provenance"] == provenance
    assert client.get(f"/history/{data['generation_id']}").json() == data
    exported = client.post("/export", json={"generation_id": data["generation_id"]})
    assert exported.status_code == 200
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        assert json.loads(archive.read("provenance.json")) == provenance
        assert json.loads(archive.read("bundle.json")) == data["result"]
        assert "demo_template" in archive.read("README.md").decode()
        assert "string title" in archive.read("ERD.md").decode()
        assert "title: string" in archive.read("API_SPEC.md").decode()


def test_openai_success_uses_supported_sdk_parameters(client, monkeypatch):
    draft = build_demo_draft(PAYLOAD["product_idea"]).model_dump_json()
    calls = fake_provider(monkeypatch, SimpleNamespace(status="completed", output_text=draft))
    response = client.post("/generate", json=PAYLOAD)
    assert response.status_code == 200
    assert response.json()["provenance"]["source"] == "openai"
    assert response.json()["provenance"]["status"] == "generated"
    assert calls[1]["text"] == {"format": {"type": "json_object"}}
    assert "response_format" not in calls[1]
    assert calls[0]["max_retries"] == 0


@pytest.mark.parametrize(
    "error, code, status",
    [
        (RuntimeError("private provider error and key"), "provider_error", 502),
        (
            APITimeoutError(request=httpx.Request("POST", "https://example.com")),
            "provider_timeout",
            504,
        ),
        (
            APIConnectionError(request=httpx.Request("POST", "https://example.com")),
            "provider_unavailable",
            503,
        ),
        (
            RateLimitError(
                "private",
                response=httpx.Response(429, request=httpx.Request("POST", "https://example.com")),
                body=None,
            ),
            "provider_rate_limit",
            503,
        ),
        (
            AuthenticationError(
                "private",
                response=httpx.Response(401, request=httpx.Request("POST", "https://example.com")),
                body=None,
            ),
            "provider_error",
            502,
        ),
    ],
)
def test_provider_failure_never_becomes_demo(client, db, monkeypatch, error, code, status):
    fake_provider(monkeypatch, error=error)
    response = client.post("/generate", json=PAYLOAD)
    assert response.status_code == status
    detail = response.json()["detail"]
    assert detail["code"] == code
    assert detail["mode"] == "openai"
    assert detail["status"] == "failed"
    assert detail["used_fallback"] is False
    assert "private" not in response.text
    assert "result" not in response.json()
    assert db.query(Generation).count() == 0


@pytest.mark.parametrize(
    "response, code",
    [
        (
            SimpleNamespace(status="completed", output_text="broken json"),
            "invalid_provider_response",
        ),
        (SimpleNamespace(status="incomplete", output_text="{}"), "incomplete_response"),
        (SimpleNamespace(status="completed", output_text=""), "incomplete_response"),
        (
            SimpleNamespace(status="completed", output_text='{"title":"invalid"}'),
            "invalid_specification",
        ),
    ],
)
def test_invalid_provider_output_is_not_saved(client, db, monkeypatch, response, code):
    fake_provider(monkeypatch, response=response)
    result = client.post("/generate", json=PAYLOAD)
    assert result.status_code == 502
    assert result.json()["detail"]["code"] == code
    assert db.query(Generation).count() == 0


def test_inconsistent_documents_are_not_saved(client, db, monkeypatch):
    raw = build_demo_draft(PAYLOAD["product_idea"]).model_dump()
    raw["contract"]["endpoints"][0]["response_fields"].append("nonexistent")
    fake_provider(
        monkeypatch, response=SimpleNamespace(status="completed", output_text=json.dumps(raw))
    )
    result = client.post("/generate", json=PAYLOAD)
    assert result.status_code == 502
    assert "unknown field Item.nonexistent" in str(result.json()["detail"]["issues"])
    assert db.query(Generation).count() == 0


def test_missing_key_does_not_select_mock(client, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "openai")
    get_settings.cache_clear()
    result = client.post("/generate", json=PAYLOAD)
    assert result.status_code == 503
    assert result.json()["detail"]["code"] == "missing_api_key"


def test_unknown_mode_is_an_error(client, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "typo")
    get_settings.cache_clear()
    assert client.post("/generate", json=PAYLOAD).status_code == 503


def test_legacy_rows_remain_exportable_and_are_unverified(client, db):
    old = (
        build_demo_draft("A legacy specification idea").to_bundle().model_dump(exclude={"contract"})
    )
    repository.save_generation(db, "old", datetime.now(UTC), "Legacy", "{}", json.dumps(old))
    data = client.get("/history/old").json()
    assert data["provenance"]["source"] == "legacy_unknown"
    assert data["provenance"]["consistency_checked"] is False
    assert client.get("/history").json()[0]["provenance"]["status"] == "unverified"
    exported = client.post("/export", json={"generation_id": "old"})
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        assert "legacy_unknown" in archive.read("README.md").decode()


def test_bad_input_and_missing_records(client):
    assert client.post("/generate", json={"product_idea": "          "}).status_code == 422
    assert client.get("/history/missing").status_code == 404
    assert client.post("/export", json={"generation_id": "missing"}).status_code == 404
    assert client.get("/history?limit=21").status_code == 422
