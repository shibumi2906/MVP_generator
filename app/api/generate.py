from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.models import GenerationRequest
from app.core.schemas import GenerationResponse
from app.services.mvp_service import generate_mvp
from app.storage.database import get_db


router = APIRouter()


@router.post("", response_model=GenerationResponse)
def generate(
    payload: GenerationRequest, db: Session = Depends(get_db)
) -> GenerationResponse:
    response, _ = generate_mvp(db, payload)
    return response



