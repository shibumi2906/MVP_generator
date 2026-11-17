from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.errors import GenerationError
from app.services import token_budget
from app.storage.models import Base


def test_reserve_caps_output_to_remaining_and_blocks_when_full():
    day, reserved, output = token_budget.reserve(140_000)
    assert reserved == 150_000
    assert output == 10_000
    with pytest.raises(GenerationError) as error:
        token_budget.reserve(1)
    assert error.value.status_code == 429
    assert token_budget.budget_status()["remaining"] == 0
    token_budget.settle(day, reserved, 142_000)
    assert token_budget.budget_status()["remaining"] == 8_000


def test_daily_reset_and_late_response_use_original_day(monkeypatch):
    monkeypatch.setattr(token_budget, "current_day", lambda: "2026-11-17")
    day, reserved, _ = token_budget.reserve(100)
    monkeypatch.setattr(token_budget, "current_day", lambda: "2026-11-18")
    assert token_budget.budget_status()["remaining"] == 150_000
    token_budget.settle(day, reserved, 1_000)
    assert token_budget.budget_status()["remaining"] == 150_000
    monkeypatch.setattr(token_budget, "current_day", lambda: day)
    assert token_budget.budget_status()["used_or_reserved"] == 1_000


def test_persistent_budget_handles_concurrent_requests(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'budget.db'}")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(token_budget, "SessionLocal", sessionmaker(bind=engine))

    def attempt(_):
        try:
            return token_budget.reserve(10_000)[1]
        except GenerationError:
            return 0

    with ThreadPoolExecutor(max_workers=8) as pool:
        reservations = list(pool.map(attempt, range(12)))
    assert sum(reservations) == 150_000
    engine.dispose()
    restarted_engine = create_engine(f"sqlite:///{tmp_path / 'budget.db'}")
    monkeypatch.setattr(token_budget, "SessionLocal", sessionmaker(bind=restarted_engine))
    assert token_budget.budget_status()["remaining"] == 0
    restarted_engine.dispose()
