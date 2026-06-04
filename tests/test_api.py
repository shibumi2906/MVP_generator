from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "MVP Generator"
    assert data["version"] == "0.1.0"


def test_generate_mock_mode():
    payload = {
        "product_idea": "API test product idea for MVP.",
        "target_users": None,
        "core_user_flow": None,
        "constraints": None,
        "output_stack": "FastAPI + SQLite + Streamlit",
    }
    resp = client.post("/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "generation_id" in data
    assert "created_at" in data
    assert "result" in data
    assert data["result"]["title"]


