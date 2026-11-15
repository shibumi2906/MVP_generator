from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.schemas import GenerationResponse, HistoryItem
from app.services.history_service import list_history
from app.services.saved_generation import read_saved_generation
from app.storage import repository
from app.storage.database import get_db

router = APIRouter()


@router.get("", response_model=list[HistoryItem])
def history(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[HistoryItem]:
    return list_history(db, limit=limit)


@router.get("/{generation_id}", response_model=GenerationResponse)
def history_detail(generation_id: str, db: Session = Depends(get_db)) -> GenerationResponse:
    row = repository.get_generation(db, generation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Generation not found")
    return read_saved_generation(row)
