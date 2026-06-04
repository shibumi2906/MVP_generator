from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.models import GenerationRequest
from app.services.mvp_service import generate_mvp
from app.storage.database import SessionLocal
from app.storage.models import Base, Generation
from app.utils.config import get_settings


def _setup_temp_db():
    engine = create_engine("sqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_mvp_service_mock_mode_saves_to_db(monkeypatch):
    settings = get_settings()
    monkeypatch.setenv("LLM_MODE", "mock")

    TestingSessionLocal = _setup_temp_db()
    db: Session = TestingSessionLocal()

    req = GenerationRequest(product_idea="A test product idea for MVP generation.")

    response, used_fallback = generate_mvp(db, req)

    assert response.generation_id
    assert response.result.title
    # Should work even if fallback is used internally
    assert isinstance(used_fallback, bool)

    # Ensure it was saved
    row = db.query(Generation).filter_by(id=response.generation_id).first()
    assert row is not None
    assert row.title == response.result.title


