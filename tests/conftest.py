import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.storage.database import get_db
from app.storage.models import Base
from app.utils.config import get_settings


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db, monkeypatch):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr("app.main.create_tables", lambda: None)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
