import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name: str = "MVP Generator"
    version: str = "0.2.0"

    openai_api_key: str | None
    openai_model: str
    llm_mode: str

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY") or None
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.llm_mode = os.getenv("LLM_MODE", "mock").strip().lower()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
