import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


# Load .env from project root reliably (…/project/app/utils/config.py -> …/project/.env)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


class Settings:
    app_name: str = "MVP Generator"
    version: str = "0.1.0"

    openai_api_key: str | None
    openai_model: str
    llm_mode: str

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY") or None
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        # If LLM_MODE is not set, choose openai when key exists, otherwise mock.
        self.llm_mode = os.getenv("LLM_MODE") or ("openai" if self.openai_api_key else "mock")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


