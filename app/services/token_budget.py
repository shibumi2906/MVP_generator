from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from app.core.errors import GenerationError
from app.storage.database import SessionLocal
from app.storage.models import DailyTokenUsage

DAILY_TOKEN_LIMIT = 150_000
MAX_OUTPUT_TOKENS = 16_000
TIMEZONE = "Asia/Jerusalem"


def current_day() -> str:
    return datetime.now(ZoneInfo(TIMEZONE)).date().isoformat()


def budget_status() -> dict:
    day = current_day()
    with SessionLocal() as db:
        used = db.scalar(select(DailyTokenUsage.tokens).where(DailyTokenUsage.day == day)) or 0
    return {
        "day": day,
        "timezone": TIMEZONE,
        "limit": DAILY_TOKEN_LIMIT,
        "used_or_reserved": used,
        "remaining": max(0, DAILY_TOKEN_LIMIT - used),
    }


def reserve(input_tokens: int) -> tuple[str, int, int]:
    day = current_day()
    with SessionLocal.begin() as db:
        db.execute(insert(DailyTokenUsage).values(day=day, tokens=0).on_conflict_do_nothing())
        # Acquire the SQLite write lock before reading the shared balance.
        db.execute(
            update(DailyTokenUsage)
            .where(DailyTokenUsage.day == day)
            .values(tokens=DailyTokenUsage.tokens)
        )
        used = db.scalar(select(DailyTokenUsage.tokens).where(DailyTokenUsage.day == day))
        output_tokens = min(MAX_OUTPUT_TOKENS, DAILY_TOKEN_LIMIT - used - input_tokens)
        if output_tokens < 16:
            raise GenerationError(
                "daily_token_limit",
                "Daily token budget exhausted (150,000 input + output tokens). "
                "It resets at midnight Asia/Jerusalem. Shorten the brief or try tomorrow.",
                status_code=429,
            )
        reserved = input_tokens + output_tokens
        db.execute(
            update(DailyTokenUsage)
            .where(DailyTokenUsage.day == day)
            .values(tokens=DailyTokenUsage.tokens + reserved)
        )
    return day, reserved, output_tokens


def settle(day: str, reserved: int, actual: int) -> None:
    # Never refund more than the reservation; unexpected excess is still recorded.
    with SessionLocal.begin() as db:
        db.execute(
            update(DailyTokenUsage)
            .where(DailyTokenUsage.day == day)
            .values(tokens=DailyTokenUsage.tokens + max(0, actual) - reserved)
        )
