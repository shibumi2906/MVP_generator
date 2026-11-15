from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.errors import GenerationError
from app.core.models import GenerationRequest
from app.core.schemas import GenerationResponse
from app.services.mvp_service import generate_mvp
from app.storage.database import get_db

router = APIRouter()


@router.post("", response_model=GenerationResponse)
def generate(payload: GenerationRequest, db: Session = Depends(get_db)) -> GenerationResponse:
    try:
        response = generate_mvp(db, payload)
    except GenerationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    return response
