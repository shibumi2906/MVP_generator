from fastapi import APIRouter

from app.utils.config import get_settings


router = APIRouter()


@router.get("")
def health():
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "version": settings.version}



