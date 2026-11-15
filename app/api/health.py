from fastapi import APIRouter

from app.utils.config import get_settings

router = APIRouter()


@router.get("")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "llm_mode": settings.llm_mode,
        "generation_ready": settings.llm_mode == "mock"
        or (settings.llm_mode == "openai" and bool(settings.openai_api_key)),
    }
